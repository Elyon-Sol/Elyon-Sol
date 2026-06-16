# OPA sidecar build — clean-context kickoff

Purpose: bootstrap a NEW session to build the OPA ext-authz sidecar in isolation, grounded
in the repository (not in any prior conversation). This file is the continuity layer for
that work — read it and the cited sources first; do not rely on chat history. Mirrors the
SESSION_PROTOCOL resume discipline (task-to-source binding, VL-008).

---

## 0. Objective (one sentence)
Build a thin HTTP ext-authz "admissibility sidecar" that wraps the SHIPPED verifier so an
OPA/Envoy deployment can enforce Elyon-Sol envelope admissibility without writing Python —
reusing verify_envelope / ExecutorGate, adding no new admissibility logic and no crypto.

## 1. Read first (primary sources — do not skip, do not summarize from memory)
1. docs/design/opa_sidecar_design.md   — the design this build implements (authoritative).
2. IMPLEMENTATION/verifier.py          — verify_envelope(envelope, interaction, target_url,
   record_source, pinned_public_keys, now, key_record_view, clock_skew) -> {ok/accept, reason}.
3. IMPLEMENTATION/executor_sdk.py      — ExecutorGate.check(envelope, interaction) -> Decision(honored, reason).
4. IMPLEMENTATION/reference_target.py  — the consume-path being refactored into an authorizer
   (header read -> anchor check -> verify_envelope -> 200 honor / 403 refuse).
5. IMPLEMENTATION/request_validator.py — interaction normalization (dedupe+sort) to reuse.
6. IMPLEMENTATION/replay_cache.py + issuance_log.py — the *_from_env seam pattern to copy.
7. STATE.md + EVIDENCE/verification_ledger.md (tail) — current state + ledger discipline.

## 2. Scope
IN: an HTTP ext-authz endpoint wrapping ExecutorGate; default header-read interaction
extractor; env-driven trust/config (parity with *_from_env); Envoy two-filter example
(Mode A); tests; fail-closed everywhere.
OUT (named, not built now): the declarative CUSTOM interaction-mapping format (phase 4);
OPA external-data mode (deferred); any change to verify_envelope, evaluator, envelope, or
the crypto; any live-host run (that is the separate G5 track).

## 3. Guardrails (do not violate)
- REUSE only. No re-implementation of admissibility or signature logic. If you find
  yourself writing crypto or set-logic, stop — call the existing function.
- Build-then-wire: the sidecar ships defaulting OFF; no existing default path changes
  byte-behavior. Parity with VL-074/076/078/099.
- Fail-closed: every error/missing-config/exception -> DENY (403 + REF_*). Never fail open,
  never 5xx-as-allow.
- Reuse the REF_VERIFY_* / REF_TARGET_* reason vocabularies; introduce no new refusal codes
  unless the design names one.
- Normalization must be byte-identical to issuance (reuse request_validator helpers).
- ASCII, LF, type hints, pytest — match the existing code conventions.

## 4. Build order (from design section 11) with acceptance per step
1. IMPLEMENTATION/authz_sidecar.py — FastAPI ext-authz endpoint wrapping ExecutorGate;
   default extractor reads the gate-forwarded interaction from a structured header.
   ACCEPT: returns ALLOW(200)/DENY(403 + reason) over verify_envelope; no gate logic
   duplicated (it imports ExecutorGate/verify_envelope).
2. TESTS/adversarial/test_authz_sidecar.py — allow on a valid attested request; deny on
   each REF_* class (absent / forged / replay / rebind / target-swap / stale / drift);
   fail-closed on bad/missing config; replay shared across two sidecar instances via the
   external ReplayCache.
   ACCEPT: full suite green; existing suite unchanged in count except the new tests.
3. deploy/elyon-authz (container) + deploy/envoy.example.yaml — Mode A two-filter chain
   (elyon-authz then opa-envoy). ACCEPT: documented stand-up; config validates.
4. Declarative CUSTOM interaction-mapping format + tests (gate-less deployments).
5. Ledger it (append a VL entry) once verified in-container; THEN it is a citable
   integration. Update STATE.md Next-open-action per CLOSE PROTOCOL.

## 5. Anti-drift instructions (for the model in the new session)
- Answer and decide from the FILES, re-reading them; do not trust any narrative about what
  the code does. If a claim can't be traced to a file+line, treat it as unverified.
- For any "is this design right" judgment, re-derive from the sources above or spawn a
  fresh-eyes subagent; do not smooth toward agreement.
- If the design doc and the code disagree, the CODE wins — flag the discrepancy, don't
  paper over it.

## 6. IP / publication note
This is a conventional ext-authz adapter over already-filed verification (Provisional
64/088,457). Likely not separately patentable, but do not publish the repo/sidecar before
counsel confirms coverage (open task #13/#14 in the main plan). Keep build artifacts in the
repo (private) until then.

## 7. Definition of done
Sidecar + tests green in-container; Envoy example present; build-then-wire (default path
byte-unchanged); VL entry appended; STATE.md updated. At that point the "upstream of OPA"
claim is shipped, not just positioned — and it is the concrete artifact to bring to a first
OPA-shop design partner.
