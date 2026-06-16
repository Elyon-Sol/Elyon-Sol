# Cross-model verification request - OPA sidecar (VL-104/105)

This is a verification request prepared under the procedure established in
`EVIDENCE/verification_ledger.md` entry VL-008.

Read this entire document before doing the task. Read the "Procedure"
section twice. The procedure is load-bearing: a response that deviates from
it carries no verification weight, regardless of its conclusions.

---

## What you are being asked to do

Classify each of the numbered claims below. Each claim is a statement about
the behavior of the attached implementation, test, and deployment files for
the Elyon-Sol ext-authz "admissibility sidecar". For each claim, determine -
from the attached files only - whether the code supports it, contradicts it,
or leaves it under-specified. The output shape is a per-claim classification
table plus divergence notes.

The verification IS: does each claim hold of the attached files? It is NOT
an evaluation of whether the sidecar, the tests, or the deployment are
well-designed, and it is NOT a judgment about anything the files do not
themselves determine.

---

## Primary sources attached

Under verification (load-bearing):

- `authz_sidecar.py` - the ext-authz sidecar. Load-bearing for CA-*.
- `test_authz_sidecar.py` - the adversarial test suite. Load-bearing for CT-*.
- `gen_certs.py` - TLS cert tooling. Load-bearing for CD-1.
- `test_authz_sidecar_tls.py` - TLS handshake test. Load-bearing for CD-2.
- `authz_sidecar_tls_001_runner.py` - real-loopback-TLS proof runner.
  Load-bearing for CD-3.
- `docker-compose.authz.yml`, `docker-compose.authz.tls.yml`,
  `envoy.example.yaml` - Mode A + TLS deployment. Load-bearing for CD-4, CD-5.
- `ci.yml` - the CI workflow. Load-bearing for the CD-3 skip clause.

Secondary (cited by claims, not themselves under verification):

- `executor_sdk.py` - `ExecutorGate` / `Decision`; what the sidecar wraps.
- `verifier.py` - `verify_envelope`, the `REF_VERIFY_*` vocabulary.
- `reference_target.py` - `REF_TARGET_NOT_CONFIGURED` /
  `REF_TARGET_ANCHOR_MISMATCH` and the `config_from_env` pattern.
- `replay_cache.py` - the `ReplayCache` seam and `replay_cache_from_env`.
- `opa_sidecar_design.md` - the design the build implements (the source of
  the normative statements the claims restate).

---

## Procedure (VL-008)

Three rules govern this verification. All three must hold or the response is
discarded:

(a) **Scope-bound to primary sources.** Your work may use only the attached
    files. Material from anywhere else - your training data about Elyon-Sol,
    prior conversation history, the project's GitHub, general knowledge of
    FastAPI, Envoy, OPA, TLS, or software engineering - is OUT OF SCOPE.

(b) **Scope-adherence is checkable.** At the end of your response, include a
    section titled "Scope check" listing every concept, term, or claim used
    in your work. For each one, cite which attached file it comes from and
    which function/section within that file. If any item cannot be cited to
    an attached file, name it explicitly as out-of-scope and remove it from
    your work.

(c) **Prior project exposure is permitted** if (a) and (b) hold. You may
    have seen Elyon-Sol material before. That does not disqualify you. What
    disqualifies the response is referencing material not derivable from the
    attached files, even if true.

The variable that matters is task-to-source binding, not memory cleanliness.

---

## The claims

Sidecar behavior (`authz_sidecar.py`):

- **CA-1**: The module contains no independent admissibility or cryptographic
  logic. It computes no signature check, no AP/OP set comparison, no
  reassert/currency check of its own; every accept/deny decision returned to
  the caller is the `Decision` produced by `ExecutorGate.check`, which it
  imports.
- **CA-2**: The only refusal codes the module itself names are
  `REF_TARGET_NOT_CONFIGURED` and `REF_TARGET_ANCHOR_MISMATCH`, both imported
  from `reference_target`. It defines no new `REF_*` constant. Every other
  DENY reason placed on the response is the reason string carried by the
  gate's `Decision`, surfaced unchanged.
- **CA-3**: The decision endpoint is fail-closed. `config_provider()`
  returning None yields HTTP 403 with `REF_TARGET_NOT_CONFIGURED`; any
  exception raised inside the handler is caught and converted to HTTP 403
  DENY (`REF_TARGET_ANCHOR_MISMATCH`). No code path returns a 5xx, and none
  returns 200/ALLOW on an error.
- **CA-4**: An absent or unparseable `X-Elyon-Sol-Envelope` header is treated
  as `envelope=None` (not an error), which `ExecutorGate.check` /
  `verify_envelope` refuse as `REF_VERIFY_ENVELOPE_ABSENT` (the un-attested
  path).
