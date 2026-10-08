# Zenodo Rev 9 — compiled posting pack (ready to publish)

Compiled from `docs/zenodo/enforcement_evidence_addendum_rev9.md` (the deposit document; its
PDF is rendered locally with pandoc/pdflatex and is git-ignored). This one file is everything
needed to cut Revision 9.

> **PUBLISHED 2026-10-08** as Rev 9 — DOI `10.5281/zenodo.23228423`, record https://zenodo.org/records/23228423. This pack is retained as the record of how it was cut. As published: the Description carries the pack's related-identifier, keyword and additional-notes text appended after its closing line (author's choice); the bold lead-ins are literal asterisks; the term list lives in the record's References field (17 terms inherited from Rev 8), as it has for every revision — Zenodo's upload form shows no Keywords field for this record.

Snapshot: commit `2d5c6bf6c97edacc12748e6186b6ccf4eb853115` (2026-10-08), suite **689 passed**.
Canonical model **v0.9.8.4 unchanged**; canon `d1c9d187` and manifest `ac18ac78` unchanged;
evaluator pin `ca7c922c` (moved once, at VL-150). Supersedes Revision 8 (DOI
`10.5281/zenodo.21364720`). Concept DOI `10.5281/zenodo.19367848`.

---

## 0. How to cut this version (do this first)

1. Open the CURRENT live record — Revision 8: https://zenodo.org/records/21364720
2. Click **"New version"** (keeps the concept DOI and the version chain; a new version DOI is
   minted on publish). Do NOT edit Rev 8 in place for this — it is a real snapshot advance
   (616 → 689, evaluator pin moved, four Rev 8 statements corrected). The in-place edit already
   made to Rev 8's licensing paragraph on 2026-10-08 stays as the erratum on that version.
3. **Remove** the attached Rev 8 addendum files (`enforcement_evidence_addendum_rev8.md/.pdf`)
   and `webhook.site.stats.png` (the third-party leg was not re-run; its screenshot belongs to Rev 8).
4. **Attach** the Rev 9 files:
   - `docs/zenodo/enforcement_evidence_addendum_rev9.pdf`
   - `docs/zenodo/enforcement_evidence_addendum_rev9.md`
   - the two architecture diagram files carried from Rev 8, unchanged
     (`elyon_sol_framework_architecture_rev8.png/.svg`) — the model and its components did not change.
5. Apply the metadata fields in sections 1–8 below.
6. Publish. Then record the new version DOI in STATE.md and `site/index.html` (the site cites
   the concept DOI, which now resolves here).

---

## 1. Title
Elyon-Sol v0.9.8.4 — Enforcement Evidence Addendum (Revision 9)

## 2. Authors / Creators
LaPorte, Justin — ORCID 0009-0008-3785-3089 (Researcher)

## 3. Resource type / Publisher / Language
Report · Zenodo · English

## 4. License
Creative Commons Attribution 4.0 International (CC BY 4.0) — this deposit is the document.
(AGPL-3.0 governs the code, which is not in this deposit.)

## 5. Description  (paste into the Zenodo "Description" field)

> Render-safe: bold lead-ins only, no multi-line bullet lists and no code/backtick spans.
> Paste as-is. It deliberately differs from the addendum: the addendum is the referent-bound
> evidence document; this is the record page's summary of what the revision is and corrects.

**Elyon-Sol** is a deterministic, fail-closed HTTP admission gate derived from a formal admissibility specification. The canonical model is unchanged from v0.9.8.4: **G(I) = AC³ ∧ T²⁶ ∧ CCS** — Authority and Coverage are the two per-request set-containment checks against a SHA-256-pinned manifest, and Continuity is the property that a past admission is not honored after the policy or decision logic it depended on changes. Per the canon, the superscripts are nominal labels from the original notation, not exponents.

**This revision (Revision 9) supersedes Revision 8** (DOI 10.5281/zenodo.21364720). It is a **correction-and-evidence revision**, not a model advance: it corrects four statements in Revision 8 that are no longer true, re-measures the enforcement evidence at a new snapshot with a harness that is now committed, and adds evidence from a real multi-container stack. Snapshot commit 2d5c6bf6c97edacc12748e6186b6ccf4eb853115, observed 2026-10-08.

