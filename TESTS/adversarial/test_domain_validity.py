"""Domain-semantic validity D(I, domain) - the D_ namespace.

assess() names WHICH domain condition caused an INVALID verdict, one code per
failure class, short-circuit (first predicate) order. domain_valid()/
domain_reason() are the additive projections. D is deterministic and fail-closed;
the D_ set is disjoint from the evaluator G_ vocabulary and the boundary REF_*
vocabulary. This module is ABOVE G(I) and UNWIRED - these tests exercise it
directly (nothing on the default admissibility path calls it).
"""
import importlib
import json

import pytest

from IMPLEMENTATION.domain_validity import (
    assess, domain_valid, domain_reason,
    safe_domain_manifest, domain_manifest_sha256, load_domain_manifest,
    D_MANIFEST_MALFORMED, D_DOMAIN_UNKNOWN, D_DOMAIN_UNDECLARED,
    D_FIELD_ABSENT, D_FIELD_INVALID, D_INTERNAL,
    DOMAIN_MANIFEST_EXAMPLE_PATH,
)


# --- fixtures -----------------------------------------------------------------

def _armed():
    """A small armed domain manifest exercising every rule + nesting."""
    return {
        "version": "1.0",
        "require_pin": False,
        "domains": {
            "healthcare_admin": {
                "bind_interaction_type": False, "predicates": [
                    {"path": "patient_consent", "rule": "equals", "value": True},
                    {"path": "compliance.hipaa_attestation", "rule": "equals", "value": "current"},
                    {"path": "record_basis", "rule": "present"},
                    {"path": "purpose", "rule": "in", "value": ["treatment", "payment", "operations"]},
                ]
            }
        },
    }


def _valid_healthcare_ctx():
    return {"domain": "healthcare_admin", "context": {
        "patient_consent": True,
        "compliance": {"hipaa_attestation": "current"},
        "record_basis": "chart-2026-07-26",
        "purpose": "treatment",
    }}


# --- unarmed manifest is a no-op pass-through (byte-behavior safety) -----------

def test_unarmed_no_domains_is_valid_noop():
    for dm in ({"version": "1.0"}, {"version": "1.0", "require_pin": False, "domains": {}}):
        assert assess({"domain": "anything", "context": {}}, dm) == ("VALID", None, None)
        assert domain_valid({}, dm) is True


def test_unarmed_ignores_declared_domain_entirely():
    # No domains configured -> even a would-be-invalid payload passes (D inert).
    assert domain_valid({"domain": "healthcare_admin", "context": {"patient_consent": False}},
                        {"version": "1.0", "require_pin": False, "domains": {}}) is True


# --- armed + valid content ----------------------------------------------------

def test_armed_valid_content_is_valid():
    assert assess(_valid_healthcare_ctx(), _armed()) == ("VALID", None, None)
    assert domain_valid(_valid_healthcare_ctx(), _armed()) is True
    assert domain_reason(_valid_healthcare_ctx(), _armed()) is None


# --- each rule fails to its code, first-failure short-circuit -----------------

def test_equals_bool_failure():
    ctx = _valid_healthcare_ctx(); ctx["context"]["patient_consent"] = False
    state, code, detail = assess(ctx, _armed())
    assert (state, code) == ("INVALID", D_FIELD_INVALID)
    assert detail["path"] == "patient_consent"


def test_recursive_nested_path_failure():
    # compliance.hipaa_attestation is a RECURSIVE descent into a nested object.
    ctx = _valid_healthcare_ctx(); ctx["context"]["compliance"]["hipaa_attestation"] = "lapsed"
    state, code, detail = assess(ctx, _armed())
    assert (state, code) == ("INVALID", D_FIELD_INVALID)
    assert detail["path"] == "compliance.hipaa_attestation"


def test_present_rule_absent_field():
    ctx = _valid_healthcare_ctx(); del ctx["context"]["record_basis"]
    assert assess(ctx, _armed())[:2] == ("INVALID", D_FIELD_ABSENT)


