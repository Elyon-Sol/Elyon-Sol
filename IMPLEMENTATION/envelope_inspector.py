"""
Envelope inspector / reconciler for Elyon-Sol (VL-097).

Built per docs/restructure/26_envelope_inspector_spec.md from primary
sources IMPLEMENTATION/envelope.py and IMPLEMENTATION/verifier.py
(re-read in full in the VL-097 session per SESSION_PROTOCOL step 4).

==============================================================
What this module does
==============================================================

A LOCAL, read-only audit tool over signed admissibility envelopes.
Four capabilities (the four named in STATE.md's Next-open-action
directive, chosen 2026-06-10):

1. inspect_envelope(envelope): decode the exact scope a signed envelope
   binds (AP / OP / context / target_url + manifest version+sha pins)
   plus issuance metadata. Decode only; fail-closed on shape.
2. verify_issuer(envelope, pinned_public_keys, ...): the issuer
   signature + validity-window check ALONE (verifier steps 1.5 + 1.5b
   semantics), so an auditor can attribute an envelope to an issuer
   without asserting currency or binding.
3. Currency: not wrapped - callers (and the CLI) use
   envelope.reassert(envelope, record_source=...) directly; its outcome
   vocabulary is already closed and public.
4. reconcile(executed_actions, issued_envelopes, ...): classify every
   EXECUTED action against the ISSUED envelopes. An action with no
   matching, bound, single-use envelope is OUT_OF_SCOPE (the
   auditability property from the VL-096 follow-on discussion).
5. reevaluate_envelope(envelope) (VL-098, spec 27): the semantic rung -
   internal consistency of the recorded decision vs the recorded
   condition_results, plus a live re-run of the PRODUCTION evaluate()
   (and the three condition functions) over the envelope's recorded
   request_context against the live manifest. This is the tool that
   PERFORMS the re-evaluation reassert()'s RE-EVALUATE-REQUIRED
   outcome demands; before VL-098 that outcome named work no tool did.

The evaluation ladder: shape (inspect) -> provenance (verify_issuer) ->
currency (reassert) -> semantics (reevaluate) -> log completeness
(reconcile). The rungs are orthogonal and composable by design.

==============================================================
Honest scope (GR-3 / canon section 14)
==============================================================

Enabling / audit infrastructure and red-team ergonomics, NOT a G5
closer. Non-executing: it computes verdicts over artifacts and performs
no action. No new canonical invariant. No production module changes; no
caller on the default pep.py path (build-then-wire, parity with
VL-074/076/078). The reconciler audits a LOG: a target that acts
without logging, or logs falsely, is outside what any log audit can
establish. That trustworthy-log assumption is the explicit bound on
capability 4.

==============================================================
Integration boundary (one-sided per VL-025 pattern)
==============================================================

Imports FROM envelope.py (reassert, canonical_json, and
_SIGNATURE_EXCLUDED_KEYS - the one canonical definition of the signed
region, so this module cannot diverge from sign_envelope) and FROM
verifier.py (the REF_VERIFY_* vocabulary it reuses and the
structural-guard key tuples). Nothing imports this module.

The binding predicate applied by reconcile() is the same five
comparisons verify_envelope step 3 applies: target_url string equality;
AP / OP normalized-set equality (canon sections 11.5 / 11.6 define them
as sets); manifest-pinning string equality; context canonical_json
equality (the artifact-08-gap-candidate-1 [INFERENCE] choice, reused
unchanged for consistency).

Deliberate non-checks (spec section 3.4, recorded honestly):
(a) reassert() currency is NOT part of the matching predicate - the
repository may have legitimately transitioned since issuance, and a
then-current envelope must not be retro-invalidated at audit time;
(b) not_after vs execution time is NOT checked - the minimal action
shape carries no timestamp (future knob, not built);
(c) matching is greedy in log order - exact under single-use
decision_ids (the gate's issuance behavior since VL-066),
deterministic and order-documented without them.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from IMPLEMENTATION.envelope import (
    _SIGNATURE_EXCLUDED_KEYS,
    canonical_json,
    reassert,
)
from IMPLEMENTATION.evaluator import (
    ac3_valid,
    evaluate,
    load_manifest,
    manifest_integrity_valid,
    safe_manifest,
    t26_valid,
)
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_SIGNATURE_INVALID,
    REF_VERIFY_SIGNATURE_UNKNOWN_KEY,
    _REQUEST_CONTEXT_KEYS,
    _REQUIRED_ENVELOPE_KEYS,
    _normalize_set_field,
)


# ---------------------------------------------------------------------------
# Verdict vocabulary (closed sets; spec section 3.4). AUDIT_* parallels the
# REF_SCHEMA_* / REF_VERIFY_* convention: a distinct layer owns a distinct
# prefix. verifier.py stays the canonical REF_VERIFY_* home; the audit layer
# introduces no REF_* code because reconcile() refuses nothing - it reports.
# ---------------------------------------------------------------------------

ISSUER_VERIFIED = "ISSUER_VERIFIED"

AUDIT_MATCHED = "MATCHED"
AUDIT_OUT_OF_SCOPE = "OUT_OF_SCOPE"
AUDIT_DUPLICATE_CONSUMPTION = "DUPLICATE_CONSUMPTION"

ENVELOPE_CONSUMED = "CONSUMED"
ENVELOPE_UNUSED = "UNUSED"
ENVELOPE_INVALID = "INVALID_ENVELOPE"

# Metadata fields decoded by inspect_envelope (None where absent).
_META_OPTIONAL_KEYS = (
    "issuer_key_id",
    "decision_id",
    "not_after",
    "timestamp_utc",
    "envelope_version",
)


# ---------------------------------------------------------------------------
# Capability 1: inspect
# ---------------------------------------------------------------------------


def _structurally_sound(envelope: Any) -> bool:
    """The verifier's structural presence guard (verify_envelope step 1),
    reproduced over the imported key tuples so the inspector accepts and
    rejects exactly the shapes the verifier would."""
    if not isinstance(envelope, dict):
        return False
    for key in _REQUIRED_ENVELOPE_KEYS:
        if key not in envelope:
            return False
    rc = envelope["request_context"]
    if not isinstance(rc, dict):
        return False
    for key in _REQUEST_CONTEXT_KEYS:
        if key not in rc:
            return False
    return True


def inspect_envelope(envelope: Any) -> Dict[str, Any]:
    """
    Decode the exact scope a signed envelope binds, plus issuance
    metadata. Pure structural decode: no signature, no currency, no
    binding judgment. Fail-closed on shape (canon section 9): a
    non-dict, or a dict failing the verifier's structural guard, is
    {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}.

    Returns {"ok": True, "scope": {...}, "meta": {...}} where scope is
    exactly the bound surface (what verify_envelope's binding check
    would compare) and meta is the issuance/pinning record.
    """
    if not _structurally_sound(envelope):
        return {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}

    rc = envelope["request_context"]
    scope = {
        "target_url": envelope["target_url"],
        "AP": list(rc["AP"]) if isinstance(rc["AP"], list) else rc["AP"],
        "OP": list(rc["OP"]) if isinstance(rc["OP"], list) else rc["OP"],
        "context": rc["context"],
        "expected_manifest_version": rc["expected_manifest_version"],
        "expected_manifest_sha256": rc["expected_manifest_sha256"],
    }
    meta: Dict[str, Any] = {
        "decision": envelope.get("decision"),
        "decision_sha256": envelope["decision_sha256"],
        "canon": envelope["canon"],
        "evaluator": envelope["evaluator"],
        "evaluated_against": envelope["evaluated_against"],
        "signed": isinstance(envelope.get("issuer_signature"), str),
    }
    for key in _META_OPTIONAL_KEYS:
        meta[key] = envelope.get(key)
    return {"ok": True, "scope": scope, "meta": meta}


# ---------------------------------------------------------------------------
# Capability 2: issuer verification (signature + window ALONE)
# ---------------------------------------------------------------------------


def verify_issuer(
    envelope: Any,
    pinned_public_keys: Dict[str, Any],
    now: Optional[datetime] = None,
    clock_skew: timedelta = timedelta(0),
) -> Dict[str, Any]:
    """
    Verify the issuer signature and validity window of an envelope
    against a pinned {key_id: public_key} map - verifier.py steps
    1.5 + 1.5b semantics, standalone, with the identical fail-closed
    codes. Asserts NOTHING about currency (reassert) or binding.

    pinned_public_keys is required: the unsigned path is not an audit
    path (an unattributable envelope cannot anchor an audit claim).
    clock_skew per VL-075: non-negative; widens the not_after window
    symmetrically; default 0 is the strict check.

    Returns {"verified": bool, "reason": str}; accept reason
    ISSUER_VERIFIED.
    """
    if clock_skew < timedelta(0):
        raise ValueError("clock_skew must be non-negative")
    if pinned_public_keys is None:
        raise ValueError("pinned_public_keys is required (audit is signed-path only)")

    if not isinstance(envelope, dict):
        return {"verified": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}

    key_id = envelope.get("issuer_key_id")
    signature_hex = envelope.get("issuer_signature")
    if not isinstance(key_id, str) or not isinstance(signature_hex, str):
        return {"verified": False, "reason": REF_VERIFY_SIGNATURE_INVALID}
    public_key = pinned_public_keys.get(key_id)
    if public_key is None:
        return {"verified": False, "reason": REF_VERIFY_SIGNATURE_UNKNOWN_KEY}

    # The signed region: the one canonical definition, imported from
    # envelope.py (_SIGNATURE_EXCLUDED_KEYS), so this check cannot diverge
    # from sign_envelope.
    region = {k: v for k, v in envelope.items() if k not in _SIGNATURE_EXCLUDED_KEYS}
    message = canonical_json(region).encode("utf-8")
    try:
        public_key.verify(bytes.fromhex(signature_hex), message)
    except Exception:
        return {"verified": False, "reason": REF_VERIFY_SIGNATURE_INVALID}

    # Validity window (verifier step 1.5b): not_after, when present, is
    # inside the just-verified signed region, hence tamper-proof. Absence
    # means no expiry (VL-040 semantics). Fail-closed on malformed/naive.
    not_after_raw = envelope.get("not_after")
    if not_after_raw is not None:
        try:
            not_after = datetime.fromisoformat(not_after_raw)
        except (ValueError, TypeError):
            return {"verified": False, "reason": REF_VERIFY_SIGNATURE_EXPIRED}
        if not_after.tzinfo is None:
            return {"verified": False, "reason": REF_VERIFY_SIGNATURE_EXPIRED}
        current = now if now is not None else datetime.now(timezone.utc)
        if current >= not_after + clock_skew:
            return {"verified": False, "reason": REF_VERIFY_SIGNATURE_EXPIRED}

    return {"verified": True, "reason": ISSUER_VERIFIED}


# ---------------------------------------------------------------------------
# Capability 5: semantic re-evaluation (VL-098, spec 27)
# ---------------------------------------------------------------------------

# Inconsistency reasons (closed set; spec 27 section 2.1). The recorded
# decision and the recorded condition_results must agree under evaluate()'s
# own short-circuit logic; anything undecidable is inconsistent (canon
# section 9 fail-closed).
INCONSISTENT_CONDITIONS_MALFORMED = "CONDITIONS_MALFORMED"
INCONSISTENT_ELIGIBLE_WITH_FAILED_CONDITION = "ELIGIBLE_WITH_FAILED_CONDITION"
INCONSISTENT_REFUSE_WITH_ALL_CONDITIONS_TRUE = "REFUSE_WITH_ALL_CONDITIONS_TRUE"
INCONSISTENT_UNKNOWN_DECISION = "UNKNOWN_DECISION"

_CONDITION_KEYS = ("ac3", "t26", "manifest_integrity")


def _record_consistency(envelope: Dict[str, Any]) -> Optional[str]:
    """Spec 27 section 2.1: return None if the recorded decision agrees
    with the recorded condition_results under evaluate()'s short-circuit
    logic, else the inconsistency reason. condition_results.ccs is None at
    issuance (VL-029 Decision A) and is NOT consulted - it is
    reassert-time, not issue-time."""
    conditions = envelope.get("condition_results")
    if not isinstance(conditions, dict):
        return INCONSISTENT_CONDITIONS_MALFORMED
    values = []
    for key in _CONDITION_KEYS:
        value = conditions.get(key)
        if not isinstance(value, bool):
            return INCONSISTENT_CONDITIONS_MALFORMED
        values.append(value)
    decision = envelope.get("decision")
    if decision == "ELIGIBLE":
        return None if all(values) else INCONSISTENT_ELIGIBLE_WITH_FAILED_CONDITION
    if decision == "REFUSE":
        return None if not all(values) else INCONSISTENT_REFUSE_WITH_ALL_CONDITIONS_TRUE
    return INCONSISTENT_UNKNOWN_DECISION


def reevaluate_envelope(
    envelope: Any,
    manifest: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    The semantic rung (spec 27): judge an envelope's CONTENTS.

    Two checks:
    1. Internal consistency - the recorded decision vs the recorded
       condition_results, under evaluate()'s own short-circuit logic
       (the hash region protects these fields against TAMPER; this
       check catches an issuer that wrote a self-contradictory record).
    2. Live re-evaluation - rebuild the evaluator ctx from the recorded
       request_context (AP, OP, expected_manifest_version,
       expected_manifest_sha256 - the four fields evaluate() consults;
       context does not enter AC3/T26/integrity) and run the PRODUCTION
       evaluate() plus the three condition functions individually
       against the live manifest. This performs the re-evaluation that
       reassert()'s RE-EVALUATE-REQUIRED outcome demands.

    Live-state semantics are inherent: manifest_integrity_valid() fails
    closed unless the passed manifest equals the on-disk
    MANIFEST/manifest.json (the G11 fix, VL-053). The manifest parameter
    exists for test injection of malformed manifests only. An ELIGIBLE
    envelope issued under a since-transitioned manifest correctly
    re-evaluates REFUSE - that IS the answer, not a tool defect.

    Returns {"ok": True, "consistent", "inconsistency",
    "recorded_decision", "live_decision", "live_conditions",
    "reproduced"} or fail-closed {"ok": False, "reason":
    REF_VERIFY_ENVELOPE_ABSENT} on shape. Judges, never raises on
    content (canon section 9).
    """
    if not _structurally_sound(envelope):
        return {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}

    inconsistency = _record_consistency(envelope)

    rc = envelope["request_context"]
    ctx = {
        "AP": rc["AP"],
        "OP": rc["OP"],
        "expected_manifest_version": rc["expected_manifest_version"],
        "expected_manifest_sha256": rc["expected_manifest_sha256"],
    }
    live_manifest = manifest if manifest is not None else load_manifest()
    live_decision = evaluate(ctx, live_manifest)

    checked = safe_manifest(live_manifest)
    if checked is None:
        live_conditions = {key: False for key in _CONDITION_KEYS}
    else:
        live_conditions = {
            "ac3": ac3_valid(ctx, checked["AR"]),
            "t26": t26_valid(ctx, checked["R"]),
            "manifest_integrity": manifest_integrity_valid(ctx, checked),
        }

    recorded_decision = envelope.get("decision")
    return {
        "ok": True,
        "consistent": inconsistency is None,
        "inconsistency": inconsistency,
        "recorded_decision": recorded_decision,
        "live_decision": live_decision,
        "live_conditions": live_conditions,
        "reproduced": live_decision == recorded_decision,
    }


