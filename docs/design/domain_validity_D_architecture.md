# D(I, domain) — domain-semantic validity as the fourth admissibility invariant

> **Status: model-authored DESIGN, not evidence (GR-3).** The `D` mechanism built this
> session (`IMPLEMENTATION/domain_validity.py`, the example domain manifest, and the proof
> tests) is real and default-off/unwired; the **canon expansion** described here is a proposal
> for the author to ratify via the GR-1 lock ceremony. Nothing in `CANON/` is touched. Per GR-3
> this design is NOT external validation; **G5 remains NOT-MET** and `D` does not touch it.
>
> **Provenance.** The author's committed forward direction (`elyon-sol-forward-direction`
> memory; commit `83d9868`, `docs/design/future_directions_domain_semantic_evaluation.md`),
> sharpened 2026-07-26 with the author's thesis framing: *recursive assessment of envelope
> content; rubber-stamping; policy adherence inside the admissible envelope state.* Every
> "already shipped" primitive below was verified against source this session (GR-2).

---

## 1. The thesis — two questions, in order

The gate today answers **one** question and stops:

> **Q1 (admissibility / authorization).** *Should this interaction occur at all?*
> `G(I) = AC³ ∧ T²⁶ ∧ CCS` — the caller's authorities cover the requirement (`AP ⊇ AR`),
> the operations are covered (`OP ⊇ R`), and continuity holds. Pure set-containment + continuity.

The advancement adds a **strictly-later second question**, asked only of an *already-admissible*
interaction:

> **Q2 (domain-semantic validity).** *This action is admissible — established. But is the
> content it carries **semantically valid and safe within its declared domain**?*
> `D(I, domain)` — a deterministic predicate verdict over the interaction's domain payload.

The target invariant, adopted **openly** at a canon-version event:

```
G(I) = AC³ ∧ T²⁶ ∧ CCS ∧ D(I, domain)
eligible  ⟺  G(I) ∧ D(I, domain)
```

`D` moves Elyon-Sol from an **authorization** boundary to an **admissibility-and-validity**
boundary — "the gate becomes more than a gate."

## 2. The problem D solves: rubber-stamping inside the admissible state

The challenge docs already concede the gap: *"an authorized action could be unwise — the gate
checks authorization, not wisdom."* Between authorization and wisdom sits **domain compliance**,
and it is exactly where a gate silently fails:

- An interaction passes `G(I)` — correct authorities, covered operations, continuity intact.
- Under the human-oversight path (`202 PENDING_APPROVAL`), a human signs a grant.
- **Nothing deterministic inspects the domain content.** The approval *is* the check — and a
  hurried or complicit approver **rubber-stamps** a HIPAA-non-compliant record change, an
  OFAC-flagged transfer, a purpose outside permitted use. The authority set was never the
  problem; the *data inside the envelope* was.

`D` closes this — with a limit that must be stated precisely, because the unqualified version of
the claim is false.

**The structural half is un-waveable.** A domain-invalid *content* check (`D_FIELD_INVALID`,
`D_DOMAIN_UNDECLARED`, `D_DOMAIN_MISBOUND`, …) refuses deterministically, independently of any
approval, and no human grant releases it. For that half, policy adherence is genuinely enforced
on the content rather than assumed from the stamp.

**The verdict half re-introduces a trusted party, by construction.** Once a domain sets
`requires_verdict`, a correctly-signed `SAFE` attestation from the pinned authority *does*
release the call. `D` does not eliminate trust there; it *relocates* it — from an implicit human
stamp to an explicit, role-distinct, cryptographically bound, freshness-windowed, single-use
attestation that is verified deterministically. That is a real improvement in accountability and
auditability, but it is **not** a claim that no party can wave the call through.

So: `D` guards the admissible envelope state against rubber-stamping **structurally**, and makes
the substantive judgment an attributable signed act rather than an invisible one.

## 3. Recursive assessment of envelope content

