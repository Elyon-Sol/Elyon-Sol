# Elyon-Sol POC — Medical — e-prescribing / medication orders

_Mode: **inproc** · cases: 13 · passed: 13/13 · generated 2026-06-10 19:47:07Z_

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
  - decision_id: `7b754b7b58294e04b278fea7b0dc346c`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.198754+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `3c5424aeaf2fd895…`
  - decision_sha256: `dae3695ea8e839b7…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_secondary — ✅ PASS

_The same prescriber orders lisinopril 10 mg daily — admitted and executed._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-3C9B12; drug: lisinopril; dose: 10 mg; route: PO; frequency: daily; ordering_provider_npi: 1730000017; encounter_id: ENC-22974; order_sha256: 25bf4442fa8c56b5…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `40bb9303ddec463092d87a0e47101941`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.209665+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `33ac288b53d919a9…`
  - decision_sha256: `048ef0a11c15e86d…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_minimal_authority — ✅ PASS

_Exactly the required credentials, no extras — still admissible._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `5333a3d7334847df962a905a4f862e14`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.220652+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `ba223c3703d54f04…`
  - decision_sha256: `64d8e3f27a4c0984…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### insufficient_authority — ✅ PASS

_A nurse without prescriptive authority cannot create a medication order._

- **actor (AP)**: `clinician_identity, active_license, nursing_credential`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: REFUSE — AC3 unsatisfied
  - AC³=False · T²⁶=True · manifest-integrity=True
- **executor**: not reached (refused at the gate)

### wrong_operation — ✅ PASS

_A read-only request is not an order-creation and is refused._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:read`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: REFUSE — T26 unsatisfied
  - AC³=True · T²⁶=False · manifest-integrity=True
- **executor**: not reached (refused at the gate)

### stale_policy_pin — ✅ PASS

_An order written against a superseded formulary policy version is refused._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: REFUSE — MANIFEST_INTEGRITY unsatisfied
  - AC³=True · T²⁶=True · manifest-integrity=False
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
  - decision_id: `a68aba35b44a4f82a7131f4589df559e`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.245234+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `ae8b34a11f9bbd65…`
  - decision_sha256: `dae3695ea8e839b7…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_INVALID`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_INVALID`)

### replay — ✅ PASS

_A single authorization cannot be used to dispense the medication twice._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `2149421c039242b5a0f1196743bb42bc`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.253395+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `517f4252a7ad739d…`
  - decision_sha256: `dae3695ea8e839b7…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_REPLAY`)
- **expected**: refused (`REF_VERIFY_REPLAY`)

### rebind_operation — ✅ PASS

_An order-creation authorization cannot be repurposed to cancel an order._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:cancel`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `18916525ab8e4776bb8ed01eb47a0842`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.266116+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `e980d13f482b84ba…`
  - decision_sha256: `dae3695ea8e839b7…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### rebind_context — ✅ PASS

_The dose cannot be altered to 5000 mg after the order was authorized._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 5000 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: dbb364e75c6a270d…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `2c1d6cde494b43d09ce11c72916debf4`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.276987+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `08f125ee759785a7…`
  - decision_sha256: `dae3695ea8e839b7…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### target_swap — ✅ PASS

_An EHR authorization cannot be redirected to the pharmacy dispense endpoint._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `4aecc426187a4d5fa134ace9ba73da88`
  - bound target_url: `https://pharmacy.hospital.example/dispense`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:52:07.288776+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `b4795c4689b4532c…`
  - decision_sha256: `378c13151aa95d3d…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### stale_decision — ✅ PASS

_An expired authorization is not honored._

- **actor (AP)**: `clinician_identity, active_license, prescriptive_authority, dea_registration`
- **operation (OP)**: `medication_order:create`
- **medication order (context)**: patient_ref: MRN-0F1A77; drug: amoxicillin; dose: 500 mg; route: PO; frequency: q8h; ordering_provider_npi: 1730000017; encounter_id: ENC-22931; order_sha256: ce1bb7f50521abc8…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `950941da44214c8c95160368cf25e51f`
  - bound target_url: `https://ehr.hospital.example/orders/execute`
  - manifest pin: `med-1.0` / `18142d287672…`
  - not_after: `2026-06-10T19:47:08.299525+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `4ede713ce056e414…`
  - decision_sha256: `dae3695ea8e839b7…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_EXPIRED`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_EXPIRED`)

