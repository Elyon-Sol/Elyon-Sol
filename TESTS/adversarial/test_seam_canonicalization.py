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
  3. The KNOWN two-implementation divergence (envelope.canonical_json
     ensure_ascii=True vs replay/receipt.canonical_json ensure_ascii=False,
     self-flagged in envelope.py's docstring since VL-012/VL-025) is PINNED, so a
     future change to either side surfaces here instead of silently creating a
     cross-path hash mismatch on non-ASCII input.
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


# --- 3. Pin the known two-implementation divergence -----------------------

def test_envelope_and_receipt_canonicalization_agree_on_ascii():
    data = {"b": 2, "a": "plain-ascii", "n": 1}
    assert canonical_json(data) == receipt_canonical_json(data)


def test_envelope_and_receipt_canonicalization_diverge_on_non_ascii():
    # envelope: ensure_ascii=True (escapes); receipt: ensure_ascii=False (raw).
    # Pinned so a future edit that unifies them - or that routes a non-ASCII
    # value across the two paths - surfaces here instead of silently mismatching.
    data = {"x": "café"}
    assert canonical_json(data) != receipt_canonical_json(data)
    assert "\\u00e9" in canonical_json(data)          # escaped form
    assert "é" in receipt_canonical_json(data)   # raw form
