# Elyon-Sol POC — Legal — court e-filing

_Mode: **inproc** · cases: 13 · passed: 13/13 · generated 2026-06-10 19:47:07Z_

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
  - decision_id: `cfd825b30ecf4d2fb9e8f676a22c11b7`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.326677+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `bd138a2ee4ecc78f…`
  - decision_sha256: `a18e775a82b08a7d…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_secondary — ✅ PASS

_The same attorney submits a reply brief on the same matter — admitted and filed._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: reply_brief; bar_number: CA-298344; client_ref: CLT-7731; privilege: work-product; document_sha256: 99d8ee1bd28b2c30…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `2216fa52b2e644d391b638365ae15dc8`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.337095+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `ca8fac0d0f1cd4ff…`
  - decision_sha256: `d70e4f3a10789f17…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_minimal_authority — ✅ PASS

_Exactly the required standing, no extras — still admissible._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `893137926daf4e3ab4ae58ea8bd9160a`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.347719+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `3082e31f1eaf1cb3…`
  - decision_sha256: `5b29df91ba829662…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### insufficient_authority — ✅ PASS

_A paralegal without active bar admission cannot submit a filing._

- **actor (AP)**: `attorney_identity, paralegal_credential, matter_authorization`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: REFUSE — AC3 unsatisfied
  - AC³=False · T²⁶=True · manifest-integrity=True
- **executor**: not reached (refused at the gate)

### wrong_operation — ✅ PASS

_A draft action is not a submission and is refused._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:draft`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: REFUSE — T26 unsatisfied
  - AC³=True · T²⁶=False · manifest-integrity=True
- **executor**: not reached (refused at the gate)

### stale_policy_pin — ✅ PASS

_A filing pinned to a superseded local-rules policy version is refused._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: REFUSE — MANIFEST_INTEGRITY unsatisfied
  - AC³=True · T²⁶=True · manifest-integrity=False
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
  - decision_id: `cf5c372adb3a4dbb955f8ed5cb0a55e5`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.372423+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `9459ae1143029aee…`
  - decision_sha256: `a18e775a82b08a7d…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_INVALID`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_INVALID`)

### replay — ✅ PASS

_A single authorization cannot be used to double-file the same document._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `11921c6df50f48fb941260c7175481bf`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.380710+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `6c2a2aeaecf1b0ad…`
  - decision_sha256: `a18e775a82b08a7d…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_REPLAY`)
- **expected**: refused (`REF_VERIFY_REPLAY`)

### rebind_operation — ✅ PASS

_A submit authorization cannot be repurposed to withdraw a filing._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:withdraw`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `53deb60b701e4afcae63ae7ff733cfa0`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.394463+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `52999ffb98a628e7…`
  - decision_sha256: `a18e775a82b08a7d…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### rebind_context — ✅ PASS

_The filing cannot be swapped to a stipulation of dismissal after authorization._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: stipulation_of_dismissal; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 7492b5c8562818ea…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `34d0710e869743e7977f2a4d185b5b2f`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.405244+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `646094042929739f…`
  - decision_sha256: `a18e775a82b08a7d…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### target_swap — ✅ PASS

_An N.D. Cal. authorization cannot be redirected to the S.D.N.Y. e-filing endpoint._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `7a8407119c9d43e1aeb321eb4913678f`
  - bound target_url: `https://ecf.nysd.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:52:07.415399+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `058afb12c75c7e04…`
  - decision_sha256: `ec31491f3ed64aa7…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### stale_decision — ✅ PASS

_An expired authorization is not honored._

- **actor (AP)**: `attorney_identity, bar_admission_active, matter_authorization, efiling_credential`
- **operation (OP)**: `court_filing:submit`
- **court filing (context)**: matter_id: 2026-CV-04417; court: N.D. Cal.; filing_type: motion_to_compel; bar_number: CA-298344; client_ref: CLT-7731; privilege: attorney-client; document_sha256: 1aaba9c595e3537c…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `2068529707014e1194e6ab59030950a5`
  - bound target_url: `https://ecf.cand.uscourts.example/file`
  - manifest pin: `legal-1.0` / `c90c85da1e35…`
  - not_after: `2026-06-10T19:47:08.425846+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `3f237a6a89125b3c…`
  - decision_sha256: `a18e775a82b08a7d…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_EXPIRED`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_EXPIRED`)

