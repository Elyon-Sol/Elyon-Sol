"""
Adversarial tests for the request schema at the PEP boundary.

Derived from SPEC/request_schema.md (post-VL-016, CORRECTED). One test
per refusal class named in "Rejected shapes" and "PEP boundary
behavior," plus a positive case that round-trips a valid request.

THESE TESTS MUST FAIL against IMPLEMENTATION/pep.py at HEAD. That
failure is the honest G2 signal: pep.py at HEAD performs no schema
validation; it accepts `{target_url, context}` opaquely and lets
`evaluate()` fail closed on whatever shape arrives. The schema's
build-order step 2 specifies that the failing tests come before the
validator (step 3) and PEP wiring (step 4).

Per VL-008 procedure and the schema's "PEP boundary behavior":
- Schema-layer refusal MUST return HTTP 403 with
  `detail.refusal_reason_code` set to the schema-named code.
- Schema-layer refusal MUST NOT call evaluate().
- Schema-layer refusal MUST NOT forward to target_url.

Each negative case asserts the first; the upstream-not-called
invariant is asserted via a fixture that records any call to
`requests.post` and fails the test if a schema-rejected request
reaches it.

Ledger: VL-017 (proposed; closes the failing-tests half of G2).
Sibling work: VL-018 (validator), VL-019 (PEP wiring, G2 close in
code), VL-020 (artifact 05 freshness pass).

Notes on scope:
- The schema names a step-4 "no unknown top-level keys inside
  interaction" rule. As of VL-054 it enumerates a distinct refusal
  code for that case: REF_SCHEMA_UNKNOWN_KEY (SPEC/request_schema.md
  "Rejected shapes" -> "Unknown key inside interaction"), distinct
  from REF_SCHEMA_RESERVED_CCS (narrower: keys containing 'ccs') and
  from REF_SCHEMA_TYPE_MISMATCH (a present field of the wrong type).
  The case "unknown_key_inside_interaction" below asserts it; it
  derives from the spec's rejected-shapes list, not from canon (G7
  discipline). Before VL-054 the case was intentionally NOT tested
  (inventing a code would have been tests driving the schema); the
  VL-054 spec commit added the code, so the test now derives from it.
- REF_SCHEMA_PARSE_ERROR (malformed JSON) is tested via raw bytes
  sent to TestClient; the other negative cases send well-formed
  JSON with schema-rejected shape.
"""

import pytest
from fastapi.testclient import TestClient

from IMPLEMENTATION.pep import app


# Live manifest values used by the positive case. Sourced from
# TESTS/adversarial/test_adversarial_evaluator.py's SHA constant
# and MANIFEST/manifest.json's version field. The positive case
# uses values that WOULD pass manifest_integrity_valid() if the
# validator existed; today it fails for the orthogonal reason
# that pep.py rejects the `interaction` envelope at the Pydantic
# layer (no `interaction` field on GovernedCallRequest).
LIVE_MANIFEST_VERSION = "1.0"
# VL-115: derive the manifest sha LIVE rather than pinning a literal, so this
# fixture survives a manifest change (e.g. adding HIGH_IMPACT). The literal
# was the suite's one hand-coded manifest hash; deriving it matches the
# manifest_sha256() discipline the rest of the suite already uses (VL-034).
from IMPLEMENTATION.evaluator import manifest_sha256 as _manifest_sha256
LIVE_MANIFEST_SHA256 = _manifest_sha256()


def _valid_interaction():
    """The canonical accepting shape per SPEC/request_schema.md."""
    return {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {},
        "expected_manifest_version": LIVE_MANIFEST_VERSION,
        "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
    }


def _valid_request():
    return {
        "target_url": "http://127.0.0.1:9000/target",
        "interaction": _valid_interaction(),
    }


