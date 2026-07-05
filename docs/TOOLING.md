# Elyon-Sol - Functional tooling inventory (VL-101)

One page: every functional tool in the framework, what it does, and how
it is invoked. This is an INDEX, not a source of truth - each entry
names its spec (docs/restructure/NN) and/or ledger increment (VL-NNN);
behavior claims live there and in the code. Orientation order for a new
reader: `STATE.md` -> `EVIDENCE/verification_ledger.md` -> this page.

Conventions used below: run everything from the repository root;
`python -m ...` invocations assume the suite's environment (Python 3,
fastapi/httpx/cryptography per CI); test counts are never stated here
(G1 discipline - `STATE.md` + the latest VL entry are the count of
record).

---

## 1. The gate (production decision chain)

| Tool | What it does | Invocation |
|---|---|---|
| `IMPLEMENTATION/pep.py` | The HTTP admission gate: schema validation -> `evaluate()` -> signed envelope -> push to target. Fail-closed at every layer. (Specs: SPEC/request_schema.md, artifact 05; VL-019/029/047/065/099) | `uvicorn IMPLEMENTATION.pep:app` ; env: `ELYON_SIGNING_KEY_HEX` + `ELYON_SIGNING_KEY_ID` (required to admit), `ELYON_DECISION_MAX_AGE_SECONDS` (default 300), `ELYON_ISSUANCE_LOG_PATH` (optional, VL-099) |
| `IMPLEMENTATION/evaluator.py` | AC^3 / T^26 / manifest-integrity condition functions + `evaluate()` over `MANIFEST/manifest.json`. (Canon 11.7-11.9) | library; self-check: `python -m IMPLEMENTATION.evaluator` |
| `IMPLEMENTATION/request_validator.py` | Wire-shape validator; the seven `REF_SCHEMA_*` refusal codes. (SPEC/request_schema.md; VL-018) | library (called by pep.py) |
| `IMPLEMENTATION/envelope.py` | `build_envelope` / `sign_envelope` / `reassert` - the admissibility envelope and canonical CCS reassertion. (Artifact 05; VL-029/040/041/066) | library |
| `IMPLEMENTATION/verifier.py` | `verify_envelope`: signature -> currency -> binding; the `REF_VERIFY_*` vocabulary's canonical home. (Artifact 08; VL-037/040/042/075) | library |
| `IMPLEMENTATION/transport.py` | TLS-aware HTTP seam for the gate push and record fetch (CA bundle / client cert config). (Artifact 12 step 1) | library; env per artifact 12 |

## 2. Target side (executors)

| Tool | What it does | Invocation |
|---|---|---|
| `IMPLEMENTATION/reference_target.py` | Deployable enforcing target: verifies envelopes (signed mode: pinned publisher key + fresh signed record), exactly-once via the replay cache, acts only on accept; `/received` observability. (Artifact 12 step 4; VL-061/066/091/094) | `uvicorn IMPLEMENTATION.reference_target:app` ; env per `deploy/runbook.md` (incl. `ELYON_PUBLISHER_URL`, `ELYON_TARGET_URL`, `ELYON_REPLAY_REDIS_URL`) |
| `IMPLEMENTATION/executor_sdk.py` | `ExecutorGate.check(envelope, interaction) -> Decision` - the whole executor sequence (record + verify + replay) in one component for integrators. (Artifact 18; VL-078) | library |
| `IMPLEMENTATION/replay_cache.py` | The exactly-once seam: `InMemoryReplayCache` / `ExternalStoreReplayCache` / `RedisReplayStore` + `replay_cache_from_env()`. (Artifact 16/24; VL-076/094) | library; env: `ELYON_REPLAY_REDIS_URL` |
| `IMPLEMENTATION/mcp_server.py` | Real MCP server (JSON-RPC 2.0 / stdio) with the admissibility gate on `tools/call` - a tool fires once or not at all. (Artifact 17; VL-077) | `python -m IMPLEMENTATION.mcp_server` (stdio; see artifact 17) |

## 3. Trust records (publish + read)

| Tool | What it does | Invocation |
|---|---|---|
| `IMPLEMENTATION/publisher.py` | Standing publisher service for the published hash record (the cross-host currency source). (Artifact 12 steps 2-3) | `uvicorn IMPLEMENTATION.publisher:app` |
| `IMPLEMENTATION/published_source.py` | Byte-anchored published-record reader (pinned sha over record bytes). (VL-039) | library |
| `IMPLEMENTATION/published_record_source.py` | SIGNED published-record reader with freshness (`not_after` + monotonic serial; `REF_VERIFY_PUBLISHED_RECORD_*`). (Artifact 14; VL-074/091) | library |
| `IMPLEMENTATION/key_record_source.py` | Signed issuer-key record reader (revocation / validity windows; `REF_VERIFY_KEY_*`). (Artifact 09; VL-042) | library |
| `IMPLEMENTATION/root_record_source.py` | Signed root-record reader (root retire/revoke; `REF_VERIFY_ROOT_*`). (Artifact 11; VL-044) | library |
| `EVIDENCE/published_hashes_gen.py` / `published_hashes_signed_gen.py` / `published_keys_gen.py` / `published_roots_gen.py` | Generators for the published record (plain and signed), the key record, and the root record. | `python EVIDENCE/<gen>.py` (see each header) |
| `IMPLEMENTATION/readiness.py` + `EVIDENCE/readiness.json` | Readiness predicates: every TRUE flag must name a proof; the suite enforces it. (Artifact 10; VL-083 `REAL_TRANSPORT`) | library + JSON (validated by the suite) |

