# Zenodo Rev 6 — compiled posting pack (ready to publish)

Compiled from `docs/ZENODO_REV6_ADDENDUM.md` (paste-ready fields) and
`docs/zenodo/enforcement_evidence_addendum_rev6.md` (the deposit document).
This one file is everything needed to cut Revision 6.

Snapshot: commit `9645fb82236131ce686d22c2dfed1416d54c252d` (2026-06-18), suite **512/512, 0 xfailed**.
Canonical model **v0.9.8.4 unchanged**. Supersedes Revision 5 (DOI `10.5281/zenodo.20751592`).

> **PUBLISHED 2026-07-01** as Rev 6 — DOI `10.5281/zenodo.21107731`, record https://zenodo.org/records/21107731 (v25). This pack is retained as the record of how it was cut.

---

## 0. How to cut this version (do this first)

1. Open the CURRENT live record — Revision 5: https://zenodo.org/records/20751592
2. Click **"New version"** (this keeps the concept DOI and the version chain; a new version DOI is minted on publish). Do NOT edit Rev 5 in place — this is a real code-snapshot advance (419 → 512 tests + the governance layer), so it must be a new version, not a metadata edit.
3. **Remove** the attached Rev 5 files (`enforcement_evidence_addendum_rev5.md/.pdf`).
4. **Attach** the Rev 6 files:
   - `docs/zenodo/enforcement_evidence_addendum_rev6.pdf`
   - `docs/zenodo/enforcement_evidence_addendum_rev6.md`
   - the architecture PNG (`elyon_sol_architecture (3).png`, carried from Rev 5 — re-attach)
5. Apply the metadata fields in sections 1–8 below.
6. Publish. Then update any citation that should point to the new version DOI (the concept DOI always resolves to latest).

---

## 1. Title
Elyon-Sol v0.9.8.4 — Enforcement Evidence Addendum (Revision 6)

## 2. Authors / Creators
LaPorte, Justin — ORCID 0009-0008-3785-3089 (Researcher)

## 3. Resource type / Publisher / Language
Report · Zenodo · English

## 4. License
Creative Commons Attribution 4.0 International (CC BY 4.0) — this deposit is the document.
(AGPL-3.0 governs the code, which is not in this deposit.)

## 5. Description  (paste into the Zenodo "Description" field)

> Render-safe: bold lead-ins only, no wide multi-line bullet lists and no code/backtick spans
> (those flow into newspaper columns and slide under the Versions panel). Paste as-is.

**Elyon-Sol** is a deterministic, fail-closed HTTP admission gate derived from a formal admissibility specification. The canonical model is unchanged from v0.9.8.4: **G(I) = AC³ ∧ T²⁶ ∧ CCS**. This revision (Revision 6) supersedes Revision 5 (DOI 10.5281/zenodo.20751592); it carries Revision 5's distribution correction forward unchanged and advances the implementation snapshot.

**Licensing and access.** The canonical model remains published for citation. The core implementation is **AGPL-3.0 licensed (open-core)** — the admission gate, the admissibility envelope, the target-side verifier, and the ext-authz sidecar; a commercial license is available for uses that cannot accept AGPL's terms; and a separate administration/tooling SDK is proprietary. The **source repository is private; access is granted on request** — email admin@elyon-sol.io or justin@elyon-sol.io. This document is licensed CC BY 4.0.

**The invariants.** All three canonical invariants — Authority (AC³), Coverage (T²⁶), and Continuity (CCS) — are implemented and exercised in code. Continuity is realized at the admissibility-envelope layer: a content-hashed record of decision state, reasserted against live state, where any change in canon, manifest, or evaluator state invalidates a prior ELIGIBLE (canon §12.4), and eligibility does not persist across transitions without revalidation (§13).

**Capabilities (built since Revision 5): a governance / human-oversight layer.** The gate can classify a manifest-declared high-impact action and **hold** it in a pending-approval state until a human approver, using a **separate key**, signs an approval grant that the gate verifies — bound to the exact decision, separated in duty from the gate, fresh, and single-use — and consumes exactly once before forwarding. Approver trust flows through the signed key-record chain with an explicit **approver role distinct from the issuer**, so separation of duties is a property of the signed record, not a key-identifier comparison. Grant single-use and the pending slot hold across instances with a shared store, and a horizontally-scaled gate without one **fails closed at startup**. A mutual-TLS client-authentication proof shows a direct call without the gate's client certificate is refused at the TLS handshake. A startup wiring guard fails the gate closed if a high-impact policy is configured without safe oversight wiring. The filename-level inventory is in the attached document.

