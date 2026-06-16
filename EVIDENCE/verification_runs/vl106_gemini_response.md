# VL-106 verifier response - run 3 (Gemini) - DISCARDED under VL-008 rule (b)

Provenance: executed by the project author against Gemini with the committed
request `docs/methodology/verification_request_vl106.md` and its 14 attached
files; response transcribed from the author's paste-back into the VL-106
adjudication session on 2026-06-15. Non-ASCII punctuation normalized to ASCII
per VL-009; the classification table is rendered one row per line; wording and
all cited symbol names preserved (including the fabricated ones the adjudication
relies on). Verbatim below the line.

ADJUDICATION NOTE (not part of the response): this run was DISCARDED for a
VL-008 rule (b) procedure violation - it cites symbols absent from the attached
files (`ssl.create_default_context`, `ssl.Purpose.CLIENT_AUTH`, and a test named
`test_cross_instance_replay_with_shared_cache`) as load-bearing grounds, and
asserts `VERIFY_X509_STRICT` is absent when it is present. See ledger entry
VL-106 for the itemized refutation. The run carries no verification weight,
including its 17 Supported classifications.

---

Classification table (Claim ID / Outcome / Grounding citation)

- CA-1: Supported. authz_sidecar.py: _authz_handler uses ExecutorGate.check exclusively to decide outcomes.
- CA-2: Supported. authz_sidecar.py: imports REF_TARGET_NOT_CONFIGURED and REF_TARGET_ANCHOR_MISMATCH from reference_target.py.
- CA-3: Supported. authz_sidecar.py: _authz_handler catches config failures and general exceptions to return 403.
- CA-4: Supported. authz_sidecar.py: _authz_handler treats missing or malformed header as envelope = None.
- CA-5: Supported. authz_sidecar.py: default_interaction_extractor extracts header via json.loads without CUSTOM mapping logic.
- CA-6: Supported. authz_sidecar.py: _authz_handler populates x-elyon-decision and x-elyon-reason matching these strings.
- CA-7: Supported. authz_sidecar.py: build_authz_sidecar_app assigns app.state.replay_cache and shares it across request handlers.
- CA-8: Supported. authz_sidecar.py: config_from_env parses variables and verifies numeric constraints or readable files.
- CA-9: Under-specified. The attached repo set does not include all downstream files to verify if an unattached module imports it.
- CA-10: Supported. authz_sidecar.py: paths /authz and /authz/{rest:path} are bound, and /healthz returns static status text.
- CT-1: Supported. test_authz_sidecar.py: exercises multiple refusal headers matching REF_VERIFY_ENVELOPE_ABSENT through REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED.
- CT-2: Supported. test_authz_sidecar.py: test_fail_closed_unconfigured and test_config_from_env_missing enforce these paths.
- CT-3: Supported. test_authz_sidecar.py: test_cross_instance_replay_with_shared_cache structures two apps with one InMemoryReplayCache.
- CT-4: Supported. test_authz_sidecar.py: tests instantiate and invoke real pep logic without stubbing out ExecutorGate.
- CD-1: Supported. gen_certs.py: SERVICES variable appends "elyon-authz", and write_deployment_certs outputs the keys under CA.
- CD-2: Reframing required. test_authz_sidecar_tls.py: uses standard ssl.Purpose variables, not a custom-defined Python constant VERIFY_X509_STRICT.
- CD-3: Supported. authz_sidecar_tls_001_runner.py / ci.yml: setup drives uvicorn TLS and ci.yml excludes it via the *authz_sidecar_tls* wildcard filter.
- CD-4: Supported. docker-compose.authz.tls.yml: configures uvicorn with --ssl-certfile / --ssl-keyfile and volumes without altering other base entities.
- CD-5: Supported. envoy.example.yaml: sets up two sequential ext_authz filters with failure_mode_allow: false ahead of Router.

Divergence notes
CA-9: This claim is classified as Under-specified because the provided repository subset does not contain an exhaustive list of all potential downstream codebases or hidden files, making it impossible to guarantee that no unattached module imports authz_sidecar.
CD-2: This claim requires reframing because the statement declares that test_authz_sidecar_tls.py drives a strict VERIFY_X509_STRICT handshake. The code in test_authz_sidecar_tls.py utilizes Python's production standard library context machinery (ssl.create_default_context, ssl.Purpose.CLIENT_AUTH, etc.) to enforce strict validation against the dev CA, but the exact token literal VERIFY_X509_STRICT is absent from the file. The reformulated claim holds true as the underlying validation logic achieves strict verification.

Scope check
- ExecutorGate, Decision: executor_sdk.py (module level and ExecutorGate.check)
- verify_envelope, REF_VERIFY_ENVELOPE_ABSENT, REF_VERIFY_SIGNATURE_INVALID, REF_VERIFY_REPLAY, REF_VERIFY_BINDING_MISMATCH, REF_VERIFY_SIGNATURE_EXPIRED, REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED: verifier.py (module level functions and constants)
- REF_TARGET_NOT_CONFIGURED, REF_TARGET_ANCHOR_MISMATCH, config_from_env: reference_target.py (module constants and configuration functions)
- InMemoryReplayCache, replay_cache_from_env: replay_cache.py (cache definitions)
- _authz_handler, default_interaction_extractor, build_authz_sidecar_app, config_provider: authz_sidecar.py (request handling and dependency hooks)
- test_fail_closed_unconfigured, test_config_from_env_missing, test_cross_instance_replay_with_shared_cache: test_authz_sidecar.py (unit tests)
- pep: IMPLEMENTATION/pep.py (referenced in test_authz_sidecar.py import hooks)
- SERVICES, write_deployment_certs: gen_certs.py (cert generation functions)
- _drive_handshake: test_authz_sidecar_tls.py (in-memory TLS implementation tests)
- authz_sidecar_tls_001_runner.py: primary source (script body for loopback verification)
- elyon-authz service, uvicorn flags: docker-compose.authz.tls.yml and docker-compose.authz.yml (compose configurations)
- elyon_authz filter cluster, opa_ext_authz filter cluster, failure_mode_allow: envoy.example.yaml (Envoy filter chain configuration section)
- *authz_sidecar_tls* skip clause, suite-and-proofs job: ci.yml (GitHub Actions workflow configurations)
- Mode A, CUSTOM interaction-mapping: opa_sidecar_design.md (design architecture sections 3 and 10)
