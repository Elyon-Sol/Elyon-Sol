"""
Adversarial canonicalization seam tests (external-review hardening, 2026-07).

Motivated by an external assessment: "a break would almost certainly come from
an implementation seam - a canonicalization mismatch between gate and target ...
not from breaking the signature scheme." These attack the canonicalization layer
directly:

  1. Gate build and target reassert/verify AGREE under non-ASCII / unicode
     content (both sides use envelope.canonical_json -> no gate/target mismatch
     within a single envelope). Credit-and-pin.
  2. Canonicalization does NOT silently unify unicode-normalization variants or
     int-vs-float (characterization: distinct bytes -> distinct decision_sha256).
  3. Canonicalization UNIFICATION (SES-5 / VL-143): the former
     two-implementation divergence (envelope.canonical_json ensure_ascii=True
     vs replay/receipt's local copy ensure_ascii=False, self-flagged since
     VL-012/VL-025, dispositioned OPEN at VL-141) is RESOLVED — receipt.py
     reuses envelope.canonical_json. Pinned in BOTH directions: the two paths
     must AGREE on non-ASCII (revert-catcher: RED if receipt.py regrows a
     local ensure_ascii=False copy) AND the unified form must be the
     ASCII-ESCAPED one (direction-catcher: RED if anyone "unifies" by
     flipping envelope.canonical_json to ensure_ascii=False, which would
     change decision_sha256 on non-ASCII input and break ASCII-safe header
     transport).
"""
import unicodedata

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.envelope import (
    build_envelope,
    canonical_json,
    reassert,
    sign_envelope,
    REASSERTED,
    INVALIDATED,
)
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.verifier import verify_envelope, ACCEPT_REASSERTED_AND_BOUND
from IMPLEMENTATION.replay.receipt import canonical_json as receipt_canonical_json

TARGET_URL = "http://127.0.0.1:9000/target"
KEY_ID = "gate-ed25519-001"


def _interaction(context=None):
    return {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {} if context is None else context,
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }


def _build(context=None, ts="2026-07-09T00:00:00+00:00"):
    return build_envelope(
        decision="ELIGIBLE",
        target_url=TARGET_URL,
        normalized_interaction=_interaction(context),
        manifest=load_manifest(),
        ac3=True,
        t26=True,
        manifest_integrity=True,
        timestamp_utc=ts,
    )


# --- 1. Non-ASCII content round-trips cleanly gate -> target ---------------

def test_non_ascii_context_reasserts():
    env = _build(context={"note": "café ☕ 你好"})
    assert reassert(env)["outcome"] == REASSERTED


def test_non_ascii_context_signed_verify_accepts():
    priv = Ed25519PrivateKey.generate()
    ctx = {"note": "résumé \U0001f512"}
    env = sign_envelope(_build(context=ctx), priv, KEY_ID)
    r = verify_envelope(
        env, _interaction(ctx), TARGET_URL,
        pinned_public_keys={KEY_ID: priv.public_key()},
    )
    assert r["accepted"] is True
    assert r["reason"] == ACCEPT_REASSERTED_AND_BOUND


def test_non_ascii_tamper_without_rehash_invalidated():
    env = _build(context={"note": "café"})
    # Swap to a visually-similar but byte-different value, no re-hash.
    env["request_context"]["context"] = {"note": "cafe"}
    assert reassert(env)["outcome"] == INVALIDATED


# --- 2. No silent unicode / number unification ----------------------------

def test_unicode_nfc_nfd_hash_differently():
    nfc = unicodedata.normalize("NFC", "café")   # ...é
    nfd = unicodedata.normalize("NFD", "café")   # ...e + ́
    assert nfc != nfd
    h_nfc = _build(context={"x": nfc})["decision_sha256"]
    h_nfd = _build(context={"x": nfd})["decision_sha256"]
    assert h_nfc != h_nfd  # canonicalization does not normalize unicode


def test_int_vs_float_hash_differently():
    h_int = _build(context={"n": 1})["decision_sha256"]
    h_float = _build(context={"n": 1.0})["decision_sha256"]
    assert h_int != h_float


# --- 3. Pin the SES-5 unification (VL-143) ---------------------------------

def test_envelope_and_receipt_canonicalization_agree_on_ascii():
    data = {"b": 2, "a": "plain-ascii", "n": 1}
    assert canonical_json(data) == receipt_canonical_json(data)


def test_envelope_and_receipt_canonicalization_agree_on_non_ascii():
    # SES-5 revert-catcher: before VL-143 receipt.py carried a LOCAL
    # ensure_ascii=False canonical_json that diverged from envelope's on
    # non-ASCII input. receipt.py now reuses envelope.canonical_json; if a
    # local divergent copy is ever reintroduced, this test goes RED.
    data = {"x": "café", "y": "你好 ☕"}
    assert canonical_json(data) == receipt_canonical_json(data)


def test_unified_canonicalization_is_ascii_escaped():
    # SES-5 direction-catcher: the unification must land on the ENVELOPE's
    # ensure_ascii=True form (ASCII-escaped). Unifying the other way would
    # change decision_sha256 for non-ASCII envelopes (breaking the deployed
    # chain's hashes) and put raw UTF-8 in the X-Elyon-Sol-Envelope header.
    data = {"x": "café"}
    assert "\\u00e9" in receipt_canonical_json(data)  # escaped, not raw
    assert "é" not in receipt_canonical_json(data)
    assert receipt_canonical_json(data) == canonical_json(data)


def test_receipt_non_ascii_round_trip_verifies():
    # The receipt path stays self-consistent under the unified
    # canonicalization: a receipt with non-ASCII field values verifies.
    from IMPLEMENTATION.replay.receipt import create_receipt, verify_receipt
    r = create_receipt(
        request_id="REQ-café-你好",
        terminal_state="REFUSED",
        manifest_version="1.0",
        manifest_sha256="ab" * 32,
        refusal_reason_code="REF_TEST_☕",
    )
    assert verify_receipt(r) is True
    r["request_id"] = "REQ-cafe-你好"  # byte-different, no re-hash
    assert verify_receipt(r) is False
