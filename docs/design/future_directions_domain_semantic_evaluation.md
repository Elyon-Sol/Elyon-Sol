> # ⛔ SUPERSEDED — ATTEMPTED, BUILT, AND WITHDRAWN (2026-07-27)
>
> **This document no longer describes the project's direction. It is retained, unedited below
> this header, as the record of a direction that was taken and then reversed.** Deleting it
> would hide a decision that has more value stated than erased.
>
> **What happened.** The `D(I, domain)` layer described below was built in full: four modules,
> a signed out-of-band policy-verdict protocol, a third trust role, a hash-pinned domain ruleset,
> and an attested human-override path — with 168 tests. It was then removed in its entirety.
>
> **Why it was withdrawn.** The expansion added seams and holes and pulled the project off its
> own thesis:
>
> - **It competed on planes where the project loses.** A five-predicate vocabulary duplicating
>   what OPA, Cedar and Rego do far better — the opposite of the stated position that Elyon-Sol
>   *composes with* policy engines rather than replacing them.
> - **Its most-praised distinction was prior art.** "Post-authorization structural refuse" is
>   Gatekeeper/Kyverno since 2019 and Kubernetes VAP+CEL since 2024.
> - **New surface produced a real hole.** An authentication bypass — an unsigned request header
>   reviving an expired SAFE verdict, admitting the call and replayable — which the layer's own
>   168 tests did not catch. Found by adversarial review, reproduced by execution, fixed, and
>   then removed with the rest.
> - **Nothing consumed it.** Absent from every runbook, compose file, Dockerfile, env example,
>   the README, `readiness.json`, the ext-authz sidecar and the MCP server. Built capability,
>   zero deployed capability.
> - **The claimed advantage was inflated.** An in-session estimate of "+7" against comparable
>   stacks did not survive adversarial analysis, which put it at +1 to +2 in novelty and 0
>   deployed.
>
> **What was preserved.** The frozen core was never touched: `evaluator.py`, `MANIFEST/manifest.json`,
> `EVIDENCE/published_hashes.json` and `CANON/*` are byte-identical across the entire attempt.
> `G(I) = AC^3 ∧ T^26 ∧ CCS` is unchanged and no canon-version event occurred. The suite returned
> to exactly its pre-attempt count of 645. Build-then-wire and the GR-1 canon boundary held under
> pressure — the discipline worked even where the judgment did not.
>
> **The lesson, stated plainly.** The failure was not in the engineering; the modules were
> competent and tested. It was in scope: an admission gate that starts inspecting content is on
> its way to becoming a policy engine, and every new plane of competition is new surface to
> defend. A mistake found and removed is worth more than a mistake erased — provided it is
> stated. This is the statement.
>
> Full record: `docs/design/domain_validity_withdrawal.md`. Code history is preserved in git.

# Canon advancement — domain-semantic validity as a new invariant

> **Status: the author's committed forward direction.** Elyon-Sol is developed by a single author
> (no forks, no clones, no team). The public *program* is wound down — no commercial layer, no live
> surface, no external engagement — but the author continues to advance the work. This document is
> the intended next major evolution: **the gate becomes more than a gate.** Beyond deciding whether
> an interaction is *authorized*, it will evaluate whether the action is *valid within its domain*.
> That capability is intended to **expand the invariants and advance the canon** (`G(I)` gains a new
> conjunct), which under GR-1 is a deliberate canon-version event: a new canon PDF the author
> authors, a new lock, a new ledger entry — never an in-place edit.
>
> Discipline still binds: GR-2 (verify every "already shipped" claim below against the code before
> building; no claimed-but-unwired), GR-3 (this document is design, not evidence). Provenance: the
> author's own articulation (July 2026), captured here so a future session — of the author or of an
> AI context resuming from this repo — continues the exact trajectory rather than re-deriving it.

---

## The thesis

Today the gate answers **authorization**: `G(I) = AC³ ∧ T²⁶ ∧ CCS` — the caller's authorities cover
the requirement (`AP ⊇ AR`), the operations are covered (`OP ⊇ R`), and continuity holds. Pure
set-containment + continuity.

The advancement is a **fourth dimension — domain-semantic validity `D(I, domain)`** — so the gate
answers not only *"is this authorized?"* but *"should this action be approved within its domain's
context?"*. The target invariant:

```
G(I) = AC³ ∧ T²⁶ ∧ CCS ∧ D(I, domain)
```

The author's worked example: a healthcare administrative action that stops maintaining compliance —
the envelope **becomes aware**, **forks the stream**, and the readmissibility change requires **not
just a new pin but out-of-band determination**. Plus **agent monitoring of envelopes for
domain-specific adherence.**

**This is the "more than a gate" step: `D` moves Elyon-Sol from an authorization boundary to an
admissibility-*and*-validity boundary.**

## Read this first: most of the *mechanism* is already shipped

Do not reinvent the plumbing. The "fork the stream / require out-of-band determination" behavior is
largely existing primitives. Verify each against the code (GR-2), then build the **one genuinely new
layer — `D` — on top.**

| Already in the repo (build ON this) | Where |
|---|---|
| Reassertion: `reasserted` / `invalidated` / `re-evaluate-required` — a past "yes" is never honored after the state it depended on changes | `IMPLEMENTATION/envelope.py::reassert()` (VL-029) |
| Per-type evaluation: required (AR/R) sets selected by the interaction's declared type, fail-closed on unknown type | `evaluator.resolve_required_sets` (typed-impact, VL-132/133) |
| Out-of-band human determination: `202 PENDING_APPROVAL` → a human signs a single-use grant with their own key (SoD, local custody), trust via a signed key-record chain | `approval.py`, `approver_trust.py`, `pep.governed_call` (VL-114/115/119, VL-148) |
| Refusal reason codes: the evaluator names *which* condition failed (`G_*`), disjoint from the boundary `REF_*` vocabulary | `evaluator.decide` / `refusal_reason` (VL-150) |
| Domain-shaped characterization: medical / legal / finance inputs through the one unchanged chain | `EVIDENCE/proofs/three_domain_poc/` (VL-096) |
| Envelope audit ladder + reconcile (issued vs executed) | `IMPLEMENTATION/envelope_inspector.py` |