`G(I)` reads only the top-level authority/coverage **sets** (`AP`, `OP`, `AR`, `R`). `D` reaches
**into the data the admissible envelope carries** — the `context` sub-object that
`build_envelope()` records verbatim under `request_context.context`
(`IMPLEMENTATION/envelope.py:298–308`). Predicate `path`s address fields by dotted key, walked
**recursively** into nested objects (`compliance.hipaa_attestation`, `sanctions.ofac_cleared`).
This is the "recursive assessment of envelope content": `D` inspects the semantic payload the
envelope contains, not merely the sets that decided authorization.

Determinism is load-bearing (canon §9 reproducibility): dict-only descent, a closed rule
vocabulary, first-failure short-circuit — identical `(interaction, domain manifest)` always
yields the identical verdict. `D` is a **bounded predicate set, not a policy engine** — the
README is explicit that Elyon-Sol composes *with* OPA, not replacing it; a Rego runtime inside
`D` is resisted on purpose.

## 4. What is built (default-off, PEP-enforced, proven)

> **Wiring status (current).** D is wired at the **PEP layer** and enforces at runtime when
> `ELYON_DOMAIN_MANIFEST` names a domain ruleset; unset, the block is skipped and the path is
> byte-behavior-identical. D is **NOT** wired into `evaluator.decide()` / `G(I)` — that is the
> admissibility-semantics change and remains an author-ratified canon-version event (§5, §8).
> So the gate genuinely refuses domain-invalid interactions, while canon does not yet claim `D`
> as an invariant. Both halves are asserted by tests so neither drifts silently.

| Artifact | What it is |
|---|---|
| `IMPLEMENTATION/domain_validity.py` | The `D(I, domain)` evaluator: `assess()` → `(state, code, detail)`; `domain_valid()`/`domain_reason()` projections (mirrors `decide`/`evaluate`/`refusal_reason`, VL-150). Deterministic, fail-closed, recursive. |
| Rule vocabulary | Closed set `{present, absent, equals, in, not_in}`. Not a rule engine. |
| `D_*` reason codes | Closed set `{D_MANIFEST_MALFORMED, D_DOMAIN_UNKNOWN, D_DOMAIN_UNDECLARED, D_FIELD_ABSENT, D_FIELD_INVALID, D_INTERNAL}` — **prefix-disjoint** from the evaluator `G_*` and boundary `REF_*` vocabularies (proven in tests). |
| `MANIFEST/domain_manifest.example.json` | An **example** (not live/armed) domain ruleset — the author's `healthcare_admin` worked example + `finance_transfer`. Hash-pinnable via `domain_manifest_sha256()`. |
| `TESTS/adversarial/test_domain_validity.py` | 32 proof tests: unarmed no-op, every rule, recursive nested paths, fail-closed malformation, unknown/undeclared domain, the rubber-stamp scenario, determinism, `D_/G_/REF_` disjointness, and an **unwired-guard** asserting evaluator/pep never import `D`. |

Also built since: `domain_verdict.py` (signed out-of-band attestation + `claim_verdict_once`),
`domain_control.py` (the PASS / HOLD_FOR_VERDICT / HOLD_FOR_HIL / REFUSE state machine),
`domain_authority.py` (verdict-signer trust by signed-chain role), `resolve_domain_manifest()`
(the ABSENT-vs-MALFORMED compose-in contract), a tracked **unarmed**
`MANIFEST/domain_manifest.json`, and the pep-layer wiring.

**Frozen (the canon boundary):** `evaluator.py` (`evaluator_sha256 ca7c922c…` unchanged),
`MANIFEST/manifest.json` (`manifest_sha256` unchanged), `EVIDENCE/published_hashes.json`,
`CANON/*` (GR-1). `D` imports nothing into the hashed core. `pep.py` and `envelope.py` are not
hash-pinned, so PEP-layer enforcement moves no pin.

**Request-schema change:** `domain` is an OPTIONAL declared selector inside `interaction`
(mirroring `interaction_type`), carried through normalization and bound into the envelope — so
`decision_sha256` covers the domain declaration and a verdict bound to that hash is transitively
bound to the domain it was issued for. Undomained requests stay byte-identical.

### Domain manifest shape (hash-pinnable, versioned — canon §11.9 discipline)

