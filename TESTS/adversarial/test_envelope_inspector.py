"""
Envelope inspector / reconciler tests (VL-097).

Derived from docs/restructure/26_envelope_inspector_spec.md and canon:
  - section 9 (fail-closed: every undecidable shape is a non-accept)
  - sections 11.5 / 11.6 (AP / OP are sets; binding compares set-equal)
  - sections 12-13 (currency is reassert()'s domain; deliberately NOT
    part of the reconcile matching predicate - spec section 3.4 (a))
  - section 14 (non-executing: the inspector computes verdicts only)

VL-098 extends with the semantic rung (spec 27): recorded-decision
consistency + live re-evaluation through the production evaluate().

The reconciler's auditability property under test: every executed action
maps to a signed, bound, single-use issued envelope, or is named
OUT_OF_SCOPE / DUPLICATE_CONSUMPTION. The trustworthy-log assumption is
the spec's explicit bound and is not (cannot be) tested here.

Per VL-040 constraint (i): no hash-value pinning - manifest hashes are
computed live; envelopes are built with a pinned timestamp_utc for
determinism; keypairs are generated live and never written to disk.

Ledger: VL-097, VL-098.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from IMPLEMENTATION.envelope import build_envelope, sign_envelope
from IMPLEMENTATION.envelope_inspector import (
    AUDIT_DUPLICATE_CONSUMPTION,
    AUDIT_MATCHED,
    AUDIT_OUT_OF_SCOPE,
    ENVELOPE_CONSUMED,
    ENVELOPE_INVALID,
    ENVELOPE_UNUSED,
    INCONSISTENT_CONDITIONS_MALFORMED,
    INCONSISTENT_ELIGIBLE_WITH_FAILED_CONDITION,
    INCONSISTENT_REFUSE_WITH_ALL_CONDITIONS_TRUE,
    INCONSISTENT_UNKNOWN_DECISION,
    ISSUER_VERIFIED,
    inspect_envelope,
    reconcile,
    reevaluate_envelope,
    verify_issuer,
)
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_SIGNATURE_INVALID,
    REF_VERIFY_SIGNATURE_UNKNOWN_KEY,
)


TARGET_URL = "http://127.0.0.1:9000/target"
KEY_ID = "gate-ed25519-001"
PINNED_TS = "2026-06-10T00:00:00+00:00"


def _interaction(**overrides):
    manifest = load_manifest()
    interaction = {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {"purpose": "inspector-test"},
        "expected_manifest_version": manifest["version"],
        "expected_manifest_sha256": manifest_sha256(),
    }
    interaction.update(overrides)
    return interaction


def _envelope(interaction=None, decision="ELIGIBLE"):
    manifest = load_manifest()
    return build_envelope(
        decision=decision,
        target_url=TARGET_URL,
        normalized_interaction=interaction or _interaction(),
        manifest=manifest,
        ac3=True,
        t26=True,
        manifest_integrity=True,
        timestamp_utc=PINNED_TS,
    )


@pytest.fixture()
def issuer():
    priv = Ed25519PrivateKey.generate()
    return {"private": priv, "public": priv.public_key(), "key_id": KEY_ID}


def _signed(issuer, interaction=None, decision_id=None, not_after=None,
            decision="ELIGIBLE"):
    return sign_envelope(
        _envelope(interaction=interaction, decision=decision),
        issuer["private"],
        issuer["key_id"],
        not_after=not_after,
        decision_id=decision_id,
    )


def _action(interaction=None, decision_id=None, target_url=TARGET_URL):
    action = {"target_url": target_url, "interaction": interaction or _interaction()}
    if decision_id is not None:
        action["decision_id"] = decision_id
    return action


# ---------------------------------------------------------------------------
# Capability 1: inspect (decode + structural fail-closed; canon section 9)
# ---------------------------------------------------------------------------


def test_inspect_decodes_bound_scope(issuer):
    """Spec 3.1: scope carries exactly the bound surface; meta carries the
    issuance record. Canon 11.5/11.6: AP/OP reported as recorded."""
    env = _signed(issuer, decision_id="d-001",
                  not_after=datetime(2027, 1, 1, tzinfo=timezone.utc))
    decoded = inspect_envelope(env)
    assert decoded["ok"] is True
    scope = decoded["scope"]
    assert scope["target_url"] == TARGET_URL
    assert scope["AP"] == ["identity", "role"]
    assert scope["OP"] == ["session", "request"]
    assert scope["context"] == {"purpose": "inspector-test"}
    assert scope["expected_manifest_sha256"] == manifest_sha256()
    meta = decoded["meta"]
    assert meta["decision"] == "ELIGIBLE"
    assert meta["signed"] is True
    assert meta["issuer_key_id"] == KEY_ID
    assert meta["decision_id"] == "d-001"
    assert meta["not_after"] == "2027-01-01T00:00:00+00:00"


def test_inspect_unsigned_envelope_reports_unsigned():
    """Spec 3.1: decode-only also serves unsigned envelopes; meta.signed
    False, optional fields None."""
    decoded = inspect_envelope(_envelope())
    assert decoded["ok"] is True
    assert decoded["meta"]["signed"] is False
    assert decoded["meta"]["issuer_key_id"] is None
    assert decoded["meta"]["decision_id"] is None


@pytest.mark.parametrize("bad", [None, [], "envelope", 7])
def test_inspect_non_dict_fails_closed(bad):
    """Canon section 9: a non-dict is undecidable -> fail-closed."""
    decoded = inspect_envelope(bad)
    assert decoded == {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}


def test_inspect_missing_required_key_fails_closed():
    """Canon section 9 / verifier structural guard parity: each missing
    required key fails closed."""
    env = _envelope()
    for key in ("canon", "evaluator", "evaluated_against",
                "request_context", "decision_sha256", "target_url"):
        broken = {k: v for k, v in env.items() if k != key}
        assert inspect_envelope(broken)["ok"] is False


def test_inspect_missing_request_context_subkey_fails_closed():
    env = _envelope()
    for key in ("AP", "OP", "context",
                "expected_manifest_version", "expected_manifest_sha256"):
        broken = dict(env)
        broken["request_context"] = {
            k: v for k, v in env["request_context"].items() if k != key
        }
        assert inspect_envelope(broken)["ok"] is False


# ---------------------------------------------------------------------------
# Capability 2: verify_issuer (signature + window alone; spec 3.2)
# ---------------------------------------------------------------------------


def test_verify_issuer_accepts_genuine(issuer):
    """Spec 3.2: a genuine signature from a pinned key verifies."""
    env = _signed(issuer)
    result = verify_issuer(env, {KEY_ID: issuer["public"]})
    assert result == {"verified": True, "reason": ISSUER_VERIFIED}


def test_verify_issuer_rejects_tamper(issuer):
    """Canon 11.9 (integrity-verifiable): any signed-region mutation
    breaks the signature."""
    env = _signed(issuer)
    tampered = dict(env)
    tampered["target_url"] = "http://evil.example/target"
    result = verify_issuer(tampered, {KEY_ID: issuer["public"]})
    assert result == {"verified": False, "reason": REF_VERIFY_SIGNATURE_INVALID}


def test_verify_issuer_rejects_unknown_key(issuer):
    """Canon section 9: an unpinned key_id is a refuse, not a downgrade."""
    env = _signed(issuer)
    result = verify_issuer(env, {"other-key": issuer["public"]})
    assert result == {"verified": False, "reason": REF_VERIFY_SIGNATURE_UNKNOWN_KEY}


def test_verify_issuer_rejects_missing_signature(issuer):
    """Canon section 9: an unsigned envelope cannot be attributed."""
    result = verify_issuer(_envelope(), {KEY_ID: issuer["public"]})
    assert result == {"verified": False, "reason": REF_VERIFY_SIGNATURE_INVALID}


def test_verify_issuer_rejects_expired(issuer):
    """VL-041 semantics: now >= not_after refuses (strict, skew 0)."""
    not_after = datetime(2026, 1, 1, tzinfo=timezone.utc)
    env = _signed(issuer, not_after=not_after)
    result = verify_issuer(env, {KEY_ID: issuer["public"]},
                           now=datetime(2026, 6, 1, tzinfo=timezone.utc))
    assert result == {"verified": False, "reason": REF_VERIFY_SIGNATURE_EXPIRED}


def test_verify_issuer_clock_skew_widens_window(issuer):
    """VL-075 parity: now within not_after + skew verifies; negative skew
    raises (config error, fail-loud)."""
    not_after = datetime(2026, 6, 1, tzinfo=timezone.utc)
    env = _signed(issuer, not_after=not_after)
    keys = {KEY_ID: issuer["public"]}
    just_after = not_after + timedelta(seconds=30)
    assert verify_issuer(env, keys, now=just_after)["verified"] is False
    assert verify_issuer(env, keys, now=just_after,
                         clock_skew=timedelta(seconds=60))["verified"] is True
    with pytest.raises(ValueError):
        verify_issuer(env, keys, clock_skew=timedelta(seconds=-1))


def test_verify_issuer_requires_pinned_keys(issuer):
    """Spec 3.2: the unsigned path is not an audit path."""
    with pytest.raises(ValueError):
        verify_issuer(_signed(issuer), None)


def test_verify_issuer_asserts_no_currency(issuer):
    """Spec 3.2: issuer verification alone says nothing about currency -
    an envelope pinned to a STALE evaluator hash still attributes to its
    issuer (currency is reassert()'s domain, canon sections 12-13).
    Mutating evaluator_sha256 breaks the signature, so the stale pin is
    signed in from the start."""
    manifest = load_manifest()
    env = build_envelope(
        decision="ELIGIBLE", target_url=TARGET_URL,
        normalized_interaction=_interaction(), manifest=manifest,
        ac3=True, t26=True, manifest_integrity=True, timestamp_utc=PINNED_TS,
    )
    env["evaluator"] = {"version": "0.9.8.4", "evaluator_sha256": "0" * 64}
    signed = sign_envelope(env, issuer["private"], issuer["key_id"])
    assert verify_issuer(signed, {KEY_ID: issuer["public"]})["verified"] is True


# ---------------------------------------------------------------------------
# Capability 4: reconcile (spec 3.4)
# ---------------------------------------------------------------------------


def test_reconcile_matched_consumes_envelope(issuer):
    """The positive control: one issued, one executed, bound -> MATCHED,
    envelope CONSUMED, summary clean."""
    env = _signed(issuer, decision_id="d-001")
    report = reconcile([_action(decision_id="d-001")], [env],
                       pinned_public_keys={KEY_ID: issuer["public"]})
    assert report["actions"][0]["verdict"] == AUDIT_MATCHED
    assert report["actions"][0]["envelope_index"] == 0
    assert report["envelopes"][0]["status"] == ENVELOPE_CONSUMED
    assert report["summary"]["clean"] is True


def test_reconcile_no_envelopes_out_of_scope():
    """The core auditability property: an executed action with no issued
    envelope at all is OUT_OF_SCOPE (the A1-shaped event in audit)."""
    report = reconcile([_action()], [])
    assert report["actions"][0]["verdict"] == AUDIT_OUT_OF_SCOPE
    assert report["summary"]["clean"] is False


@pytest.mark.parametrize("mutate", [
    lambda a: a.update(target_url="http://other.example/target"),
    lambda a: a["interaction"].update(AP=["identity"]),
    lambda a: a["interaction"].update(OP=["session", "request", "files:write"]),
    lambda a: a["interaction"].update(context={"purpose": "swapped"}),
    lambda a: a["interaction"].update(expected_manifest_version="9.9.9"),
    lambda a: a["interaction"].update(expected_manifest_sha256="0" * 64),
])
def test_reconcile_binding_mismatch_each_field_out_of_scope(issuer, mutate):
    """Verifier step-3 parity: each of the bound fields discriminates.
    An action diverging on any one field does not match (canon 11.5/11.6
    set semantics for AP/OP; string equality for target_url and pins;
    canonical_json equality for context)."""
    env = _signed(issuer)
    action = _action()
    mutate(action)
    report = reconcile([action], [env])
    assert report["actions"][0]["verdict"] == AUDIT_OUT_OF_SCOPE


def test_reconcile_ap_op_set_semantics(issuer):
    """Canon 11.5/11.6: AP/OP compare as sets - an action logging the
    same AP unsorted and duplicated still matches."""
    env = _signed(issuer)
    action = _action(interaction=_interaction(
        AP=["role", "identity", "role"]))
    report = reconcile([action], [env])
    assert report["actions"][0]["verdict"] == AUDIT_MATCHED


def test_reconcile_duplicate_consumption(issuer):
    """Single-use (VL-066 exactly-once): the same authorization honored
    twice in the log is DUPLICATE_CONSUMPTION on the second action."""
    env = _signed(issuer, decision_id="d-001")
    actions = [_action(decision_id="d-001"), _action(decision_id="d-001")]
    report = reconcile(actions, [env])
    assert report["actions"][0]["verdict"] == AUDIT_MATCHED
    assert report["actions"][1]["verdict"] == AUDIT_DUPLICATE_CONSUMPTION
    assert report["summary"]["clean"] is False


def test_reconcile_unused_envelope_is_informational(issuer):
    """Spec 3.4: issued-but-never-exercised is UNUSED, not a violation."""
    report = reconcile([], [_signed(issuer)])
    assert report["envelopes"][0]["status"] == ENVELOPE_UNUSED
    assert report["summary"]["unused"] == 1
    assert report["summary"]["clean"] is True


def test_reconcile_forged_issuance_entry_cannot_legitimize(issuer):
    """Spec 3.4: with pinned keys, an issuance-log entry signed by a
    non-pinned key is INVALID_ENVELOPE and excluded - the action it
    would have covered is OUT_OF_SCOPE."""
    attacker = Ed25519PrivateKey.generate()
    forged = sign_envelope(_envelope(), attacker, KEY_ID)
    report = reconcile([_action()], [forged],
                       pinned_public_keys={KEY_ID: issuer["public"]})
    assert report["envelopes"][0]["status"] == ENVELOPE_INVALID
    assert report["actions"][0]["verdict"] == AUDIT_OUT_OF_SCOPE


def test_reconcile_refuse_decision_never_matches(issuer):
    """Spec 3.4: only decision == ELIGIBLE authorizes; a REFUSE envelope
    in the issuance log cannot cover an action."""
    refused = _signed(issuer, decision="REFUSE")
    report = reconcile([_action()], [refused])
    assert report["envelopes"][0]["status"] == ENVELOPE_INVALID
    assert report["envelopes"][0]["reason"] == "DECISION_NOT_ELIGIBLE"
    assert report["actions"][0]["verdict"] == AUDIT_OUT_OF_SCOPE


def test_reconcile_decision_id_discriminates(issuer):
    """Spec 3.4: an action carrying a decision_id matches only the
    envelope with that id, even when another envelope binds the same
    interaction."""
    env_a = _signed(issuer, decision_id="d-aaa")
    env_b = _signed(issuer, decision_id="d-bbb")
    report = reconcile([_action(decision_id="d-bbb")], [env_a, env_b])
    assert report["actions"][0]["verdict"] == AUDIT_MATCHED
    assert report["actions"][0]["envelope_index"] == 1
    assert report["envelopes"][0]["status"] == ENVELOPE_UNUSED


def test_reconcile_currency_not_in_matching_predicate(issuer):
    """Spec 3.4 deliberate non-check (a): an envelope whose evaluator pin
    no longer matches live state (RE-EVALUATE-REQUIRED under reassert)
    STILL matches in reconcile - audit-time transitions must not
    retro-invalidate a then-current authorization. Currency is
    capability 3, run separately. The stale pin is signed in, so the
    issuer screen passes."""
    env = _envelope()
    env["evaluator"] = {"version": "0.9.8.4", "evaluator_sha256": "0" * 64}
    signed = sign_envelope(env, issuer["private"], issuer["key_id"])
    report = reconcile([_action()], [signed],
                       pinned_public_keys={KEY_ID: issuer["public"]})
    assert report["actions"][0]["verdict"] == AUDIT_MATCHED


def test_reconcile_malformed_action_out_of_scope(issuer):
    """Canon section 9: an undecidable action record is OUT_OF_SCOPE,
    never a raise and never a match."""
    report = reconcile([{"target_url": TARGET_URL}, "not-a-dict"],
                       [_signed(issuer)])
    assert [a["verdict"] for a in report["actions"]] == [
        AUDIT_OUT_OF_SCOPE, AUDIT_OUT_OF_SCOPE]


# ---------------------------------------------------------------------------
# Capability 5: reevaluate (VL-098, spec 27)
# ---------------------------------------------------------------------------


def test_reevaluate_reproduces_current_eligible():
    """Spec 27 positive control: a freshly issued ELIGIBLE envelope is
    internally consistent and reproduces ELIGIBLE against live state
    (canon 11.7 AC3, 11.8 T26, 11.9 integrity all re-confirmed)."""
    result = reevaluate_envelope(_envelope())
    assert result["ok"] is True
    assert result["consistent"] is True
    assert result["inconsistency"] is None
    assert result["recorded_decision"] == "ELIGIBLE"
    assert result["live_decision"] == "ELIGIBLE"
    assert result["live_conditions"] == {
        "ac3": True, "t26": True, "manifest_integrity": True}
    assert result["reproduced"] is True


@pytest.mark.parametrize("failed", ["ac3", "t26", "manifest_integrity"])
def test_reevaluate_eligible_with_failed_condition_inconsistent(failed):
    """Spec 27 section 2.1: ELIGIBLE requires all three recorded
    conditions True; each single False is the contradiction evaluate()'s
    short-circuit could never produce."""
    env = _envelope()
    env["condition_results"][failed] = False
    result = reevaluate_envelope(env)
    assert result["consistent"] is False
    assert result["inconsistency"] == INCONSISTENT_ELIGIBLE_WITH_FAILED_CONDITION


def test_reevaluate_refuse_with_all_true_inconsistent():
    """Spec 27 section 2.1: all three conditions True forces ELIGIBLE in
    evaluate(); a REFUSE recording all-True is self-contradictory."""
    env = _envelope(decision="REFUSE")
    result = reevaluate_envelope(env)
    assert result["consistent"] is False
    assert result["inconsistency"] == INCONSISTENT_REFUSE_WITH_ALL_CONDITIONS_TRUE


def test_reevaluate_refuse_with_failed_condition_consistent():
    """Spec 27 section 2.1: REFUSE with at least one False condition is
    exactly what evaluate() produces - consistent."""
    interaction = _interaction(AP=["identity"])  # AC3 fails (missing "role")
    env = _envelope(interaction=interaction, decision="REFUSE")
    env["condition_results"]["ac3"] = False
    result = reevaluate_envelope(env)
    assert result["consistent"] is True
    assert result["recorded_decision"] == "REFUSE"
    assert result["live_decision"] == "REFUSE"
    assert result["live_conditions"]["ac3"] is False
    assert result["reproduced"] is True


@pytest.mark.parametrize("mutate", [
    lambda e: e.pop("condition_results"),
    lambda e: e.update(condition_results="not-a-dict"),
    lambda e: e["condition_results"].pop("t26"),
    lambda e: e["condition_results"].update(ac3="true"),
])
def test_reevaluate_malformed_conditions_fail_closed(mutate):
    """Canon section 9: missing or non-boolean condition_results is
    undecidable -> inconsistent, never a raise. (The structural guard
    does not require condition_results; reevaluate checks it itself.)"""
    env = _envelope()
    mutate(env)
    result = reevaluate_envelope(env)
    assert result["ok"] is True
    assert result["consistent"] is False
    assert result["inconsistency"] == INCONSISTENT_CONDITIONS_MALFORMED


def test_reevaluate_unknown_decision_inconsistent():
    """Spec 27 section 2.1: the decision vocabulary is closed."""
    env = _envelope()
    env["decision"] = "MAYBE"
    result = reevaluate_envelope(env)
    assert result["inconsistency"] == INCONSISTENT_UNKNOWN_DECISION


def test_reevaluate_ccs_none_not_consulted():
    """VL-029 Decision A: condition_results.ccs is None at issuance and
    is reassert-time, not issue-time; it must not affect consistency."""
    env = _envelope()
    assert env["condition_results"]["ccs"] is None
    assert reevaluate_envelope(env)["consistent"] is True


def test_reevaluate_stale_manifest_pin_decision_changed():
    """Spec 27 section 2.2: an ELIGIBLE envelope whose recorded manifest
    pins no longer match live state re-evaluates REFUSE (integrity fails)
    - the answer RE-EVALUATE-REQUIRED demands, performed by a tool. The
    recorded conditions stay all-True (consistent at issuance); only the
    LIVE verdict changes."""
    interaction = _interaction(expected_manifest_sha256="0" * 64)
    env = _envelope(interaction=interaction)
    result = reevaluate_envelope(env)
    assert result["consistent"] is True
    assert result["live_decision"] == "REFUSE"
    assert result["live_conditions"]["manifest_integrity"] is False
    assert result["live_conditions"]["ac3"] is True
    assert result["reproduced"] is False


def test_reevaluate_malformed_manifest_fails_closed():
    """Canon section 9 / safe_manifest: a malformed live manifest yields
    REFUSE and all-False live conditions, never a raise."""
    result = reevaluate_envelope(_envelope(), manifest={"AR": "not-a-list"})
    assert result["live_decision"] == "REFUSE"
    assert result["live_conditions"] == {
        "ac3": False, "t26": False, "manifest_integrity": False}
    assert result["reproduced"] is False


@pytest.mark.parametrize("bad", [None, [], "envelope", 7])
def test_reevaluate_structural_fail_closed(bad):
    """Parity with inspect: the verifier's structural guard, fail-closed."""
    assert reevaluate_envelope(bad) == {
        "ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}


def test_cli_reevaluate_exit_codes(tmp_path):
    """Spec 27 section 3: exit 0 iff ok and consistent and reproduced."""
    good = tmp_path / "good.json"
    good.write_text(json.dumps(_envelope()), encoding="utf-8")
    assert _run_cli(["reevaluate", str(good)]).returncode == 0

    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps(_envelope(
        interaction=_interaction(expected_manifest_sha256="0" * 64))),
        encoding="utf-8")
    result = _run_cli(["reevaluate", str(stale)])
    assert result.returncode == 1
    assert '"reproduced": false' in result.stdout


# ---------------------------------------------------------------------------
# CLI (spec 3.5): exit codes over tmp files
# ---------------------------------------------------------------------------


def _run_cli(args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "IMPLEMENTATION.envelope_inspector"] + args,
        capture_output=True, text=True, cwd=cwd,
    )


