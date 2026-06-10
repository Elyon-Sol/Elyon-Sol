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