```json
{
  "version": "1.0",
  "require_domain": false,
  "domains": {
    "healthcare_admin": {
      "predicates": [
        {"path": "patient_consent", "rule": "equals", "value": true, "label": "..."},
        {"path": "compliance.hipaa_attestation", "rule": "equals", "value": "current"}
      ]
    }
  }
}
```

A manifest with no `domains` (or empty) is **unarmed**: `D` is a no-op pass-through, mirroring the
flat/default `manifest.json` in the typed-impact machinery. An **armed** manifest with a declared,
unknown domain fails closed (`D_DOMAIN_UNKNOWN`); an armed manifest + `require_domain:true` +
no declared domain fails closed (`D_DOMAIN_UNDECLARED`). The default deployment is unarmed, so
turning `D` on is a deliberate operator act, not a consequence of this build.

## 5. Composition seam and re-pin discipline (the canon-increment step, NOT done here)

The single composition point is `evaluator.decide()` (`IMPLEMENTATION/evaluator.py:222`), after
`manifest_integrity_valid` establishes admissibility and before `return "ELIGIBLE", None`:

```python
        if not manifest_integrity_valid(ctx, manifest):
            return "REFUSE", G_MANIFEST_INTEGRITY
        # --- compose-in (canon increment only): ---
        # dstate, dcode, _ = domain_validity.assess(ctx, load_domain_manifest())
        # if dstate != "VALID":
        #     return "REFUSE", dcode        # a D_ code, disjoint from G_
        return "ELIGIBLE", None
```

Composing it moves `evaluator_sha256` and REDs the ~49-test verify-against-pinned family until
the record is regenerated via its generator (VL-115 discipline — expected churn, not breakage).
It also adds a **`domain_manifest_sha256` / `domain_manifest_version` pin** to
`published_hashes_gen.py` and the envelope, so the domain ruleset is pinned exactly like the
manifest. **None of that is done** — it belongs to the ratified canon version.

**What IS done instead is Wiring B: enforcement one layer out, in `pep.governed_call`.** D runs
after the ELIGIBLE envelope is built (so `decision_sha256` exists to bind a verdict to) and
before the approval gate, as explicit early returns so no outcome can be swallowed by a
fail-closed `except`. `REFUSE` → 403 carrying the `D_` code; `HOLD_FOR_VERDICT` /
`HOLD_FOR_HIL` → 202 with distinct terminal states; `PASS` → claim `verdict_id` once via the
`ReplayCache`, then fall through to the unchanged sign-and-forward. The verdict arrives on a
request header and is passed *into* `domain_control`, so the gate never calls a policy agent
inline — the determinism firewall, in the wiring as well as the module.

**The distinction that matters:** Wiring B makes D *enforced*; only Wiring A makes D *canonical*.
A deployment running Wiring B genuinely refuses domain-invalid interactions, but `G(I)` is still
`AC³ ∧ T²⁶ ∧ CCS` and no artifact should claim otherwise.

## 6. Mid-stream domain drift → out-of-band re-determination (design, next increment)

Reassertion today detects **hash** changes (`reassert()` Rows 1–4). Domain-compliance drift may be
a change in **external domain state** the pure, stateless verifier cannot see (an attestation
lapses *after* issuance). The design:

- A **new reassertion outcome — `RE-DETERMINE-OUT-OF-BAND`** — distinct from
  `RE-EVALUATE-REQUIRED`. It means: a domain-compliance change needs a **human/authority grant**,
  not an automatic re-pin.
- It **should** route into the existing `202 PENDING_APPROVAL` + signed-grant path
  (`pep.governed_call`, VL-114/115/119/148), keyed to **domain-compliance** rather than the
  `HIGH_IMPACT` designation.
  > **NOT BUILT — the loop is open.** `HOLD_FOR_HIL` currently returns a 202 with a distinct
  > terminal state, but the wiring does **not** call `_PENDING.issue(...)` and emits no
  > `approval_request_id`. Nothing binds that decision into the pending set, so the existing
  > grant path cannot release it: an authentic `UNSAFE` verdict leaves the interaction reported
  > but stuck. Closing this — issuing the pending request with a domain-compliance hold reason
  > that `reconcile_approvals` can distinguish from a `HIGH_IMPACT` hold — is the next increment.
  > Do not describe the re-determination loop as operational until it lands.