# ---------------------------------------------------------------------------
# Capability 4: reconcile
# ---------------------------------------------------------------------------


def _binding_holds(envelope: Dict[str, Any], action: Dict[str, Any]) -> bool:
    """
    The same five comparisons verify_envelope step 3 applies, over an
    executed-action record {"target_url", "interaction": {...}}. Any
    structural surprise is a non-match (fail-closed), never a raise.
    """
    interaction = action.get("interaction")
    if not isinstance(interaction, dict):
        return False
    rc = envelope["request_context"]
    if envelope["target_url"] != action.get("target_url"):
        return False
    try:
        if _normalize_set_field(rc["AP"]) != _normalize_set_field(interaction["AP"]):
            return False
        if _normalize_set_field(rc["OP"]) != _normalize_set_field(interaction["OP"]):
            return False
    except (KeyError, TypeError):
        return False
    if rc["expected_manifest_version"] != interaction.get("expected_manifest_version"):
        return False
    if rc["expected_manifest_sha256"] != interaction.get("expected_manifest_sha256"):
        return False
    if "context" not in interaction:
        return False
    try:
        if canonical_json(rc["context"]) != canonical_json(interaction["context"]):
            return False
    except (TypeError, ValueError):
        return False
    return True


def reconcile(
    executed_actions: List[Dict[str, Any]],
    issued_envelopes: List[Any],
    pinned_public_keys: Optional[Dict[str, Any]] = None,
    now: Optional[datetime] = None,
    clock_skew: timedelta = timedelta(0),
) -> Dict[str, Any]:
    """
    Classify every executed action against the issued envelopes.

    An issued envelope is ELIGIBLE-FOR-MATCHING iff it passes the
    structural guard, its decision is "ELIGIBLE", and - when
    pinned_public_keys is supplied - verify_issuer accepts it. A failing
    issued-log entry is reported INVALID_ENVELOPE and excluded: a forged
    entry in the issuance log must not legitimize an executed action.

    Per-action classification (closed set, log order, greedy):
      MATCHED               - an unconsumed eligible envelope binds the
                              action (and decision_id matches when the
                              action carries one); the envelope is
                              consumed (single-use, VL-066 exactly-once).
      DUPLICATE_CONSUMPTION - every envelope that would match is already
                              consumed (replay evidence at audit time).
      OUT_OF_SCOPE          - no envelope matches at all (unattested or
                              unauthorized execution; the A1-shaped
                              event, visible only in audit).

    Deliberate non-checks per spec section 3.4: no reassert() currency,
    no not_after-vs-execution-time. The trustworthy-log assumption is
    the explicit bound (module docstring).

    Returns {"actions": [...], "envelopes": [...], "summary": {...}};
    summary.clean is True iff out_of_scope == duplicate_consumption == 0.
    """
    env_status: List[Dict[str, Any]] = []
    matchable: List[bool] = []
    for idx, env in enumerate(issued_envelopes):
        invalid_reason = None
        if not _structurally_sound(env):
            invalid_reason = REF_VERIFY_ENVELOPE_ABSENT
        elif env.get("decision") != "ELIGIBLE":
            invalid_reason = "DECISION_NOT_ELIGIBLE"
        elif pinned_public_keys is not None:
            issuer = verify_issuer(env, pinned_public_keys, now=now, clock_skew=clock_skew)
            if not issuer["verified"]:
                invalid_reason = issuer["reason"]
        if invalid_reason is not None:
            env_status.append({"index": idx, "status": ENVELOPE_INVALID,
                               "reason": invalid_reason})
            matchable.append(False)
        else:
            env_status.append({"index": idx, "status": ENVELOPE_UNUSED})
            matchable.append(True)

    consumed = [False] * len(issued_envelopes)
    action_results: List[Dict[str, Any]] = []
    counts = {"matched": 0, "out_of_scope": 0, "duplicate_consumption": 0}

    for a_idx, action in enumerate(executed_actions):
        action_decision_id = (
            action.get("decision_id") if isinstance(action, dict) else None
        )
        match_idx = None
        saw_consumed_match = False
        for e_idx, env in enumerate(issued_envelopes):
            if not matchable[e_idx]:
                continue
            if action_decision_id is not None and env.get("decision_id") != action_decision_id:
                continue
            if not isinstance(action, dict) or not _binding_holds(env, action):
                continue
            if consumed[e_idx]:
                saw_consumed_match = True
                continue
            match_idx = e_idx
            break

        if match_idx is not None:
            consumed[match_idx] = True
            env_status[match_idx]["status"] = ENVELOPE_CONSUMED
            env_status[match_idx]["action_index"] = a_idx
            verdict = AUDIT_MATCHED
            counts["matched"] += 1
        elif saw_consumed_match:
            verdict = AUDIT_DUPLICATE_CONSUMPTION
            counts["duplicate_consumption"] += 1
        else:
            verdict = AUDIT_OUT_OF_SCOPE
            counts["out_of_scope"] += 1
        action_results.append(
            {"index": a_idx, "verdict": verdict, "envelope_index": match_idx}
        )

    summary = {
        **counts,
        "unused": sum(1 for s in env_status if s["status"] == ENVELOPE_UNUSED),
        "invalid_envelopes": sum(
            1 for s in env_status if s["status"] == ENVELOPE_INVALID
        ),
        "clean": counts["out_of_scope"] == 0 and counts["duplicate_consumption"] == 0,
    }
    return {"actions": action_results, "envelopes": env_status, "summary": summary}


