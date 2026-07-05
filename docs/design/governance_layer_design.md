# Elyon-Sol — Governance-Layer Design & Build Kickoff (corrected)

**Scope:** two features that turn the admission *gate* into a governance *substrate*:
1. **Human oversight** — a `PENDING_APPROVAL` path (out-of-band human approval for
   high-impact actions).
2. **Non-bypassable enforcement** — closing A1 so traffic cannot skip the gate.

**Status:** design. This revision folds in the eight findings of the adversarial design
review (H1–H8; see `docs/design/governance_layer_adversarial_review.md`). Each correction is marked
inline `[FIX H#]`. Build in increments under SESSION_PROTOCOL + VL discipline; canon stays
locked (GR-1). Grounded in `HEAD` = `dcc66dd` (design originally compiled against `c6b4094`,
one commit earlier — no material drift).

> **Provenance of this revision.** The base design is unchanged in intent. The eight `[FIX H#]`
> insertions are the *minimal* design changes named by the review; they do not introduce new
> capability, do not touch canon, and keep both features layered above `G(I)`.

---

## 0. The load-bearing decision (read first): keep `G(I)` two-valued; layer above it

`CANON/canon.md` is locked and SHA-pinned. It enumerates exactly two admissibility states
— `ELIGIBLE` and `REFUSE` — and defines `G(I) ∈ {0,1}`. `evaluator.evaluate()` returns
exactly those two strings.

**Neither feature changes `G(I)`.** Introducing a third *canonical* admissibility value
(`PENDING_APPROVAL`) would be a canon-version event (a new canon hash, supersession of
v0.9.8.4) — out of scope and against the "canon stays locked" discipline (GR-1). So:

- `evaluate()` stays two-valued. `ELIGIBLE` keeps its exact current meaning: *admissible per
  authority (AC³), coverage (T²⁶), and continuity (CCS).*
- The new states live at the **PEP / orchestration layer** — the same layer where `reassert()`
  already returns non-binary outcomes (`REASSERTED` / `INVALIDATED` / `RE-EVALUATE-REQUIRED`)
  without touching `G(I)`. There is precedent for richer states *outside* the core predicate.

Mental model: **`ELIGIBLE` becomes necessary but not sufficient for a high-impact action.**
The gate will only sign+forward a high-impact `ELIGIBLE` call once a valid human approval is
also present.

---

## 1. Feature 1 — Human oversight (`PENDING_APPROVAL`)

### 1.1 Concept

For an operation the policy marks **high-impact**, an `ELIGIBLE` decision is *held* rather
than executed. The gate emits a `PENDING_APPROVAL` response and does **not** sign, log an
issuance, or forward. Execution happens only when the caller re-submits with a valid,
out-of-band **human approval grant**. No grant, or an expired one → the action never runs
(fail-closed, canon §9). This closes the EU AI Act Art 14 / NSA human-approval GAP.

### 1.2 Impact classification — manifest-driven, pinned, never caller-supplied

Add a `HIGH_IMPACT` declaration to `MANIFEST/manifest.json` alongside `AR`/`R`. It is read
from the **SHA-pinned manifest**, never from caller input.

A new pure function `requires_approval(ctx, manifest) -> bool` in `evaluator.py`, derived the
same way `ac3_valid`/`t26_valid` are.