## 4. Audit layer (the envelope evaluation ladder)

| Tool | What it does | Invocation |
|---|---|---|
| `IMPLEMENTATION/envelope_inspector.py` | The ladder over a minted envelope: shape (`inspect`) -> provenance (`verify_issuer`) -> currency (`reassert`, called directly) -> semantics (`reevaluate`) -> log completeness (`reconcile`). Exit code = audit verdict. (Specs 26/27; VL-097/098) | `python -m IMPLEMENTATION.envelope_inspector inspect <env.json> [--keys keys.json] [--record record.json]` ; `... reevaluate <env.json>` ; `... reconcile --issued issued.jsonl --executed executed.jsonl [--keys keys.json]` |
| `IMPLEMENTATION/issuance_log.py` | Gate-side issuance log: one canonical JSONL line per signed ELIGIBLE envelope; the `--issued` input above. Fail-closed when configured. (Spec 28; VL-099) | env on the gate: `ELYON_ISSUANCE_LOG_PATH=<path>` |

## 5. Adversarial harness and proof runners

| Tool | What it does | Invocation |
|---|---|---|
| `EVIDENCE/proofs/attack_harness.py` + `attack_suite_001_runner.py` | The gate-2 attack suite (forge / replay / rebind / swap / stale / unattested + positive control) over an in-process surface; exit 0 = all defeated. (Artifact 19; VL-079) | `PYTHONPATH=. python3 EVIDENCE/proofs/attack_suite_001_runner.py` |
| `EVIDENCE/proofs/attack_suite_live_runner.py` | The SAME suite over a real TLS deployment (CI-excluded; author-executed; C3/C4). (Artifact 22; VL-083/090) | env `ELYON_LIVE_*` per the runner header |
| `EVIDENCE/proofs/three_domain_poc/poc_runner.py` | Three-domain characterization (medical/legal/finance), in-process self-verify or live. (Spec 25; VL-096) | `PYTHONPATH=. python3 -m EVIDENCE.proofs.three_domain_poc.poc_runner [--mode live ...]` per `RUNBOOK_live.md` |
| `EVIDENCE/proofs/*_runner.py` (the family) | Hermetic, executable proofs per capability - enforcement (g4), cross-host/TLS (g5_*), signing + expiry, key/root records, latency budget, MCP stdio, default-secure cutover. Each names its ledger entry in its header; CI runs the hermetic subset. (VL-052/073) | `PYTHONPATH=. python3 EVIDENCE/proofs/<runner>.py` |

## 6. Deployment

| Tool | What it does | Invocation |
|---|---|---|
| `deploy/Dockerfile` + `docker-compose.yml` / `.tls.yml` / `.replay.yml` | The packaged stack: gate + reference target + publisher; TLS overlay; shared-Redis replay overlay. (Artifacts 20/21; VL-081/082/094) | `docker compose -f deploy/docker-compose.yml [-f ...tls.yml] [-f ...replay.yml] up --build` per `deploy/runbook.md` |
| `deploy/bootstrap_config.py` | Generates a coherent deployment config (keys, records, env) that round-trips admit->verify. (VL-081) | `python deploy/bootstrap_config.py` per runbook |
| `deploy/tls/gen_certs.py` + `trust_bootstrap.md` | Dev-CA certificate generation and the trust bootstrap procedure. (Artifact 21; VL-082) | `python deploy/tls/gen_certs.py` |
| `deploy/runbook.md` / `docker-compose*.yml` | The single-box + containerized live procedures (the author's live tier: VL-085..096). | documents |

## 7. Repository governance (method on record)

| Tool | What it does | Invocation |
|---|---|---|
| `scripts/lock_canon.sh`, `establish_ledger.sh`, `append_vl*.sh`, `update_state_vl011.sh` | The scripts that built the canon lock and the early ledger entries - kept as method-on-record, not for re-running. (VL-006..VL-011) | historical |
| `POE/generate_poe_hashes.py` | Proof-of-existence hash manifest generator for the POE record. | `python POE/generate_poe_hashes.py` |
| `docs/methodology/` | The reusable procedure artifacts: verification-request template (+ the committed VL-100 request), build-resumption template, apply-script template, session mechanics lessons, deposit-readiness audit, falsifiable claim sheet. | documents |

---

Maintenance rule: a new functional tool (a new module with an entry
point, CLI, env seam, or deployable surface) adds one row here in the
same increment that lands it; a doc-only index update needs no ledger
entry of its own beyond the landing increment's mention. This page
deliberately contains no test counts and no behavior detail beyond one
line - those live in the specs, the ledger, and the code.
