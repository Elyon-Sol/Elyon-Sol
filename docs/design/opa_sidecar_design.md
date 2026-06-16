# OPA sidecar / admissibility ext-authz adapter — design (DRAFT)

Status: DRAFT for review. Not yet ledgered (does not carry a VL entry; if adopted it
should enter the normal build-then-wire + ledger discipline). Grounded in the shipped
verifier interface — IMPLEMENTATION/verifier.py `verify_envelope(...)` and
IMPLEMENTATION/executor_sdk.py `ExecutorGate.check(envelope, interaction) -> Decision`.
Introduces NO new admissibility logic and NO new cryptography; it is a transport adapter
that makes the existing verifier consumable by an OPA/Envoy deployment without the user
writing Python.

IP note: this is a conventional ext-authz integration adapter over the already-filed
verification method (Provisional 64/088,457). Likely not separately patentable (standard
Envoy/OPA wiring), but confirm with counsel before publishing if you intend to claim it.
Keep this draft private until that check.

---

## 1. The gap it closes
Today an OPA-downstream user must write Python glue: import `ExecutorGate`, reconstruct
the interaction, call `.check()`, and compose the result with their OPA decision. There is
no drop-in. This adapter turns "write glue" into "run a sidecar container + add an Envoy
filter," which is the idiom OPA shops already use (OPA-Envoy / ext-authz).

## 2. What it is
A thin HTTP service ("elyon-authz") that:
- receives an authorization check for an incoming request,
- reconstructs the canonical interaction tuple from that request,
- calls the production `verify_envelope` / `ExecutorGate.check` (no re-implementation),
- returns ALLOW (200) or DENY (403) with the existing REF_VERIFY_* / REF_TARGET_* reason
  code,
- fails closed on any error.

It is the `reference_target.py` consume-path (read X-Elyon-Sol-Envelope header -> anchor
check -> verify_envelope -> honor/refuse) refactored from "a target that acts" into "an
authorizer that answers allow/deny," so it can sit in front of ANY target, including one
that is OPA-gated.

## 3. Where it sits (composition with OPA)
Elyon-Sol answers a different question than OPA: "is this interaction admissible to be
considered at all?" (authority/coverage/integrity + attestation) vs OPA's "does policy
permit it?" They compose as an ordered, fail-closed chain — admissibility BEFORE policy:

    client -> Envoy
                |-- ext_authz #1: elyon-authz  (admissibility + envelope attestation)
                |       deny -> 403, stop
                |-- ext_authz #2: opa-envoy    (policy)
                |       deny -> 403, stop
                -> upstream service (acts)

Two supported modes:
- MODE A (recommended): two ext_authz filters in the Envoy chain — elyon-authz first, OPA
  second. Clean separation; each layer independently fail-closed; neither imports the
  other.
- MODE B (combined): elyon-authz optionally forwards an allowed request to an OPA endpoint
  and ANDs the verdicts, returning allow only if BOTH allow. Use when the deployment has no
  Envoy filter chain (e.g., a single middleware hook).

## 4. The decision contract (HTTP)
Request to the sidecar (Envoy ext_authz HTTP, or any caller):
- Method/path/headers of the original request are provided by Envoy ext_authz, OR a caller
  POSTs a check body.
- Required inputs the sidecar needs to verify:
  - the envelope: from the `X-Elyon-Sol-Envelope` header (canonical-JSON).
  - the live interaction: reconstructed (see section 5).
  - the target identity (`target_url`): the route/authority the request is bound for.

Response:
- 200 with header `x-elyon-decision: ALLOW` on accept.
- 403 with header `x-elyon-decision: DENY` and `x-elyon-reason: <REF_*>` on refuse.
- 403 + `REF_TARGET_*` on any internal/anchor/parse error (fail closed — never 5xx-allow).

This mirrors verify_envelope's accept/reason dict and the reference target's 200/403.