@pytest.fixture
def upstream_guard(monkeypatch):
    """
    Records calls to requests.post. Schema-layer refusals MUST NOT
    reach this. The positive case is allowed to reach it once; a
    canned 200 response is returned without making a network call.
    """
    calls = []

    class _CannedResponse:
        status_code = 200
        text = '{"ok": true}'

    def _fake_post(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return _CannedResponse()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", _fake_post)
    return calls


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Negative cases - one per refusal class in SPEC/request_schema.md
# ---------------------------------------------------------------------------

# Each case is (id, request_body, expected_refusal_code). request_body
# is sent as JSON unless it is the literal bytes for the parse-error
# case, which is handled separately.

NEGATIVE_CASES = [
    # REF_SCHEMA_TOP_LEVEL: missing `interaction` entirely
    (
        "top_level_missing_interaction",
        {"target_url": "http://127.0.0.1:9000/target"},
        "REF_SCHEMA_TOP_LEVEL",
    ),
    # REF_SCHEMA_TOP_LEVEL: missing `target_url`
    (
        "top_level_missing_target_url",
        {"interaction": _valid_interaction()},
        "REF_SCHEMA_TOP_LEVEL",
    ),
    # REF_SCHEMA_TOP_LEVEL: `interaction` not an object
    (
        "top_level_interaction_wrong_type",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": "not-an-object",
        },
        "REF_SCHEMA_TOP_LEVEL",
    ),
    # REF_SCHEMA_BAD_URL: target_url not a syntactically valid
    # absolute URL. Schema cites RFC 3986 absolute URL.
    (
        "bad_url_relative",
        {
            "target_url": "/target",
            "interaction": _valid_interaction(),
        },
        "REF_SCHEMA_BAD_URL",
    ),
    (
        "bad_url_no_scheme",
        {
            "target_url": "127.0.0.1:9000/target",
            "interaction": _valid_interaction(),
        },
        "REF_SCHEMA_BAD_URL",
    ),
    (
        "bad_url_empty_string",
        {
            "target_url": "",
            "interaction": _valid_interaction(),
        },
        "REF_SCHEMA_BAD_URL",
    ),
    # REF_SCHEMA_FLAT_KEYS: the archived interception_proof_001
    # shape. AP/OP/pinning at top level alongside target_url, no
    # `interaction` envelope. This is the exact shape G2 retires.
    (
        "flat_keys_archived_proof_001_shape",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "AP": ["identity"],
            "OP": ["session", "request"],
            "expected_manifest_version": LIVE_MANIFEST_VERSION,
            "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
        },
        "REF_SCHEMA_FLAT_KEYS",
    ),
    # REF_SCHEMA_FLAT_KEYS: AP at top level alongside a valid
    # `interaction`. The schema says any AP/OP at top level is
    # schema-malformed regardless of other fields.
    (
        "flat_keys_ap_at_top_level_with_interaction_present",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "AP": ["identity", "role"],
            "interaction": _valid_interaction(),
        },
        "REF_SCHEMA_FLAT_KEYS",
    ),
    (
        "flat_keys_op_at_top_level_with_interaction_present",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "OP": ["session", "request"],
            "interaction": _valid_interaction(),
        },
        "REF_SCHEMA_FLAT_KEYS",
    ),
    # REF_SCHEMA_MANIFEST_PINNING_MISSING: version absent
    (
        "manifest_pinning_version_missing",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_MANIFEST_PINNING_MISSING",
    ),
    # REF_SCHEMA_MANIFEST_PINNING_MISSING: sha256 absent
    (
        "manifest_pinning_sha256_missing",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
            },
        },
        "REF_SCHEMA_MANIFEST_PINNING_MISSING",
    ),
    # REF_SCHEMA_MANIFEST_PINNING_MISSING: both absent
    (
        "manifest_pinning_both_missing",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
            },
        },
        "REF_SCHEMA_MANIFEST_PINNING_MISSING",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: AP is a string, not array of strings
    (
        "type_mismatch_ap_string",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": "identity,role",
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: AP is a dict, not array of strings.
    # This is the case ADVERSARIAL_RESULTS.md cites as the original
    # set(dict)-coercion bug at the evaluator layer; here it is the
    # schema-layer refusal.
    (
        "type_mismatch_ap_dict",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": {"identity": True, "role": True},
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: AP is an array with non-string elements
    (
        "type_mismatch_ap_mixed_types",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", 42, None],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: OP is a string
    (
        "type_mismatch_op_string",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": "session,request",
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: context is a string, not an object
    (
        "type_mismatch_context_string",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": "not-an-object",
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: expected_manifest_version is a number
    (
        "type_mismatch_version_number",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": 1.0,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256,
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: expected_manifest_sha256 wrong length
    # (schema says 64-char lowercase hex; this is 16 chars).
    (
        "type_mismatch_sha256_wrong_length",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": "deadbeefdeadbeef",
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_TYPE_MISMATCH: expected_manifest_sha256 has
    # uppercase hex (schema says lowercase).
    (
        "type_mismatch_sha256_uppercase",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                "AP": ["identity", "role"],
                "OP": ["session", "request"],
                "context": {},
                "expected_manifest_version": LIVE_MANIFEST_VERSION,
                "expected_manifest_sha256": LIVE_MANIFEST_SHA256.upper(),
            },
        },
        "REF_SCHEMA_TYPE_MISMATCH",
    ),
    # REF_SCHEMA_RESERVED_CCS: legacy ccs_valid at top level (the
    # exact shape archived interception_proof_001 and _002 used).
    (
        "reserved_ccs_legacy_ccs_valid_at_top_level",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "ccs_valid": True,
            "interaction": _valid_interaction(),
        },
        "REF_SCHEMA_RESERVED_CCS",
    ),
    # REF_SCHEMA_RESERVED_CCS: ccs_valid inside interaction
    (
        "reserved_ccs_inside_interaction",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                **_valid_interaction(),
                "ccs_valid": True,
            },
        },
        "REF_SCHEMA_RESERVED_CCS",
    ),
    # REF_SCHEMA_RESERVED_CCS: continuity_token (a CCS-shaped
    # field by name, named in schema as an example).
    (
        "reserved_ccs_continuity_token",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                **_valid_interaction(),
                "continuity_token": "abc123",
            },
        },
        "REF_SCHEMA_RESERVED_CCS",
    ),
    # REF_SCHEMA_RESERVED_CCS: prior_state_hash (a CCS-shaped
    # field by name, named in schema as an example).
    (
        "reserved_ccs_prior_state_hash",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                **_valid_interaction(),
                "prior_state_hash": "deadbeef" * 8,
            },
        },
        "REF_SCHEMA_RESERVED_CCS",
    ),
    # REF_SCHEMA_RESERVED_CCS: case-insensitive substring match
    # ('CCS_state'). Schema says case-insensitive.
    (
        "reserved_ccs_case_insensitive",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                **_valid_interaction(),
                "CCS_state": "verified",
            },
        },
        "REF_SCHEMA_RESERVED_CCS",
    ),
    # REF_SCHEMA_UNKNOWN_KEY: an unknown non-CCS key directly inside
    # `interaction`, with valid pinning present so step 4c passes and
    # the set-difference check at step 4d fires (VL-054 / G14). Distinct
    # from REF_SCHEMA_TYPE_MISMATCH (present field of wrong type) and
    # REF_SCHEMA_RESERVED_CCS (key containing 'ccs').
    (
        "unknown_key_inside_interaction",
        {
            "target_url": "http://127.0.0.1:9000/target",
            "interaction": {
                **_valid_interaction(),
                "extra_field": "unexpected",
            },
        },
        "REF_SCHEMA_UNKNOWN_KEY",
    ),
]


