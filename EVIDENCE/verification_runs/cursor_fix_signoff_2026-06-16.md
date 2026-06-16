WHITE-BOX in-house Cursor review record - internal evidence, NOT external validation (VL-057), NOT a G5 referent.
Verdict: TEST WEAKNESS
The production fixes for R-01 and P-01 are sound for their stated scope (single-process + threadpool; duplicate ASGI header fields). The P-01 envelope tests are real revert-catchers via TestClient. The R-01 concurrency test did not fail when the lock was removed on this platform (0/40 and 0/200 rounds at 32–128 threads), so it does not reliably prove the R-01 fix.
1. R-01 fully closed
Holds (for claimed scope: one process, shared cache, threadpool)
replay_cache.py:122-128: prune → membership → insert are all inside with self._lock:; _seen is only assigned in __init__ (106) and mutated inside that block.
_utcnow(now) at 120 is outside the lock; it does not touch _seen.
All claim paths go through check_and_claim:
reference_target.py:308
executor_sdk.py:127-128 (sidecar via authz_sidecar.py:305)
mcp_server.py:154-155
No alternate _seen access in IMPLEMENTATION (grep confirms only replay_cache.py).
Sidecar shares one cache: authz_sidecar.py:261-263 sets app.state.replay_cache once; 305 passes it into every ExecutorGate. Not per-request cache.
Second-cache bypass: only if a caller omits injection — executor_sdk.py:88 creates a fresh InMemoryReplayCache() per gate. Sidecar always injects the shared instance; not a supported sidecar path.
Lock region: no await, no I/O; only dict prune/check/set. verify_envelope runs before claim in executor_sdk.py:113-130, outside the lock. No deadlock/re-entrancy path (non-reentrant Lock, no nested check_and_claim).
Out of scope (not claimed fixed): multi-worker / multi-replica without ELYON_REPLAY_REDIS_URL (R-02) — separate processes, separate caches.
2. R-01 test actually catches a revert
Gap — weak revert-catcher on CPython
test_findings_002.py:26-49: 32 threads, barrier, 40 rounds — structurally reasonable.
Empirical check on HEAD: simulating pre-fix logic (subclass overriding check_and_claim without lock, same 32×40 parameters) → 0/40 rounds with honored != 1.
Same at 128 threads × 200 rounds → 0/200.
With time.sleep(0.001) between membership check and insert (widened race window) → 20/20 failures — the bug is real; the test window is too narrow for CPython’s GIL-heavy dict ops.
Conclusion: removing threading.Lock may leave this test green by luck on CPython; it is not a dependable revert-catcher. The lock fix is still correct; proof is not.
Suggested change: add a sidecar-level concurrent replay test (two run_in_threadpool/TestClient parallel POSTs, same minted envelope, assert exactly one ALLOW), or inject a test-only widen hook in the critical section for regression only.
3. P-01 fully closed
Holds (security: no first-wins ALLOW)
Form    Sidecar    Reference target
Duplicate X-Elyon-Sol-Envelope (getlist > 1)
authz_sidecar.py:280-281 → raw=None → DENY
reference_target.py:246-247 → absent → 403
Duplicate X-Elyon-Sol-Interaction
authz_sidecar.py:211-212 → extractor None → binding/absent DENY
N/A (interaction from body)
Comma-folded single header
getlist == 1 → guard skipped → json.loads fails (283-287) → DENY
Same (249-253)
JSON array / non-dict parse
Sidecar passes list to gate → executor_sdk.py:106-107 coerces to absent
verify_envelope → REF_VERIFY_ENVELOPE_ABSENT
No remaining first-wins .get() on admission headers in production paths (only guarded envelope + interaction reads above).
pep.py only sets envelope header; MCP uses _meta, not HTTP duplicates.
Semantic note: comma-folded duplicates are not detected as duplicates; they fail closed as unparseable/absent. No ALLOW bypass found.
Construct folded valid envelope bypass: two canonical_json(envelope) blobs joined with , → json.loads raises “Extra data” → absent → DENY. JSON array [env, env] → non-dict → coerced absent. No parse-to-valid-envelope bypass found.
4. P-01 tests actually catch a revert
Holds for envelope integration tests; partial for interaction
Duplicate envelope — real revert-catchers
test_authz_sidecar.py:326-327: headers=[(ENVELOPE_HEADER, body), (ENVELOPE_HEADER, body), ...] → asserts 403.
Revert guard → first-wins on two identical valid bodies → 200 ALLOW → test fails. ✓
test_reference_target.py:318-322: same duplicate pattern → 403 + REF_VERIFY_ENVELOPE_ABSENT + received == []. Revert → honor → fails. ✓
TestClient delivers separate fields (not folded)
Starlette TestClient builds ASGI scope with request.headers.multi_items() (starlette/testclient.py:250), preserving duplicate keys as separate (bytes, bytes) entries.
Therefore getlist() returns length 2 and the duplicate guard is exercised — not passing for the wrong reason via folding.
Your 403 observation is consistent with this mechanism.
Other P-01 tests
test_p01_duplicate_interaction_header_is_absent (test_findings_002.py:67-70): revert-catcher for interaction extractor (unit / hand-built Request).
test_p01_folded_envelope_header_fails_closed (test_authz_sidecar.py:331-340): fail-closed assertion only, not a revert-catcher (passes with or without duplicate guard; asserts unparseable → 403). Label: fail-closed smoke test.
Minor gap: no sidecar TestClient test for duplicate X-Elyon-Sol-Interaction (unit test only); envelope half is fully covered at integration depth.
5. No new problem introduced
Holds
Full suite: 397 passed (run on HEAD, 10.51s).
R-01 lock: serializes only claim; single-threaded semantics unchanged; no I/O under lock → no new deadlock/starvation risk identified.
P-01: stricter than first-wins (duplicate → deny); no fail-open regression.
New tests are deterministic (no sleeps/time windows in P-01; R-01 uses barrier, not wall clock).
test_findings_001.py:228-273 (F5) still pins first-wins on build_enforcing_target_app test harness, not production reference_target.py — pre-existing, not weakened by these commits.
6. Residual
Documented, non-blocking for this sign-off scope
Item    Status
R-02 multi-process replay
Still open; not in 3343e32 claim
Comma-fold strict-parse hardening
Optional; fold → unparseable → DENY today
Envoy real ext_authz
deploy/envoy.example.yaml:59-68 forwards allowed headers; HTTP intermediaries may comma-combine duplicate field lines per RFC 7230 → getlist len 1 → duplicate guard skipped, but parse-fail → DENY (fail-closed, not first-wins)
Sidecar duplicate-interaction integration test
Missing; covered by unit test only
R-01 integration/concurrent sidecar test
Missing; unit test weak on CPython
No folded/encoded value found that parses to a valid signed envelope and yields ALLOW without the gate key.
Scope check
Read: commits 3343e32, 2711fd7; IMPLEMENTATION/replay_cache.py, authz_sidecar.py, reference_target.py, executor_sdk.py, mcp_server.py; TESTS/adversarial/test_findings_002.py, test_authz_sidecar.py (P-01 tests), test_reference_target.py (P-01 test); deploy/envoy.example.yaml; starlette/testclient.py:250; verifier.py / executor_sdk.py non-dict envelope paths.
Executed: targeted pytest (6 tests), full TESTS (397 passed); R-01 lock-revert simulation (0 failures without lock at test parameters; 20/20 with artificial sleep).
Not grounded in live Envoy/h11 capture: exact duplicate-header wire form from production Envoy → sidecar (inferred from RFC + example config + Starlette TestClient source).
Adjudication summary: Treat R-01 + P-01 code as done for single-process ext-authz. Treat “proven by tests” as not fully met until R-01 has a revert-catcher that fails without the lock on CPython (or a sidecar concurrent replay integration test). P-01 envelope proof is solid; fold test is fail-closed smoke only. If you accept “fix sound, R-01 proof thin,” you can close the fixed area and move to the pre-exposure list; a one-increment test hardening for R-01 would close the proof gap cleanly.
