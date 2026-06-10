# Elyon-Sol POC — Legal — court e-filing

_Mode: **live** · cases: 13 · passed: 12/13 · generated 2026-06-10 20:47:44Z_

> **Synthetic data.** All identifiers (patient/account/matter/bar/NPI numbers, URLs) are fictional and resolve to nothing real. This is a characterization run of the production admission chain (GR-3), not an external validation.

## Policy manifest (what this domain requires to admit)

- **version**: `legal-1.0`
- **manifest sha256**: `c90c85da1e35cf308712a2d1c0e3f75b68c423089671ae781021d6cf2089d5c4`
- **required authority set (AR)** — the caller's authorities must cover this: `attorney_identity, bar_admission_active, matter_authorization`
- **required operation set (R)** — the operation must cover this: `court_filing:submit`

A call is **admitted** only if its authority set ⊇ AR (AC³), its operation set ⊇ R (T²⁶), and it is pinned to this exact manifest version+sha (manifest-integrity); otherwise the gate **refuses**. An admitted call carries a signed envelope the executor re-checks (signature → currency → binding → freshness → replay) before acting.

## Cases

### admit_primary — ✅ PASS

_An admitted attorney submits a motion to compel on an authorized matter — admitted and filed._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `ef4ba8ea87354e008329fb03ac001c57`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:43.784249+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `0a9a34bdd825504e…`
  - decision_sha256: `88ae8d16474c5b07…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_secondary — ✅ PASS

_The same attorney submits a reply brief on the same matter — admitted and filed._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: reply_brief; bar_number: CA-298344; client_ref: CLT-7731; privilege: work-product; document_sha256: 99d8ee1bd28b2c30…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `9a82bc48e6a04d7096ddfb155c4ee9c2`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:43.893556+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `6c0f6f2c7938e283…`
  - decision_sha256: `49c5ee55f4fa32ad…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_minimal_authority — ✅ PASS

_Exactly the required standing, no extras — still admissible._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `ce48674024a9404aa5cea8911900af30`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:43.961108+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `76b4484cf7c94c0d…`
  - decision_sha256: `51a6f0ed660c7f27…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### insufficient_authority — ✅ PASS

_A paralegal without active bar admission cannot submit a filing._

- **actor (AP)**: `attorney_identity, paralegal_credential, matter_authorization`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### wrong_operation — ✅ PASS

_A draft action is not a submission and is refused._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:draft`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### stale_policy_pin — ✅ PASS

_A filing pinned to a superseded local-rules policy version is refused._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### unattested — ✅ PASS

_A filing reaching the e-filing endpoint with no attestation is refused._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: (no envelope — A1 / un-attested path)
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_ENVELOPE_ABSENT`)
- **expected**: refused (`REF_VERIFY_ENVELOPE_ABSENT`)

### forged_envelope — ✅ PASS

_An attacker who edits the filing type inside the attestation is caught by the signature._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `a24cb5c257194a8d9102f80b4bcd9fc1`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:44.087809+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `12b9d5f08b628297…`
  - decision_sha256: `88ae8d16474c5b07…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_INVALID`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_INVALID`)

### replay — ✅ PASS

_A single authorization cannot be used to double-file the same document._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `dd19d537c68046728c65cb5e879ffedd`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:44.146411+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `8c1af9463526da23…`
  - decision_sha256: `88ae8d16474c5b07…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_REPLAY`)
- **expected**: refused (`REF_VERIFY_REPLAY`)

### rebind_operation — ✅ PASS

_A submit authorization cannot be repurposed to withdraw a filing._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:withdraw`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `92adb8f1ad9944c0b6cb4ff4df0eb4ca`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:44.227294+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `47ceb2644152a9d1…`
  - decision_sha256: `88ae8d16474c5b07…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### rebind_context — ✅ PASS

_The filing cannot be swapped to a stipulation of dismissal after authorization._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: stipulation_of_dismissal; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 7492b5c8562818ea…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `4cd775135d7147fe8d66836de99ee31d`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:44.284639+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `04058d44410ceffc…`
  - decision_sha256: `88ae8d16474c5b07…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### target_swap — ✅ PASS

_An N.D. Cal. authorization cannot be redirected to the S.D.N.Y. e-filing endpoint._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `150c5073012445759ca386fdda5c663e`
  - bound target_url: `https://192.168.56.102:9000/target-SWAP`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T20:52:44.345055+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `bcd21b1e4ff6b43e…`
  - decision_sha256: `859daa1ca3c9a917…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### stale_decision — ❌ FAIL

_An expired authorization is not honored._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: (no envelope — A1 / un-attested path)
- **executor verdict**: REFUSED — not acted (`SKIPPED (pass --decision-max-age to match the gate window)`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_EXPIRED`)

