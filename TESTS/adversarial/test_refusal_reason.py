"""Evaluator-layer refusal reason codes (the G_ namespace).

decide() names WHICH condition caused a REFUSE, one code per real refusal point,
short-circuit order preserved. evaluate() stays byte-behavior-identical (bare
"ELIGIBLE"/"REFUSE"); refusal_reason() is the additive diagnostic projection.
The G_ set is disjoint from the boundary/transport REF_* vocabulary.
"""
import pytest

from IMPLEMENTATION.evaluator import (
    decide, evaluate, refusal_reason, load_manifest, manifest_sha256,
    G_MANIFEST_MALFORMED, G_REQUIRED_SETS_UNRESOLVED, G_AC3, G_T26,
    G_MANIFEST_INTEGRITY, G_INTERNAL,
)

SHA = manifest_sha256()
M = load_manifest()


def _eligible_ctx():
    return {"AP": ["identity", "role"], "OP": ["session", "request"],
            "expected_manifest_version": "1.0", "expected_manifest_sha256": SHA}


# --- one code per real refusal point (canon section-6 short-circuit order) ---

def test_eligible_carries_no_reason():
    assert decide(_eligible_ctx(), M) == ("ELIGIBLE", None)
    assert refusal_reason(_eligible_ctx(), M) is None


def test_g_ac3_authority_shortfall():
    ctx = _eligible_ctx(); ctx["AP"] = ["role"]        # missing 'identity'
    assert decide(ctx, M) == ("REFUSE", G_AC3)
    assert refusal_reason(ctx, M) == G_AC3


def test_g_t26_coverage_shortfall():
    ctx = _eligible_ctx(); ctx["OP"] = ["session"]     # missing 'request'
    assert decide(ctx, M) == ("REFUSE", G_T26)


def test_g_manifest_integrity_sha_mismatch():
    ctx = _eligible_ctx(); ctx["expected_manifest_sha256"] = "0" * 64
    assert decide(ctx, M) == ("REFUSE", G_MANIFEST_INTEGRITY)


def test_g_manifest_malformed():
    assert decide(_eligible_ctx(), "not-a-manifest") == ("REFUSE", G_MANIFEST_MALFORMED)
    assert decide(_eligible_ctx(), {}) == ("REFUSE", G_MANIFEST_MALFORMED)


def test_g_required_sets_unresolved_unknown_type():
    typed = {"version": "1.0", "AR": ["identity", "role"], "R": ["session", "request"],
             "HIGH_IMPACT": [], "interaction_types": {
                 "read": {"AR": ["identity"], "R": ["session"], "high_impact": False}}}
    ctx = _eligible_ctx(); ctx["interaction_type"] = "does_not_exist"
    assert decide(ctx, typed) == ("REFUSE", G_REQUIRED_SETS_UNRESOLVED)


def test_g_internal_on_exception():
    # a non-dict ctx makes ac3_valid's ctx.get(...) raise -> fail-closed catch-all
    assert decide(["not", "a", "dict"], M) == ("REFUSE", G_INTERNAL)


# --- short-circuit: the FIRST failing condition wins ---

def test_shortcircuit_ac3_precedes_t26():
    ctx = _eligible_ctx(); ctx["AP"] = ["role"]; ctx["OP"] = ["session"]   # both fail
    assert decide(ctx, M)[1] == G_AC3


# --- evaluate() is byte-behavior-identical: bare state, never a code or tuple ---

def test_evaluate_backcompat_bare_state():
    assert evaluate(_eligible_ctx(), M) == "ELIGIBLE"
    bad = _eligible_ctx(); bad["AP"] = ["role"]
    r = evaluate(bad, M)
    assert r == "REFUSE" and isinstance(r, str)


# --- state and reason never disagree ---

@pytest.mark.parametrize("mut", [
    lambda c: c,
    lambda c: {**c, "AP": ["role"]},
    lambda c: {**c, "OP": ["session"]},
    lambda c: {**c, "expected_manifest_sha256": "x"},
])
def test_state_reason_consistency(mut):
    ctx = mut(_eligible_ctx())
    state, reason = decide(ctx, M)
    assert (state == "ELIGIBLE") == (reason is None)
    assert evaluate(ctx, M) == state


# --- disjoint from the boundary REF_* vocabulary ---

def test_g_codes_disjoint_from_ref_namespace():
    codes = {G_MANIFEST_MALFORMED, G_REQUIRED_SETS_UNRESOLVED, G_AC3, G_T26,
             G_MANIFEST_INTEGRITY, G_INTERNAL}
    assert len(codes) == 6
    assert all(c.startswith("G_") for c in codes)
    assert not any(c.startswith("REF_") for c in codes)


# --- end-to-end: the PEP surfaces the G_ code in its 403 (the wired gain) ---

def test_pep_403_carries_the_g_code(monkeypatch):
    from fastapi.testclient import TestClient
    from IMPLEMENTATION.pep import app

    def _no_upstream(*a, **k):
        raise AssertionError("upstream MUST NOT be reached on REFUSE")
    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", _no_upstream)

    resp = TestClient(app).post("/governed-call", json={
        "target_url": "https://upstream.example/refuse",
        "interaction": {"AP": [], "OP": [], "context": {},
                        "expected_manifest_version": "1.0",
                        "expected_manifest_sha256": SHA},
    })
    assert resp.status_code == 403
    detail = resp.json()["detail"]
    assert detail["terminal_state"] == "REFUSE"
    # AP=[] fails AC^3 first -> the gate now tells you WHICH condition refused
    assert detail["refusal_reason_code"] == G_AC3