**Genuinely unbuilt: `D(I, domain)` itself — the domain-validity evaluator — and its composition
into the decision, reassertion, and out-of-band paths.** Everything else it needs already exists.

## The four components

### A. `D(I, domain)` — the domain-validity evaluator (the new invariant)
- **New module ABOVE `G(I)`** (the VL-113 pattern: keep `evaluator.py`'s hashed core byte-identical
  until deliberately composed in; editing it moves `evaluator_sha256` and REDs the pinned tests).
- **Deterministic and fail-closed** (unknown/malformed domain → REFUSE). A non-deterministic /
  model-based `D` would be a weaker, different system — hold that line; the canon's determinism
  guarantee is load-bearing.
- Its own reason-code namespace, disjoint from `G_*` and `REF_*`.

### B. Domain rules as a hash-pinned, versioned artifact
- A **domain manifest** (the domain's compliance predicates), hash-pinned / versioned /
  integrity-verifiable like `MANIFEST/manifest.json` (canon §11.9). The interaction pins its
  `domain`; resolved fail-closed by the typed-impact machinery. A ruleset that doesn't match its
  pin refuses (`G_MANIFEST_INTEGRITY`-style).
- **Keep it a small pinned predicate set, not a policy engine.** The README is explicit that
  Elyon-Sol composes *with* OPA, not replacing it. `D` is a bounded, deterministic compliance
  predicate — resist a Rego runtime.

### C. Mid-stream compliance drift → reassertion + out-of-band determination
- Add a **domain dimension to reassertion**: a new outcome (e.g. `re-determine-out-of-band`)
  distinct from `re-evaluate-required`, meaning a domain-compliance change needs a human/authority
  grant, not an automatic re-pin — routed into the existing `202` + signed-grant path, keyed to
  domain-compliance rather than the `HIGH_IMPACT` designation.
- **The hard part is *detecting* the drift.** Reassertion today detects *hash* changes; domain-drift
  may be a change in *external domain state* the pure stateless verifier can't see. Keep the verifier
  pure and let a *stateful monitor* (D) supply the drift signal. Defining what the envelope may
  "become aware" of, without making the verifier stateful, is the core design problem.

### D. A monitor agent for domain adherence
- Watches live envelopes/decisions, evaluates domain adherence, flags/escalates drift (into C).
  Build on the inspector ladder + issuance/approval logs + `reconcile`. Operator-locus — think the
  GLESAC console (https://github.com/Elyon-Sol/GLESAC) extended with domain checks.
- **Load-bearing constraint: the monitor is NEVER authoritative and NEVER a bypass.** Read-only,
  fail-safe (down → opens nothing). The gate and the human stay the only deciders; the monitor only
  flags and escalates. A monitor that could admit/deny would reintroduce the trust it exists to
  constrain.

## The canon question — decided, and how to advance it correctly

The current canon frames the gate as *authorization / admissibility*, and the challenge docs say
outright *"an authorized action could be unwise — the gate checks authorization, not wisdom."*
Domain-compliance sits between authorization and wisdom. **The direction taken is that domain-
validity is a legitimate expansion of admissibility: an action out of domain-compliance is
*inadmissible*.** That is the deliberate scope expansion — the gate becoming more than a gate.

Advance it correctly:

1. **It is a canon-version event (GR-1).** `D` is a new admissibility conjunct — a *new invariant*.
   The canon's "no new invariants introduced" rule holds *within* a version, so this needs a version
   bump that **consciously adopts** `D`, authored as a new canon PDF, locked, ledgered. Do **not**
   smuggle it into CCS or fold it in silently — that is exactly the v0.9.8.5 Variant-B mistake
   (folding a new gate into CCS was ruled incoherent because it added an invariant while claiming
   not to). Expand the invariant set *openly*, in a version whose whole point is that expansion.
2. **Restate the scope sections** (§14, D.4) in that new canon version so "authorization, not
   wisdom" becomes "admissibility *including domain-validity*" — deliberately, on the record.

## Suggested increment order (build-then-wire, fail-closed, each default-off)

1. **Domain manifest schema** — hash-pinned, versioned domain rules. Data + validator only; no
   decision-path change (mirrors the typed-impact manifest work).
2. **`D(I, domain)` evaluator** — new module above `G(I)`; deterministic, fail-closed; own reason
   codes. Unwired.
3. **The canon increment** — author v0.9.8.x-or-9 that adopts `G(I) = AC³ ∧ T²⁶ ∧ CCS ∧ D` and
   restates §14/D.4. New PDF, new lock, ledger entry.
4. **Composition** — `eligible ⟺ G(I) ∧ D` in the evaluator; re-pin per VL-115.
5. **Domain-drift reassertion outcome** → routed into the `202` / signed-grant out-of-band path.
6. **Monitor agent** — operator-locus, read-only, non-authoritative, fail-safe. Build last.

## Honest ceiling (unchanged)

`D` makes the gate more capable; it does **not** make it externally validated. G5 — a blind external
adversary on a live surface — remains the one gate no amount of new capability closes, and it still
requires an outside party. Building `D` advances the canon and the vision; it does not substitute
for the finish line the project never reached.
