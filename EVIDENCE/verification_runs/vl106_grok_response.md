# VL-106 verifier response - run 1 (Grok)

Provenance: executed by the project author against Grok with the committed
request `docs/methodology/verification_request_vl106.md` and its 14 attached
files; response transcribed from the author's paste-back into the VL-106
adjudication session on 2026-06-15. Non-ASCII punctuation normalized to ASCII
per VL-009; wording and all cited symbol names preserved. Verbatim below the
line; adjudication is ledger entry VL-106.

---

CA-1: Supported. authz_sidecar.py imports ExecutorGate from executor_sdk.py and calls gate.check(envelope, interaction) (lines ~140-150 in _authz_handler); no signature checks, set comparisons, reassert, or other logic is present in the module.
CA-2: Supported. Only REF_TARGET_NOT_CONFIGURED and REF_TARGET_ANCHOR_MISMATCH are imported from reference_target.py and used (e.g., config_from_env, _deny calls, exception handler); no new REF_* constants are defined.
CA-3: Supported. In _authz_handler (authz_sidecar.py): config_provider() None -> _deny(REF_TARGET_NOT_CONFIGURED); outer try/except Exception -> _deny(REF_TARGET_ANCHOR_MISMATCH); no 5xx or ALLOW-on-error paths.
CA-4: Supported. authz_sidecar.py lines ~115-120: raw = request.headers.get(ENVELOPE_HEADER); absent/unparseable -> envelope=None; passed to gate.check.
CA-5: Supported. default_interaction_extractor in authz_sidecar.py (lines ~70-85) reads/parses X-Elyon-Sol-Interaction (or None); injectable via build_authz_sidecar_app parameter; no CUSTOM mapping format.
CA-6: Supported. _allow and _deny in authz_sidecar.py (lines ~90-100) set exactly the stated 200/403 + x-elyon-decision/x-elyon-reason headers.
CA-7: Supported. build_authz_sidecar_app (authz_sidecar.py lines ~105-110) sets app.state.replay_cache once; passed to every ExecutorGate; injectable for sharing.
CA-8: Supported. config_from_env in authz_sidecar.py (lines ~30-65) checks required env vars, record read, key parse, and ELYON_CLOCK_SKEW_SECONDS (negative/malformed -> None).
CA-9: Under-specified. authz_sidecar.py defines app = build_authz_sidecar_app() at module level with no imports of itself visible in attached files; whether other modules import it cannot be determined from the provided set.
CA-10: Supported. build_authz_sidecar_app registers /authz and /authz/{rest:path} (authz_sidecar.py lines ~155-160); decision uses only headers; /healthz GET returns {"status": "ok"} (no config/trust info).
CT-1: Supported. test_authz_sidecar.py asserts exactly these: ALLOW on valid (test_allow_on_valid_attested_request); specific DENY reasons for absent/unparseable (test_deny_absent_unattested, test_deny_unparseable...), forged (test_deny_forged_signature), replay (test_deny_replay), rebind/target-swap (test_deny_rebind..., test_deny_target_swap), stale (test_deny_stale), record-drift (test_deny_record_drift).
CT-2: Supported. test_fail_closed_unconfigured, test_fail_closed_wrong_anchor, and test_config_from_env_missing_returns_none in test_authz_sidecar.py.
CT-3: Supported. test_replay_shared_across_two_sidecar_instances in test_authz_sidecar.py builds two clients sharing one InMemoryReplayCache and asserts cross-refusal.
CT-4: Supported. Tests use _admit (real pep gate via TestClient, real gate_signing key) and call production paths; no stubbing of verify_envelope/ExecutorGate.
CD-1: Supported. gen_certs.py: SERVICES includes "elyon-authz" (line ~30); write_deployment_certs generates its .crt/.key with listed SANs (lines ~80-95).
CD-2: Supported. test_authz_sidecar_tls.py: _handshake with VERIFY_X509_STRICT succeeds for dev-CA elyon-authz leaf and raises SSLCertVerificationError for wrong CA (tests test_elyon_authz_leaf_verifies_with_trusted_ca / test_elyon_authz_leaf_refused_with_wrong_ca).
CD-3: Supported. authz_sidecar_tls_001_runner.py serves production sidecar under real uvicorn TLS, drives ALLOW/DENY over HTTPS client with CA verify, and exits 0 on success; ci.yml contains *authz_sidecar_tls* skip.
CD-4: Supported. docker-compose.authz.tls.yml overrides only elyon-authz command (uvicorn --ssl-*) and volumes; no changes to other services.
CD-5: Supported. envoy.example.yaml: two ext_authz filters in order (elyon-authz first, OPA second), both failure_mode_allow: false, router last (lines ~30-80).

Divergence notes
CA-9 is Under-specified (imports of the sidecar cannot be determined from attached files). All other claims are Supported with no divergences.

Scope check
All concepts/terms/claims classified using only: authz_sidecar.py (build_authz_sidecar_app, config_from_env, _authz_handler, default_interaction_extractor, allow/deny); test_authz_sidecar.py (all test functions); executor_sdk.py (ExecutorGate.check, Decision); reference_target.py (REF_TARGET*); replay_cache.py (InMemoryReplayCache); gen_certs.py (SERVICES, write_deployment_certs); test_authz_sidecar_tls.py (_handshake tests); authz_sidecar_tls_001_runner.py (main TLS serve/POST); docker-compose.authz.yml / docker-compose.authz.tls.yml (service overrides); envoy.example.yaml (filters); ci.yml (skip clause). No out-of-scope material used.