def _pub_hex(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()


def test_cli_inspect_and_reconcile_exit_codes(tmp_path, issuer):
    """Spec 3.5: inspect exits 0 on a current, verifiable envelope;
    reconcile exits 0 iff clean, 1 otherwise. Runs from the repo root so
    reassert() reads the live local state."""
    env = _signed(issuer, decision_id="d-001")
    env_path = tmp_path / "envelope.json"
    env_path.write_text(json.dumps(env), encoding="utf-8")
    keys_path = tmp_path / "keys.json"
    keys_path.write_text(
        json.dumps({KEY_ID: _pub_hex(issuer["public"])}), encoding="utf-8")

    result = _run_cli(["inspect", str(env_path), "--keys", str(keys_path)])
    assert result.returncode == 0, result.stdout + result.stderr

    issued = tmp_path / "issued.jsonl"
    issued.write_text(json.dumps(env) + "\n", encoding="utf-8")
    executed_clean = tmp_path / "executed_clean.jsonl"
    executed_clean.write_text(
        json.dumps(_action(decision_id="d-001")) + "\n", encoding="utf-8")
    result = _run_cli(["reconcile", "--issued", str(issued),
                       "--executed", str(executed_clean),
                       "--keys", str(keys_path)])
    assert result.returncode == 0, result.stdout + result.stderr

    executed_dirty = tmp_path / "executed_dirty.jsonl"
    executed_dirty.write_text(
        json.dumps(_action(decision_id="d-001")) + "\n"
        + json.dumps(_action(decision_id="d-001")) + "\n", encoding="utf-8")
    result = _run_cli(["reconcile", "--issued", str(issued),
                       "--executed", str(executed_dirty)])
    assert result.returncode == 1
    assert "DUPLICATE_CONSUMPTION" in result.stdout
