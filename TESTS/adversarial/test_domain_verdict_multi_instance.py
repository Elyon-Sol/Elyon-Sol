"""Multi-instance replay for the domain verdict (deployment-topology verification).

verify_verdict() is stateless, so single-use lives in claim_verdict_once() against
the ReplayCache seam. Under >1 gate worker/replica a PER-PROCESS cache cannot
enforce it: each process would honor the same verdict once. This file verifies the
two properties that matter for a real topology:

  (a) with a SHARED store, a verdict claimed on instance A is refused on instance B;
  (b) without one, a deployment that declares itself multi-instance FAILS CLOSED at
      construction (the R-02 declare-or-fail guard) rather than silently handing out
      per-process caches.
"""
import os
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.domain_verdict import (
    build_verdict, sign_verdict, claim_verdict_once,
    VERDICT_SAFE, ACCEPT_VERDICT_VALID, REF_VERDICT_REPLAY,
)
from IMPLEMENTATION.replay_cache import (
    InMemoryReplayCache, ExternalStoreReplayCache, replay_cache_from_env,
)

DEC = "d" * 64
AUTH = "AUTH1"


class _SharedStore:
    """Stands in for Redis SET NX EX / a unique-key INSERT: one atomic claim,
    visible to every instance that points at it."""

    def __init__(self):
        self.claimed = {}

    def claim(self, decision_id, expiry, now):
        if decision_id in self.claimed:
            return False
        self.claimed[decision_id] = expiry
        return True


def _verdict(verdict_id="vd-multi"):
    sk = Ed25519PrivateKey.generate()
    return sign_verdict(build_verdict(
        decision_sha256=DEC, domain="d", verdict=VERDICT_SAFE, verdict_id=verdict_id,
        not_after=datetime.now(timezone.utc) + timedelta(seconds=300)), sk, AUTH)


# --- (a) a shared store enforces single-use ACROSS instances -----------------

def test_shared_store_catches_cross_instance_replay():
    """The property a real deployment needs: two gate replicas, one shared store,
    a verdict released exactly once in total."""
    store = _SharedStore()
    instance_a = ExternalStoreReplayCache(store)
    instance_b = ExternalStoreReplayCache(store)   # a DIFFERENT process/replica

    v = _verdict()
    first = claim_verdict_once(v, instance_a)
    second = claim_verdict_once(v, instance_b)

    assert first["accepted"] is True and first["reason"] == ACCEPT_VERDICT_VALID
    assert second["accepted"] is False and second["reason"] == REF_VERDICT_REPLAY


def test_distinct_verdicts_are_independent_across_instances():
    store = _SharedStore()
    a, b = ExternalStoreReplayCache(store), ExternalStoreReplayCache(store)
    assert claim_verdict_once(_verdict("vd-1"), a)["accepted"] is True
    assert claim_verdict_once(_verdict("vd-2"), b)["accepted"] is True


# --- the failure this guards against ----------------------------------------

def test_per_process_caches_do_NOT_enforce_single_use_across_instances():
    """Documents WHY the shared store is required: two per-process caches each
    honor the same verdict once. This is the behavior the R-02 guard exists to
    prevent a deployment from getting silently."""
    a, b = InMemoryReplayCache(), InMemoryReplayCache()
    v = _verdict()
    assert claim_verdict_once(v, a)["accepted"] is True
    assert claim_verdict_once(v, b)["accepted"] is True   # released TWICE


# --- (b) declare-or-fail: multi-instance without a shared store fails closed --

def test_declared_multi_instance_without_shared_store_fails_closed(monkeypatch):
    monkeypatch.delenv("ELYON_REPLAY_REDIS_URL", raising=False)
    monkeypatch.setenv("ELYON_REPLAY_MULTI_INSTANCE", "1")
    with pytest.raises(RuntimeError, match="MULTI_INSTANCE"):
        replay_cache_from_env()


@pytest.mark.parametrize("flag", ["1", "true", "yes", "TRUE", "Yes"])
def test_declare_or_fail_accepts_the_documented_spellings(monkeypatch, flag):
    monkeypatch.delenv("ELYON_REPLAY_REDIS_URL", raising=False)
    monkeypatch.setenv("ELYON_REPLAY_MULTI_INSTANCE", flag)
    with pytest.raises(RuntimeError):
        replay_cache_from_env()


def test_single_instance_default_unchanged(monkeypatch):
    """No flag, no shared store -> the per-process default, as before."""
    monkeypatch.delenv("ELYON_REPLAY_REDIS_URL", raising=False)
    monkeypatch.delenv("ELYON_REPLAY_MULTI_INSTANCE", raising=False)
    assert isinstance(replay_cache_from_env(), InMemoryReplayCache)


def test_the_gate_verdict_cache_inherits_the_guard(monkeypatch):
    """pep builds _VERDICT_REPLAY via replay_cache_from_env(), so a gate that
    declares multi-instance without a shared store cannot even import."""
    import importlib
    monkeypatch.delenv("ELYON_REPLAY_REDIS_URL", raising=False)
    monkeypatch.setenv("ELYON_REPLAY_MULTI_INSTANCE", "1")
    import IMPLEMENTATION.pep as pep
    try:
        with pytest.raises(RuntimeError):
            importlib.reload(pep)
    finally:
        os.environ.pop("ELYON_REPLAY_MULTI_INSTANCE", None)
        importlib.reload(pep)
