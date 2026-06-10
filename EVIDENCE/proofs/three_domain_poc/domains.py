"""
Three-domain synthetic POC content (docs/restructure/25_three_domain_poc_spec.md,
VL-096). PURE DATA: the three domain manifests + the synthetic, reviewer-legible
case vocabulary. No gate logic here; poc_runner.py drives the production chain.

ALL DATA IS FICTIONAL. Patient MRNs, NPIs, bar numbers, account numbers, trader
ids and URLs are invented for demonstration and resolve to nothing real. The
`*.example` hosts are RFC-2606 reserved and never resolve. No real PHI / PII /
PCI is present.

A domain differs from the others ONLY in:
  - manifest.AR  (required AUTHORITY set; AP must be a superset -> AC^3)
  - manifest.R   (required OPERATION set; OP must be a superset -> T^26)
  - manifest.version
  - the free-form context (canon 11.1 C) and the AP/OP token strings

The decision logic is the one production evaluator/verifier, unchanged.
"""

import hashlib
import json


def _digest(payload: dict) -> str:
    """sha256 over a canonical serialization of the domain payload. The envelope
    BINDS to this exact content; a payload altered after authorization yields a
    different digest AND a different context dict, so the binding check refuses
    it (rebind_context)."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _context(payload: dict, digest_field: str) -> dict:
    """A domain context = the legible payload fields + a content digest under a
    domain-named key."""
    ctx = dict(payload)
    ctx[digest_field] = _digest(payload)
    return ctx


# ===========================================================================
# MEDICAL
# ===========================================================================

_MED_PRIMARY = {
    "patient_ref": "MRN-0F1A77",
    "drug": "amoxicillin",
    "dose": "500 mg",
    "route": "PO",
    "frequency": "q8h",
    "ordering_provider_npi": "1730000017",
    "encounter_id": "ENC-22931",
}
_MED_SECONDARY = {
    "patient_ref": "MRN-3C9B12",
    "drug": "lisinopril",
    "dose": "10 mg",
    "route": "PO",
    "frequency": "daily",
    "ordering_provider_npi": "1730000017",
    "encounter_id": "ENC-22974",
}
_MED_MUTATED = dict(_MED_PRIMARY, dose="5000 mg")  # 10x overdose injected post-authorization

MEDICAL = {
    "name": "medical",
    "title": "Medical — e-prescribing / medication orders",
    "manifest": {
        "version": "med-1.0",
        "interaction_type": "default",
        "AR": ["clinician_identity", "active_license", "prescriptive_authority"],
        "R": ["medication_order:create"],
    },
    "superseded_version": "med-0.9",
    "digest_field": "order_sha256",
    "payload_label": "Medication order",
    "target_primary": "https://ehr.hospital.example/orders/execute",
    "target_swap": "https://pharmacy.hospital.example/dispense",
    # authority/operation vocabularies
    "ap_full": ["clinician_identity", "active_license", "prescriptive_authority", "dea_registration"],
    "ap_minimal": ["clinician_identity", "active_license", "prescriptive_authority"],
    "ap_insufficient": ["clinician_identity", "active_license", "nursing_credential"],  # no prescriptive_authority
    "op_required": ["medication_order:create"],
    "op_wrong": ["medication_order:read"],
    "op_other": ["medication_order:cancel"],
    "ctx_primary": _context(_MED_PRIMARY, "order_sha256"),
    "ctx_secondary": _context(_MED_SECONDARY, "order_sha256"),
    "ctx_mutated": _context(_MED_MUTATED, "order_sha256"),
    "actor_full": "a licensed clinician with prescriptive authority and DEA registration",
    "actor_insufficient": "a nurse (no prescriptive authority)",
    "glosses": {
        "admit_primary": "A licensed prescriber orders amoxicillin 500 mg PO — admitted and executed.",
        "admit_secondary": "The same prescriber orders lisinopril 10 mg daily — admitted and executed.",
        "admit_minimal_authority": "Exactly the required credentials, no extras — still admissible.",
        "insufficient_authority": "A nurse without prescriptive authority cannot create a medication order.",
        "wrong_operation": "A read-only request is not an order-creation and is refused.",
        "stale_policy_pin": "An order written against a superseded formulary policy version is refused.",
        "unattested": "A medication order reaching the EHR with no admissibility attestation is refused.",
        "forged_envelope": "An attacker who edits the authorized dose inside the attestation is caught by the signature.",
        "replay": "A single authorization cannot be used to dispense the medication twice.",
        "rebind_operation": "An order-creation authorization cannot be repurposed to cancel an order.",
        "rebind_context": "The dose cannot be altered to 5000 mg after the order was authorized.",
        "target_swap": "An EHR authorization cannot be redirected to the pharmacy dispense endpoint.",
        "stale_decision": "An expired authorization is not honored.",
    },
}


# ===========================================================================
# LEGAL
# ===========================================================================

_LAW_PRIMARY = {
    "matter_id": "2026-CV-04417",
    "court": "N.D. Cal.",
    "filing_type": "motion_to_compel",
    "bar_number": "CA-298344",
    "client_ref": "CLT-7731",
    "privilege": "attorney-client",
}
_LAW_SECONDARY = {
    "matter_id": "2026-CV-04417",
    "court": "N.D. Cal.",
    "filing_type": "reply_brief",
    "bar_number": "CA-298344",
    "client_ref": "CLT-7731",
    "privilege": "work-product",
}
_LAW_MUTATED = dict(_LAW_PRIMARY, filing_type="stipulation_of_dismissal")  # different filing swapped in post-authorization

LEGAL = {
    "name": "legal",
    "title": "Legal — court e-filing",
    "manifest": {
        "version": "legal-1.0",
        "interaction_type": "default",
        "AR": ["attorney_identity", "bar_admission_active", "matter_authorization"],
        "R": ["court_filing:submit"],
    },
    "superseded_version": "legal-0.9",
    "digest_field": "document_sha256",
    "payload_label": "Court filing",
    "target_primary": "https://ecf.cand.uscourts.example/file",
    "target_swap": "https://ecf.nysd.uscourts.example/file",
    "ap_full": ["attorney_identity", "bar_admission_active", "matter_authorization", "efiling_credential"],
    "ap_minimal": ["attorney_identity", "bar_admission_active", "matter_authorization"],
    "ap_insufficient": ["attorney_identity", "paralegal_credential", "matter_authorization"],  # no bar_admission_active
    "op_required": ["court_filing:submit"],
    "op_wrong": ["court_filing:draft"],
    "op_other": ["court_filing:withdraw"],
    "ctx_primary": _context(_LAW_PRIMARY, "document_sha256"),
    "ctx_secondary": _context(_LAW_SECONDARY, "document_sha256"),
    "ctx_mutated": _context(_LAW_MUTATED, "document_sha256"),
    "actor_full": "an attorney with active bar admission authorized on the matter",
    "actor_insufficient": "a paralegal (no active bar admission)",
    "glosses": {
        "admit_primary": "An admitted attorney submits a motion to compel on an authorized matter — admitted and filed.",
        "admit_secondary": "The same attorney submits a reply brief on the same matter — admitted and filed.",
        "admit_minimal_authority": "Exactly the required standing, no extras — still admissible.",
        "insufficient_authority": "A paralegal without active bar admission cannot submit a filing.",
        "wrong_operation": "A draft action is not a submission and is refused.",
        "stale_policy_pin": "A filing pinned to a superseded local-rules policy version is refused.",
        "unattested": "A filing reaching the e-filing endpoint with no attestation is refused.",
        "forged_envelope": "An attacker who edits the filing type inside the attestation is caught by the signature.",
        "replay": "A single authorization cannot be used to double-file the same document.",
        "rebind_operation": "A submit authorization cannot be repurposed to withdraw a filing.",
        "rebind_context": "The filing cannot be swapped to a stipulation of dismissal after authorization.",
        "target_swap": "An N.D. Cal. authorization cannot be redirected to the S.D.N.Y. e-filing endpoint.",
        "stale_decision": "An expired authorization is not honored.",
    },
}


# ===========================================================================
# FINANCE
# ===========================================================================

_FIN_PRIMARY = {
    "account": "ACCT-55012",
    "instrument": "AAPL",
    "side": "BUY",
    "quantity": 1000,
    "notional_usd": 195000,
    "desk": "equities-cash",
    "trader_id": "TRD-441",
}
_FIN_SECONDARY = {
    "account": "ACCT-55012",
    "instrument": "MSFT",
    "side": "SELL",
    "quantity": 500,
    "notional_usd": 210000,
    "desk": "equities-cash",
    "trader_id": "TRD-441",
}
_FIN_MUTATED = dict(_FIN_PRIMARY, quantity=100000, notional_usd=19500000)  # size inflated 100x post limit-check

FINANCE = {
    "name": "finance",
    "title": "Finance — order/trade execution",
    "manifest": {
        "version": "fin-1.0",
        "interaction_type": "default",
        "AR": ["trader_identity", "desk_authorization", "limit_check_cleared"],
        "R": ["trade:execute"],
    },
    "superseded_version": "fin-0.9",
    "digest_field": "order_sha256",
    "payload_label": "Trade order",
    "target_primary": "https://oms.bank.example/orders/execute",
    "target_swap": "https://settlement.bank.example/instruct",
    "ap_full": ["trader_identity", "desk_authorization", "limit_check_cleared", "compliance_attestation"],
    "ap_minimal": ["trader_identity", "desk_authorization", "limit_check_cleared"],
    "ap_insufficient": ["trader_identity", "desk_authorization", "compliance_attestation"],  # no limit_check_cleared
    "op_required": ["trade:execute"],
    "op_wrong": ["trade:quote"],
    "op_other": ["trade:cancel"],
    "ctx_primary": _context(_FIN_PRIMARY, "order_sha256"),
    "ctx_secondary": _context(_FIN_SECONDARY, "order_sha256"),
    "ctx_mutated": _context(_FIN_MUTATED, "order_sha256"),
    "actor_full": "a trader on an authorized desk, within limits, compliance-attested",
    "actor_insufficient": "a trader whose pre-trade limit check did not clear",
    "glosses": {
        "admit_primary": "A desk-authorized trader executes BUY 1,000 AAPL within limits — admitted and executed.",
        "admit_secondary": "The same trader executes SELL 500 MSFT — admitted and executed.",
        "admit_minimal_authority": "Exactly the required clearances, no extras — still admissible.",
        "insufficient_authority": "A trade that failed the pre-trade limit check is not admissible.",
        "wrong_operation": "A quote request is not an execution and is refused.",
        "stale_policy_pin": "A trade pinned to a superseded risk-policy version is refused.",
        "unattested": "An execution reaching the OMS with no attestation is refused.",
        "forged_envelope": "An attacker who edits the size inside the attestation is caught by the signature.",
        "replay": "A single execution authorization cannot be used to execute the trade twice.",
        "rebind_operation": "An execute authorization cannot be repurposed to cancel an order.",
        "rebind_context": "The size cannot be inflated to 100,000 after the limit check passed.",
        "target_swap": "An OMS authorization cannot be redirected to the settlement-instruction endpoint.",
        "stale_decision": "An expired authorization is not honored.",
    },
}


DOMAINS = {d["name"]: d for d in (MEDICAL, LEGAL, FINANCE)}
DOMAIN_ORDER = ["medical", "legal", "finance"]
