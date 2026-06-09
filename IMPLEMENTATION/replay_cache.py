"""
Shared-replay-cache seam (docs/restructure/16_shared_replay_cache_spec.md,
increment VL-076, artifact 13 Phase B step B3).

Purpose: give the in-window exactly-once replay defense built at VL-066 a seam,
so the per-decision de-dup that lives today as the inline `app.state.seen` dict
in reference_target.py can instead be backed by a CROSS-INSTANCE store. A
horizontally-scaled deployment running N target processes keeps N independent
in-process dicts, so a `decision_id` can be honored once on each instance -
replay survives across instances. A single shared cache closes that gap.

The seam is one atomic question, per decision_id:

    check_and_claim(decision_id, not_after, *, now=None) -> bool

True  = decision_id was not seen and is now claimed -> the caller may HONOR.
False = decision_id was already claimed            -> the caller must REFUSE
                                                       (REF_VERIFY_REPLAY).

`not_after` is the already-parsed expiry of the decision: a timezone-aware
datetime, or None when the decision carries no parseable not_after. Parsing the
wire `not_after` string into a datetime stays at the CALL site (the target),
mirroring the VL-066 code; this module is format-agnostic and stores only the
parsed expiry.

Build-then-wire (the project discipline since VL-025; the transport seam VL-039
was wired only at VL-060): this module has NO callers at the commit that
introduces it. reference_target.py is NOT changed here. Wiring the target to take
an injected `replay_cache` - defaulting to a fresh InMemoryReplayCache, which
reproduces today's inline-dict behavior exactly - is a later increment with its
own VL.

No new canonical invariant (canon section 14): replay defense is the acting
party's stateful concern, not a canonical invariant (verify_envelope stays pure
and does not emit REF_VERIFY_REPLAY - VL-066). This seam only changes WHERE the
seen-set lives (process-local dict vs shared store); it never touches WHAT the
gate decides or WHAT the target verifies.

Fail-closed (canon section 9): check_and_claim never returns True on doubt. True
is reserved for a positively-fresh, positively-claimed decision_id. An external
store that cannot decide (a backend error) raises through to the target's
existing per-request try/except, which maps it to a refusal - the call is NOT
honored on an undecidable claim.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class ReplayCache(Protocol):
    """The seam contract. An implementation answers, atomically per decision_id,
    whether this decision may be honored (newly claimed) or must be refused as a
    replay (already claimed)."""

    def check_and_claim(
        self,
        decision_id: str,
        not_after: Optional[datetime],
        *,
        now: Optional[datetime] = None,
    ) -> bool:  # pragma: no cover - structural contract
        ...


@runtime_checkable
class ReplayStore(Protocol):
    """The cross-process primitive an ExternalStoreReplayCache delegates to. A
    single atomic claim, shared by every target process. Maps directly onto a
    real backend: Redis `SET decision_id 1 NX EX <ttl>`, Memcached `add`, or an
    INSERT against a unique key. Returns True iff decision_id was newly claimed
    (not already present)."""

    def claim(
        self,
        decision_id: str,
        expiry: Optional[datetime],
        now: datetime,
    ) -> bool:  # pragma: no cover - structural contract
        ...


def _utcnow(now: Optional[datetime]) -> datetime:
    return now if now is not None else datetime.now(timezone.utc)


class InMemoryReplayCache:
    """Process-local replay cache - behavior-identical to the VL-066 inline
    `app.state.seen` dict in reference_target.py.

    On each claim: prune every entry whose expiry is non-None and has passed
    (`<= now`), then refuse (return False) a decision_id still present, else
    record `decision_id -> not_after` and honor (return True). An entry with a
    None expiry (no parseable not_after) is never pruned by time and is retained
    until the process drops it.

    Constructed fresh per process and injected as the default, this reproduces
    today's behavior exactly - the load-bearing property the future wiring step
    relies on. Injected as a SINGLE shared instance across call sites, it closes
    the cross-instance replay gap in-process (a true cross-PROCESS store is the
    ExternalStoreReplayCache path).
    """

    def __init__(self) -> None:
        self._seen: Dict[str, Optional[datetime]] = {}

    def check_and_claim(
        self,
        decision_id: str,
        not_after: Optional[datetime],
        *,
        now: Optional[datetime] = None,
    ) -> bool:
        current = _utcnow(now)
        seen = self._seen
        for k in [k for k, exp in seen.items() if exp is not None and exp <= current]:
            del seen[k]
        if decision_id in seen:
            return False
        seen[decision_id] = not_after
        return True


class ExternalStoreReplayCache:
    """Cross-process replay cache: delegates the atomic claim to an injected
    shared store (a ReplayStore). Because the store is shared by every target
    process, the claim is global and exactly-once holds across instances.

    The adapter holds no state of its own; the prune/TTL discipline lives in the
    backing store (Redis EX, a TTL column, etc.). A store that raises on `claim`
    propagates the exception (fail-closed: the caller refuses rather than honors
    on an undecidable claim)."""

    def __init__(self, store: ReplayStore) -> None:
        self._store = store

    def check_and_claim(
        self,
        decision_id: str,
        not_after: Optional[datetime],
        *,
        now: Optional[datetime] = None,
    ) -> bool:
        current = _utcnow(now)
        return self._store.claim(decision_id, not_after, current)
