# 16 - Shared-replay-cache seam: cross-instance exactly-once

Repo path: docs/restructure/16_shared_replay_cache_spec.md. Increment VL-076 (B3,
artifact 13 Phase B). Adjacent to `12_g5_transport_design.md` (the transport seam, the
structural precedent this mirrors) and to the replay defense built at VL-066. B3 is the
third Phase-B item: it gives the in-window exactly-once property a seam so it can be backed
by a cross-instance store, instead of the single in-process dict it lives in today.

## 1. Purpose and scope

The replay defense (VL-066) is the inline `app.state.seen` dict in
`IMPLEMENTATION/reference_target.py`: on each honored call the target prunes expired
`decision_id` entries, refuses a `decision_id` it has already honored
(`REF_VERIFY_REPLAY`), and records the new `decision_id -> not_after`. The window bounds the
set - an entry is pruned once its `not_after` passes, past which the freshness check refuses
it anyway - so exactly-once holds over the freshness window. The honest ceiling that
comment already names: the dict is PER-INSTANCE and PER-PROCESS. A horizontally-scaled
deployment running N target processes keeps N independent seen-sets, so the same
`decision_id` can be honored once on each instance - replay survives across instances. The
property is "exactly-once per process," not "exactly-once."

This is the gap the artifact-13 directive names B3: a SHARED replay cache so in-window
exactly-once survives beyond a single process.

In scope (VL-076): a replay-cache seam - a small interface (`check_and_claim`) that the
de-dup step is expressed against; an in-memory default (`InMemoryReplayCache`) that is
behavior-identical to today's inline dict; and an external-store adapter
(`ExternalStoreReplayCache`) that delegates the atomic claim to an injected store, so a
cross-process backend (Redis `SET key val NX EX ttl`, Memcached `add`, a row with a unique
constraint) plugs in by CONFIGURATION, never by changing the target's decision code. The
acceptance test proves a single shared cache catches a cross-instance replay that two
independent in-memory caches miss.

Out of scope (named, not built):
- Wiring the seam into `reference_target.py`. Per build-then-wire (the project discipline
  since VL-025; the transport seam VL-039 was wired only at VL-060), this increment
  introduces the seam with NO caller. `reference_target.py` is byte-unchanged, so the
  default path, the g4/g5 runners, and the existing replay test are untouched. Wiring the
  target to take an injected `replay_cache` (defaulting to a fresh `InMemoryReplayCache`,
  which preserves today's behavior exactly) is a later increment with its own VL.
- A real Redis / Memcached process. The adapter targets the atomic-claim PRIMITIVE those
  stores expose; standing one up is deployment configuration, exactly as the transport seam
  named TLS/CA material in the environment without committing a CA. The hermetic test drives
  the adapter with an in-memory fake store shared across two app instances.
- The G5 real-transport floor and a real external attacker (the binding NOT-READY reason);
  unchanged here.

## 2. The seam contract

A replay cache answers one question atomically, per `decision_id`:

    check_and_claim(decision_id, not_after, *, now=None) -> bool

It returns True if `decision_id` was NOT seen and is now claimed (the caller may honor), and
False if `decision_id` was already claimed (the caller must refuse as a replay). `not_after`
is the already-parsed expiry of this decision: a timezone-aware `datetime`, or `None` when
the decision carries no parseable `not_after` (no expiry - the entry is retained until the
process / store drops it). `now` is injectable for deterministic tests; absent, the cache
reads `datetime.now(timezone.utc)`.

Parsing the wire `not_after` string into a `datetime` stays at the CALL site (the target),
mirroring today's code; the cache is format-agnostic and stores only the parsed expiry. The
method is the whole seam: the de-dup step becomes `if not cache.check_and_claim(...): refuse`.

## 3. The two implementations

`InMemoryReplayCache` reproduces the VL-066 inline dict exactly: prune every entry whose
expiry is non-`None` and `<= now`, return False if `decision_id` is still present, else store
`decision_id -> not_after` and return True. Constructed fresh per process, injected as the
default, it is byte-behavior-identical to the current code - the load-bearing property a
future wiring step relies on.

`ExternalStoreReplayCache` delegates to an injected store implementing a single atomic
primitive:

    store.claim(decision_id, expiry, now) -> bool   # True iff newly claimed

This is the seam's cross-process shape. `claim` maps directly onto a real backend:
Redis `SET decision_id 1 NX EX <ttl>` (ttl computed from `expiry - now`; no EX when
`expiry` is `None`), Memcached `add`, or an `INSERT` against a unique key. Because the store
is shared by every target process, the claim is global and exactly-once holds across
instances. The adapter itself holds no state; it is hermetically testable against a fake
in-memory store.

## 4. Fail-closed (canon section 9)

The seam preserves the fail-closed posture. A cache that cannot decide must not let a call
through: an `ExternalStoreReplayCache` whose backing store raises (network/Redis error) lets
the exception propagate to the target's existing per-request try/except, which maps it to a
refusal - the call is NOT honored on an undecidable claim. `check_and_claim` never returns
True on doubt; True is reserved for a positively-fresh, positively-claimed `decision_id`.

## 5. No new canonical invariant (canon section 14)

Replay defense is the acting party's stateful concern, not a canonical invariant
(verify_envelope stays pure and does not emit `REF_VERIFY_REPLAY` - VL-066). This seam only
changes WHERE the seen-set lives (process-local dict vs shared store); it does not change
WHAT the gate decides or WHAT the target verifies. No canon, evaluator, MANIFEST, or envelope
contract changes.

## 6. Honest ceiling

The seam makes cross-instance exactly-once REACHABLE; it does not by itself deliver it on the
default path (unwired this increment) and it does not provide the shared store (that is
deployment configuration). A shared cache is only as available as its backend: a store
outage fails closed (refuse), which trades availability for the exactly-once guarantee -
the correct trade for an admission gate, named here so a deployment chooses it knowingly.
Exactly-once remains bounded by the freshness window in either implementation; the window,
not the cache, is what keeps the set finite.

## 7. Acceptance (VL-076)

- `InMemoryReplayCache` honors a `decision_id` once and refuses the exact replay; prunes an
  expired entry so a post-expiry re-presentation is treated as fresh (matching VL-066, where
  freshness would independently refuse it); retains a `None`-expiry entry across prunes.
- A single `InMemoryReplayCache` SHARED between two app-instance call sites catches the
  cross-instance replay; two SEPARATE `InMemoryReplayCache` instances do NOT (the contrast
  that pins the gap, mirroring VL-074's `test_byte_anchor_model_has_no_freshness`).
- `ExternalStoreReplayCache` over one shared fake store catches a cross-instance replay; a
  store that raises on `claim` propagates (fail-closed, never a silent honor).
- `reference_target.py` is byte-unchanged (`git diff` empty); the full suite stays green.
