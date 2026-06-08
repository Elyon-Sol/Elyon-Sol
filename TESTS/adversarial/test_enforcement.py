"""
End-to-end refused-bypass demonstration for Elyon-Sol (VL-038).

This is the terminus increment per the VL-038 opener: a call that did not
come through the gate, or carries a forged / replayed / mismatched
envelope, is REFUSED by an enforcing target, and the verification is
against Elyon-Sol's PUBLISHED, hash-locked record (EVIDENCE/published_hashes.json),
so the refusal is defensible to a third party who does not trust the
target's own working files. That is the first moment the project is a gate
rather than a validator (artifact 05 open question 3; artifact 08 sections
4.2 / 4.3 / 4.4 / 7 / 8).

What this file adds, and how it composes existing pieces:

  - delivery (VL-038): IMPLEMENTATION/pep.py now pushes the envelope on
    the ELIGIBLE forward as the out-of-band attestation header
    X-Elyon-Sol-Envelope (canonical_json of the envelope). The forwarded
    body is unchanged (normalized_interaction), so a routed call and a
    direct (A1) call differ only by the header.
  - defensible verification (VL-038, Decision C): the enforcing target
    verifies the envelope's pinned hashes against the committed
    EVIDENCE/published_hashes.json (the published record), NOT against the
    target's own local disk. This is the load-bearing anchor; the
    test_published_record_mismatch case proves it is independent of the
    local-disk reassert() (an envelope that passes local-disk reassert and
    binding is still refused when its pins do not match the published
    record).
  - integrity + binding (VL-037, reused as-is per Decision D):
    verify_envelope() supplies decision_sha256 integrity (Row 2; closes
    forgery A2) and the request_context / target_url binding check (closes
    same-state replay A3). No verifier.py change.

Honest scope (artifact 08 sections 4.4 / 6):
  - A1 (the declining caller) is closeable only by the target running an
    admission policy that refuses un-attested calls; the gate cannot force
    routing. This file demonstrates A1 and the target-side defense.
  - reassert() reads LOCAL disk; the published-record check is what makes
    the demonstration defensible co-located. Cross-host TRANSPORT of the
    published record (the target fetching it from a canonical published
    location rather than a committed local copy) is named, NOT built, and
    is the remaining hardening after VL-038.

Ledger: VL-038 (T-G4-enforce; delivery + defensible refused bypass).
"""

import hashlib
import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from IMPLEMENTATION.envelope import (
    build_envelope,
    canonical_json,
)
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.pep import app as pep_app
from IMPLEMENTATION.verifier import (
    ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_BINDING_MISMATCH,
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_REASSERT_INVALIDATED,
    verify_envelope,
)


TARGET_URL = "http://127.0.0.1:9000/target"
PUBLISHED_HASHES_PATH = "EVIDENCE/published_hashes.json"

# The single new harness reason. Everything else reuses the verifier's
# REF_VERIFY_* vocabulary (no-header maps to verify_envelope(None, ...)).
REF_TARGET_PUBLISHED_RECORD_MISMATCH = "REF_TARGET_PUBLISHED_RECORD_MISMATCH"


# ---------------------------------------------------------------------------
# Published-source reader (Decision C: verify against the published record).
# Test-scope for VL-038; promotion to IMPLEMENTATION/ is part of cross-host
# transport (after VL-038).
# ---------------------------------------------------------------------------