**Results.** The full repository test suite passes **512 of 512, 0 xfailed** (up from 419 at Revision 5 and 211 at Revision 3). Carried forward from Revision 3: a 204-call enforcement run — 102 REFUSE → 403 with zero external executions; 102 ELIGIBLE → 200 with exactly 102 external executions, each gate-signed.

**Adversarial review.** The governance layer received an independent **three-model white-box review** (separate runs); it found no exploitable defect on a correctly-wired single-process gate and converged on a small set of deployment-posture hardening items, since addressed or scheduled. This is internal convergence evidence, **not** external validation.

**Honest scope.** No external, third-party adversarial validation on a real multi-host public surface has been performed. The human-oversight guarantee is **built and tested in-repo**; it becomes claimable only inside a deployment that wires the operator-controlled non-bypass layers (inline body binding, mutual-TLS, network isolation) together with a shared store, and it has not been certified by an external adversary. Real cross-host external red-team validation remains the open finish line.

*This is an evidence publication for provenance, not a build guide.*

## 6. Additional notes  (paste into the Zenodo "Additional notes" field)

Revision 6 — governance layer + snapshot advance. Supersedes Revision 5 (DOI 10.5281/zenodo.20751592). The canonical model (v0.9.8.4) is unchanged. This revision advances the implementation snapshot to add a governance / human-oversight layer (high-impact hold → human-signed approval grant → verified, single-use, audited forward), approver provenance + role via the signed key-record chain, shared-store hardening for horizontal scale, a mutual-TLS non-bypass proof, an in-process integration proof, and a fail-closed deployment wiring guard. The test suite is 512/512 (up from 419). Revision 5's distribution correction is carried forward: the core is AGPL-3.0 licensed with the source repository private and access on request. Honest scope retained: the oversight guarantee is in-repo / white-box and is NOT externally validated; no external adversarial validation on a real multi-host surface yet.

## 7. Copyright / Rights  (paste into the Zenodo "Copyright" field)

© 2026 Justin Laporte. This document is licensed CC BY 4.0. The Elyon-Sol core implementation is AGPL-3.0 licensed (open-core); the source repository is private and access is granted on request (admin@elyon-sol.io or justin@elyon-sol.io). The canonical model is published for citation; the administration/tooling SDK is proprietary.

## 8. Keywords
AI governance, human-in-the-loop, pre-execution, deterministic refusal, interaction validity, access control, separation of duties, continuity constraints, fail-closed systems, admission control, ext-authz, OPA, Envoy

## 9. Related identifiers
- Supersedes / is-new-version-of: Revision 5, DOI 10.5281/zenodo.20751592
- Do **NOT** add the GitHub URL as a related identifier — the repository is private and the link would 404.

---

## 10. Honest caveat to keep in mind (carried from Rev 5 — license-choice, not wording)

AGPL-3.0 grants every recipient the right to redistribute. "Access on request" controls who gets the FIRST copy, not who can republish it afterward. If permanent control over who sees the source is the goal, AGPL is the wrong instrument — a source-available / no-redistribution license would be required instead.

---

## 11. Pre-publish check
- [ ] New version cut from the Rev 5 record (20751592), not a metadata-only edit.
- [ ] Rev 5 files removed; Rev 6 `.pdf` + `.md` + architecture PNG attached.
- [ ] Description, Additional notes, Copyright, Keywords set exactly as above.
- [ ] Title says "Revision 6".
- [ ] Snapshot commit in the attached document is `9645fb8…c252d`, suite 512/512.
- [ ] No GitHub related-identifier added.
- [ ] Honest-scope paragraph present (no external-validation claim).

---

## Appendix — the deposit document (attached as enforcement_evidence_addendum_rev6.md/.pdf)

The full Revision-6 deposit document — abstract, what-changed, capability inventory, the 512-test
table by file, the carried-forward interception run, honest-scope open items, reproducibility,
consistency statement, and provenance — is in `docs/zenodo/enforcement_evidence_addendum_rev6.md`
(and its PDF). That file is the attachment; this pack is the record-metadata around it.
