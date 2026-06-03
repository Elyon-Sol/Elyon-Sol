"""
Canon/spec-derived tests for the B-prime-3 root record (VL-044, T-root-recovery).

Covers IMPLEMENTATION/root_record_source.py (the root reader) and the cross-record
status gate added to IMPLEMENTATION/key_record_source.py, against
docs/restructure/11_root_record_spec.md and CANON/canon.md sections 8.2/9/11.9/13.

Per constraint (i): every key and record is derived LIVE here; no literal key or
signature is pinned. The reject codes are imported from verifier.py (the
REF_VERIFY_* home), never hardcoded as string literals in assertions.
"""

import json
from datetime import datetime, timezone, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from EVIDENCE.published_roots_gen import build_root_record, make_root_entry
from EVIDENCE.published_keys_gen import build_key_record, make_key_entry
from IMPLEMENTATION.root_record_source import load_root_record_from_bytes
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ROOT_RECORD_INVALID,
    REF_VERIFY_ROOT_RECORD_STALE,
    REF_VERIFY_ROOT_RETIRED,
    REF_VERIFY_ROOT_REVOKED,
    REF_VERIFY_KEY_RECORD_INVALID,
)

NOW = datetime.now(timezone.utc)


# --------------------------------------------------------------------------
# Live-keypair fixtures and builders (constraint i: derived live, never pinned)
# --------------------------------------------------------------------------

@pytest.fixture
def roots():
    return {"r1": Ed25519PrivateKey.generate(), "r2": Ed25519PrivateKey.generate()}


@pytest.fixture
def issuer():
    return Ed25519PrivateKey.generate()


@pytest.fixture
def pinned(roots):
    # A target that pins ONLY root-1 (the bootstrap anchor).
    return {"root-1": roots["r1"].public_key()}


def root_record_bytes(roots, entries, signer="r1", sid="root-1", serial=1,
                      not_after=None):
    if not_after is None:
        not_after = NOW + timedelta(hours=24)
    rec = build_root_record(sid, roots[signer], entries, serial, not_after,
                            issued_at=NOW)
    return json.dumps(rec).encode("utf-8")


def status_view_for(roots, pinned, entries, **kw):
    res = load_root_record_from_bytes(root_record_bytes(roots, entries, **kw),
                                      pinned, now=NOW)
    assert res["reason"] is None, res["reason"]
    return res["status_view"]


def key_record_bytes(roots, issuer, signer, root_id, issued_at):
    entry = make_key_entry("issuer-a", issuer.public_key(),
                           not_before=NOW - timedelta(days=1),
                           not_after=NOW + timedelta(days=365))
    rec = build_key_record(root_id, roots[signer], [entry], 1,
                           NOW + timedelta(hours=24), issued_at=issued_at)
    return json.dumps(rec).encode("utf-8")


def active(rid, pk, successor_of=None):
    return make_root_entry(rid, pk, "active", NOW - timedelta(days=1),
                           NOW + timedelta(days=365), successor_of=successor_of)


# --------------------------------------------------------------------------
# Root reader: record validation (spec section 7)
# --------------------------------------------------------------------------

def test_active_root_record_builds_status_view(roots, pinned):
    """An active root record signed by a pinned root yields a status view
    (spec section 7; canon section 11.9 integrity-verifiability)."""
    sv = status_view_for(roots, pinned, [active("root-1", roots["r1"].public_key())])
    assert sv["root-1"]["status"] == "active"


def test_designated_successor_in_view(roots, pinned):
    """R1 (pinned) designating R2 puts R2 in the status view as active - the
    in-band rotation primitive (spec section 3)."""
    sv = status_view_for(roots, pinned, [
        active("root-1", roots["r1"].public_key()),
        active("root-2", roots["r2"].public_key(), successor_of="root-1"),
    ])
    assert set(sv) == {"root-1", "root-2"} and sv["root-2"]["status"] == "active"


