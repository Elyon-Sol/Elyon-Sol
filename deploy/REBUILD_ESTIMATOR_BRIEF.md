# Rebuild-cost estimator — commissioning brief (ext-readiness Gate 3 / plan Phase 3.2)

> **What this is.** The commissioning pack for the stake-free rebuild attempt required by
> `docs/methodology/external_verification_readiness.md` Gate 3 and
> `docs/restructure/29_external_validation_execution_plan.md` Phase 3.2. It is an
> author-authored ASSET; Gate 3 is met only when a stake-free person ships the report
> described below — whatever it concludes. This brief being written meets nothing.

---

## The question (verbatim scope — cost only)

Attempt to assemble the **equivalent admission-and-attestation substrate** from
**OPA + SPIFFE + a PKI** — or your own judgment of the right off-the-shelf components —
and report whether it was cheaper. The answer is **bound to whether it shipped**, not to
an estimate. "A small team could do it in 1–2 months" is explicitly NOT an acceptable
answer, whether it comes from a person or a model (non-evidential per the project's
referent-binding rule, VL-057).

This is Gate 3 ONLY. You are not being asked to attack the live surface (that is Gate 4,
a different, blindness-filtered person), review the code for bugs, or evaluate the
project's claims. Cost, shipped-or-not, and your component judgment — nothing else.

## Who qualifies

An engineer with **no stake** in this project: no authorship, no collaboration on the
build, no investment in the ledger. Prior awareness of the project does not disqualify
you for THIS gate (blindness is Gate 4's filter, not Gate 3's). You may read the repo and
specs freely. The one thing the commissioning party must NOT show you is the project's
prior cross-model review verdicts (demoted at VL-057; showing them re-inflates).

## What "equivalent" means (the functional target)

Your assembly must provide the behaviors in Section 1 of
`docs/methodology/falsifiable_claim_sheet.md`, which for this brief are summarized as:

1. **Deterministic, fail-closed admission** against a hash-pinned policy/manifest:
   ELIGIBLE only on satisfied authority + operation sets and matching manifest
   hash/version; REFUSE otherwise and on any exception (target never called on REFUSE).
2. **Signed, action-bound attestation** of each admitted call: an envelope binding the
   specific tool, canonical args digest, and target URL, signed by an issuer key —
   so an envelope minted for action A / args X / target T cannot authorize anything else
   (claim-sheet rows 5–7).
3. **Freshness + single-use:** a verbatim replay of an honored envelope is refused;
   expired envelopes are refused (row 4).
4. **Drift refusal:** acceptances minted against a superseded published state are
   refused after re-publication (row 8).
5. **Enforcement locus:** a target/sidecar that refuses absent, forged, rebound,
   replayed, stale, and drifted presentations while honoring the positive control
   (rows 1–3).

Partial assembly is a valid result — report what shipped and what did not. This gate is
independent of the project's live surface; you need no access to it.

## Deliverable (the report — this is what meets the gate)

A written report, in your words, containing:

- **Shipped or not:** what you assembled, what works end-to-end, what does not.
- **Cost actuals:** hours spent, calendar span, component inventory (versions), and any
  spend. Actuals only — no extrapolated team-months.
- **Where it was harder/easier than expected**, per functional item 1–5 above.
- **Your verdict:** cheaper or not cheaper than adopting this substrate, and by roughly
  what margin, given the actuals.
- **Your effort bound, stated up front:** declare the time-box you gave it (e.g. "N
  working days") so "did not ship within the bound" is a meaningful, honest outcome.

Both verdicts are acceptable. A report concluding "cheaper, and here is the working
assembly" is as valid a Gate-3 referent as the opposite. The report is ledgered verbatim
in `EVIDENCE/verification_ledger.md` with named credit (the project's recognition model:
permanent named ledger entry; Zenodo co-credit with ORCID if wanted —
see `deploy/BREAK_IT.md`, Recognition).

## Engagement terms (author fills before commissioning)

- **Estimator:** [name / handle] — stake-free per the filter above.
- **Time-box:** [N working days, estimator-declared].
- **Compensation:** [TBD — author decision; recognition model applies regardless].
- **Report channel:** security@elyon-sol.io or a repo PR adding the report under
  `EVIDENCE/verification_runs/`.

---

**Status line (keep honest):** Gate 3 is **NOT MET** as of this brief's authoring. The
only rebuild "estimate" on record is model-sourced and non-evidential. This gate can run
in parallel with the Phase-1/2 live-surface work and does not depend on it.
