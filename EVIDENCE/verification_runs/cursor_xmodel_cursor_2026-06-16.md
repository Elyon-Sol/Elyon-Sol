WHITE-BOX cross-model run | model=cursor (Cursor-run; underlying family unlabeled) | 2026-06-16 | internal evidence, NOT external validation (VL-057), NOT a G5 referent. Verbatim Cursor output, ASCII-normalized (VL-009).

Verdict: BREAK FOUND | R-01: SOUND | P-01: SOUND

Findings
id | class | file:line | invariant violated | trigger | severity | repro/PoC | suggested fix
R-02 | replay | replay_cache.py:193-203, authz_sidecar.py:261-263, reference_target.py:228 | single-use | Deploy N>1 processes/replicas with default replay_cache_from_env() (no ELYON_REPLAY_REDIS_URL); replay the same gate-signed envelope to each instance | high | test_replay_shared_across_two_sidecar_instances in TESTS/adversarial/test_authz_sidecar.py:276-288 shows shared cache fixes it when injected; default per-instance cache does not | Default fail-closed when workers>1/replicas>1 without shared store, or require ELYON_REPLAY_REDIS_URL in multi-instance manifests
F-01 | freshness/time | authz_sidecar.py:156-158, authz_sidecar.py:300-307, executor_sdk.py:91-94, published_source.py:117-128 | published record current (not stale) | Sidecar/SDK/MCP use byte-anchor load_record_from_bytes only; mount stale published_hashes.json bytes that still match ELYON_PINNED_ROOT_SHA256; present a captured envelope whose pinned hashes match that stale record and whose not_after has not passed | medium | readiness.json:35-39 documents bare default is byte-anchor; END_TO_END_NO_SHORTCUT note at readiness.json:75 admits stale-but-anchor-matching signed records are still honored | Wire published_record_source.fetch_signed_record into sidecar (as reference_target.py:264-271 optional signed mode), or fail-closed when signed freshness is required
K-01 | freshness/time | verifier.py:340-343, reference_target.py:283-288, authz_sidecar.py:300-307, executor_sdk.py:113-118 | issuer/root keys in-window | Default consumers pass pinned_public_keys only, never key_record_view; verifier's key-window/revocation gate (verifier.py:322-336) is skipped on the static-pin branch | medium | readiness.json:17-20 - key-record consultation is built but not on default enforce path; any envelope signed with the pinned key verifies until envelope not_after, regardless of key-record revocation/expiry | Fetch key record + pass key_record_view into verify_envelope on enforce surfaces, or fail-closed when key-record mode is required
B-01 | binding | authz_sidecar.py:194-220, authz_sidecar.py:289-290, reference_target.py:241 | bound to executed target_url + operation + arguments | Envoy ext_authz: sidecar binds envelope to X-Elyon-Sol-Interaction header; upstream target reads JSON body (reference_target.py:241). Mismatching header/body can yield sidecar ALLOW while upstream would bind differently | low (architectural) | Documented open in EVIDENCE/verification_runs/cursor_whitebox_review_2026-06-16.md:14; not exploitable on standalone sidecar alone | Phase-4 CUSTOM body->interaction extractor; or require upstream to consume the same header the sidecar verified
No signature-forgery, canonical-JSON mismatch, unsigned-downgrade, or duplicate-header first-wins bypass found on the signed enforce path.

Probed-and-held (class | file:line | note)
(1) signature / canonical JSON | envelope.py:148, envelope.py:509-511, verifier.py:344-353, envelope.py:133-140, envelope.py:407-414 | Sign and verify use the same exclusions; tamper -> REF_VERIFY_SIGNATURE_INVALID
(1) mandatory signed path | pep.py:279-292, reference_target.py:283-288, verifier.py:313-317 | Gate fails closed without signing key; enforce surfaces always supply pinned_public_keys
(3) binding AP/OP/context | verifier.py:417-440, request_validator.py:413-418 | Symmetric sort-dedup; rebinding -> REF_VERIFY_BINDING_MISMATCH
(3) target_url binding | verifier.py:404-405 | String equality
(4) decision not_after | verifier.py:368-379, pep.py:286-292 | Gate stamps signed not_after; expired -> REF_VERIFY_SIGNATURE_EXPIRED
(4) signed published record (when wired) | published_record_source.py:175-183, reference_target.py:264-270 | Stale signed record -> REF_VERIFY_PUBLISHED_RECORD_STALE
(5) manifest/anchor pinning | evaluator.py:93-94, published_source.py:117-118, envelope.py:434-439 | Divergent manifest fails closed; anchor mismatch before parse
(6) fail-closed PEP | pep.py:227-235, pep.py:303-311 | Exceptions -> REF_PEP_FAIL_CLOSED, no unsigned forward
(6) fail-closed sidecar | authz_sidecar.py:272-275, authz_sidecar.py:317-321 | Config/parse/internal errors -> 403 DENY, not 5xx
(2) replay atomicity (in-process) | replay_cache.py:111, replay_cache.py:122-128, executor_sdk.py:125-130 | Lock serializes prune+check+set; second concurrent claim -> REF_VERIFY_REPLAY
(2) replay cross-process (when configured) | replay_cache.py:185-190 | Redis SET NX EX is atomic
(7) duplicate-header ambiguity | authz_sidecar.py:211-212, authz_sidecar.py:280-281, reference_target.py:246-247 | len(getlist(...))>1 -> treat as absent
(7) comma-folded header | authz_sidecar.py:283-287 | Unparseable JSON -> absent -> DENY (test_p01_folded_envelope_header_fails_closed)

R-01 / P-01 verification
R-01 - SOUND. InMemoryReplayCache holds threading.Lock() (replay_cache.py:111) and wraps prune+membership+set in with self._lock (replay_cache.py:122-128). The sidecar runs ExecutorGate.check in run_in_threadpool (authz_sidecar.py:312 -> executor_sdk.py:127-128). Concurrent claims of the same decision_id serialize; only one returns True. Verify and claim are not one lock scope, but honor is gated solely on check_and_claim; a second concurrent thread gets REF_VERIFY_REPLAY, not a second ALLOW.
P-01 - SOUND. Duplicate envelope/interaction headers -> absent (authz_sidecar.py:280-281, :211-212; reference_target.py:246-247). Integration tests deny duplicate valid envelopes. No first-wins path remains. Comma-concatenated single-header payloads fail JSON parse -> absent.

Scope check
Every claim maps to cited IMPLEMENTATION/*.py lines. Tests cited only as PoC corroboration.
Out of scope (not asserted): A1 caller bypass (verifier.py:67-72); root/publisher/host/TLS compromise; semantic legitimacy / canon section 14; DoS; cross-signer root overlap (root_record_source.py:32-36); reference_target.py lacks sidecar's outer except -> 500 on unhandled exception (not an ALLOW path); key_record_source/root_record_source readers built+tested but not wired into default enforce paths.
