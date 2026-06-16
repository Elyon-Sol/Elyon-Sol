WHITE-BOX in-house Cursor review record - internal evidence, NOT external validation (VL-057), NOT a G5 referent.
Verdict: TESTS INADEQUATE
R-01 is sound for the scoped claim (same process, shared cache). P-01 is sound for duplicate ASGI header fields and fail-closed overall, but envelope-duplicate behavior is untested at integration depth, and comma-folded headers bypass the duplicate detector (still DENY). Tests prove R-01 and interaction-header P-01 only.
Point 1 — R-01 lock scope (_seen access)
Sound
replay_cache.py:120-128: _utcnow(now) runs outside the lock; all _seen reads/writes (prune → membership → insert) are inside with self._lock:.
_seen is only touched in InMemoryReplayCache.__init__ (106) and check_and_claim (122-128). No other mutation path.
All production callers use check_and_claim only:
reference_target.py:308
executor_sdk.py:127-128 (sidecar path)
mcp_server.py:154-155
No direct _seen access elsewhere.
Point 2 — Sidecar shares one cache instance
Sound
authz_sidecar.py:261-263: app.state.replay_cache is set once at app build.
authz_sidecar.py:305: every request passes request.app.state.replay_cache into ExecutorGate.
A new ExecutorGate is built per request (300-307), but the cache object is shared. The lock therefore serializes concurrent claims on the live sidecar path.
Out of scope for this fix: multi-worker / multi-replica still get separate caches (R-02); not a regression in 3343e32.
Point 3 — run_in_threadpool makes the race real
Sound
authz_sidecar.py:312: await run_in_threadpool(gate.check, ...).
Starlette’s run_in_threadpool runs sync work on a thread-pool worker, not on the asyncio event loop. Pre-fix TOCTOU between two /authz requests was real; the lock is necessary (not merely GIL masking).
reference_target.py:308 calls check_and_claim synchronously on the event loop (no threadpool for claim). Lock is belt-and-suspenders there; primary beneficiary is the sidecar.
Point 4 — Deadlock / re-entrancy / exception / await
Sound
threading.Lock() is non-reentrant; no recursive check_and_claim in the codebase → no self-deadlock.
No await inside the locked block.
with self._lock: releases the lock on exception from prune/in/assignment.
Minor note: current = _utcnow(now) at 120 is outside the lock, so prune uses a slightly stale timestamp. Effect is conservative (may retain entries longer), not a double-claim bypass.
Point 5 — ExternalStoreReplayCache / Redis path
Sound
replay_cache.py:144-152: unchanged; still delegates to ReplayStore.claim.
RedisReplayStore.claim (178-190) still uses SET … NX EX — independently atomic. Lock applies only to InMemoryReplayCache.
Point 6 — Header delivery (uvicorn / Envoy / comma folding)
Sound for security (DENY); partial gap vs “duplicate → absent” wording
Duplicate ASGI fields (primary case): h11/uvicorn and httpx/Starlette preserve duplicate header lines as separate scope entries → getlist() length > 1 → guard fires. Matches how test_findings_002._request builds scope.
Comma-folded into one field: If a proxy delivers
X-Elyon-Sol-Envelope: <json1>, <json2> as a single header, getlist() length == 1 → duplicate guard does not fire.
Fail-closed trace still holds:
Sidecar: json.loads on the combined string fails → envelope = None → verify_envelope → REF_VERIFY_ENVELOPE_ABSENT → _deny (283-287, 314-316).
Reference target: same → REF_VERIFY_ENVELOPE_ABSENT (249-253, 290-291).
So folded duplicates do not yield ALLOW; they yield deny via unparseable/absent, not via explicit duplicate detection. Two valid signed JSON blobs comma-joined cannot produce one valid signed envelope via standard json.loads.
Hardening (optional): reject envelope/interaction header values containing },{ or require strict single-object parse before verify.
Point 7 — Other decision-influencing headers still using first-wins .get()
Sound (no remaining gap in IMPLEMENTATION)
Security-relevant attestation headers are only:
X-Elyon-Sol-Envelope — guarded in authz_sidecar.py:280-281, reference_target.py:246-247
X-Elyon-Sol-Interaction — guarded in authz_sidecar.py:211-212
No other X-Elyon-* headers read for admission. pep.py only sets the envelope header. MCP uses _meta, not HTTP headers.
Note: TESTS/adversarial/test_enforcement.py build_enforcing_target_app still uses unguarded .get() (136) — test harness only, not production reference_target.py.
Point 8 — “Treat as absent” → provably DENY (no ALLOW path)
Sound
Sidecar — duplicate envelope:
raw = None (280-281) → envelope stays None → ExecutorGate.check coerces non-dict to None (106-107) → verify_envelope → REF_VERIFY_ENVELOPE_ABSENT → _deny (403). No honored=True path.
Sidecar — duplicate interaction:
default_interaction_extractor returns None (211-212) → with valid envelope, verify_envelope → REF_VERIFY_BINDING_MISMATCH (399-400 in verifier) → _deny. Still not ALLOW.
Reference target — duplicate envelope:
raw = None → envelope = None → verify_envelope → _refuse(REF_VERIFY_ENVELOPE_ABSENT) (290-291). No honor path.
Interaction is body-sourced on reference target; duplicate header interaction is N/A there (by design).
Point 9 — Test adequacy (test_findings_002.py)
Gap — tests inadequate for full P-01 claim
Test    Revert R-01 lock?    Revert P-01 envelope guard?    Revert P-01 interaction guard?
test_r01_inmemory_cache_honors_one_concurrent_claim
Would fail (32 threads × 40 rounds, barrier)
N/A
N/A
test_p01_duplicate_interaction_header_is_absent
N/A
N/A
Would fail
test_p01_single_interaction_header_parses
N/A
N/A
Sanity only
(missing) duplicate envelope on sidecar
N/A
Would NOT fail
N/A
(missing) duplicate envelope on reference_target via TestClient
N/A
Would NOT fail
N/A
(missing) sidecar/authz end-to-end duplicate test
N/A
Would NOT fail
N/A
Additional gaps:
P-01 tests use hand-built Starlette Request, not TestClient/uvicorn — adequate for getlist() semantics, not for full HTTP stack/Envoy.
TESTS/adversarial/test_findings_001.py:228-273 (F5) still pins first-wins on build_enforcing_target_app (unfixed harness). It was not updated in 3343e32 and does not exercise reference_target.py’s new behavior. No test in test_reference_target.py or test_authz_sidecar.py covers duplicate envelope denial.
R-01 regression coverage: adequate at the primitive layer. P-01 regression coverage: inadequate for the envelope half and production integration paths.
Scope check
Read: commit 3343e32 diff; IMPLEMENTATION/replay_cache.py, authz_sidecar.py, reference_target.py, executor_sdk.py, mcp_server.py; TESTS/adversarial/test_findings_002.py, test_findings_001.py, test_authz_sidecar.py, test_reference_target.py (grep); verifier.py (deny routing).
Not read / not executed: Live uvicorn/Envoy capture of duplicate vs folded headers; full pytest run with lock reverted; Envoy authorization_request header-forwarding config beyond deploy/envoy.example.yaml; EVIDENCE/proofs/three_domain_poc/poc_runner.py concurrency behavior.
Bottom line: Merge the R-01 fix as-is. Merge the P-01 fix for deny semantics, but add TestClient tests for duplicate X-Elyon-Sol-Envelope on sidecar + reference_target, and update or supersede test_findings_001 F5 so it asserts deny-on-duplicate on the production target, not first-wins on the old harness.