- **CA-5**: The default interaction extractor reads the
  `X-Elyon-Sol-Interaction` header (canonical-JSON) and returns the parsed
  dict, or None on an absent / unparseable / non-dict value. The extractor is
  an injectable parameter; no declarative "CUSTOM" interaction-mapping format
  is implemented in this module.
- **CA-6**: On accept the response is HTTP 200 with header
  `x-elyon-decision: ALLOW`; on refuse it is HTTP 403 with
  `x-elyon-decision: DENY` and `x-elyon-reason: <code>`.
- **CA-7**: The replay cache is created once per app (`app.state.replay_cache`)
  and shared by every per-request `ExecutorGate` (passed as
  `request.app.state.replay_cache`), so a `decision_id` honored on one request
  is refused on a later request to the same app. The cache is injectable, so
  two app instances sharing one cache refuse a cross-instance replay.
- **CA-8**: `config_from_env()` returns None (the fail-closed signal) if any
  of `ELYON_TARGET_URL`, `ELYON_RECORD_PATH`, `ELYON_PINNED_ROOT_SHA256`,
  `ELYON_GATE_KEY_ID`, `ELYON_GATE_PUBLIC_KEY_HEX` is absent, if the record
  file is unreadable, if the public-key hex is malformed, or if
  `ELYON_CLOCK_SKEW_SECONDS` is non-numeric or negative.
- **CA-9**: Build-then-wire holds: nothing in the attached files imports
  `authz_sidecar`, and the module defines its own app at import time without
  modifying any other module's behavior. (Classify Under-specified if the
  attached set does not determine whether an unattached module imports it.)
- **CA-10**: The handler is registered on both `/authz` and
  `/authz/{rest:path}`, and the decision is computed from request headers
  only - the request path does not enter the decision. A separate `GET
  /healthz` returns `{"status": "ok"}` and reports no configuration or trust
  state.

Test coverage (`test_authz_sidecar.py`):

- **CT-1**: The suite asserts ALLOW (200, `x-elyon-decision: ALLOW`) on a
  valid attested request, and a distinct DENY (403) with the specific
  `x-elyon-reason` for each refusal class: absent and unparseable-absent
  (`REF_VERIFY_ENVELOPE_ABSENT`), forged signature
  (`REF_VERIFY_SIGNATURE_INVALID`), replay (`REF_VERIFY_REPLAY`), rebind and
  target-swap (`REF_VERIFY_BINDING_MISMATCH`), stale
  (`REF_VERIFY_SIGNATURE_EXPIRED`), and record-drift
  (`REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED`).
- **CT-2**: The suite asserts fail-closed on unconfigured
  (`REF_TARGET_NOT_CONFIGURED`) and wrong-anchor (`REF_TARGET_ANCHOR_MISMATCH`)
  config, and that `config_from_env` with the relevant env vars unset returns
  None.
- **CT-3**: The cross-instance replay test builds two sidecar apps that share
  one injected `InMemoryReplayCache` and asserts the second instance refuses
  (`REF_VERIFY_REPLAY`) a `decision_id` the first instance honored.
- **CT-4**: The envelopes exercised by the suite are produced by the real gate
  (`pep`) signed by the conftest key; the tests do not stub or replace
  `verify_envelope` / `ExecutorGate` - the production gate is the acceptance
  authority under test.

Deployment and TLS (`gen_certs.py`, the TLS test/runner, the compose/Envoy
files, `ci.yml`):

- **CD-1**: `gen_certs.py` `SERVICES` includes `elyon-authz`, so
  `write_deployment_certs` emits `elyon-authz.crt` / `elyon-authz.key` whose
  SAN covers `elyon-authz`, `localhost`, `127.0.0.1`, and any extra hostnames
  passed; the gate/target/publisher leaves are otherwise unchanged.
- **CD-2**: `test_authz_sidecar_tls.py` drives a strict (`VERIFY_X509_STRICT`)
  in-memory MemoryBIO TLS handshake with the `elyon-authz` leaf that SUCCEEDS
  against the dev CA and is REFUSED against a different CA, using no sockets or
  processes.
- **CD-3**: `authz_sidecar_tls_001_runner.py` serves the production sidecar on
  a real uvicorn TLS socket and asserts ALLOW (200) for a gate-minted envelope
  and DENY (403) for a tampered one over an HTTPS client that verifies the CA,
  exiting 0 on that outcome; `ci.yml` excludes it from the proof-runner loop
  via an `*authz_sidecar_tls*` skip clause.
- **CD-4**: `docker-compose.authz.tls.yml` serves `elyon-authz` via `uvicorn
  --ssl-certfile/--ssl-keyfile` with the `elyon-authz` leaf and mounts the
  cert directory; it changes only the command/volumes for that service and
  introduces no change to the gate/target/publisher service definitions.