def test_unknown_signing_root_refused(roots, pinned):
    """A record signed by a root not in pinned_root_keys cannot be validated;
    folded to RECORD_INVALID (spec section 7 step 2; artifact 09 section 6)."""
    res = load_root_record_from_bytes(
        root_record_bytes(roots, [active("root-2", roots["r2"].public_key())],
                          signer="r2", sid="root-2"),
        pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_INVALID


def test_bad_publisher_signature_refused(roots, pinned):
    """A record whose signing_root_key_id is pinned but signed by a different key
    fails the signature check -> RECORD_INVALID (canon section 9 fail-closed)."""
    res = load_root_record_from_bytes(
        root_record_bytes(roots, [active("root-1", roots["r1"].public_key())],
                          signer="r2", sid="root-1"),
        pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_INVALID


def test_stale_record_refused(roots, pinned):
    """now >= record.not_after -> STALE (spec section 5)."""
    res = load_root_record_from_bytes(
        root_record_bytes(roots, [active("root-1", roots["r1"].public_key())],
                          not_after=NOW - timedelta(hours=1)),
        pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_STALE


def test_serial_rollback_refused(roots, pinned):
    """A serial below last_seen_root_serial -> STALE when state persisted
    (spec section 5)."""
    res = load_root_record_from_bytes(
        root_record_bytes(roots, [active("root-1", roots["r1"].public_key())],
                          serial=2),
        pinned, now=NOW, last_seen_root_serial=5)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_STALE


def test_tz_naive_not_after_refused(roots, pinned):
    """A tz-naive record not_after fails closed to STALE (spec section 5)."""
    rec = build_root_record("root-1", roots["r1"],
                            [active("root-1", roots["r1"].public_key())],
                            1, NOW + timedelta(hours=24), issued_at=NOW)
    rec["not_after"] = "2099-01-01T00:00:00"  # naive
    # re-sign over the mutated record so the signature is valid and the STALE
    # path is reached on the timestamp, not on the signature.
    from IMPLEMENTATION.envelope import canonical_json
    rec.pop("publisher_signature")
    rec["publisher_signature"] = roots["r1"].sign(
        canonical_json(rec).encode("utf-8")).hex()
    res = load_root_record_from_bytes(json.dumps(rec).encode("utf-8"), pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_STALE


def test_within_record_duplicate_root_id_refused(roots, pinned):
    """A root_key_id appearing more than once in roots[] is malformed ->
    RECORD_INVALID (spec section 6.3 within-record analog). This is the loader's
    conflict check; the CROSS-signer overlap conflict is NOT a loader function."""
    res = load_root_record_from_bytes(
        root_record_bytes(roots, [
            active("root-1", roots["r1"].public_key()),
            active("root-2", roots["r2"].public_key()),
            make_root_entry("root-2", roots["r2"].public_key(), "revoked",
                            NOW - timedelta(days=1), NOW + timedelta(days=365),
                            revoked_at=NOW),
        ]),
        pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_ROOT_RECORD_INVALID


def test_self_revocation_downgraded_to_retired(roots, pinned):
    """The signing root cannot revoke ITSELF in-band; a self-revoked assertion is
    treated as at-most retired, with retired_at = revoked_at (spec section 6.2,
    the bootstrap floor)."""
    sv = status_view_for(roots, pinned, [
        make_root_entry("root-1", roots["r1"].public_key(), "revoked",
                        NOW - timedelta(days=1), NOW + timedelta(days=365),
                        revoked_at=NOW - timedelta(minutes=5)),
    ])
    assert sv["root-1"]["status"] == "retired"
    assert sv["root-1"]["retired_at"] == sv["root-1"]["revoked_at"] is not None


def test_cross_signer_overlap_conflict_is_not_loader_resolved(roots, pinned):
    """BOUNDARY (spec section 6.3): cross-signer overlap conflict (two trusted
    roots in two DIFFERENT records asserting contradictory status) is a named
    deployment-layer hazard the single-record loader does NOT resolve. Each record
    validates independently; the loader offers no merge. Resolving the conflict is
    out-of-band re-pin. This test documents the boundary, it does not close it."""
    # R1 says "R2 active"
    sv_a = status_view_for(roots, pinned, [
        active("root-1", roots["r1"].public_key()),
        active("root-2", roots["r2"].public_key(), successor_of="root-1"),
    ])
    # A second record signed by R2 (now in the trusted set) says "R2 active, R1
    # revoked". Pinning R2 too so this record validates on its own.
    pinned_both = dict(pinned); pinned_both["root-2"] = roots["r2"].public_key()
    res_b = load_root_record_from_bytes(
        root_record_bytes(roots, [
            active("root-2", roots["r2"].public_key()),
            make_root_entry("root-1", roots["r1"].public_key(), "revoked",
                            NOW - timedelta(days=1), NOW + timedelta(days=365),
                            revoked_at=NOW),
        ], signer="r2", sid="root-2"),
        pinned_both, now=NOW)
    # Both records validate independently; neither loader call sees the other.
    assert sv_a["root-2"]["status"] == "active"
    assert res_b["reason"] is None and res_b["status_view"]["root-1"]["status"] == "revoked"
    # The loader never merged them into a single contradiction verdict; the merge
    # (and the out-of-band re-pin it implies) is the deployment's responsibility.


def test_bootstrap_floor_sole_root_only_out_of_band(roots, pinned):
    """BOUNDARY (spec section 6.2): a sole pinned root cannot revoke itself
    in-band. A record signed by root-1 marking root-1 revoked is downgraded to
    retired (not distrusted), so the only way to actually distrust root-1 is a
    DIFFERENT trusted root or out-of-band re-pin. Documents the floor."""
    sv = status_view_for(roots, pinned, [
        make_root_entry("root-1", roots["r1"].public_key(), "revoked",
                        NOW - timedelta(days=1), NOW + timedelta(days=365),
                        revoked_at=NOW - timedelta(minutes=1)),
    ])
    # The self-revocation did NOT distrust root-1; it retired it. In-band
    # self-revocation is impossible by construction.
    assert sv["root-1"]["status"] != "revoked"


# --------------------------------------------------------------------------
# Cross-record gate at the key reader (spec section 8)
# --------------------------------------------------------------------------

def test_successor_key_record_accepted_via_view(roots, pinned, issuer):
    """A key record signed by designated-active R2 (NOT pinned) is accepted, its
    signing key sourced from the status view (spec section 8 case 1, active)."""
    sv = status_view_for(roots, pinned, [
        active("root-1", roots["r1"].public_key()),
        active("root-2", roots["r2"].public_key(), successor_of="root-1"),
    ])
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r2", "root-2", NOW),
        pinned, now=NOW, root_status_view=sv)
    assert res["reason"] is None and "issuer-a" in res["trust_view"]


def test_revoked_root_key_record_refused(roots, pinned, issuer):
    """A key record signed by a revoked root -> REF_VERIFY_ROOT_REVOKED
    (spec section 8 case 1, revoked; canon section 9)."""
    sv = status_view_for(roots, pinned, [
        active("root-1", roots["r1"].public_key()),
        make_root_entry("root-2", roots["r2"].public_key(), "revoked",
                        NOW - timedelta(days=1), NOW + timedelta(days=365),
                        revoked_at=NOW - timedelta(minutes=5)),
    ])
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r2", "root-2", NOW),
        pinned, now=NOW, root_status_view=sv)
    assert res["reason"] == REF_VERIFY_ROOT_REVOKED


def test_retired_root_new_record_refused(roots, pinned, issuer):
    """A retired root's NEW key record (issued_at >= retired_at) ->
    REF_VERIFY_ROOT_RETIRED (spec section 6.1, reader-enforced retirement)."""
    retired_at = NOW - timedelta(hours=1)
    sv = status_view_for(roots, pinned, [
        active("root-1", roots["r1"].public_key()),
        make_root_entry("root-2", roots["r2"].public_key(), "retired",
                        NOW - timedelta(days=1), NOW + timedelta(days=365),
                        retired_at=retired_at),
    ])
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r2", "root-2", NOW),  # issued NOW > retired_at
        pinned, now=NOW, root_status_view=sv)
    assert res["reason"] == REF_VERIFY_ROOT_RETIRED


def test_retired_root_past_record_honored(roots, pinned, issuer):
    """A retired root's PAST key record (issued_at < retired_at) is honored to its
    freshness ceiling (spec section 6.1; 'signs no new records' but past ones age
    out naturally)."""
    retired_at = NOW - timedelta(hours=1)
    sv = status_view_for(roots, pinned, [
        active("root-1", roots["r1"].public_key()),
        make_root_entry("root-2", roots["r2"].public_key(), "retired",
                        NOW - timedelta(days=1), NOW + timedelta(days=365),
                        retired_at=retired_at),
    ])
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r2", "root-2", NOW - timedelta(hours=2)),
        pinned, now=NOW, root_status_view=sv)
    assert res["reason"] is None and "issuer-a" in res["trust_view"]


def test_none_view_is_vl042_byte_behavior_pinned(roots, pinned, issuer):
    """root_status_view=None: a pinned root's key record works exactly as VL-042
    (no status gate; backward-compatible)."""
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r1", "root-1", NOW), pinned, now=NOW)
    assert res["reason"] is None and "issuer-a" in res["trust_view"]


def test_none_view_unknown_root_invalid(roots, pinned, issuer):
    """root_status_view=None: an unpinned signing root -> KEY_RECORD_INVALID,
    the VL-042 byte-behavior (no ROOT_* codes on the None path)."""
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r2", "root-2", NOW), pinned, now=NOW)
    assert res["reason"] == REF_VERIFY_KEY_RECORD_INVALID


def test_pinned_not_in_view_is_active_by_pinning(roots, pinned, issuer):
    """A pinned root absent from the supplied status view is active-by-pinning -
    the bootstrap default (spec section 8 case 2)."""
    sv = status_view_for(roots, pinned, [active("root-2", roots["r2"].public_key())])
    res = load_key_record_from_bytes(
        key_record_bytes(roots, issuer, "r1", "root-1", NOW),
        pinned, now=NOW, root_status_view=sv)
    assert res["reason"] is None and "issuer-a" in res["trust_view"]
