WHITE-BOX in-house Cursor review record - internal evidence, NOT external validation (VL-057), NOT a G5 referent.
Verdict: FINAL SIGN-OFF (sound + proven + record accurate + no residual)
Minor caveats only: STATE.md still cites suite 394 at one bullet (HEAD is 399); R-01 deterministic test has low-probability timing sensitivity under extreme CI load (not observed in 15 consecutive local runs).
1. R-01 fix still sound
Holds
replay_cache.py:122-128: all _seen mutation (prune → in → assign) is inside with self._lock:.
_seen only created at 106; no other IMPLEMENTATION access to _seen.
Claim paths: reference_target.py:308, executor_sdk.py:127-128, mcp_server.py:154-155 — all via check_and_claim.
Sidecar: one shared cache (authz_sidecar.py:261-263, 305); not per-request.
Scope unchanged: single-process + threadpool; R-02 (multi-process) correctly remains named-open.
2. R-01 corrected test is a reliable revert-catcher
Holds (with low-probability timing margin noted below)
Determinism (verified on HEAD):
test_findings_002.py:82-87: BlockingSeen.__contains__ captures present before release.wait(2.0) and returns the stale value — the follow-up-3 fix that made the test real.
With lock: simulated run → (1, 2) honored count; pytest passes.
Without lock (no-op context manager): simulated run → (2, 2); matches follow-up-3 claim that revert yields 2 claims.
Why it works:
With lock: t1 holds lock inside __contains__ until check_and_claim completes; t2 cannot enter until t1 finishes → [True, False].
Without lock: both capture present=False while blocked, then both set → [True, True].
Flakiness assessment (98-102):
Mechanism    Risk    Direction
entered.wait(2.0) assert (98)
t1 slow to schedule on overloaded CI
Spurious FAIL with lock present (timeout before assert)
time.sleep(0.2) + release.set() (100-101)
t2 might not reach __contains__ before t1 sets
Spurious PASS without lock (revert not caught) — theoretical under extreme scheduler delay
t1.join(2.0); t2.join(2.0) (102)
No is_alive() check after join
Incomplete results → spurious fail if join times out (unlikely; test ~0.5s locally)
Assert failure before release.set()
release.wait(2.0) eventually times out in threads
Not a permanent hang; threads exit after 2s wait
Empirical: 15 consecutive pytest runs of test_r01_lock_serializes_concurrent_claims — all passed (~0.51s each).
Hardening (optional, not blocking): replace fixed sleeps with a second threading.Event signaling t2 entered __contains__; assert both entered before release.set(); check is_alive() after joins.
Note: test_r01_inmemory_cache_honors_one_concurrent_claim (26-49) remains a weak stress supplement (GIL may mask unlock on CPython); follow-up-3 correctly treats test_r01_lock_serializes_concurrent_claims as the authoritative revert-catcher.
3. P-01 fixes + tests sound
Holds
No first-wins ALLOW in production paths:
Duplicate envelope: authz_sidecar.py:280-281, reference_target.py:246-247 → raw=None → DENY/absent.
Duplicate interaction: authz_sidecar.py:211-212 → extractor None → DENY.
Comma-fold: getlist len 1 → json.loads fails → absent → DENY.
Integration revert-catchers (each fails if guard reverted):
Test    Revert behavior
test_authz_sidecar.py:319-328 duplicate envelope
Revert → first-wins on two identical valid bodies → 200 ALLOW → test fails ✓
test_reference_target.py:314-325 duplicate envelope
Revert → honor → 200 + received append → test fails ✓
test_authz_sidecar.py:343-354 duplicate interaction
First header matches envelope; revert → 200 ALLOW → test fails ✓
Fail-closed-only (not revert-catcher):
test_p01_folded_envelope_header_fails_closed (331-340): docstring explicitly states comma-fold bypasses duplicate detector; asserts 403 only. Passes with or without duplicate guard. Label: fail-closed smoke test ✓
Unit tests in test_findings_002.py:67-70 additionally cover interaction extractor revert.
4. Ledger ⟷ code consistency at HEAD (97180f7)
Holds for VL-109 follow-ups; one peripheral stale line
Entry    Claim    HEAD match
VL-109 main (16142-16156)
R-01/P-01 fixed at 3343e32; 391→394
✓ for that commit
Follow-up 1 (16167-16168)
Envelope DENY tests; 394→397
✓ code + count
Follow-up 2 (16170-16171)
Deterministic R-01 test + interaction integration; 397→399; "verified red/green"
Tests exist; red/green claim was false
Follow-up 3 (16173-16174)
Retracts follow-up-2 claim; capture-before-block fix; lock on→pass / lock off→fail; 399 green
✓ matches code at 97180f7; retraction complete
Retraction complete: follow-up-3 explicitly marks follow-up-2's "verified red-without-lock / green-with-lock" as FALSE and documents the BlockingSeen bug. No other arc entry repeats that false claim as current truth.
Peripheral staleness (not in VL-109 follow-ups): STATE.md:1006 still says "suite 394 green" while HEAD is 399 (follow-up-3 ledger is correct). cursor_whitebox_review_2026-06-16.md:24-25 frozen at 394 — acceptable as point-in-time snapshot at 3343e32.
"Deployed" claims: in VL-109 main / STATE (author-native redeploy); not re-verified in this audit run.
5. No residual in fixed area; named-open correctly scoped
Holds
B-01 (header vs upstream body): unbuilt; no step-4 mapping in diff — correctly named-open, not a regression.
F-01 (sidecar signed freshness): sidecar still byte-anchor only (authz_sidecar.py:300-307 via ExecutorGate + record_bytes); target has optional signed mode — unchanged by arc; correctly named-open.
R-02 (multi-worker replay): default InMemoryReplayCache per process; not worsened — still documented boundary.
Intentional behavior change (not weakening): duplicate headers deny instead of first-wins — the fix itself.
Unchanged / documented: test_findings_001 F5 on old build_enforcing_target_app harness (ledger follow-up-1 note).
6. Suite integrity
Holds
399 passed on HEAD (TESTS, 11.18s) — matches follow-up-3.
P-01 integration tests: 4/4 pass.
R-01 deterministic test: 15/15 consecutive passes locally.
New timing in R-01 test (sleep(0.2), wait(2.0)) — wall-clock dependent but bounded; not flaky in observed runs. See point 2 for CI edge cases.
Scope check
Read: commits 5394a0f..97180f7 (3343e32, 2711fd7, 45b737e, 97180f7, a85bd96); IMPLEMENTATION/replay_cache.py, authz_sidecar.py, reference_target.py; TESTS/adversarial/test_findings_002.py, test_authz_sidecar.py, test_reference_target.py; EVIDENCE/verification_ledger.md VL-109 + follow-ups 1–3; STATE.md, cursor_whitebox_review_2026-06-16.md (grep).
Executed: full suite 399 green; R-01 deterministic test ×15; lock on/off simulation (1 vs 2 honored); P-01 integration tests ×4; lock-revert simulation (not in-repo file edit).
Not grounded here: live redeploy verification; Envoy production duplicate-header wire form; lock-disabled pytest run via actual file edit (simulation used no-op lock instead).
Adjudication: The R-01/P-01 hardening arc is done for the fixed area. Production fixes are sound; P-01 integration tests are genuine revert-catchers; R-01 revert-catcher is deterministic after 97180f7; follow-up-3 retraction is complete and accurate. Optional follow-up: bump STATE.md:1006 to 399 and add t2-entered synchronization if you want zero CI timing margin on the R-01 test.