def load_published_hashes(path=PUBLISHED_HASHES_PATH):
    """Read the committed published hash record."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_against_published_record(envelope, published):
    """
    Compare the envelope's pinned canon / evaluator / manifest hashes
    against the published record. This is the defensible currency anchor:
    it does not read the target's local disk, only the committed published
    record (and the envelope's own bytes). Returns True iff all three pins
    match the published record.
    """
    if not isinstance(envelope, dict):
        return False
    try:
        return (
            envelope["canon"]["canon_sha256"] == published["canon_sha256"]
            and envelope["evaluator"]["evaluator_sha256"]
            == published["evaluator_sha256"]
            and envelope["evaluated_against"]["manifest_sha256"]
            == published["manifest_sha256"]
        )
    except (KeyError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Enforcing target harness (Decision A: refuses, not a recording mock).
# ---------------------------------------------------------------------------


def build_enforcing_target_app(published, expected_target_url=TARGET_URL):
    """
    Build a minimal enforcing target. On each call it:
      1. reads the X-Elyon-Sol-Envelope attestation header (absent /
         unparseable -> treated as no envelope);
      2. checks the envelope's pins against the PUBLISHED record;
      3. runs verify_envelope() (integrity + binding + local reassert);
      4. honors (200, records the interaction) iff every check passes;
         otherwise returns 403 and does NOT record (does not act).

    Returns (app, received) where `received` is the list of acted-upon
    interactions. A refused call never appends to it.
    """
    app = FastAPI()
    received = []

    @app.post("/act")
    async def act(request: Request):
        interaction = await request.json()

        raw = request.headers.get("X-Elyon-Sol-Envelope")
        envelope = None
        if raw is not None:
            try:
                envelope = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                envelope = None  # unparseable header -> treated as absent

        # Structural presence: route absent / malformed through
        # verify_envelope so the reason is REF_VERIFY_ENVELOPE_ABSENT
        # (reuses the verifier vocabulary; no new code).
        if not isinstance(envelope, dict):
            result = verify_envelope(envelope, interaction, expected_target_url)
            raise HTTPException(
                status_code=403,
                detail={"honored": False, "reason": result["reason"]},
            )

        # Defensible currency anchor: the published record, not local disk.
        if not verify_against_published_record(envelope, published):
            raise HTTPException(
                status_code=403,
                detail={
                    "honored": False,
                    "reason": REF_TARGET_PUBLISHED_RECORD_MISMATCH,
                },
            )

        # Integrity (decision_sha256) + binding (request_context /
        # target_url) + local reassert, reused as-is (VL-037, Decision D).
        result = verify_envelope(envelope, interaction, expected_target_url)
        if not result["accepted"]:
            raise HTTPException(
                status_code=403,
                detail={"honored": False, "reason": result["reason"]},
            )

        received.append(interaction)  # the target acts only here
        return {"honored": True, "reason": result["reason"]}

    return app, received


# ---------------------------------------------------------------------------
# Fixtures (mirroring test_verifier.py's self-contained pattern)
# ---------------------------------------------------------------------------


def _normalized_interaction(ap=None, op=None, context=None):
    return {
        "AP": ["identity", "role"] if ap is None else ap,
        "OP": ["session", "request"] if op is None else op,
        "context": {} if context is None else context,
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }


def _build_valid_envelope(interaction=None, target_url=TARGET_URL,
                          timestamp_utc="2026-05-29T00:00:00+00:00"):
    if interaction is None:
        interaction = _normalized_interaction()
    return build_envelope(
        decision="ELIGIBLE",
        target_url=target_url,
        normalized_interaction=interaction,
        manifest=load_manifest(),
        ac3=True,
        t26=True,
        manifest_integrity=True,
        timestamp_utc=timestamp_utc,
    )


# ---------------------------------------------------------------------------
# The committed published record is correct (sanity: it equals the live
# pins an envelope carries).
# ---------------------------------------------------------------------------


def test_published_record_matches_live_envelope_pins():
    """
    The committed EVIDENCE/published_hashes.json must equal the hashes a
    freshly built envelope pins, or every verification below would be
    against a stale anchor. Derived live at build time per VL-038
    constraint (i); this guards that derivation.
    """
    published = load_published_hashes()
    env = _build_valid_envelope()
    assert env["canon"]["canon_sha256"] == published["canon_sha256"]
    assert env["evaluator"]["evaluator_sha256"] == published["evaluator_sha256"]
    assert (
        env["evaluated_against"]["manifest_sha256"]
        == published["manifest_sha256"]
    )


# ---------------------------------------------------------------------------
# Accept: a valid call routed through the gate is honored by the target.
# ---------------------------------------------------------------------------


def test_routed_valid_call_honored_end_to_end(monkeypatch):
    """
    The full two-hop happy path. A valid request is POSTed to the PEP; the
    PEP pushes the envelope as the X-Elyon-Sol-Envelope header on its
    forward (captured here via the monkeypatched requests.post). That
    captured (body, header, target_url) triple is delivered to the
    enforcing target, which verifies it against the published record and
    HONORS it (200) and acts on it exactly once.
    """
    captured = {}

    class _Resp:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers or {}
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    pep_client = TestClient(pep_app)
    pep_response = pep_client.post(
        "/governed-call",
        json={
            "target_url": TARGET_URL,
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": "1.0",
                "expected_manifest_sha256": manifest_sha256(),
            },
        },
    )
    assert pep_response.status_code == 200
    assert "X-Elyon-Sol-Envelope" in captured["headers"]

    published = load_published_hashes()
    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    target_client = TestClient(target_app)

    target_response = target_client.post(
        "/act",
        json=captured["json"],
        headers={"X-Elyon-Sol-Envelope": captured["headers"]["X-Elyon-Sol-Envelope"]},
    )
    assert target_response.status_code == 200
    assert target_response.json()["honored"] is True
    assert len(received) == 1  # the target acted exactly once


# ---------------------------------------------------------------------------
# Refusals. Each asserts the target returns non-200 AND did not act.
# ---------------------------------------------------------------------------


def test_direct_call_no_envelope_refused_a1():
    """
    A1 (the declining caller): a direct call to the target carries no
    attestation header. The enforcing target refuses
    (REF_VERIFY_ENVELOPE_ABSENT via verify_envelope(None, ...)) and does
    not act. The gate never saw this call; only the target-side policy
    closes A1 (artifact 08 section 4.4).
    """
    published = load_published_hashes()
    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    client = TestClient(target_app)
    response = client.post("/act", json=_normalized_interaction())  # no header
    assert response.status_code == 403
    assert response.json()["detail"]["reason"] == REF_VERIFY_ENVELOPE_ABSENT
    assert received == []


def test_forged_envelope_refused_a2():
    """
    A2 (forgery): a mutated envelope (a request_context field changed
    without re-hashing decision_sha256) fails reassert() Row 2. The target
    refuses (REF_VERIFY_REASSERT_INVALIDATED) and does not act
    (artifact 08 section 4.2).
    """
    published = load_published_hashes()
    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    client = TestClient(target_app)

    env = _build_valid_envelope()
    env["request_context"]["AP"] = ["identity", "role", "admin"]  # tamper, no rehash
    response = client.post(
        "/act",
        json=_normalized_interaction(),
        headers={"X-Elyon-Sol-Envelope": canonical_json(env)},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["reason"] == REF_VERIFY_REASSERT_INVALIDATED
    assert received == []


def test_replayed_envelope_binding_mismatch_refused_a3():
    """
    A3 (same-state replay): a genuine, current envelope issued for
    interaction X delivered alongside a different live interaction Y.
    reassert() alone would REASSERT (no repo-state change); the binding
    check refuses (REF_VERIFY_BINDING_MISMATCH). The target does not act
    (artifact 08 section 7).
    """
    published = load_published_hashes()
    target_app, received = build_enforcing_target_app(published, TARGET_URL)
    client = TestClient(target_app)

    interaction_x = _normalized_interaction(ap=["identity", "role"])
    env = _build_valid_envelope(interaction=interaction_x)
    interaction_y = _normalized_interaction(ap=["identity", "role", "admin"])
    response = client.post(
        "/act",
        json=interaction_y,
        headers={"X-Elyon-Sol-Envelope": canonical_json(env)},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["reason"] == REF_VERIFY_BINDING_MISMATCH
    assert received == []


def test_target_url_mismatch_refused():
    """
    A genuine envelope issued for target_url X delivered to a target
    serving target_url Y. reassert() REASSERTS; the binding check refuses
    (REF_VERIFY_BINDING_MISMATCH). The target does not act
    (artifact 08 section 4.2: target_url is inside the signed region and
    part of the binding obligation).
    """
    published = load_published_hashes()
    # Enforcing target serves a DIFFERENT url than the envelope records.
    target_app, received = build_enforcing_target_app(
        published, expected_target_url="http://127.0.0.1:9000/other"
    )
    client = TestClient(target_app)

    interaction = _normalized_interaction()
    env = _build_valid_envelope(interaction=interaction, target_url=TARGET_URL)
    response = client.post(
        "/act",
        json=interaction,
        headers={"X-Elyon-Sol-Envelope": canonical_json(env)},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["reason"] == REF_VERIFY_BINDING_MISMATCH
    assert received == []


def test_envelope_not_matching_published_record_refused():
    """
    THE Decision-C load-bearing case. A genuine envelope that passes
    local-disk reassert() AND the binding check is still REFUSED when its
    pinned hashes do not match the published record. This proves the
    published-record check is independent of the target's local disk: the
    verification is anchored to the committed published record, not to
    whatever the target holds locally.

    Staged by handing the enforcing target a published record whose
    canon_sha256 differs from the live (and therefore from the envelope's
    pin). reassert() (local disk) would accept; the published-record check
    refuses with REF_TARGET_PUBLISHED_RECORD_MISMATCH. The target does not
    act.
    """
    live = load_published_hashes()
    divergent = dict(live)
    divergent["canon_sha256"] = "0" * 64  # published record disagrees with live
    target_app, received = build_enforcing_target_app(divergent, TARGET_URL)
    client = TestClient(target_app)

    interaction = _normalized_interaction()
    env = _build_valid_envelope(interaction=interaction)  # valid against LOCAL disk
    response = client.post(
        "/act",
        json=interaction,
        headers={"X-Elyon-Sol-Envelope": canonical_json(env)},
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]["reason"]
        == REF_TARGET_PUBLISHED_RECORD_MISMATCH
    )
    assert received == []