# ---------------------------------------------------------------------------
# Capability 5: reconcile_approvals (governance Feature 1, [FIX H8])
# ---------------------------------------------------------------------------

# Approval-audit violation vocabulary (closed set).
APPROVAL_FORWARDED_WITHOUT_GRANT = "FORWARDED_WITHOUT_GRANT"
APPROVAL_ORPHAN_CONSUMPTION = "ORPHAN_CONSUMPTION"
APPROVAL_DUPLICATE_GRANT = "DUPLICATE_GRANT"
APPROVAL_DUPLICATE_REQUEST_CONSUMPTION = "DUPLICATE_REQUEST_CONSUMPTION"


def reconcile_approvals(
    issued_envelopes: List[Any],
    approval_records: List[Any],
) -> Dict[str, Any]:
    """
    Audit the governance trail: prove no HELD high-impact decision was
    FORWARDED without a recorded human grant ([FIX H8]).

    Inputs:
      issued_envelopes : the gate issuance log (the same JSONL `reconcile`
                         consumes). A structurally-sound ELIGIBLE entry means
                         the decision was forwarded.
      approval_records : the approval log (JSONL) pep writes - `approval_request`
                         records (the 202 holds) and `grant_consumed` records
                         (the approved releases).

    Binding key is `decision_sha256` (present in both the envelope and every
    approval record; it transitively binds target/AP/OP/context/manifest). A
    decision is HIGH-IMPACT-AND-HELD iff it has an approval_request; it was
    FORWARDED iff its decision_sha256 appears among the issued envelopes.

    Violations (closed set; the log is the trustworthy referent, as for
    reconcile()):
      FORWARDED_WITHOUT_GRANT       - a decision that was held AND forwarded but
                                      has NO grant_consumed: the governance
                                      guarantee broken (an action executed
                                      without a recorded human grant).
      ORPHAN_CONSUMPTION            - a grant_consumed with no matching
                                      approval_request (same request_id +
                                      decision_sha256): a release with no hold.
      DUPLICATE_GRANT               - one grant_id consumed more than once.
      DUPLICATE_REQUEST_CONSUMPTION - one approval_request_id consumed more than
                                      once (a single 202 honored twice).

    Returns {"violations": [...], "summary": {...}}; summary.clean is True iff
    there are zero violations. Fail-closed on malformed records (a record that
    is not a dict, or lacks its keys, is itself an ORPHAN/STRUCTURAL violation
    rather than being silently dropped).

    Scope (honest): keyed on decision_sha256, which is issuance-invariant, so
    this proves "every held+forwarded high-impact decision has at least one
    recorded grant", not a per-issuance 1:1 match (the grant is claimed before
    the envelope's decision_id is assigned). Per-issuance linkage is a later
    refinement. Deliberate non-checks (parity with reconcile): no signature or
    freshness re-verification - those are the runtime gate's job (VL-114/115);
    this audits the LOG.
    """
    violations: List[Dict[str, Any]] = []

    # issued (forwarded) decision_sha256 set
    forwarded = set()
    for env in issued_envelopes:
        # The issuance log is the gate-produced, trustworthy referent (parity
        # with reconcile's trustworthy-log bound). An entry counts as FORWARDED
        # iff it is an ELIGIBLE record carrying a decision_sha256; full envelope
        # structure is reconcile()'s concern, not the approval audit's.
        if isinstance(env, dict) and env.get("decision") == "ELIGIBLE":
            ds = env.get("decision_sha256")
            if isinstance(ds, str):
                forwarded.add(ds)

    # index requests and consumptions
    requested_decisions = set()              # decision_sha256 with a hold
    request_pairs = set()                    # (request_id, decision_sha256)
    consumed_by_decision = set()             # decision_sha256 with a release
    grant_id_seen = {}                       # grant_id -> count
    request_consumed = {}                    # approval_request_id -> count
    consumptions = []                        # (request_id, decision_sha256, grant_id, idx)

    for idx, rec in enumerate(approval_records):
        if not isinstance(rec, dict):
            violations.append({"index": idx, "violation": APPROVAL_ORPHAN_CONSUMPTION,
                               "reason": "record is not an object"})
            continue
        rtype = rec.get("type")
        ds = rec.get("decision_sha256")
        rid = rec.get("approval_request_id")
        if rtype == "approval_request":
            if isinstance(ds, str):
                requested_decisions.add(ds)
            if isinstance(rid, str) and isinstance(ds, str):
                request_pairs.add((rid, ds))
        elif rtype == "grant_consumed":
            gid = rec.get("grant_id")
            if isinstance(ds, str):
                consumed_by_decision.add(ds)
            if isinstance(gid, str):
                grant_id_seen[gid] = grant_id_seen.get(gid, 0) + 1
            if isinstance(rid, str):
                request_consumed[rid] = request_consumed.get(rid, 0) + 1
            consumptions.append((rid, ds, gid, idx))
        else:
            violations.append({"index": idx, "violation": APPROVAL_ORPHAN_CONSUMPTION,
                               "reason": "unknown or missing record type"})

    # ORPHAN_CONSUMPTION: a release with no matching hold
    for rid, ds, gid, idx in consumptions:
        if (rid, ds) not in request_pairs:
            violations.append({"index": idx, "violation": APPROVAL_ORPHAN_CONSUMPTION,
                               "decision_sha256": ds, "approval_request_id": rid})

    # DUPLICATE_GRANT / DUPLICATE_REQUEST_CONSUMPTION
    for gid, n in grant_id_seen.items():
        if n > 1:
            violations.append({"violation": APPROVAL_DUPLICATE_GRANT,
                               "grant_id": gid, "count": n})
    for rid, n in request_consumed.items():
        if n > 1:
            violations.append({"violation": APPROVAL_DUPLICATE_REQUEST_CONSUMPTION,
                               "approval_request_id": rid, "count": n})

    # FORWARDED_WITHOUT_GRANT: held AND forwarded but never released
    for ds in sorted(requested_decisions & forwarded):
        if ds not in consumed_by_decision:
            violations.append({"violation": APPROVAL_FORWARDED_WITHOUT_GRANT,
                               "decision_sha256": ds})

    summary = {
        "forwarded": len(forwarded),
        "held": len(requested_decisions),
        "consumed": len(consumed_by_decision),
        "violations": len(violations),
        "clean": len(violations) == 0,
    }
    return {"violations": violations, "summary": summary}