- **CD-5**: `envoy.example.yaml` defines two ext_authz HTTP filters in order -
  `elyon-authz` first, OPA second - each with `failure_mode_allow: false`, and
  the router last; a request that fails either filter is denied, and only a
  request that passes both is routed to the upstream cluster.

---

## What "classify" means (and what it does not mean)

Classify MEANS: for each numbered claim, read the relevant code and assign
exactly one outcome category below, citing the specific functions, lines, or
clauses (file + location) that ground the assignment.

Classify DOES NOT MEAN:

- "Tell me whether the sidecar or tests are good." That is code review, not
  classification. Verdicts carry no verification weight under VL-008.
- "Suggest improvements." Out of scope; the task is classify, not co-design.
- "Compare with how other ext-authz adapters do this." Out of scope; only the
  attached files are in scope.
- "Re-run the tests or the TLS proof." You are classifying what the test and
  runner files ASSERT, from reading them - not executing them.
- "Re-derive the claims list." The claims above are the fixed object of this
  round; if a claim misquotes the code, classify it Reframing required and say
  what the code actually does.

---

## What outcome means what

Each claim receives exactly one of:

- **Supported.** The attached code does what the claim says, and you can cite
  the function/lines that do it.
- **Contradicted.** The attached code demonstrably does something the claim
  excludes, or fails to do something the claim requires; cite the
  contradicting code.
- **Under-specified.** The attached files neither clearly support nor
  contradict the claim (e.g., the claim depends on whether an unattached
  module imports the sidecar); name exactly what is missing.
- **Reframing required.** The claim as stated is ambiguous, ill-formed, or
  misquotes the code; name the reformulation and classify the reformulated
  claim. Do not silently substitute a different question.

These are classification outcomes, not verdicts on the artifacts or the
project. All listed outcomes are useful; only a procedure violation under
VL-008 (a) or (b) is a failure of the verification.

Status implications (for the future ledger entry, not for the verifier):
VL-104 and VL-105 are currently RECORDED single-source. Every claim Supported
by two independent procedurally-clean runs transitions the corresponding
build to CONFIRMED; any Contradicted claim transitions it to DISPUTED pending
correction; Under-specified claims become named gap candidates without
blocking CONFIRMED status for the rest.

---

## What you do NOT need to address

- Whether the two-VM cross-host test (`VM_TLS_TEST.md`) was actually run on
  real hosts. That is the author's execution and is out of scope; CD-3 is
  about what the in-sandbox runner file asserts, nothing more.
- The canon, the manifest, the gap tracker, STATE.md, or the ledger.
- The design document's "good idea / bad idea" merits; it is attached only as
  the source of the normative statements the claims restate.
- Any file not on the attached list - speculating about it is out of scope.

---

## Submission format

Respond in this structure, in this order:

```
## Classification table

[One row per claim, CA-1 through CD-5: claim ID, outcome category, one
sentence ground citing file + function/section.]

## Divergence notes

[One short paragraph per claim NOT classified Supported, explaining the
contradiction, the missing determinant, or the reformulation. "None" if all
claims are Supported.]

## Scope check

[For every concept, term, or claim used above, cite which attached file and
which function/section it comes from. Name any item that cannot be cited as
out-of-scope and remove it from the work above.]
```

Do not include sections beyond these. Do not rate, review, or suggest. Do not
reference any artifact you are not being shown.

---

## Attached files

- `authz_sidecar.py`
- `test_authz_sidecar.py`
- `executor_sdk.py`
- `verifier.py`
- `reference_target.py`
- `replay_cache.py`
- `gen_certs.py`
- `test_authz_sidecar_tls.py`
- `authz_sidecar_tls_001_runner.py`
- `docker-compose.authz.yml`
- `docker-compose.authz.tls.yml`
- `envoy.example.yaml`
- `ci.yml`
- `opa_sidecar_design.md`

If any file is missing or appears truncated, stop and say so. Do not work
from a partial source.

---

## Ledger context (informational, not part of the task)

This request was executed against three independent verifiers; the
adjudication is ledger entry VL-106. Two procedurally-clean runs (Grok,
OpenAI) classified the claims unanimously (18/19 Supported, CA-9
Under-specified, 0 Contradicted); a third run (Gemini) was discarded under
VL-008 rule (b) for fabricated citations. The verbatim responses are at
`EVIDENCE/verification_runs/vl106_{grok,openai,gemini}_response.md`. The
result transitions the VL-104/105 sidecar claim set to CONFIRMED at
CONFORMANCE scope (faithful-to-design); it is internal conformance evidence,
NOT external validation, and G5 is unchanged.