@pytest.mark.parametrize(
    "case_id,body,expected_code",
    NEGATIVE_CASES,
    ids=[c[0] for c in NEGATIVE_CASES],
)
def test_schema_rejects(client, upstream_guard, case_id, body, expected_code):
    """
    Each schema-rejected request must:
      1. return HTTP 403,
      2. carry the schema-named refusal code in detail.refusal_reason_code,
      3. not have reached requests.post (upstream not called).

    Against pep.py at HEAD, all three assertions fail for most cases.
    That failure is the honest G2 signal that the validator (VL-018)
    and the PEP wiring (VL-019) must close.
    """
    response = client.post("/governed-call", json=body)

    assert response.status_code == 403, (
        f"[{case_id}] expected 403, got {response.status_code}; "
        f"body={response.text}"
    )

    detail = response.json().get("detail", {})
    assert detail.get("refusal_reason_code") == expected_code, (
        f"[{case_id}] expected refusal_reason_code={expected_code}, "
        f"got detail={detail}"
    )

    assert upstream_guard == [], (
        f"[{case_id}] schema-layer refusal must not forward to "
        f"target_url; upstream was called: {upstream_guard}"
    )


# ---------------------------------------------------------------------------
# REF_SCHEMA_PARSE_ERROR - sent as raw non-JSON bytes
# ---------------------------------------------------------------------------

def test_schema_rejects_parse_error(client, upstream_guard):
    """
    Malformed JSON must REFUSE with REF_SCHEMA_PARSE_ERROR per PEP
    boundary step 1. Sent as raw bytes so FastAPI's JSON parser
    fails before any handler runs - currently FastAPI returns 422
    (the Pydantic/JSON-decode default); the schema requires 403
    with the schema-named code. The test fails today on both
    status and code.
    """
    response = client.post(
        "/governed-call",
        content=b"this is not json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 403, (
        f"expected 403 on parse error, got {response.status_code}; "
        f"body={response.text}"
    )

    detail = response.json().get("detail", {})
    assert detail.get("refusal_reason_code") == "REF_SCHEMA_PARSE_ERROR", (
        f"expected refusal_reason_code=REF_SCHEMA_PARSE_ERROR, "
        f"got detail={detail}"
    )

    assert upstream_guard == [], (
        "parse-error refusal must not forward to target_url"
    )


# ---------------------------------------------------------------------------
# Positive case - a fully valid request round-trips
# ---------------------------------------------------------------------------

def test_schema_accepts_valid_request(client, upstream_guard):
    """
    A request that conforms to the schema in every respect must:
      1. reach evaluate(),
      2. return HTTP 200 with body containing decision="ELIGIBLE"
         and an envelope (assuming AC^3 and T^26 are satisfied,
         which they are for the AP/OP supplied here against the
         live manifest),
      3. forward to target_url exactly once.

    Against pep.py at HEAD, this fails because GovernedCallRequest
    has no `interaction` field; the request fails Pydantic
    validation at the wire boundary with HTTP 422, never reaching
    evaluate(). That failure is the honest signal that pep.py's
    wire shape must change as part of VL-019.

    The upstream_guard returns a canned 200 response so no network
    call is made; the assertion is on whether the call was
    attempted, not on what came back.
    """
    response = client.post("/governed-call", json=_valid_request())

    assert response.status_code == 200, (
        f"expected 200 on valid request, got {response.status_code}; "
        f"body={response.text}"
    )

    body = response.json()
    assert body.get("decision") == "ELIGIBLE", (
        f"expected decision=ELIGIBLE, got body={body}"
    )

    assert len(upstream_guard) == 1, (
        f"expected exactly one upstream call, got {len(upstream_guard)}: "
        f"{upstream_guard}"
    )