> **[FIX H1] — `HIGH_IMPACT` must be a validated field; absence/malformation fails *closed*,
> never to an empty set.** `safe_manifest()` validates only `AR`/`R`/`version` today, so the
> natural `manifest.get("HIGH_IMPACT", [])` would make a *missing or typo'd* key yield an empty
> high-impact set — silently disabling oversight for the whole deployment (fail-*open*).
> Required design:
> - A `safe_high_impact(manifest)` helper validates the `HIGH_IMPACT` structure (a list of
>   string tokens). Malformed/missing → returns `None` (a sentinel for "cannot prove
>   low-impact"), exactly as `safe_set`/`safe_manifest` return `None` on malformation.
> - `requires_approval()` **defaults to `True` on any doubt**: `None` from `safe_high_impact`,
>   a malformed `ctx`, or any internal error → `True` (require a human). Never `.get(..., [])`.
> - An operator who genuinely wants "nothing is high-impact" must declare an **explicit empty**
>   `HIGH_IMPACT: []` — a conscious, auditable choice — which is distinct from a *missing* key.
> - Revert-catcher: a manifest with `HIGH_IMPACT` removed must make `requires_approval` return
>   `True` (the silent-disable catcher), proven RED on revert.

> **[FIX H2] — the high-impact selector must key only on tokens the caller is *forced* to
> declare truthfully.** Eligibility forces only `AP ⊇ AR` and `OP ⊇ R`. If a `HIGH_IMPACT`
> token is not also a required token (`∈ R`/`AR`), a caller can simply omit it from `OP`,
> escape the high-impact match, and still be `ELIGIBLE` — self-declaring its action
> low-impact. Required design:
> - Every `HIGH_IMPACT` selector token MUST be a member of the manifest's required sets
>   (`R` ∪ `AR`). A `HIGH_IMPACT` token outside `R ∪ AR` is a **manifest error** →
>   `safe_high_impact` returns `None` → `requires_approval` fails closed (`True`).
> - `requires_approval` then matches `HIGH_IMPACT` against the caller's `OP`/`AP` *as already
>   constrained by coverage*: because the caller cannot drop a required token without `REFUSE`,
>   it cannot drop a high-impact token to escape approval.
> - Honest scope (§1.9): this is *token-level* impact. A benign-labelled call that is
>   *semantically* high-impact is out of scope by design (the gate does not judge wisdom).

Default fail-closed: a malformed manifest → treat as requires-approval, never as low-impact.

### 1.3 New PEP flow (where it slots in)

In `pep.governed_call`, **after** `evaluate()` returns `ELIGIBLE` and **before** envelope
signing/issuance/forward:

```
evaluate() == ELIGIBLE
   └─ requires_approval(ctx, manifest)?
        ├─ no  → existing path: build → sign → issuance-log → forward → 200 ELIGIBLE
        └─ yes → is a valid approval grant present on THIS request?
                   ├─ no  → 202 PENDING_APPROVAL  (do NOT sign, do NOT forward,
                   │         do NOT issuance-log a forward; record an approval REQUEST)
                   └─ yes → verify grant (§1.4); valid →
                            existing path (sign → log → forward → 200 ELIGIBLE);
                            invalid → 403 REFUSE (REF_APPROVAL_*)
```

`PENDING_APPROVAL` is **not an admit.** It is a hold.

> **[FIX H6] — the hold must be an explicit early `return`, outside the sign/forward
> try/except.** `pep.governed_call` wraps envelope-build + sign + issuance-log **and** the
> upstream forward in a broad `except Exception → REF_PEP_FAIL_CLOSED (403)`, and
> `post_to_target(...)` is the unconditional tail of the ELIGIBLE block. Two consequences the
> design must prevent:
> - If the 202 hold is *raised* as an exception inside that try, it is converted to a 403
>   (wrong terminal state, muddied audit trail). The hold MUST be a normal response object via
>   an explicit `return`, placed **after** the `requires_approval` check and **before** the
>   envelope/sign/forward try-block.
> - The 202 leg and the approved leg MUST be **mutually exclusive returns**; the approved leg
>   *falls through to the single existing sign+forward* (no second forward). No code path may
>   reach `post_to_target` for a high-impact call that lacked a valid grant.
> - TOCTOU: there is no admit-then-revoke window **iff** the grant is consumed (claimed)
>   atomically *before* `post_to_target` (see [FIX H3]) and the two legs are exclusive returns.
> - Revert-catcher (the design's core ★): high-impact `ELIGIBLE` with no grant → `202` AND
>   `requests.post` is never called.

### 1.4 The approval grant (reuse your own primitives)

Model approval as a small signed object — an **"approval grant"** — using the same Ed25519
machinery as the envelope, but with a **separate approver identity**.

> **[FIX H4] — bind to `decision_sha256`; drop the "or interaction hash" disjunction; add
> gate-side pending-state for request identity.** `decision_sha256` is deliberately
> issuance-invariant (it excludes `decision_id`, `not_after`, `timestamp_utc`, issuer fields),
> so two issuances of the *same* high-impact action have an *identical* `decision_sha256`.
> Required design:
> - The grant signs over **`decision_sha256`** specifically. This transitively binds
>   `target_url`, `AP`, `OP`, `context`, and the manifest pins, because all of those are inside
>   `decision_sha256`'s hashed region. (`target_url` is a top-level field NOT inside
>   `normalized_interaction`, so an "interaction content hash" would *not* bind it — the "or"
>   branch in the original design is removed, as is the redundant separate `context.args_sha256`.)
> - Because `decision_sha256` is issuance-invariant, single-*request* binding cannot rest on it.
>   The gate keeps **server-side pending-state**: the 202 issues an `approval_request_id` into an
>   unconsumed set; the grant signs that `approval_request_id`; on resubmit the gate verifies
>   `grant.decision_sha256 == recomputed decision_sha256 of THIS request` **and**
>   `grant.approval_request_id ∈ pending-and-unconsumed`, then **atomically consumes** it.
> - This is what closes "approval of A authorizes B / different args / different target /
>   different request": A→B and arg/target changes change `decision_sha256` (reject on binding);
>   request-replay is caught by the consumed-set.

- **Separate APPROVER key.** A distinct key (`ELYON_APPROVER_*`), NOT the gate signing key.

> **[FIX H5] — SoD is a custody invariant, not a key-id string compare.**
> `approver_key_id != gate_key_id` rejects only the trivial same-id case; it does not stop the
> gate minting its own approval under a different key_id if it holds the approver private key or
> controls the approver-key trust source. Required design:
> - **Custody:** the approver *private* key is NEVER resolvable by the gate process. Mirror
>   `_get_signing_key`'s "never in the repo/env" rule: the gate holds only the approver *public*
>   key, for verification. (A deployment proof must show the gate cannot read the approver
>   private key.)
> - **Provenance + role:** the approver public key flows through the **existing signed
>   key-record / root-record chain** (`key_record_source` / `root_record_source`) with an
>   explicit `approver` role distinct from `issuer`. SoD is enforced as **role-distinctness in
>   the signed record**, not a key_id string. `approver_key_id != gate_key_id` is retained as a
>   cheap belt-and-braces check, not the guarantee.

- **Bound to the exact action.** Via `decision_sha256` (see [FIX H4]).
- **Bound to one request.** Carries the `approval_request_id` the gate issued with the 202,
  tracked in gate-side pending-state (see [FIX H4]).
- **Fresh + single-use.**

> **[FIX H7] — grant freshness reuses the proven primitive; consumed-but-not-forwarded is
> fail-closed-by-design.** The grant gets its own `not_after` (approval freshness), independent
> of the decision's 300 s window. Required design:
> - Grant freshness uses the **exact** checks `verify_envelope` already applies to a decision's
>   `not_after`: tz-aware required (naive → REFUSE), `current >= not_after + clock_skew` →
>   REFUSE, same `clock_skew` config. Do not re-implement.
> - Consumption (claim) happens *before* the forward; a forward that then fails leaves a
>   **consumed-but-not-forwarded** grant → the human must re-approve. This is fail-closed by
>   design (availability traded for never-double-executing), recorded as honest scope.

> **[FIX H3] — single-use is mandatory-id, shared-under-scale, and is the *only* barrier to
> one-approval→N-executions.** Each approved resubmit mints a *new* `decision_id` and a fresh
> 300 s window, so the target's `decision_id` de-dup will NOT catch a grant replayed at the
> gate (different `decision_id` each time). The gate is also stateless today (`pep.py` imports
> no replay cache). Required design:
> - Grant single-use is keyed on a **mandatory `grant_id`** — a grant lacking it is REFUSED.
>   Never the `executor_sdk` `if id is not None: claim` pattern (an absent id there *skips* the
>   check); an id-less grant must fail closed, not bypass.
> - The gate consumes the grant via the existing `ReplayCache` seam, claimed **atomically
>   before** the forward.
> - Under horizontal scaling the gate MUST use the **shared** `ExternalStoreReplayCache`; reuse
>   `replay_cache_from_env`'s R-02 guard so a multi-instance gate without a shared store
>   **refuses to start** rather than handing each instance a per-process cache that honors the
>   same grant once.
> - Honest scope: single-use holds across instances only with a shared store.

New module `IMPLEMENTATION/approval.py`: `build_grant()`, `sign_grant()`, `verify_grant()`
— mirroring `envelope.py` so it reuses, not re-implements, the crypto.

### 1.5 The human surface (out-of-band, deliberately minimal)

- A tiny **approver CLI/endpoint** (separate process, separate key, per [FIX H5] custody) that
  shows the pending request (decision content + args) and, on a human's action, emits a signed
  grant.
- The caller re-submits `/governed-call` with the grant attached (header or body field).

The gate never decides approval; it only *verifies* a grant a human authorized.

### 1.6 States, HTTP, audit

- `200` `{decision: ELIGIBLE}` — approved (or not high-impact) and forwarded.
- `202` `{terminal_state: PENDING_APPROVAL, approval_request_id, decision_sha256}` — held.
- `403` `{terminal_state: REFUSE, refusal_reason_code: REF_APPROVAL_*}` — bad/expired/forged
  grant, replayed grant, unknown request_id, or SoD/role violation.

> **[FIX H8] — the audit trail must record held-request + grant-consumption, and reconcile must
> check them.** `issuance_log` records only signed ELIGIBLE *forwards*; without held-request and
> grant-consumption records in the *same* reconcilable log, the §1.6 guarantee ("no high-impact
> forward without a recorded human grant") has nothing to check against. Required design:
> - Extend the issuance-log schema + `envelope_inspector reconcile`