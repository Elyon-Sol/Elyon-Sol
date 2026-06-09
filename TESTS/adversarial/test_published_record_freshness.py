"""
B1 (VL-074) acceptance + characterization for record freshness (A3b sub-case b).

The gap (artifact 04 G5 / A3b sub-case (b)): the byte-anchor published record
(IMPLEMENTATION/published_source.py) has NO temporal dimension, so a stale-but-
anchor-matching record is honored arbitrarily later. The fix: the signed
published record (IMPLEMENTATION/published_record_source.py) carries not_after +
a monotonic serial under a publisher signature, and the reader refuses a stale
record with REF_VERIFY_PUBLISHED_RECORD_STALE.

The flip (artifact 13 B1 acceptance, "a failing test (stale record honored)
flips to refused"): test_stale_record_is_refused FAILS against the byte-anchor
model (which honors it - characterized in test_byte_anchor_model_has_no_freshness)
and PASSES against the signed model built here.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from EVIDENCE.published_hashes_signed_gen import (
    build_signed_record,
    public_key_b64,
)
from EVIDENCE.published_hashes_gen import build_record as build_currency_pins
from IMPLEMENTATION.published_record_source import (
    load_signed_record_from_bytes,
)
from IMPLEMENTATION.published_source import (
    anchor_sha256,
    load_record_from_bytes,
)
from IMPLEMENTATION.verifier import (
    REF_VERIFY_PUBLISHED_RECORD_INVALID,
    REF_VERIFY_PUBLISHED_RECORD_STALE,
)

NOW = datetime(2026, 6, 9, 12, 0, 0, tzinfo=timezone.utc)
KEY_ID = "publisher-test-1"


def _keypair():
    priv = Ed25519PrivateKey.generate()
    return priv, {KEY_ID: priv.public_key()}


def _record_bytes(priv, *, serial=1, not_after=None, issued_at=None):
    if not_after is None:
        not_after = NOW + timedelta(hours=24)
    if issued_at is None:
        issued_at = NOW - timedelta(minutes=1)
    rec = build_signed_record(
        publisher_key_id=KEY_ID,
        publisher_private_key=priv,
        serial=serial,
        not_after=not_after,
        pins=build_currency_pins(),
        issued_at=issued_at,
    )
    return json.dumps(rec).encode("utf-8"), rec


# ---- the acceptance flip ----------------------------------------------------

def test_fresh_record_is_accepted_and_carries_pins():
    priv, pinned = _keypair()
    raw, rec = _record_bytes(priv, not_after=NOW + timedelta(hours=1))
    out = load_signed_record_from_bytes(raw, pinned, now=NOW)
    assert out["reason"] is None
    assert out["record"] is not None
    # drop-in currency view for reassert(record_source=...)
    for pin in ("canon_sha256", "evaluator_sha256", "manifest_sha256"):
        assert out["record"][pin] == rec[pin]


def test_stale_record_is_refused():
    """The flip: a record whose not_after is in the past is REFUSED."""
    priv, pinned = _keypair()
    raw, _ = _record_bytes(priv, not_after=NOW - timedelta(seconds=1))
    out = load_signed_record_from_bytes(raw, pinned, now=NOW)
    assert out["record"] is None
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_STALE


def test_not_after_boundary_is_strict():
    priv, pinned = _keypair()
    raw, _ = _record_bytes(priv, not_after=NOW)  # now == not_after -> not (now < na)
    out = load_signed_record_from_bytes(raw, pinned, now=NOW)
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_STALE


def test_serial_rollback_is_refused():
    priv, pinned = _keypair()
    raw, _ = _record_bytes(priv, serial=3, not_after=NOW + timedelta(hours=1))
    out = load_signed_record_from_bytes(raw, pinned, now=NOW, last_seen_serial=5)
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_STALE


def test_serial_monotonic_advance_is_accepted():
    priv, pinned = _keypair()
    raw, _ = _record_bytes(priv, serial=7, not_after=NOW + timedelta(hours=1))
    out = load_signed_record_from_bytes(raw, pinned, now=NOW, last_seen_serial=5)
    assert out["reason"] is None


# ---- invalid (not stale) faults --------------------------------------------

def test_unknown_publisher_key_is_invalid():
    priv, _ = _keypair()
    raw, _ = _record_bytes(priv, not_after=NOW + timedelta(hours=1))
    out = load_signed_record_from_bytes(raw, {"other-key": priv.public_key()}, now=NOW)
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_INVALID


def test_tampered_signature_is_invalid():
    priv, pinned = _keypair()
    raw, rec = _record_bytes(priv, not_after=NOW + timedelta(hours=1))
    rec = dict(rec)
    rec["evaluator_sha256"] = "0" * 64  # mutate a signed pin
    tampered = json.dumps(rec).encode("utf-8")
    out = load_signed_record_from_bytes(tampered, pinned, now=NOW)
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_INVALID


def test_wrong_format_is_invalid():
    priv, pinned = _keypair()
    raw, rec = _record_bytes(priv, not_after=NOW + timedelta(hours=1))
    rec = dict(rec)
    rec["format"] = "not-the-published-record"
    out = load_signed_record_from_bytes(json.dumps(rec).encode("utf-8"), pinned, now=NOW)
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_INVALID


def test_transport_failure_fails_closed_invalid():
    priv, pinned = _keypair()
    # empty / non-JSON bytes -> INVALID (parse)
    out = load_signed_record_from_bytes(b"", pinned, now=NOW)
    assert out["reason"] == REF_VERIFY_PUBLISHED_RECORD_INVALID


# ---- the contrast that pins the gap ----------------------------------------

def test_byte_anchor_model_has_no_freshness():
    """Characterize the gap: the byte-anchor reader honors a record regardless
    of any temporal dimension (it has none). The same staleness the signed
    reader refuses above cannot even be expressed, let alone checked, here."""
    pins = build_currency_pins()  # the 6-field byte-anchor record shape
    raw = json.dumps(pins).encode("utf-8")
    anchor = anchor_sha256(raw)
    out = load_record_from_bytes(raw, anchor)
    # honored: the anchor matches and there is no not_after to fail on
    assert out is not None
    assert "not_after" not in out
