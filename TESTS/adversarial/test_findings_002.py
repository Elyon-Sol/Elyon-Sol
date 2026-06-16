"""Regression tests for the Cursor white-box review fixes (R-01, P-01).

R-01: InMemoryReplayCache.check_and_claim must be atomic - the ext-authz sidecar
runs the gate check in a threadpool, so a check-then-set without a lock lets two
threads both claim the same decision_id (a concurrent single-use bypass).

P-01: a duplicate attestation/interaction header is ambiguous (which value is
verified would depend on header ordering); the sidecar/target must treat a
duplicate as absent and fail closed, never silently honor the first value.
"""

import threading
from datetime import datetime, timedelta, timezone

from starlette.requests import Request

from IMPLEMENTATION.replay_cache import InMemoryReplayCache
from IMPLEMENTATION.authz_sidecar import (
    default_interaction_extractor,
    INTERACTION_HEADER,
)


# --- R-01: concurrent single-use ------------------------------------------------

def test_r01_inmemory_cache_honors_one_concurrent_claim():
    """Under maximal contention, exactly ONE of N concurrent claims of the same
    decision_id may be honored. Without the lock this intermittently honors >1."""
    not_after = datetime.now(timezone.utc) + timedelta(seconds=300)
    for _ in range(40):  # repeat rounds to surface a race if the lock regressed
        cache = InMemoryReplayCache()
        n = 32
        barrier = threading.Barrier(n)
        results = []
        guard = threading.Lock()

        def worker():
            barrier.wait()  # release all threads as simultaneously as possible
            ok = cache.check_and_claim("decision-xyz", not_after)
            with guard:
                results.append(ok)

        threads = [threading.Thread(target=worker) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        honored = results.count(True)
        assert honored == 1, "single-use violated: %d concurrent claims honored" % honored


# --- P-01: ambiguous duplicate headers -----------------------------------------

def _request(header_pairs):
    """Build a minimal Starlette Request carrying the given (name, value) headers,
    duplicates allowed (the ASGI scope header list preserves duplicates)."""
    raw = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in header_pairs]
    return Request({"type": "http", "method": "POST", "path": "/authz",
                    "query_string": b"", "headers": raw})


def test_p01_single_interaction_header_parses():
    req = _request([(INTERACTION_HEADER, '{"AP": ["read"], "OP": ["x"]}')])
    assert default_interaction_extractor(req) == {"AP": ["read"], "OP": ["x"]}


def test_p01_duplicate_interaction_header_is_absent():
    req = _request([(INTERACTION_HEADER, '{"AP": ["read"]}'),
                    (INTERACTION_HEADER, '{"AP": ["admin"]}')])
    assert default_interaction_extractor(req) is None


def test_r01_lock_serializes_concurrent_claims():
    """Deterministic R-01 revert-catcher: force two threads to interleave at the
    check-then-set via a blocking membership check. With the lock, exactly one
    claims; remove the lock and both observe 'absent' and both claim (-> 2)."""
    import time
    cache = InMemoryReplayCache()
    entered = threading.Event()
    release = threading.Event()

    class BlockingSeen(dict):
        def __contains__(self, key):
            entered.set()        # inside the critical region
            release.wait(2.0)    # hold to widen the window
            return dict.__contains__(self, key)

    cache._seen = BlockingSeen()
    results = []

    def claim():
        results.append(cache.check_and_claim("decision-xyz", None))

    t1 = threading.Thread(target=claim)
    t2 = threading.Thread(target=claim)
    t1.start()
    assert entered.wait(2.0)     # t1 is inside __contains__ (holding the lock, if present)
    t2.start()
    time.sleep(0.2)              # if unlocked, t2 reaches __contains__ too
    release.set()
    t1.join(2.0); t2.join(2.0)
    assert results.count(True) == 1, \
        "R-01: %d concurrent claims honored (lock missing?)" % results.count(True)