def test_in_rule_failure():
    ctx = _valid_healthcare_ctx(); ctx["context"]["purpose"] = "marketing"
    assert assess(ctx, _armed())[:2] == ("INVALID", D_FIELD_INVALID)


def test_first_failing_predicate_wins():
    # break the 1st (consent) and the 4th (purpose); the 1st code is returned.
    ctx = _valid_healthcare_ctx()
    ctx["context"]["patient_consent"] = False
    ctx["context"]["purpose"] = "marketing"
    assert assess(ctx, _armed())[2]["path"] == "patient_consent"


def test_not_in_rule():
    dm = {"version": "1.0", "require_pin": False, "domains": {"fx": {"bind_interaction_type": False, "predicates": [
        {"path": "jurisdiction", "rule": "not_in", "value": ["EMBARGOED"]}]}}}
    assert domain_valid({"domain": "fx", "context": {"jurisdiction": "US"}}, dm) is True
    assert domain_reason({"domain": "fx", "context": {"jurisdiction": "EMBARGOED"}}, dm) == D_FIELD_INVALID


def test_absent_rule():
    dm = {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": [
        {"path": "override", "rule": "absent"}]}}}
    assert domain_valid({"domain": "d", "context": {}}, dm) is True
    assert domain_reason({"domain": "d", "context": {"override": "x"}}, dm) == D_FIELD_INVALID


def test_value_predicate_on_missing_field_fails_closed():
    # equals/in on a field that does not resolve -> INVALID, not a crash.
    ctx = {"domain": "healthcare_admin", "context": {}}
    assert assess(ctx, _armed())[0] == "INVALID"


# --- domain resolution fail-closed --------------------------------------------

def test_declared_unknown_domain_fails_closed():
    ctx = {"domain": "no_such_domain", "context": {}}
    assert assess(ctx, _armed())[:2] == ("INVALID", D_DOMAIN_UNKNOWN)


def test_armed_undeclared_fails_closed_by_default():
    # DV-01 mitigation: an armed manifest DEMANDS a declared domain. Previously
    # this passed, letting any caller bypass the whole layer by omission.
    ctx = {"context": {}}  # armed manifest, no domain declared
    assert assess(ctx, _armed())[:2] == ("INVALID", D_DOMAIN_UNDECLARED)


def test_armed_undeclared_fails_closed_when_explicitly_required():
    dm = _armed(); dm["require_domain"] = True
    assert assess({"context": {}}, dm)[:2] == ("INVALID", D_DOMAIN_UNDECLARED)


def test_armed_undeclared_passes_only_on_explicit_opt_out():
    dm = _armed(); dm["require_domain"] = False   # eyes-open deployment choice
    assert assess({"context": {}}, dm) == ("VALID", None, None)


# --- malformed manifests fail closed ------------------------------------------

