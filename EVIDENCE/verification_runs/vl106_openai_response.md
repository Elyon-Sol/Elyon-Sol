# VL-106 verifier response - run 2 (OpenAI)

Provenance: executed by the project author against OpenAI with the committed
request `docs/methodology/verification_request_vl106.md` and its 14 attached
files; response transcribed from the author's paste-back into the VL-106
adjudication session on 2026-06-15. Non-ASCII punctuation normalized to ASCII
per VL-009; the classification table is rendered one row per line; wording and
all cited symbol names preserved. Verbatim below the line; adjudication is
ledger entry VL-106.

---

Classification table (Claim / Outcome / Ground)

- CA-1: Supported. build_authz_sidecar_app constructs an ExecutorGate and returns ALLOW/DENY from decision.honored and decision.reason; no signature verification, AP/OP comparison, or reassert logic is implemented in authz_sidecar.py itself.
- CA-2: Supported. The only imported REF codes referenced directly in the module are REF_TARGET_NOT_CONFIGURED and REF_TARGET_ANCHOR_MISMATCH; no new REF_* constant is defined, and gate refusal reasons are surfaced from decision.reason.
- CA-3: Supported. _authz_handler returns REF_TARGET_NOT_CONFIGURED when config_provider() yields None, and its outer try/except converts unexpected exceptions into REF_TARGET_ANCHOR_MISMATCH; ALLOW is only returned from a positive gate decision.
- CA-4: Supported. The handler treats a missing or JSON-unparseable envelope header as envelope=None; ExecutorGate.check converts non-dict envelopes to None, and verify_envelope rejects non-dicts as REF_VERIFY_ENVELOPE_ABSENT.
- CA-5: Supported. default_interaction_extractor reads X-Elyon-Sol-Interaction, returns a parsed dict, and returns None for absent, unparsable, or non-dict values; interaction_extractor is injectable and no declarative CUSTOM mapping implementation exists in the module.
- CA-6: Supported. _allow() emits HTTP 200 with x-elyon-decision: ALLOW; _deny() emits HTTP 403 with x-elyon-decision: DENY and x-elyon-reason.
- CA-7: Supported. app.state.replay_cache is created once per app and passed into every per-request ExecutorGate; the injected-cache path exists, and the shared-cache behavior is exercised by the replay tests.
- CA-8: Supported. config_from_env() returns None on missing required env vars, unreadable record file, malformed public-key bytes, malformed clock skew, or negative clock skew.
- CA-9: Under-specified. The attached files show that authz_sidecar.py defines a module-level app, but the attached set cannot determine whether some unattached module imports it.
- CA-10: Supported. Routes are registered on both /authz and /authz/{rest:path}; the handler reads headers and never consults the request path; /healthz returns {"status": "ok"}.
- CT-1: Supported. The suite contains explicit tests for ALLOW, absent, unparseable-absent, forged signature, replay, rebind, target-swap, stale, and record-drift refusal outcomes with the stated reason codes.
- CT-2: Supported. The suite contains test_fail_closed_unconfigured, test_fail_closed_wrong_anchor, and test_config_from_env_missing_returns_none.
- CT-3: Supported. test_replay_shared_across_two_sidecar_instances creates two apps sharing one InMemoryReplayCache and asserts replay refusal on the second instance.
- CT-4: Supported. _admit() drives the real gate (pep.app) to mint envelopes; the tests exercise the sidecar through ExecutorGate and do not replace verify_envelope or ExecutorGate with test doubles.
- CD-1: Supported. SERVICES includes elyon-authz; write_deployment_certs() generates leaves for every service using SANs [service, localhost, 127.0.0.1, *extra_sans].
- CD-2: Supported. The TLS test performs a MemoryBIO handshake, enables VERIFY_X509_STRICT when available, verifies success under the generated CA, and expects refusal under a different CA.
- CD-3: Supported. The runner serves build_authz_sidecar_app() under uvicorn TLS, verifies ALLOW for a valid envelope and DENY for a tampered one over HTTPS, returns success only on that outcome, and ci.yml contains an *authz_sidecar_tls* skip clause.
- CD-4: Supported. The TLS overlay changes the elyon-authz service command to include --ssl-certfile and --ssl-keyfile and mounts ./tls/certs:/certs:ro; the file contains no modifications to gate/target/publisher service definitions.
- CD-5: Supported. envoy.example.yaml documents and configures two ext_authz filters in order (elyon-authz first, OPA second), both with failure_mode_allow: false, followed by routing to the upstream cluster.

Divergence notes
CA-9 - Under-specified. The attached files establish only that authz_sidecar.py creates a module-level app and that several attached artifacts reference or deploy it. They do not determine whether some unattached module imports authz_sidecar.py. The "nothing in the attached files imports authz_sidecar" portion is not fully decidable from the provided set because the claim extends to modules outside the attachment set.

Scope check
- ExecutorGate delegation / decision source - authz_sidecar.py (build_authz_sidecar_app), executor_sdk.py (ExecutorGate.check).
- REF_TARGET_NOT_CONFIGURED / REF_TARGET_ANCHOR_MISMATCH usage - authz_sidecar.py imports; canonical definitions in reference_target.py.
- Fail-closed behavior - authz_sidecar.py (_authz_handler, _deny, _allow).
- Envelope absent/unparseable handling - authz_sidecar.py (_authz_handler), executor_sdk.py (check), verifier.py (verify_envelope).
- Interaction extraction behavior - authz_sidecar.py (default_interaction_extractor, build_authz_sidecar_app).
- Decision headers and status codes - authz_sidecar.py (_allow, _deny).
- Replay cache sharing and injection - authz_sidecar.py (app.state.replay_cache usage), test_authz_sidecar.py (test_replay_shared_across_two_sidecar_instances), replay_cache.py.
- Environment configuration failure conditions - authz_sidecar.py (config_from_env).
- Route registration and health endpoint - authz_sidecar.py (add_api_route, healthz).
- Test coverage claims - test_authz_sidecar.py individual test functions.
- Gate-minted envelopes in tests - test_authz_sidecar.py (_admit).
- Certificate generation and SAN coverage - gen_certs.py (SERVICES, write_deployment_certs, gen_leaf).
- MemoryBIO TLS verification - test_authz_sidecar_tls.py (_handshake, TLS tests).
- Loopback TLS proof runner behavior - authz_sidecar_tls_001_runner.py (main).
- CI skip clause for authz sidecar TLS runner - ci.yml ("authz_sidecar_tls" case).
- TLS compose overlay behavior - docker-compose.authz.tls.yml (elyon-authz service command and volume mount).
- Envoy filter ordering and failure_mode_allow settings - envoy.example.yaml (ext_authz filter chain comments and configuration).
- Design statements about Mode A ordering and sidecar role - opa_sidecar_design.md sections 2-9.
No additional concepts were used beyond those derivable from the attached files.