- **Keep the verifier pure.** The drift *signal* comes from a stateful **monitor** (§7), never
  from inside `verify_envelope`. Defining what the envelope may "become aware" of without making
  the verifier stateful is the core open design problem — carried forward honestly.

## 7. The monitor agent (operator-locus — GLESAC)

A read-only agent watching live envelopes/decisions for domain adherence, flagging/escalating
drift into §6. Build on the inspector ladder (`envelope_inspector.py`) + issuance/approval logs +
`reconcile`. Natural home: the **GLESAC** console (github.com/Elyon-Sol/GLESAC) extended with
domain checks. **Load-bearing constraint: the monitor is NEVER authoritative and NEVER a bypass**
— read-only, fail-safe (down → opens nothing). The gate and the human stay the only deciders; a
monitor that could admit/deny would reintroduce the trust it exists to constrain (mirrors GLESAC's
existing SoD no-signing-primitive discipline).

## 8. Advancing the canon correctly (GR-1)

`D` is a **new admissibility conjunct — a new invariant.** The canon's "no new invariants
introduced" rule holds *within* a version; adopting `D` therefore requires a version bump whose
whole point is that expansion, authored as a new canon PDF, locked, ledgered. **Do not smuggle
`D` into CCS** — that is exactly the v0.9.8.5 Variant-B mistake (folding a gate into CCS was ruled
incoherent because it added an invariant while claiming not to). Expand the invariant set openly:

1. **§13** — `G(I) = AC³ ∧ T²⁶ ∧ CCS ∧ D(I, domain)`; `D=0 → REFUSE` with a `D_` reason code.
2. **§3** — a Domain-Validity Invariant subsection + the `D_` code set, declared disjoint from
   `G_`/`REF_`.
3. **§11 / a new §16** — the domain manifest as a hash-pinned, versioned, integrity-verifiable
   artifact (parallel to §11.9's governing manifest `M`).
4. **§14, Appendix D.4** — restate scope: "authorization, not wisdom" becomes "admissibility
   *including domain-validity*," deliberately, on the record. Add a worked `D=0` example.
5. **§6** — the `evaluate()` pseudocode gains the `D` short-circuit after the integrity check.

## 9. Increment order (build-then-wire, fail-closed, each default-off)

| # | Step | Status |
|---|---|---|
| 1 | Domain manifest schema + validator (data + validator, no decision-path change) | **DONE** |
| 2 | `D(I, domain)` evaluator — new module above `G(I)`, own reason codes | **DONE** |
| 2b | Signed domain-verdict + `domain_authority` role + `domain_control` state machine | **DONE** |
| 2c | Compose-in contract (ABSENT vs MALFORMED) + unarmed tracked default | **DONE** |
| 2d | **Wiring B** — PEP-layer enforcement, opt-in; REFUSE→403, HOLD→202, single-use claim on release | **DONE** |
| 3 | **Canon increment** — author v0.9.8.6-or-9 adopting `G(I)=…∧D`, restate §14/D.4 (§8) | **AUTHOR-locus** (PDF + lock + ledger) |
| 4 | **Wiring A** — `eligible ⟺ G(I) ∧ D` in `decide()`; add `domain_manifest_sha256` pin; re-pin per VL-115 | pending (rides step 3) |
| 5 | Domain-drift reassertion outcome → `202`/signed-grant path (§6). **Partial:** `HOLD_FOR_HIL` returns a distinct 202 but does not yet issue an `approval_request_id` into the pending set, so the re-determination loop is not closed end-to-end. | partial |
| 6 | Monitor agent — operator-locus, read-only, non-authoritative, fail-safe (§7) | pending (build last) |

## 10. Honest ceiling (unchanged)

`D` makes the gate more capable; it does **not** make it externally validated. **G5 — a blind
external adversary on a live surface — remains the one gate no new capability closes**, and it
still requires an outside party. Building `D` advances the canon and the vision; it does not
substitute for the finish line the project never reached. Per GR-3 this document and the `D`
white-box tests are internal hardening, correctly labelled, not external validation.
