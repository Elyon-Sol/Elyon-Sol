# Elyon-Sol POC — Medical — e-prescribing / medication orders

_Mode: **live** · cases: 13 · passed: 12/13 · generated 2026-06-10 20:45:40Z_

> **Synthetic data.** All identifiers (patient/account/matter/bar/NPI numbers, URLs) are fictional and resolve to nothing real. This is a characterization run of the production admission chain (GR-3), not an external validation.

## Policy manifest (what this domain requires to admit)

- **version**: `med-1.0`
- **manifest sha256**: `18142d287672033b989ef1498e3d6ea3c7ef107e4a60e278ef0c0a9f19a6a4a4`
- **required authority set (AR)** — the caller's authorities must cover this: `clinician_identity, active_license, prescriptive_authority`
- **required operation set (R)** — the operation must cover this: `medication_order:create`

A call is **admitted** only if its authority set ⊇ AR (AC³), its operation set ⊇ R (T²⁶), and it is pinned to this exact manifest version+sha (manifest-integrity); otherwise the gate **refuses**. An admitted call carries a signed envelope the executor re-checks (signature → currency → binding → freshness → replay) before acting.

## Cases

### admit_primary — ✅ PASS

_A licensed prescriber orders amoxicillin 500 mg PO — admitted and executed._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `fcf0aeb2872e45c79faeb3bf6b4d5139`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.286276+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `0c62ce0d93270f16…`
  - decision_sha256: `a33920a8bdd302ad…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_secondary — ✅ PASS

_The same prescriber orders lisinopril 10 mg daily — admitted and executed._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-3C9B12; drug: lisinopril; dose: 10 mg; route: PO; frequency: daily; ordering_provider_npi: 1730000017; encounter_id: ENC-22974; order_sha256: 25bf4442fa8c56b5…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `593b4ea0cd184a0a8e82800666388ffd`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.485858+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `a1eb9583d70e64c9…`
  - decision_sha256: `fb21da7209e0830c…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_minimal_authority — ✅ PASS

_Exactly the required credentials, no extras — still admissible._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `cdad6540189c40a3b87d812cdb019c84`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.553443+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `bb89985bbbd135d8…`
  - decision_sha256: `4407a8cdade035dd…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### insufficient_authority — ✅ PASS

_A nurse without prescriptive authority cannot create a medication order._

- **actor (AP)**: `clinician_identity, active_license, nursing_credential`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### wrong_operation — ✅ PASS

_A read-only request is not an order-creation and is refused._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:read`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### stale_policy_pin — ✅ PASS

_An order written against a superseded formulary policy version is refused._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### unattested — ✅ PASS

_A medication order reaching the EHR with no admissibility attestation is refused._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: (no envelope — A1 / un-attested path)
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_ENVELOPE_ABSENT`)
- **expected**: refused (`REF_VERIFY_ENVELOPE_ABSENT`)

### forged_envelope — ✅ PASS

_An attacker who edits the authorized dose inside the attestation is caught by the signature._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `c3c8bdd58d634950ba6d3b5d15391b83`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.680314+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `9c7481ddef6601c4…`
  - decision_sha256: `a33920a8bdd302ad…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_INVALID`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_INVALID`)

### replay — ✅ PASS

_A single authorization cannot be used to dispense the medication twice._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `2f40eeebc4fc48389c95744dfb6a3a0c`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.727404+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `5f38781fb4ade960…`
  - decision_sha256: `a33920a8bdd302ad…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_REPLAY`)
- **expected**: refused (`REF_VERIFY_REPLAY`)

### rebind_operation — ✅ PASS

_An order-creation authorization cannot be repurposed to cancel an order._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:cancel`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `601d308db32447a3b20de90994a30d6b`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.808763+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `a7c6a8d550b71159…`
  - decision_sha256: `a33920a8bdd302ad…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### rebind_context — ✅ PASS

_The dose cannot be altered to 5000 mg after the order was authorized._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 5000 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: dbb364e75c6a270d…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `a814f33e29fe499f99046e8bf20b879d`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.867685+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `ae8d6abfb0cd8135…`
  - decision_sha256: `a33920a8bdd302ad…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### target_swap — ✅ PASS

_An EHR authorization cannot be redirected to the pharmacy dispense endpoint._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `ab6708f069714b57956e244bf564b747`
  - bound target_url: `https://192.168.56.102:9000/target-SWAP`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T20:50:39.923612+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `9d31a43e27af95d1…`
  - decision_sha256: `40754b45a097e50b…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### stale_decision — ❌ FAIL

_An expired authorization is not honored._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: (no envelope — A1 / un-attested path)
- **executor verdict**: REFUSED — not acted (`SKIPPED (pass --decision-max-age to match the gate window)`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_EXPIRED`)

