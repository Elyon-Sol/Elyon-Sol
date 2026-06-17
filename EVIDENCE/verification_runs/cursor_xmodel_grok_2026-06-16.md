WHITE-BOX cross-model run | model=Grok (xAI) | 2026-06-16 | internal evidence, NOT external validation (VL-057), NOT a G5 referent. Verbatim Cursor output, ASCII-normalized (VL-009).

Verdict: NO BREAK THIS PASS, R-01 SOUND, P-01 SOUND.
Findings: (none)

Probed-and-held:
(1) Signature: forged/tampered/unsigned refused on signed path; canonical-JSON determinism solid (bytes signed == bytes verified); signed fields checked, unsigned excluded from sig region. (verifier.py:313-353; envelope.py:344-348/509-511; envelope.py:173-178; verifier.py:288-298 structural guard).
(2) Replay: check_and_claim atomic under lock; single-use enforced (no double-honor). (replay_cache.py:122-128; executor_sdk.py:126-130; authz_sidecar.py:312 threadpool).
(3) Binding: exact target_url + normalized AP/OP + context + manifest pins. (verifier.py:404-440; _normalize_set_field:192-199).
(4) Freshness/time: not_after + key windows + skew; stale record refused. (verifier.py:368-379, 333-336; published/key/root record sources).
(5) Manifest/anchor pinning: enforced via reassert + record load. (verifier.py:381-396; executor_sdk.py:109-111; published_source.py etc.).
(6) Fail-open: all exception/default/config paths -> DENY/REFUSE. (authz_sidecar.py:272-321; executor_sdk.py:106-132; verifier.py:287-443).
(7) Parsing/type: guarded, no confusion leading to ALLOW. (verifier.py:288-298, 316-317; sidecar header handling).

R-01 (InMemoryReplayCache lock): SOUND. The lock serializes prune/check/claim (replay_cache.py:122). Sidecar's run_in_threadpool(gate.check) (authz_sidecar.py:312) + shared app-state cache ensures no concurrent bypass on threadpool-driven path. No TOCTOU/gap.
P-01 (duplicate headers): SOUND. getlist(...) > 1 -> treat as absent/None for both ENVELOPE and INTERACTION (authz_sidecar.py:210-212, 280-281). No first-wins; fails closed at binding/presence guard.

Scope check: All claims grounded in IMPLEMENTATION/*.py (verifier.py:210-443 primary; envelope.py, replay_cache.py, authz_sidecar.py, executor_sdk.py, evaluator.py; published_/key/root_record_source.py). No out-of-scope assertions. CANON/ and SPEC/ read only for intent. No fabrication; every line verifiable against HEAD.
The signed-path admissibility guarantee holds under the reviewed attack surface. Cross-model convergence would increase confidence further.
