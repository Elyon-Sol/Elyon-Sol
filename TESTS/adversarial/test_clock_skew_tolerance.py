"""
VL-075 (B2, artifact 13 Phase B) tests for cross-host clock-skew tolerance.

Derivation: docs/restructure/15_clock_skew_tolerance_spec.md + canon sections
9 (fail-closed) / 13 (revalidation) / 14 (no new invariant). Every consume-side
freshness check gains a non-negative `clock_skew` (timedelta, default 0) that
widens the honored time window SYMMETRICALLY by clock_skew on both ends:

  - expiry  now < not_after            -> now < not_after + clock_skew
  - start   not_before <= now          -> not_before - clock_skew <= now

The default (timedelta(0)) is byte-behavior-identical to the strict pre-VL-075
checks (covered by the existing freshness suites and re-pinned here at the
boundary). The four loci: verify_envelope decision not_after (step 1.5b) and
issuer-key validity window (step 1.5), and the three signed-record readers'
record-level not_after (published / key / root).

Run from the repo root (build_envelope reads CANON/canon.lock, MANIFEST/, and
IMPLEMENTATION/evaluator.py from disk), per constraint (m) sandbox discipline.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from IMPLEMENTATION.envelope import (
    build_envelope, sign_envelope, canonical_json, _sha256_text, _HASH_EXCLUDED_KEYS,
)
from IMPLEMENTATION.verifier import (
    verify_envelope,
    ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_KEY_OUT_OF_WINDOW,
    REF_VERIFY_PUBLISHED_RECORD_STALE,
    REF_VERIFY_KEY_RECORD_STALE,
    REF_VERIFY_ROOT_RECORD_STALE,
)
from IMPLEMENTATION.published_record_source import load_signed_record_from_bytes
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.root_record_source import load_root_record_from_bytes

NOW = datetime(2026, 6, 9, 12, 0, 0, tzinfo=timezone.utc)
SKEW = timedelta(seconds=60)
TARGET = "https://target.example/act"

C, E, M = "a" * 64, "b" * 64, "c" * 64
REC = {"canon_sha256": C, "evaluator_sha256": E, "manifest_sha256": M}
INTER = {"AP": ["role", "identity"], "OP": ["request", "session"],
         "context": {"k": "v"}, "expected_manifest_version": "1.0",
         "expected_manifest_sha256": M}


def _pub_b64(public_key):
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


# ===========================================================================
# A. Decision freshness (verify_envelope step 1.5b: signed-envelope not_after)
# ===========================================================================

def _decision_env():
    env = {
        "envelope_version": "1.0", "decision": "ELIGIBLE", "target_url": TARGET,
        "canon": {"version": "0.9.8.4", "canon_sha256": C},
        "evaluated_against": {"manifest_version": "1.0", "manifest_sha256": M},
        "request_context": {"AP": ["identity", "role"], "OP": ["session", "request"],
                            "context": {"k": "v"}, "expected_manifest_version": "1.0",
                            "expected_manifest_sha256": M},
        "evaluator": {"version": "0.9.8.4", "evaluator_sha256": E},
        "condition_results": {"ac3": True, "t26": True, "manifest_integrity": True, "ccs": None},
        "timestamp_utc": "2026-06-09T00:00:00+00:00",
    }
    hashable = {k: v for k, v in env.items() if k not in _HASH_EXCLUDED_KEYS}
    env["decision_sha256"] = _sha256_text(canonical_json(hashable))
    return env


@pytest.fixture
def keys():
    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key()


def _vfy(env, pub, **kw):
    return verify_envelope(env, INTER, TARGET, record_source=REC,
                           pinned_public_keys={"k1": pub}, **kw)


def test_decision_expired_but_within_skew_accepted(keys):
    """not_after is 30s in the past; a 60s skew tolerates it -> honored."""
    priv, pub = keys
    e = sign_envelope(_decision_env(), priv, "k1", not_after=NOW - timedelta(seconds=30))
    assert _vfy(e, pub, now=NOW, clock_skew=SKEW)["reason"] == ACCEPT_REASSERTED_AND_BOUND


def test_decision_beyond_skew_refused(keys):
    """not_after is 120s in the past; a 60s skew does NOT reach it -> EXPIRED."""
    priv, pub = keys
    e = sign_envelope(_decision_env(), priv, "k1", not_after=NOW - timedelta(seconds=120))
    assert _vfy(e, pub, now=NOW, clock_skew=SKEW)["reason"] == REF_VERIFY_SIGNATURE_EXPIRED


def test_decision_default_skew_is_strict_boundary(keys):
    """Default (no clock_skew): now == not_after is stale (strict, unchanged)."""
    priv, pub = keys
    e = sign_envelope(_decision_env(), priv, "k1", not_after=NOW)
    assert _vfy(e, pub, now=NOW)["reason"] == REF_VERIFY_SIGNATURE_EXPIRED


def test_decision_zero_skew_matches_strict(keys):
    """Explicit clock_skew=0 is identical to the strict pre-VL-075 check."""
    priv, pub = keys
    e = sign_envelope(_decision_env(), priv, "k1", not_after=NOW - timedelta(seconds=1))
    assert _vfy(e, pub, now=NOW, clock_skew=timedelta(0))["reason"] == REF_VERIFY_SIGNATURE_EXPIRED


def test_decision_skew_boundary_strict(keys):
    """now == not_after + clock_skew is still stale (the widened edge is strict)."""
    priv, pub = keys
    e = sign_envelope(_decision_env(), priv, "k1", not_after=NOW - SKEW)
    assert _vfy(e, pub, now=NOW, clock_skew=SKEW)["reason"] == REF_VERIFY_SIGNATURE_EXPIRED


# ===========================================================================
# B. Issuer-key validity window (verify_envelope step 1.5, symmetric)
# ===========================================================================

ROOT_ID = "root-test-1"


def _key_entry(key_id, public_key, not_before, not_after):
    return {
        "key_id": key_id, "public_key": _pub_b64(public_key),
        "not_before": not_before.isoformat(), "not_after": not_after.isoformat(),
        "revoked": False,
    }


def _key_record_bytes(root_private, key_entries, serial=1, record_not_after=None):
    if record_not_after is None:
        record_not_after = NOW + timedelta(hours=24)
    record = {
        "format": "elyon-sol-key-record", "version": 1, "root_key_id": ROOT_ID,
        "serial": serial, "issued_at": NOW.isoformat(),
        "not_after": record_not_after.isoformat(), "keys": list(key_entries),
    }
    record["publisher_signature"] = root_private.sign(
        canonical_json(record).encode("utf-8")).hex()
    return json.dumps(record).encode("utf-8")


def _trust_view(root_private, key_entries, **kw):
    raw = _key_record_bytes(root_private, key_entries)
    loaded = load_key_record_from_bytes(raw, {ROOT_ID: root_private.public_key()},
                                        now=NOW, **kw)
    assert loaded["reason"] is None, loaded["reason"]
    return loaded["trust_view"]


def _signed_envelope(issuer_private, key_id):
    interaction = INTER
    env = build_envelope(decision="ELIGIBLE", target_url=TARGET,
                         normalized_interaction=interaction,
                         manifest={"version": "0.9.8.4"},
                         ac3=True, t26=True, manifest_integrity=True)
    return sign_envelope(env, issuer_private, key_id), interaction


def _verify_keyview(view, env, interaction, **kw):
    return verify_envelope(env, interaction, TARGET, key_record_view=view, **kw)


def test_key_window_before_start_within_skew_accepted():
    """now is 30s before not_before; a 60s skew tolerates the early use -> honored."""
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    view = _trust_view(root, [_key_entry("issuer-1", issuer.public_key(),
                                          NOW + timedelta(seconds=30), NOW + timedelta(hours=1))])
    env, inter = _signed_envelope(issuer, "issuer-1")
    assert _verify_keyview(view, env, inter, now=NOW, clock_skew=SKEW)["reason"] \
        == ACCEPT_REASSERTED_AND_BOUND


def test_key_window_before_start_beyond_skew_refused():
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    view = _trust_view(root, [_key_entry("issuer-1", issuer.public_key(),
                                          NOW + timedelta(seconds=120), NOW + timedelta(hours=1))])
    env, inter = _signed_envelope(issuer, "issuer-1")
    assert _verify_keyview(view, env, inter, now=NOW, clock_skew=SKEW)["reason"] \
        == REF_VERIFY_KEY_OUT_OF_WINDOW


def test_key_window_after_end_within_skew_accepted():
    """now is 30s after not_after; a 60s skew tolerates the late use -> honored."""
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    view = _trust_view(root, [_key_entry("issuer-1", issuer.public_key(),
                                          NOW - timedelta(hours=1), NOW - timedelta(seconds=30))])
    env, inter = _signed_envelope(issuer, "issuer-1")
    assert _verify_keyview(view, env, inter, now=NOW, clock_skew=SKEW)["reason"] \
        == ACCEPT_REASSERTED_AND_BOUND


def test_key_window_after_end_beyond_skew_refused():
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    view = _trust_view(root, [_key_entry("issuer-1", issuer.public_key(),
                                          NOW - timedelta(hours=1), NOW - timedelta(seconds=120))])
    env, inter = _signed_envelope(issuer, "issuer-1")
    assert _verify_keyview(view, env, inter, now=NOW, clock_skew=SKEW)["reason"] \
        == REF_VERIFY_KEY_OUT_OF_WINDOW


def test_key_window_default_skew_strict():
    """Default (no clock_skew): a 30s-early use is OUT_OF_WINDOW (strict, unchanged)."""
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    view = _trust_view(root, [_key_entry("issuer-1", issuer.public_key(),
                                          NOW + timedelta(seconds=30), NOW + timedelta(hours=1))])
    env, inter = _signed_envelope(issuer, "issuer-1")
    assert _verify_keyview(view, env, inter, now=NOW)["reason"] == REF_VERIFY_KEY_OUT_OF_WINDOW


# ===========================================================================
# C. Published signed-record freshness (reader record-level not_after)
# ===========================================================================

PUB_ID = "publisher-test-1"


def _published_bytes(priv, *, serial=1, not_after, issued_at=None):
    if issued_at is None:
        issued_at = NOW - timedelta(minutes=1)
    rec = {
        "format": "elyon-sol-published-record", "version": 1,
        "publisher_key_id": PUB_ID, "serial": serial,
        "issued_at": issued_at.isoformat(), "not_after": not_after.isoformat(),
        "canon_sha256": C, "evaluator_sha256": E, "manifest_sha256": M,
    }
    rec["publisher_signature"] = priv.sign(canonical_json(rec).encode("utf-8")).hex()
    return json.dumps(rec).encode("utf-8")


@pytest.fixture
def publisher():
    priv = Ed25519PrivateKey.generate()
    return priv, {PUB_ID: priv.public_key()}


def test_published_stale_but_within_skew_accepted(publisher):
    priv, pinned = publisher
    raw = _published_bytes(priv, not_after=NOW - timedelta(seconds=30))
    res = load_signed_record_from_bytes(raw, pinned, now=NOW, clock_skew=SKEW)
    assert res["reason"] is None
    assert res["record"]["canon_sha256"] == C


def test_published_beyond_skew_refused(publisher):
    priv, pinned = publisher
    raw = _published_bytes(priv, not_after=NOW - timedelta(seconds=120))
    res = load_signed_record_from_bytes(raw, pinned, now=NOW, clock_skew=SKEW)
    assert res["reason"] == REF_VERIFY_PUBLISHED_RECORD_STALE


def test_published_default_skew_strict_boundary(publisher):
    """Default (no clock_skew): now == not_after is stale (strict, unchanged)."""
    priv, pinned = publisher
    raw = _published_bytes(priv, not_after=NOW)
    res = load_signed_record_from_bytes(raw, pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_PUBLISHED_RECORD_STALE


# ===========================================================================
# D. Key signed-record freshness (reader record-level not_after)
# ===========================================================================

def test_key_record_stale_but_within_skew_accepted():
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    raw = _key_record_bytes(
        root, [_key_entry("issuer-1", issuer.public_key(),
                          NOW - timedelta(days=1), NOW + timedelta(days=365))],
        record_not_after=NOW - timedelta(seconds=30))
    res = load_key_record_from_bytes(raw, {ROOT_ID: root.public_key()},
                                     now=NOW, clock_skew=SKEW)
    assert res["reason"] is None


def test_key_record_beyond_skew_refused():
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    raw = _key_record_bytes(
        root, [_key_entry("issuer-1", issuer.public_key(),
                          NOW - timedelta(days=1), NOW + timedelta(days=365))],
        record_not_after=NOW - timedelta(seconds=120))
    res = load_key_record_from_bytes(raw, {ROOT_ID: root.public_key()},
                                     now=NOW, clock_skew=SKEW)
    assert res["reason"] == REF_VERIFY_KEY_RECORD_STALE


# ===========================================================================
# E. Root signed-record freshness (reader record-level not_after)
# ===========================================================================

ROOT_SIGNING_ID = "signing-root-1"


def _root_record_bytes(root_private, *, serial=1, not_after):
    active_root = {
        "root_key_id": ROOT_SIGNING_ID, "public_key": _pub_b64(root_private.public_key()),
        "status": "active", "not_before": (NOW - timedelta(days=1)).isoformat(),
        "not_after": (NOW + timedelta(days=365)).isoformat(),
    }
    record = {
        "format": "elyon-sol-root-record", "version": 1,
        "signing_root_key_id": ROOT_SIGNING_ID, "serial": serial,
        "issued_at": NOW.isoformat(), "not_after": not_after.isoformat(),
        "roots": [active_root],
    }
    record["publisher_signature"] = root_private.sign(
        canonical_json(record).encode("utf-8")).hex()
    return json.dumps(record).encode("utf-8")


def test_root_record_stale_but_within_skew_accepted():
    root = Ed25519PrivateKey.generate()
    raw = _root_record_bytes(root, not_after=NOW - timedelta(seconds=30))
    res = load_root_record_from_bytes(raw, {ROOT_SIGNING_ID: root.public_key()},
                                      now=NOW, clock_skew=SKEW)
    assert res["reason"] is None


def test_root_record_beyond_skew_refused():
    root = Ed25519PrivateKey.generate()
    raw = _root_record_bytes(root, not_after=NOW - timedelta(seconds=120))
    res = load_root_record_from_bytes(raw, {ROOT_SIGNING_ID: root.public_key()},
                                      now=NOW, clock_skew=SKEW)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_STALE


# ===========================================================================
# F. Negative-skew config guard (fail loud at every entry point)
# ===========================================================================

def test_negative_skew_rejected_by_verifier(keys):
    priv, pub = keys
    e = sign_envelope(_decision_env(), priv, "k1", not_after=NOW + timedelta(hours=1))
    with pytest.raises(ValueError):
        _vfy(e, pub, now=NOW, clock_skew=timedelta(seconds=-1))


def test_negative_skew_rejected_by_published_reader(publisher):
    priv, pinned = publisher
    raw = _published_bytes(priv, not_after=NOW + timedelta(hours=1))
    with pytest.raises(ValueError):
        load_signed_record_from_bytes(raw, pinned, now=NOW, clock_skew=timedelta(seconds=-1))


def test_negative_skew_rejected_by_key_reader():
    root, issuer = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    raw = _key_record_bytes(root, [_key_entry("issuer-1", issuer.public_key(),
                                               NOW - timedelta(days=1), NOW + timedelta(days=365))])
    with pytest.raises(ValueError):
        load_key_record_from_bytes(raw, {ROOT_ID: root.public_key()},
                                   now=NOW, clock_skew=timedelta(seconds=-1))


def test_negative_skew_rejected_by_root_reader():
    root = Ed25519PrivateKey.generate()
    raw = _root_record_bytes(root, not_after=NOW + timedelta(hours=1))
    with pytest.raises(ValueError):
        load_root_record_from_bytes(raw, {ROOT_SIGNING_ID: root.public_key()},
                                    now=NOW, clock_skew=timedelta(seconds=-1))