# ---------------------------------------------------------------------------
# CLI (spec section 3.5). cryptography is imported lazily ONLY for --keys
# (parity with envelope.py's no-hard-dependency rule).
# ---------------------------------------------------------------------------


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_jsonl(path: str) -> List[Any]:
    items: List[Any] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def _load_keys(path: str) -> Dict[str, Any]:
    """Load {key_id: ed25519_public_key_hex} into {key_id: Ed25519PublicKey}."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    raw = _load_json(path)
    return {
        key_id: Ed25519PublicKey.from_public_bytes(bytes.fromhex(hex_key))
        for key_id, hex_key in raw.items()
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envelope_inspector",
        description="Elyon-Sol envelope inspector / reconciler (VL-097; "
        "read-only audit tooling).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser("inspect", help="decode one envelope's bound scope")
    p_inspect.add_argument("envelope", help="path to an envelope JSON file")
    p_inspect.add_argument("--keys", help="path to {key_id: pubkey_hex} JSON; "
                                          "also verify the issuer signature")
    p_inspect.add_argument("--record", help="path to a fetched published-record "
                                            "JSON for reassert(); default uses "
                                            "live local state")

    p_reeval = sub.add_parser(
        "reevaluate",
        help="semantic re-evaluation: recorded-decision consistency + a live "
             "re-run of the production evaluator over the recorded request",
    )
    p_reeval.add_argument("envelope", help="path to an envelope JSON file")

    p_rec = sub.add_parser("reconcile", help="reconcile executed actions "
                                             "against issued envelopes")
    p_rec.add_argument("--issued", required=True, help="issued envelopes (JSONL)")
    p_rec.add_argument("--executed", required=True, help="executed actions (JSONL)")
    p_rec.add_argument("--keys", help="path to {key_id: pubkey_hex} JSON; "
                                      "screen issued entries by issuer signature")

    args = parser.parse_args(argv)
    ok = True

    if args.command == "inspect":
        envelope = _load_json(args.envelope)
        decoded = inspect_envelope(envelope)
        print(json.dumps({"inspect": decoded}, indent=2, sort_keys=True))
        ok = decoded["ok"]
        if ok and args.keys:
            issuer = verify_issuer(envelope, _load_keys(args.keys))
            print(json.dumps({"issuer": issuer}, indent=2, sort_keys=True))
            ok = ok and issuer["verified"]
        if ok:
            record = _load_json(args.record) if args.record else None
            outcome = reassert(envelope, record_source=record)
            print(json.dumps({"reassert": outcome}, indent=2, sort_keys=True))
            ok = ok and outcome["outcome"] == "REASSERTED"
    elif args.command == "reevaluate":
        result = reevaluate_envelope(_load_json(args.envelope))
        print(json.dumps({"reevaluate": result}, indent=2, sort_keys=True))
        ok = bool(result.get("ok")) and bool(result.get("consistent")) and bool(
            result.get("reproduced"))
    else:
        issued = _load_jsonl(args.issued)
        executed = _load_jsonl(args.executed)
        keys = _load_keys(args.keys) if args.keys else None
        report = reconcile(executed, issued, pinned_public_keys=keys)
        print(json.dumps(report, indent=2, sort_keys=True))
        ok = report["summary"]["clean"]

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
