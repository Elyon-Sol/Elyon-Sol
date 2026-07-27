# STAIRCASE — the deterministic climb to a v1.0 stack (the door = re-open G5)

> **What this is.** A progress ledger, nothing else. "Staircase" is a progression metaphor for
> the build toward a noticeable, secure v1.0 Alpha/Beta — the point at which external adversarial
> validation (G5) becomes worth re-opening. Per `g5-deferred-until-v1-alpha-beta`: **build the
> stack first, then open the door.** This file records how many stairs there are, which one we are
> on, and each stair's acceptance criterion. It is used ONLY to track progress — never as framing,
> theater, or a substitute for the honest-scope discipline (G5 stays NOT-MET on every artifact,
> GR-3, until an outside party actually engages).
>
> **Keeper.** The assistant maintains this file deterministically: a stair flips to DONE only when
> its acceptance criterion is met by a real referent (a passing proof test, a frozen-pin
> verification), and the "current position" line moves in lockstep. Author-locus stairs (canon
> events) are marked and are the author's to execute.

**Top of the staircase (the door):** a v1.0 Alpha/Beta where `D(I,domain)` is composed + wired,
the domain-verdict → HIL → re-pin loop is operational, the monitor is live, the full loop is
integration-proven, the new surfaces are security-hardened, and the stack is demonstrable. THEN,
and not before, re-open G5.

---

## Current position

**Phase 1 COMPLETE (S1–S5b). D now ENFORCES at the PEP layer, default-off via `ELYON_DOMAIN_MANIFEST`.** Full suite 785 green; frozen core (`evaluator_sha256 ca7c922c…`, manifest, published_hashes, canon) intact — the canon boundary is now guarded by a test rather than by absence of wiring.

Ledger drafts: VL-151 (landing), VL-152 (S1/S3/S4), VL-153 (S2), VL-154 (S5a CVP mitigation + cross-model strengthening), VL-155 (S5b + Wiring B).

**Deployed separation moved off the pre-D baseline for the first time:** axes F/G/H contribute at runtime when armed, not just as built capability. Phase 2 (canon adoption) remains author-locus.

Total stairs: **11** across 3 phases. (Landing 0 is pre-Staircase and already done.)

---

## Landing 0 — the D substrate exists (pre-Staircase)
- **D-structural evaluator** (`IMPLEMENTATION/domain_validity.py`) + domain-manifest schema +
  32 proof tests. Deterministic, fail-closed, recursive over envelope content, `D_` namespace
  disjoint from `G_`/`REF_`, unwired, frozen core. **DONE** (VL-151).

## Phase 1 — make D load-bearing & secure (frozen core, default-off, build-then-wire)

| Stair | What | Acceptance criterion | Status |
|---|---|---|---|
| **S1** | Domain-verdict artifact (`domain_verdict.py`): signed, bound to `decision_sha256`, fresh (reuse `verifier.not_after_valid`), domain-bound, `SAFE`/`UNSAFE` payload, single-use id. Mirror of `approval.py`. | build/sign/verify proven; forged/stale/rebound/wrong-domain/wrong-value/SoD all fail-closed; core frozen. | **DONE** |
| **S2** | `domain_authority` role in the signed key-record/root trust chain (mirror `approver_trust`), structurally disjoint from `issuer` and `approver`. | a key is a trusted verdict signer only if the signed record publishes role `domain_authority`; issuer/approver keys structurally excluded. | **DONE** |
| **S3** | Domain-manifest schema: per-domain `requires_verdict` + pinned `authority_key_id` (data + validator). | schema validates fail-closed; `requires_verdict` demands an `authority_key_id`; existing tests unaffected. | **DONE** |
| **S4** | `domain_control(...)` state machine: `PASS` / `HOLD_FOR_VERDICT` / `HOLD_FOR_HIL` / `REFUSE`. Pure given inputs (verdict passed IN — the determinism firewall in code shape). | D-structural + verdict compose deterministically; verdict is never fetched inline; own `D_` codes; fail-closed. | **DONE** |
| **S5a** | **CVP mitigation** of the D layer: DV-01 (undeclared-domain bypass), DV-02 (domain-shopping), DV-03 (`gate_key_id=None` disables SoD), DV-04 (`expected_decision_sha256=None` satisfies binding), DV-05 (single-use unenforced), DV-06 (bool/int predicate confusion), DV-07 (version ungated), DV-08 (unbounded findings). | each finding's pre-fix behavior is a named revert-catcher; the original probes that returned PASS now REFUSE/HOLD. | **DONE** |
| **S5b** | Compose-in contract: a default UNARMED `MANIFEST/domain_manifest.json` + `resolve_domain_manifest()` separating ABSENT (inert) from MALFORMED (fail-closed). | absent → unarmed, not REFUSE-ALL; malformed → refuses; tracked default is inert. Proven at unit and HTTP layer. | **DONE** |
| **S5c** | **Wiring B** — D enforces at the PEP layer, opt-in via `ELYON_DOMAIN_MANIFEST`. REFUSE→403, HOLD→202 (distinct terminal states), PASS→single-use verdict claim then unchanged forward. `domain` added as an optional request selector + envelope binding. | 13 end-to-end tests; default-off path byte-behavior-identical; canon boundary asserted by test. | **DONE** |

## Phase 2 — compose & ratify (author-locus canon events; assistant preps, author executes)

| Stair | What | Status |
|---|---|---|
| **S6** | Canon increment authored: `G(I)=AC³∧T²⁶∧CCS∧D`; §3/§6/§11/§13/§14 edits; new PDF + lock. | AUTHOR-locus |
| **S7** | Compose `D` into `decide()`/`pep` atomically + add `domain_manifest_sha256` pin + re-pin (VL-115 discipline). | TODO (rides S6) |
| **S8** | `reassert()` gains `RE-DETERMINE-OUT-OF-BAND` (artifact-05 spec) + the drift→`202` routing. | TODO (build beside `reassert()`, do not mutate until ratified) |

## Phase 3 — operationalize & make it noticeable/secure (the v1.0 surface)

| Stair | What | Status |
|---|---|---|
| **S9** | GLESAC monitor extended with domain checks — read-only, non-authoritative, fail-safe (down → opens nothing). | TODO (operator-locus) |
| **S10** | End-to-end integration proof: content flagged → out-of-band verdict → HIL → gate re-mints → required re-pin; + packaging/demo. | TODO |
| **S11** | Security hardening pass: threat-model the new surfaces (verdict replay, authority-key compromise bounding, determinism-firewall audit, fail-toward-hold). | TODO |

---

## Invariants the climb must never break (or a stair does not count as DONE)
- Frozen core: `evaluator.py` (`evaluator_sha256`), `MANIFEST/manifest.json`, `published_hashes.json`,
  `CANON/*` stay byte-identical until an author-ratified compose/re-pin (GR-1, VL-115).
- Determinism firewall: no out-of-band call inside `G(I)`; verdicts enter as inputs.
- No component but the gate (issuer) and the human (approver) holds a signing/minting primitive; the
  policy authority is a **sensor** (role `domain_authority`), never an actuator.
- Fail-closed everywhere; default (unarmed) path byte-behavior-identical.
- Honest-scope stays mandatory; G5 NOT-MET; the door opens only at the top.