## 5. Interaction reconstruction (the load-bearing design point)
The binding check requires the live interaction to equal what the envelope was admitted
for. The sidecar must derive the SAME normalized interaction (AP, OP, context, pinning
fields) from the incoming request. A pluggable "interaction extractor":
- DEFAULT (attested-forward): the upstream gate (pep.py) already normalized and forwarded
  the interaction; the sidecar reads it from a structured header set by the gate
  (e.g. `X-Elyon-Sol-Interaction`, canonical-JSON) and verifies the envelope binds to it.
  Zero per-deployment mapping.
- CUSTOM (gate-less / direct): for deployments where requests are not pre-normalized, a
  declarative mapping config translates request attributes (method, path, claims, headers)
  to AP/OP/context. This mapping is deployment-specific and is the one piece the user
  authors — documented, not code.

Normalization MUST reuse request_validator's dedupe+sort so the binding comparison is
byte-identical to issuance (parity, not re-implementation).

## 6. Trust material & config (env-driven, parity with *_from_env)
Reuse the existing seam patterns (issuance_log_from_env / replay_cache_from_env):
- `ELYON_PINNED_PUBLIC_KEYS` / key-record source -> verify_envelope `pinned_public_keys`
  / `key_record_view`.
- `ELYON_RECORD_SOURCE` (published-record URL or path) -> `record_source`; anchor pinned
  via `ELYON_PINNED_ROOT_SHA256`.
- `ELYON_REPLAY_*` -> the shared ReplayCache seam (exactly-once across sidecar replicas).
- `ELYON_CLOCK_SKEW` -> verify_envelope `clock_skew`.
No secrets in the image; all injected as env/secrets, same as deploy/.

## 7. Deployment
- Package: a small container (FastAPI, reusing the stack already in pep.py) exposing the
  ext_authz endpoint. Add to deploy/ as `elyon-authz` service + an Envoy example config
  with the two-filter chain (Mode A).
- Stateless except the replay claim, which goes to the shared store (ReplayCache external
  mode) so multiple sidecar replicas share one replay domain.

## 8. Fail-closed semantics (unchanged invariant)
Every failure -> DENY: missing/unparseable envelope, anchor mismatch, signature/key/root
failure, reassert RE-EVALUATE-REQUIRED, binding mismatch, replay, stale record, missing
config, internal exception. The sidecar never fails open. (Same posture as verify_envelope
+ reference_target; DoS is conceded by design.)

## 9. What it reuses vs adds
- REUSES: verify_envelope (the whole chain), ExecutorGate.check, ReplayCache seam,
  record/key/root sources, request normalization, the REF_* vocabularies, transport.py.
- ADDS: an HTTP ext_authz envelope (request <-> check contract), the interaction extractor
  (default header-read + optional declarative mapping), an Envoy example config, and a
  container. No crypto, no admissibility logic, no new invariant.

## 10. Scope, limits, open questions
- Language-agnostic only at the HTTP boundary: the app needs Envoy (or any middleware that
  speaks ext_authz). Non-Envoy stacks use Mode B via a single HTTP call.
- The CUSTOM interaction mapping is deployment-specific and is the user's authored piece;
  the DEFAULT (gate-forwarded interaction) needs no mapping.
- Not built or tested yet. Build-then-wire: ship the sidecar + tests defaulting off, with
  an Envoy example, before claiming the integration.
- Open: whether to also emit the verdict as OPA external-data (so Rego can reference it)
  in addition to the ext_authz chain — a third mode, deferred.

## 11. Build plan (next)
1. `IMPLEMENTATION/authz_sidecar.py` — FastAPI ext_authz endpoint wrapping ExecutorGate;
   header-read interaction extractor (default).
2. Tests: allow on valid attested request; deny on each REF_* class; fail-closed on bad
   config; replay across two sidecar instances via shared store.
3. `deploy/elyon-authz` + `deploy/envoy.example.yaml` (Mode A two-filter chain).
4. Declarative mapping format for CUSTOM mode (+ tests).
5. Ledger it (VL entry) once verified; then it's a real, citable integration.