@pytest.mark.parametrize("bad", [
    "not-a-dict", 42, None, {},                                   # not a well-formed manifest
    {"version": 1},                                               # version not a string
    {"version": "1.0", "require_domain": "yes"},                  # require_domain not bool
    {"version": "1.0", "require_pin": False, "domains": "nope"},                        # domains not a dict
    {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": "nope"}}}, # predicates not a list
    {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": [{"rule": "present"}]}}},       # no path
    {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": [{"path": "x", "rule": "??"}]}}}, # bad rule
    {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": [{"path": "x", "rule": "equals"}]}}}, # equals w/o value
    {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": [{"path": "x", "rule": "in", "value": "no"}]}}}, # in w/o list
])
def test_malformed_manifest_is_D_MANIFEST_MALFORMED(bad):
    assert safe_domain_manifest(bad) is None
    assert assess({"domain": "d", "context": {}}, bad)[:2] == ("INVALID", D_MANIFEST_MALFORMED)


def test_internal_catch_all_on_pathological_predicate_value():
    # A value predicate whose pinned `value` is a non-iterable for `in` slips past
    # only if safe_domain_manifest is bypassed; call the internals to prove the
    # catch-all. Here we force an exception via a manifest that passes structural
    # validation but whose predicate list item mutates to a non-dict at eval time.
    class Exploding(list):
        def __iter__(self):
            raise RuntimeError("boom")
    dm = {"version": "1.0", "require_pin": False, "domains": {"d": {"bind_interaction_type": False, "predicates": Exploding()}}}
    # safe_domain_manifest iterates predicates -> the RuntimeError is caught -> D_INTERNAL
    assert assess({"domain": "d", "context": {}}, dm)[:2] == ("INVALID", D_INTERNAL)


# --- the rubber-stamp scenario: admissible content, domain-INVALID ------------

def test_rubber_stamp_guard_admissible_but_domain_invalid():
    """The load-bearing thesis: an interaction can be AUTHORIZED (would pass G(I))
    yet carry domain-INVALID content. D refuses it independently, so a human grant
    cannot rubber-stamp semantically-invalid data through the admissible state."""
    # Authority/coverage-shaped context (what G(I) reads) is fine; the DOMAIN
    # payload is non-compliant (consent withheld).
    ctx = {
        "AP": ["identity", "role"], "OP": ["session", "request"],
        "domain": "healthcare_admin",
        "context": {"patient_consent": False, "compliance": {"hipaa_attestation": "current"},
                    "record_basis": "x", "purpose": "treatment"},
    }
    assert domain_valid(ctx, _armed()) is False
    assert domain_reason(ctx, _armed()) == D_FIELD_INVALID


# --- determinism (canon section 9 reproducibility) ----------------------------

def test_determinism_identical_inputs_identical_verdict():
    ctx, dm = _valid_healthcare_ctx(), _armed()
    first = assess(ctx, dm)
    for _ in range(25):
        assert assess(ctx, dm) == first


# --- D_ disjoint from G_ and REF_ ---------------------------------------------

def test_D_namespace_disjoint_from_G_and_REF():
    d_codes = {D_MANIFEST_MALFORMED, D_DOMAIN_UNKNOWN, D_DOMAIN_UNDECLARED,
               D_FIELD_ABSENT, D_FIELD_INVALID, D_INTERNAL}
    assert all(c.startswith("D_") for c in d_codes)
    ev = importlib.import_module("IMPLEMENTATION.evaluator")
    g_codes = {v for k, v in vars(ev).items() if k.startswith("G_") and isinstance(v, str)}
    assert g_codes and d_codes.isdisjoint(g_codes)
    # REF_* live in pep/verifier; prefix-disjoint by construction.
    assert all(not c.startswith("REF_") for c in d_codes)


# --- the module is UNWIRED: evaluator/pep do not import it --------------------

def test_D_is_NOT_wired_into_the_evaluator_canon_boundary():
    """LOAD-BEARING (GR-1). D is wired at the PEP layer (enforcement) but must NOT
    enter evaluator.decide()/G(I) - that is an admissibility-semantics change and
    therefore an author-ratified canon-version event. If this fails, either the
    canon increment happened (update this test with it) or the boundary was
    crossed by accident."""
    import inspect
    from IMPLEMENTATION import evaluator
    assert "domain_validity" not in inspect.getsource(evaluator)
    assert "domain_control" not in inspect.getsource(evaluator)


def test_evaluator_sha256_still_matches_the_pinned_record():
    """The same boundary, checked against the pin rather than the source text."""
    import hashlib, json
    live = hashlib.sha256(open("IMPLEMENTATION/evaluator.py", "rb").read()).hexdigest()
    with open("EVIDENCE/published_hashes.json", "r", encoding="utf-8") as f:
        assert live == json.load(f)["evaluator_sha256"]


# --- example domain manifest on disk is well-formed and hash-pinnable ---------

def test_example_manifest_wellformed_and_hashable():
    dm = load_domain_manifest(DOMAIN_MANIFEST_EXAMPLE_PATH)
    assert safe_domain_manifest(dm) is not None
    h = domain_manifest_sha256(DOMAIN_MANIFEST_EXAMPLE_PATH)
    assert isinstance(h, str) and len(h) == 64
    # it is an EXAMPLE, not armed into any pinned record:
    with open("EVIDENCE/published_hashes.json", "r", encoding="utf-8") as f:
        assert "domain_manifest" not in f.read()