**What Revision 8 stated that is no longer true, corrected here.** First, licensing: the core implementation and the companion operator console are AGPL-3.0 with no commercial, proprietary, or dual-licensed components; the "open-core / proprietary tooling SDK" description was withdrawn on 2026-07-26. Second, the live surface: the four public test nodes were retired on 2026-07-20, six days after Revision 8 was published; there is no live public surface, and nothing in this revision was measured on one. Third, the evaluator pin: the SHA-pinned evaluator moved once, at ledger entry VL-150, to carry refusal reason codes that name which admission condition refused; no admissibility decision changed, the canon and manifest pins are unchanged, and the published record was regenerated through its generator. A verifier comparing a current envelope against Revision 8's record sees an evaluator mismatch; against this revision's record it does not. Fourth, the test suite is 689, up from 616.

**What changed since Revision 8.** Twelve admission fixes, each pinned by a test that fails if the fix is removed, found by a white-box review of every path that honors a token and by the follow-up that closed everything it named: among them, the forward now connects to the address the guard vetted so a resolver cannot answer differently to the guard and the forward; the executor SDK refuses a token without a single-use identifier and can never reach the verifier's unsigned path; root-key validity windows are enforced; approval holds expire; the forward-target guard covers every non-global address range and its allowlist matches origins rather than hostnames; the generated secrets file is owner-only; the sidecar's decision port is loopback-only; every container image is pinned by digest. The human-approval path was proven across two gate replicas with a shared store and a mutually-authenticated target, under containers: an unapproved high-impact call is held and the target is never called; a grant minted by a separate approver process releases it exactly once; a replayed grant is refused on both replicas; the issuance and approval logs reconcile clean. A self-host stack replaces the retired live surface, so any reader can stand up the same gate, target, publisher and sidecar and run the same attacks.

**Enforcement evidence, re-measured with a committed harness.** Revision 8 reported its 204-call census from a loopback receiver but named no committed harness for that variant. This revision commits one and re-runs it at the snapshot: 204 HTTP calls, 102 REFUSE returning 403 with zero external side effects, 102 ELIGIBLE returning 200 with exactly one external POST each — every forward carrying a signed envelope with a distinct single-use identifier, zero from the REFUSE branch, zero duplicates. The harness is hermetic and now runs in continuous integration on every push. The third-party receiver leg was **not** re-run; Revision 8's run stands as the last external confirmation of the forward count. In addition, the live attack suite — un-attested, forged, replayed, rebound and cross-target presentations plus a positive control — defeated six of six against the self-hosted stack over plain HTTP and again over TLS.

**Licensing and access.** The canonical model remains published for citation. The core implementation, and the companion operator console GLESAC, are licensed under AGPL-3.0; there are no commercial, proprietary, or dual-licensed components (see LICENSING.md in the repository). Source public at https://github.com/Elyon-Sol/Elyon-Sol. This document is licensed CC BY 4.0.

**Honest scope.** This is development-side, referent-bound evidence — the test suite, the runnable proofs, the hermetic census, and author-side executions against a stack on a single host, where custody separation between gate, approver and publisher is by container and process, not by host. No external, third-party adversarial validation on a real multi-host public surface has been performed; there has been no live public surface since 2026-07-20, so that remains the open finish line. No guarantee is claimed as deployment-certified. One deployment-visible change is recorded: an allowlist entry that is a bare hostname now admits that host on the scheme's default port only.

*This is an evidence publication for provenance, not a build guide.*

## 6. References (the term list; Zenodo's form has no Keywords field for this record)
AI Governance; Substrate; pre-execution; deterministic refusal; interaction validity; formal verification; access control; continuity constraints; human-in-the-loop; separation of duties; fail-closed systems; admission control; ext-authz; OPA; Envoy; key revocation; signed key record; enforcement census; reproducible evidence

## 7. Related identifiers
- https://github.com/Elyon-Sol/Elyon-Sol — Is supplemented by (software)
- 10.5281/zenodo.21364720 — Is new version of (Revision 8)

## 8. Additional notes
Revision 9 — correction-and-evidence revision. Corrects Revision 8 on licensing (AGPL-3.0 only; no commercial, proprietary or dual-licensed components), on the live surface (retired 2026-07-20; no live public surface exists), on the evaluator pin (ca7c922c since VL-150, refusal reason codes; canon and manifest unchanged) and on the test count (689). Twelve admission fixes since Revision 8, each pinned by a revert-proven test; the governance approval path proven across two replicas under containers; the enforcement census re-run at the snapshot commit with a committed hermetic harness (204 / 102 / 102 / 0 unexpected / 102 forwards, 0 from REFUSE); the live attack suite 6/6 over HTTP and over TLS against a self-hosted stack. Supersedes Revision 8 (DOI 10.5281/zenodo.21364720). Canonical model (v0.9.8.4) unchanged. Honest scope retained: author-side / white-box / single host; the third-party census leg not re-run; no external multi-host adversarial validation.
