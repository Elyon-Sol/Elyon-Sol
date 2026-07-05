# Elyon-Sol - Verification Ledger

Append-only record of how claims about Elyon-Sol became trusted.

## Rules
- A claim enters as SINGLE-SOURCE when first derived.
- A claim becomes CONFIRMED only when independently re-derived FROM PRIMARY
  SOURCES (canon, code) - never from an artifact that merely asserts it.
- A verdict or rating ("approved", "8.7/10") is NEVER a confirmation event
  and is never recorded here as one. Only derivations against primary sources are.
- Entries are append-only. Corrections are new entries, not edits.
- Each entry cites the sources and, where one exists, the commit hash.

## Status values
SINGLE-SOURCE | CONFIRMED | DISPUTED | RETRACTED | CORRECTED

---

## Entries

## Archived volumes

Older entries are preserved verbatim in immutable, hash-anchored archive volumes under
`EVIDENCE/ledger_archive/` (GR-5). Nothing is deleted: concatenating each volume's entry
region (in order) followed by the entries below reproduces the complete historical ledger
byte-for-byte. Manifest + reconstruction check: `EVIDENCE/ledger_archive/INDEX.md`.
Cross-volume curated map: `EVIDENCE/verification_ledger_index.md`.

| Volume | VL range | Entries | sha256 |
|--------|----------|---------|--------|
| vol_001 | VL-001 .. VL-107 | 133 | `381008b5fedb48555cd1c642529680c04e8ed438ed06b292e2915a08b0bab66a` |

---

## Entries (current era - VL-108 onward)

### VL-108 - 2026-06-16 - G5 Phase 1 executed: four-node public surface live under a real CA; author self-test green over real transport; REAL_TRANSPORT upgraded from the VirtualBox tier to the public surface
**Status:** RECORDED (an execution increment - deployment + author self-test on real public hosts; no gate / verifier / crypto / sidecar code change). Referent-bound: the run log is EVIDENCE/proofs/attack_suite_live_run_2026-06-16.log; the predicate change is EVIDENCE/readiness.json (REAL_TRANSPORT). Grounded per SESSION_PROTOCOL resume + deploy/G5_SESSION_KICKOFF.md.
**Author:** the project author (provisioned the hosts, ran every command, executed the self-test and pasted back the outputs) + Claude (verified the code contracts, generated the exact command syntax, adjudicated outputs, authored this close).
**Classification:** trajectory move - it moves G5 Phase 1 from PLANNED / AUTHOR-locus to DONE (the public surface exists and the author self-test is green over it). It does NOT close G5 (no external attacker yet).

#### What landed (on real hosts; not in the repo)
Four internet-reachable nodes on Hetzner under Let's Encrypt TLS, two continents, single carrier (a deliberate POC / red-team-stage choice; multi-carrier deferred):
- gate.elyon-sol.io:8443 (Helsinki) - pep; holds the private Ed25519 signing key (key id gate-deploy-001); systemd elyon-gate.
- target.elyon-sol.io:9443 (Hillsboro US-West) - reference_target; the primary attack target; SIGNED freshness mode (pinned publisher key); systemd elyon-target.
- pub.elyon-sol.io:9143 (Helsinki) - publisher; serves /published_hashes.json (byte-anchor) + /published_hashes_signed.json (a fresh publisher Ed25519 key, 300s not_after); systemd elyon-pub.
- authz.elyon-sol.io:9243 (Ashburn US-East) - ext-authz sidecar; local pinned record; systemd elyon-authz.
Only the minimal runtime file set was placed on the public hosts (the Dockerfile COPY set), NOT the full repo - canon.md / the ledger / STATE are kept off the attack surface (Gate-4 hygiene + the gate's key custody).

#### What landed (in the repo - this commit)
- EVIDENCE/proofs/attack_suite_live_run_2026-06-16.log - the author self-test over the public surface in signed mode: positive control HONORED + 6/6 adversarial (un-attested / forged / replay / rebind-tool / rebind-args / target-swap) refused, exit 0.
- EVIDENCE/readiness.json - REAL_TRANSPORT.proof re-pointed from the VirtualBox / dev-CA log (real_transport_attack_001.log, VL-090) to the public-surface log; blocked_by rewritten to the upgraded honest bound.
- STATE.md - Last-updated -> VL-108 (VL-107 -> PREVIOUS, VL-106 dropped); a Current-verified-state bullet; the Next-open-action pre-exposure checklist.

#### Honest ceiling (carry it intact)
The self-test is the AUTHOR's OWN scripted attack and exercises the 6 gate-2 cases + positive control ONLY. Claims 8-13 (drift / expired decision / issuer-key + root revocation / stale published record / the authz sidecar live-ALLOW path) are in-house-tested (the suite + the VL-104/105/106 sidecar work) but were NOT live-adversarially-exercised over the public surface this session. REAL_TRANSPORT's definition (the VL-079 gate-2 suite over real transport) is met; it does not assert the wider claim set. G5 (GR-3) - a real EXTERNAL stranger on the public surface - remains NOT-MET; the project remains NOT-READY for an external-validation / production claim. Standing this up makes the claim TESTABLE by a stranger; it does not make it true.

#### Open items before exposure (now the Next-open-action)
(1) REGENERATE the publisher signing key - it was exposed in the working chat - and re-pin on the target; (2) live-verify the sidecar ALLOW / DENY; (3) backfill the renewal deploy-hook on gate + pub; (4) counsel sign-off on the safe-harbor clause (deploy/SAFE_HARBOR_DRAFT.md); (5) bounty tiers + window + reporting channel; (6) publish the pack + open the listing; (7) commission the Phase 3.2 rebuild estimator.

#### Citation discipline (VL-012)
Prior substantive entry: VL-107. This entry cites VL-083 / VL-090 (the C3-live runner + the prior VirtualBox REAL_TRANSPORT referent it upgrades), VL-081 / VL-082 (the deploy + TLS bring-up artifacts executed), VL-091 (the signed-record freshness mode now configured), VL-104 / VL-105 (the sidecar now live), and VL-103 / VL-107 (artifact 29 + the forks this executes against); it does not cite its own (log + readiness + STATE + ledger) hash.

#### Next trajectory action
The pre-exposure checklist above, then publish + recruit a blind attacker. G5 is MET only when that party engages the live surface.

#### Process finding (appended) - STATE.md truncation from VL-107 (Cowork mount artifact), detected and repaired at VL-108
git object-store inspection during the VL-108 close found that the VL-107 commit (6db8ee5, already pushed) captured a TRUNCATED STATE.md: 1117 lines ending mid-word ("emitting the seventh re") inside the Known-open-gaps G2 bullet, versus the clean 1167-line 24c197a:STATE.md. The Cowork mount served `git add` a truncated working-tree view (the SESSION_PROTOCOL rule-6 stat-cache / ghost hazard); roughly 50 lines (Known-open-gaps G2-tail through G14) were lost on origin. NO content was permanently lost - the section is intact at 24c197a:STATE.md and untouched by VL-107/108 (both edit only the file head). After a Cowork restart re-mounted the folder fresh (rule 8), VL-108 rebuilt STATE.md by applying the VL-108 head edits to HEAD:STATE.md and splicing the clean "## Known open gaps" tail from 24c197a (result 1175 lines, ending correctly at the G14 entry). This VL-108 commit therefore ALSO REPAIRS the VL-107 truncation on origin (forward fix; no history rewrite). Lesson: after a mount-mediated `git add`, verify the committed blob (git cat-file -s / line count vs the prior commit), not only the working-tree grep.

### VL-108 follow-up - 2026-06-16 - pre-exposure items 1-3 executed (publisher key rotated, sidecar claim-13 live-verified, renewal hooks on all nodes)
**Status:** RECORDED (execution follow-up to VL-108; no gate / verifier / crypto code change). Referent-bound: EVIDENCE/proofs/sidecar_live_check.py + EVIDENCE/proofs/sidecar_live_check_2026-06-16.log.
**Author:** the project author (ran every command on the live hosts) + Claude (scripts, adjudication).
Three of the seven VL-108 pre-exposure items are now done:
1. PUBLISHER KEY ROTATED. The publisher Ed25519 signing key exposed in the VL-108 working chat was regenerated on pub (new public half c1eb51c9...; id pub-deploy-001 unchanged) and re-pinned on the target (ELYON_PUBLISHER_KEY_HEX). The old key is dead. Re-verified end-to-end by the item-2 mint (gate -> push -> target accepted under the new key).
2. SIDECAR LIVE-VERIFIED (claim 13). EVIDENCE/proofs/sidecar_live_check.py mints a real envelope from the gate and presents it to authz.elyon-sol.io:9243: a VALID envelope -> ALLOW (200, REASSERTED_AND_BOUND); a TAMPERED one -> DENY (403, REF_VERIFY_SIGNATURE_INVALID). PASS, exit 0 (log: sidecar_live_check_2026-06-16.log). This closes the live-ALLOW gap the VL-108 self-test left open for the sidecar; claim 13 is now live on the public surface (still the author's own check, not an external attacker).
3. CERT-RENEWAL AUTO-RELOAD. /etc/letsencrypt/renewal-hooks/deploy/restart-elyon.sh (restart elyon-*.service) is now on all four nodes (target + authz at bring-up; gate + pub backfilled here), so a renewed cert reloads the service.
Remaining VL-108 pre-exposure items (4-7), unchanged: counsel sign-off on the safe-harbor clause; bounty tiers + window + reporting channel; publish the decontaminated pack; recruit a blind attacker + commission the rebuild estimator. G5 remains NOT-MET. Does not cite its own hash (VL-012).


### VL-109 - 2026-06-16 - Cursor white-box review (Mode A): R-01 + P-01 found & fixed; B-01/F-01/R-02 named-open; in-house hardening, NOT a G5 referent
**Status:** RECORDED (an in-house white-box hardening round + the resulting build fix; verified - full suite 391 -> 394 green on a native run - committed 3343e32 and deployed to all four live nodes; the live sidecar ALLOW/DENY check re-passed). Referent-bound: EVIDENCE/verification_runs/cursor_whitebox_review_2026-06-16.md (adjudicated record); the fixes are IMPLEMENTATION/replay_cache.py + authz_sidecar.py + reference_target.py + TESTS/adversarial/test_findings_002.py at 3343e32.
**Author:** the project author (ran Cursor over the local repo, pasted the findings, ran the suite + redeploy natively) + Claude (designed the scoped Mode-A task, adjudicated every finding against HEAD, wrote the fixes + tests).
**Classification:** in-house WHITE-BOX hardening - the reviewer had the full repo (canon, ledger, tests), the antithesis of blind. Internal evidence, FORBIDDEN to present to a blind reviewer as validation (VL-057 / ext-readiness gate 4). NOT a G5 referent and does not change G5's status. Same conformance/hardening class as VL-106; the value is finding bugs to fix BEFORE a real external attacker arrives (the VirtualBox-tier precedent, VL-087..092).

#### Findings, adjudicated against HEAD (all Cursor citations verified accurate - no fabrication)
- R-01 (REAL, FIXED): InMemoryReplayCache.check_and_claim was a lock-free check-then-set; the ext-authz sidecar runs gate.check via run_in_threadpool, so two concurrent identical POST /authz could both observe a decision_id absent and both claim it -> double ALLOW, a single-use bypass on the LIVE sidecar (would win claim 13). Fix: a threading.Lock over prune+check+set in replay_cache.py; single-threaded behavior byte-identical.
- P-01 (REAL, FIXED): a duplicate X-Elyon-Sol-Envelope / X-Elyon-Sol-Interaction header was first-wins (request.headers.get); attacker-influenced ordering weakened determinism. Fix: a duplicate header is now treated as absent -> fail closed (authz_sidecar.py interaction extractor + envelope read; reference_target.py envelope read).
- B-01 (REAL, NAMED-OPEN): the ext-authz sidecar binds the envelope to the X-Elyon-Sol-Interaction HEADER, not the upstream's executed body/path; in Envoy ext_authz mode it can ALLOW while the upstream runs a different operation. Not a violation of the narrow sidecar claim (the token IS valid) and not live-exploitable on the current STANDALONE sidecar (no upstream behind it), but it defeats the gating property when the sidecar fronts a body-carrying upstream. This is build-order step 4 (the CUSTOM declarative body->interaction mapping), deliberately unbuilt. Action: build step 4 before deploying the sidecar in front of an upstream; state the sidecar's true scope in the attacker pack.
- F-01 (REAL, NAMED-OPEN): the sidecar has no signed-record freshness (ELYON_RECORD_PATH byte-anchor only); a stale-but-anchor-matching record passes currency, bounded by the decision not_after (300s). The target got signed-mode freshness at VL-108; the sidecar should too.
- R-02 (KNOWN boundary): per-process InMemoryReplayCache by default; N workers/replicas without ELYON_REPLAY_REDIS_URL -> N independent seen-sets (cross-process replay). Already documented in readiness.json; NOT live-exploitable (the live nodes run single-worker uvicorn). Action: fail-closed guard when workers>1 without a shared store.
Probed-and-held (the cryptographic core): signed region == sign_envelope; one canonical_json for hash+sign+binding; verifier-core target_url/AP/OP/context binding; manifest_integrity == on-disk + anchor-before-parse; fail-closed error mapping; verify->claim->act ordering; Redis SET NX atomicity. The real findings are in concurrency, deployment-binding, and freshness - not forgery.

#### What landed (the fix; committed at 3343e32, deployed)
replay_cache.py (the lock), authz_sidecar.py + reference_target.py (the duplicate-header guard), TESTS/adversarial/test_findings_002.py (R-01 concurrency single-claim test + P-01 extractor tests). Full suite 391 -> 394 green (native run on the author's reliable filesystem). The fix was redeployed to all four nodes and the live sidecar ALLOW/DENY check re-passed.

#### Process finding (Cowork mount instability)
Twice this session the Cowork mount served truncated WRITES (STATE.md / readiness.json at the VL-108 close) and stale/truncated READS (cp + Python import of edited modules, and a stale pre-fix view of the IMPLEMENTATION files after restart). Remedies used: the SESSION_PROTOCOL rule-8 Cowork restart (fresh mount); building commits from the git object store with blob-integrity verification (cat-file line counts) before update-ref; this VL-109 close was committed via git hash-object from tmpfs to bypass the working tree entirely; and code-edit validation was run on the author's NATIVE filesystem. Standing lesson: in the Cowork sandbox, treat working-tree file reads/writes as untrusted; the object store is the source of truth and every committed blob must be verified.

#### Citation discipline (VL-012)
Prior substantive entry: VL-108 (+ follow-up). This entry cites VL-106 (the internal-evidence / conformance class this round shares), VL-057 / ext-readiness gate 4 (the blind-reviewer-FORBIDDEN bar), VL-087..092 (the find-bugs-before-exposure precedent), VL-076 / VL-094 (the ReplayCache seam behind R-01/R-02), and VL-104 (the sidecar design + the unbuilt step 4 behind B-01/F-01); it does not cite its own (review record + 3 code files + test + STATE + ledger) hash.

#### Next trajectory action
The VL-108 pre-exposure checklist (counsel sign-off, bounty/window/channel, publish, recruit) plus the three named build items B-01 (sidecar body-binding / step 4), F-01 (sidecar signed freshness), R-02 (multi-worker replay guard). G5 remains NOT-MET until a blind external party engages the live surface.

### VL-109 follow-up - 2026-06-16 - P-01 test hardening: duplicate-envelope DENY tests (sidecar + reference target) after the Mode-A round-2 fix-verification
A second Cursor white-box pass VERIFIED 3343e32: R-01 sound (the lock covers all _seen access; one shared cache; the threadpool race is real), P-01 sound for security (every duplicate / comma-folded header form fails closed -> DENY). It found the TESTS inadequate: the P-01 ENVELOPE half was unproven (test_findings_002 covered only the interaction extractor + R-01 concurrency; a reverted envelope guard would have failed no test). Closed here: TESTS/adversarial/test_authz_sidecar.py gains duplicate-X-Elyon-Sol-Envelope -> 403 DENY (valid minted envelope, so it fails on revert) + comma-folded -> 403 fail-closed; TESTS/adversarial/test_reference_target.py gains duplicate-envelope -> REF_VERIFY_ENVELOPE_ABSENT with the target not acting. No production code change (the fix was already sound). Note: test_findings_001 F5 still pins first-wins on the build_enforcing_target_app TEST HARNESS (not production reference_target.py) and is left as-is. In-house white-box hardening, NOT a G5 referent. Suite 394 -> 397 green. Does not cite its own hash (VL-012).

### VL-109 follow-up 2 - 2026-06-16 - R-01 deterministic revert-catcher + P-01 interaction integration test (round-3 sign-off remediation)
The round-3 Cursor sign-off found the R-01 concurrency test (test_findings_002 stress test) was a WEAK revert-catcher: on CPython, removing the lock left it green (0/40, 0/200 rounds) because the GIL serializes the tiny check-then-set. The bug is real (20/20 fails with an injected sleep) and the lock is correctly placed, but the test did not prove it. Also flagged: no sidecar integration test for a duplicate INTERACTION header (unit only). Closed here: TESTS/adversarial/test_findings_002.py gains test_r01_lock_serializes_concurrent_claims - a DETERMINISTIC revert-catcher that forces the interleave via a blocking membership check (with the lock -> exactly one claim; without -> two; verified red-without-lock / green-with-lock); TESTS/adversarial/test_authz_sidecar.py gains a duplicate-INTERACTION-header integration test (valid envelope + [matching, other] -> 403, not first-wins ALLOW). P-01 envelope tests already confirmed real revert-catchers (Starlette TestClient delivers duplicate fields separately via multi_items). No production code change. test_findings_001 F5 (old-harness first-wins) left as-is. In-house white-box hardening, NOT a G5 referent. Suite 397 -> 399 green. Does not cite its own hash (VL-012).

### VL-109 follow-up 3 (CORRECTION) - 2026-06-16 - the follow-up-2 R-01 revert-catcher did not catch the revert; test fixed + false claim retracted
Process-integrity correction (self-caught). VL-109 follow-up 2 (commit 45b737e) claimed test_r01_lock_serializes_concurrent_claims was "verified red-without-lock / green-with-lock." That claim was FALSE: with the lock disabled (with self._lock: -> if True:) the test still PASSED (1 passed, not failed), so it did NOT catch the revert. Cause: BlockingSeen.__contains__ returned a FRESH dict.__contains__ AFTER release.wait, so once both threads unblocked the GIL ran them serially and the first thread's seen[decision_id]=... completed before the second thread's membership check returned -> [True, False] (count 1) even with no lock. Fix (this entry): capture membership BEFORE blocking and return the stale value, so both threads observe "absent" before either sets -> [True, True] (count 2) when unlocked. NOW PROPERLY VERIFIED: lock present -> 1 passed; lock disabled (if True:) -> 1 FAILED ("R-01: 2 concurrent claims honored"); lock restored -> 399 passed. The R-01 PRODUCTION fix (the lock in replay_cache.py) was always sound - the round-3 Cursor sign-off confirmed it and demonstrated the real bug with an injected sleep; only the test and the follow-up-2 "verified" wording were wrong. Same self-correction family as VL-012 (corrected self-referencing hash). Suite 399 green. Does not cite its own hash (VL-012).

### VL-109 follow-up 4 - 2026-06-16 - Cursor verification-run records committed; STATE suite-count corrected; zero-timing R-01 revert-catcher added
Referent-binding + cleanup. (1) The Cursor white-box rounds were committed to EVIDENCE/verification_runs/ so the arc is referent-bound (not chat-only): cursor_whitebox_review_2026-06-16.md (round 1, adjudicated), cursor_fix_verification_2026-06-16.md (round 2, "TESTS INADEQUATE"), cursor_fix_signoff_2026-06-16.md (round 3, "TEST WEAKNESS"), cursor_final_signoff_2026-06-16.md (round 4, "FINAL SIGN-OFF"). All are WHITE-BOX in-house records (full-repo reviewer; internal evidence, FORBIDDEN to show a blind reviewer as validation per VL-057); NOT G5 referents. (2) STATE.md suite-count corrected (the VL-109 bullet said 394, which was point-in-time; now notes 399 after follow-ups 1-3). (3) Added test_r01_check_and_claim_acquires_lock - a zero-timing structural R-01 revert-catcher (asserts check_and_claim enters the lock; no concurrency/sleep dependence), retiring the timing-margin caveat the round-4 sign-off flagged. Suite 399 -> 400 green. No production code change. Does not cite its own hash (VL-012).


### VL-110 - 2026-06-16 - cross-model white-box round (3 clean runs): R-01/P-01 + crypto core re-confirmed; named-posture gaps; R-02 guard + B-01 scope applied; B-01-step-4/F-01/K-01 scheduled
**Status:** RECORDED (a cross-model white-box round adjudicated under VL-008, plus two hardening increments + a schedule; suite +1 test). Referent-bound: the fixes are IMPLEMENTATION/replay_cache.py (R-02 guard) + IMPLEMENTATION/authz_sidecar.py (B-01 docstring) + TESTS/adversarial/test_findings_002.py (R-02 test) + deploy/LIVE_BRINGUP_RUNBOOK.md (posture note). The three verbatim run outputs are a pending referent commit under EVIDENCE/verification_runs/cursor_xmodel_*.
**Author:** the project author (ran the identical prompt across Cursor's models, pasted the outputs) + Claude (cross-model adjudication, the two fixes, the schedule).
**Classification:** WHITE-BOX in-house (every model had the full repo) - internal evidence, FORBIDDEN to a blind reviewer (VL-057), NOT a G5 referent. Conformance/hardening class (VL-106 precedent).

#### The round
Identical scoped adversarial+verify prompt run across distinct model families (one Anthropic-class labeled "cursor", Grok/xAI, OpenAI). Procedure check: all three procedurally clean - scope checks present, citations specific; the one novel claim (K-01) spot-checked accurate vs HEAD; NO fabricated citations in any run (contrast VL-102/106 Gemini). No runs discarded.

#### Unanimous (>=2 clean runs) - CONFIRMED
R-01 SOUND (all 3); P-01 SOUND (all 3); the cryptographic enforce path holds (signature/canonical-JSON determinism, AP/OP+target+context binding, anchor pinning, fail-closed, in-process replay atomicity) - all 3 "held". NO new protocol/crypto break found by any model.

#### Findings - all already-NAMED deployment-posture gaps; none exploitable on the current single-worker/standalone surface
- B-01 (sidecar binds the X-Elyon-Sol-Interaction HEADER, not the upstream's executed body): CONVERGENT - raised by 2 models, OpenAI rated High. Not a break of the narrow sidecar claim (the token is valid) and not exploitable on the standalone sidecar (no upstream behind it), but it defeats gating once the sidecar fronts a body-carrying upstream. = build-order step 4.
- R-02 (per-process InMemoryReplayCache default; >1 process/replica without a shared store => cross-process replay): documented in readiness.json; not exploitable single-worker.
- F-01 (sidecar byte-anchor only, no signed-record freshness): bounded by the 300s decision window; target already has signed mode.
- K-01 (issuer-key revocation/window check is only on the key_record_view branch; the default static-pin enforce path skips it - verifier.py:322-336 inside `if key_record_view is not None`, default consumers pass pinned_public_keys only): documented (issuer_key_revocation built, wired_to_default false); only matters under gate-key compromise (an out-of-band floor) and is bounded by the 300s envelope not_after.

#### Applied this entry
- R-02 fail-closed guard: replay_cache_from_env() now raises if ELYON_REPLAY_MULTI_INSTANCE is set without ELYON_REPLAY_REDIS_URL; default single-instance path (InMemory) byte-behavior-unchanged. Revert-catcher test_r02_multi_instance_without_shared_store_fails_closed.
- B-01 scope: a SECURITY SCOPE docstring on default_interaction_extractor + a deploy-posture note (do not deploy the sidecar inline in front of a body-carrying upstream until step 4).

#### Scheduled (named-open build items; none blocking the current surface)
- B-01 step 4: derive the sidecar interaction from the Envoy ext_authz request (method/path/body) instead of the client header.
- F-01: wire signed-record freshness into the sidecar (mirror reference_target's optional signed mode).
- K-01: pass key_record_view into verify_envelope on the default enforce surfaces (or shrink ELYON_DECISION_MAX_AGE_SECONDS to bound revocation lag).

#### Citation discipline (VL-012)
Prior substantive entry: VL-109 (+ follow-ups). This entry cites VL-008 (the cross-model procedure + discard rule), VL-106 (the conformance/internal-evidence class + surplus-run posture), VL-057 (the blind-reviewer-FORBIDDEN bar), VL-076/094 (the ReplayCache seam behind R-02), VL-104 (the sidecar design + step 4 behind B-01), and VL-042 (the key-record view behind K-01); it does not cite its own hash.

#### Next trajectory action
The VL-108 pre-exposure checklist (counsel, bounty/window/channel, publish, recruit) + the three scheduled build items above. G5 remains NOT-MET until a blind external party engages.


### VL-110 follow-up - 2026-06-16 - cross-model run outputs committed (referent-binding)
The three verbatim cross-model run outputs from VL-110 are now committed (closing the "pending referent commit" note): EVIDENCE/verification_runs/cursor_xmodel_cursor_2026-06-16.md, cursor_xmodel_grok_2026-06-16.md, cursor_xmodel_openai_2026-06-16.md - each with a WHITE-BOX / internal / NOT-a-G5-referent provenance header (VL-057), ASCII-normalized (VL-009). No code/test/STATE change. Does not cite its own hash (VL-012).

### VL-111 - 2026-06-17 - B-01 build-order step 4 BUILT: sidecar interaction derived from the ext_authz request BODY (in-house half of B-01 closed); build-then-wire, NOT a G5 referent
**Status:** RECORDED (an in-house build increment on the derivative OPA-sidecar track; build-then-wire, no existing default path changed; TESTS suite 401 -> 411). Referent-bound: the build is IMPLEMENTATION/authz_sidecar.py (`build_request_body_extractor` + `_resolve_tool` + an await-aware decision-path line + the narrowed SECURITY SCOPE / module / param docstrings) and TESTS/adversarial/test_authz_sidecar_body_binding.py (10 tests); the deploy-posture note is deploy/LIVE_BRINGUP_RUNBOOK.md. Grounded per SESSION_PROTOCOL resume against docs/design/opa_sidecar_design.md section 5 + 11 step 4, the VL-110 B-01 finding, and the verifier binding contract (verifier.py interaction binding: AP/OP/context/manifest-pinning equality).
**Author:** Claude (Cowork session) at the author's request (pick up B-01 step 4); the author commits + pushes natively.
**Classification:** trajectory move per VL-017a on the DERIVATIVE (OPA-sidecar) track - it closes the in-house half of the named-open B-01 gap. It is WHITE-BOX in-house build, NOT external validation and NOT a G5 referent; G5 is unchanged.

#### What B-01 step 4 is, and what this build does
B-01 (VL-109/110, cross-model convergent, OpenAI rated High): the sidecar's DEFAULT extractor reads the live interaction from the client-controllable X-Elyon-Sol-Interaction header. That is safe for the standalone decision endpoint (nothing executes a body behind it) but unsafe INLINE in front of a body-carrying upstream - the header need not match the bytes the upstream executes, so a valid envelope + benign header + a different body would gate-pass while a different action executes. Step 4 builds the CUSTOM (declarative-mapping) extractor design section 5 named: `build_request_body_extractor` derives the interaction from the ext_authz REQUEST BODY - context.args_sha256 = sha256(canonical_json(args)) over args taken from the forwarded body (whole body, or a named sub-field), reproducing IMPLEMENTATION/mcp_server.interaction_for's shape byte-identically so the gate's binding compares as before. The deployer authors the static parts (AP/OP, manifest pinning, where the tool identity comes from: a const, the path, or a header). Because Envoy forwards the same body to the sidecar and the upstream, the digest binds the envelope to the EXECUTED bytes.

#### Build-then-wire (no default path changed)
The DEFAULT extractor stays header-read and remains the module-level deployable app's extractor; nothing is wired to the body extractor by default. The only decision-path edit is an `inspect.isawaitable` await of the extractor result (the body extractor is async because it must read request.body()); the default sync extractor returns directly and is byte-behavior-identical. New module imports: hashlib, inspect, canonical_json, typing List/Union.

#### Tests (TESTS/adversarial/test_authz_sidecar_body_binding.py, +10)
allow-on-matching-body (+ reordered-keys, proving the canonical_json digest is order-independent); deny-on-tampered-body (REF_VERIFY_BINDING_MISMATCH); the headline B-01 inline-rebind DEFEATED by the body extractor; a CONTRAST test asserting the DEFAULT header extractor ALLOWs the same rebind (documents the gap the build closes, not a vulnerability in the standalone endpoint); tool-from-path and args-from-body-field mapping variants; three fail-closed paths (unparseable body, missing args field, absent tool header) - each -> DENY, never an exception, never fail-open.

#### Honest ceiling / what is NOT closed
The IN-HOUSE half of B-01 is closed: the capability now exists and is tested. SAFE inline operation still requires a DEPLOYMENT step not done here: inject this extractor AND configure Envoy `with_request_body` so the sidecar receives the same bytes the upstream executes (if Envoy is not configured to forward the body, or forwards a truncated/size-limited body, the guarantee does not hold). Until that wiring, the default header-read mode still must not go inline. This is white-box in-house work; it is not a G5 referent and does not change G5 (still NOT-MET, the only open ROAD item). F-01 (sidecar signed-record freshness) and K-01 (key_record_view on the default enforce path) remain scheduled.

#### Verification environment note (VL-108 hazard recurred - read before trusting the commit)
The Cowork mount served TRUNCATED working-tree reads this session (e.g. replay_cache.py cut at line 194; the edited authz_sidecar.py cut mid-docstring) - the same stat-cache / ghost hazard VL-108 recorded. The full suite was therefore validated NOT against the mount but against a pristine `git archive HEAD` extraction (object-store, mount-independent) into a clean tmpfs tree, with the behavior-bearing edits (imports, factory, await-handler) re-applied there: 10/10 new tests pass and the full TESTS collection is 411 passed, 0 failed (401 baseline + 10). The host file tools wrote the real laptop files intact; the AUTHOR MUST verify the committed blobs natively (git cat-file -s / line count vs the prior commit, per the VL-108 lesson) before pushing, because a mount-mediated `git add` could capture a truncated blob.

#### Citation discipline (VL-012)
Prior substantive entry: VL-110 (+ follow-up). This entry cites VL-104 (the sidecar design + the originally-deferred step 4), VL-109/110 (the B-01 finding it builds against, incl. the convergent/High rating), VL-076 (the ReplayCache seam the sidecar shares, unchanged here), VL-018 (the request_validator dedupe+sort normalization reused for byte-identical binding), and VL-108 (the Cowork mount truncation hazard whose recurrence shaped this session's verification path); it does not cite its own hash.

#### Next trajectory action
F-01 (wire sidecar signed-record freshness) and K-01 (pass key_record_view on the default enforce path) - the two remaining scheduled build items - plus the VL-108 pre-exposure checklist (counsel safe-harbor sign-off, bounty tiers/window/channel, publish, recruit). G5 remains NOT-MET until a blind external party engages the live surface.

### VL-112 - 2026-06-17 - F-01 BUILT: optional signed-record (freshness) mode wired into the ext-authz sidecar; build-then-wire, NOT a G5 referent
**Status:** RECORDED (an in-house build increment on the derivative OPA-sidecar track; build-then-wire, no existing default path changed; TESTS suite 411 -> 419). Referent-bound: the build is IMPLEMENTATION/authz_sidecar.py (config_from_env signed-mode resolution + the handler's signed-mode gate branch + the three ENV_PUBLISHER_*/SIGNED_RECORD_PATH names + the published_record_source import + docstring) and TESTS/adversarial/test_authz_sidecar_freshness.py (8 tests). Grounded per SESSION_PROTOCOL resume against the VL-110 F-01 finding, IMPLEMENTATION/reference_target.py's signed mode (VL-091, the pattern mirrored), IMPLEMENTATION/published_record_source.py (load_signed_record_from_bytes, VL-074), and IMPLEMENTATION/executor_sdk.py (ExecutorGate's record_source path).
**Author:** Claude (Cowork session) at the author's request (pick up F-01); the author commits + pushes natively.
**Classification:** trajectory move per VL-017a on the DERIVATIVE (OPA-sidecar) track - it closes the named-open F-01 gap (sidecar lacked signed-record freshness). WHITE-BOX in-house build, NOT external validation and NOT a G5 referent; G5 unchanged.

#### What F-01 is, and what this build does
F-01 (VL-109/110): the sidecar consulted only the BYTE-ANCHOR record (published_source: sha256 of the record bytes), which has NO temporal dimension - a stale-but-anchor-matching record is honored arbitrarily later (A3b sub-case (b)). The reference target already had the signed mode (VL-091): with a pinned publisher key it consults a SIGNED record carrying serial + not_after, so a stale record fails closed. This build gives the sidecar the same option. The sidecar differs from the target in transport: the target FETCHES the signed record over HTTP (fetch_signed_record); the sidecar reads a LOCAL file (it already reads the byte-anchor record from ELYON_RECORD_PATH), so it uses the pure, network-free `load_signed_record_from_bytes` and passes the validated record dict to ExecutorGate as `record_source=`.

#### Wiring (mirror of reference_target's signed mode)
- config_from_env: optional signed mode triggered by ELYON_PUBLISHER_KEY_ID + ELYON_PUBLISHER_KEY_HEX (parity with the target). When present it reconstructs the pinned publisher key (malformed -> None -> REF_TARGET_NOT_CONFIGURED) and READS the local signed record from ELYON_SIGNED_RECORD_PATH (default: the ELYON_RECORD_PATH sibling filename published_hashes.json -> published_hashes_signed.json, the same derivation the target uses for its signed URL); an unreadable file is a config fault -> None. It stores `pinned_publisher_keys` + `signed_record_bytes`. The freshness/signature DECISION is deferred to the handler so it surfaces the right reason rather than NOT_CONFIGURED.
- handler: when `pinned_publisher_keys` is configured, validate the signed record per request (load_signed_record_from_bytes with the config clock_skew); a non-None reason -> _deny(reason) (REF_VERIFY_PUBLISHED_RECORD_STALE / _INVALID); otherwise build the gate with `record_source=<validated record>`. No publisher key -> the unchanged record_bytes + pinned_root gate (byte-anchor).

#### Build-then-wire (no default path changed)
Absent a publisher key, config and the gate construction are byte-behaviour-identical to pre-VL-112; the module-level deployable app is unchanged. No new admissibility logic, no new cryptography, no new refusal code (the two REF_VERIFY_PUBLISHED_RECORD_* codes are reused from the verifier namespace via the existing reader). New import: published_record_source.load_signed_record_from_bytes.

#### Tests (TESTS/adversarial/test_authz_sidecar_freshness.py, +8)
fresh signed record -> ALLOW (REASSERTED_AND_BOUND); stale (not_after in the past) -> DENY REF_VERIFY_PUBLISHED_RECORD_STALE; record mutated after signing -> DENY REF_VERIFY_PUBLISHED_RECORD_INVALID; record signed by a non-pinned key -> INVALID; byte-anchor default (no publisher key) still ALLOWs; and three config_from_env paths (signed-mode resolves; malformed publisher key -> None; missing signed file -> None). The signed record is signed in-test by a generated publisher Ed25519 key over the reader's exact canonicalization (canonical_json of the record minus publisher_signature), carrying the live currency pins so reassert honors.

#### Honest ceiling / what is NOT closed
F-01's in-house build is closed: the sidecar can now run in signed (freshness-checked) mode. Operating in that mode is a DEPLOYMENT choice (pin a publisher key + mount a signed record); the live surface today runs the target in signed mode but the sidecar's signed mode is newly available, not yet exercised on the public surface. White-box in-house work; not a G5 referent; G5 unchanged (still NOT-MET, the only open ROAD item). K-01 (pass key_record_view on the default enforce path) is the last remaining scheduled build item; B-01 step 4 closed at VL-111.

#### Verification environment note (VL-108 hazard persists)
The Cowork mount continued to serve TRUNCATED working-tree reads this session. The suite was again validated NOT against the mount but against a pristine `git archive HEAD` (5ea2be0) extraction into a clean tmpfs tree, with the behavior-bearing edits (import, env names, config signed block, handler branch) re-applied there: the 8 new tests + the body-binding + existing sidecar tests pass (36/36 in that group) and the full TESTS collection is 419 passed, 0 failed (411 baseline + 8). The host file tools wrote the laptop files intact; the AUTHOR MUST verify the committed blobs natively (git cat-file -s / line count vs the prior commit) before pushing, per the VL-108 lesson.

#### Citation discipline (VL-012)
Prior substantive entry: VL-111. This entry cites VL-091 (the reference target's signed mode it mirrors), VL-074 (published_record_source.load_signed_record_from_bytes + the REF_VERIFY_PUBLISHED_RECORD_* codes), VL-075 (the clock_skew tolerance reused), VL-078 (ExecutorGate's record_source path), VL-109/110 (the F-01 finding it builds against), and VL-108 (the persisting Cowork mount truncation hazard); it does not cite its own hash.

#### Next trajectory action
K-01 (pass key_record_view on the default enforce path so issuer-key revocation is honored there) - the last scheduled build item - plus the VL-108 pre-exposure checklist (counsel safe-harbor sign-off, bounty tiers/window/channel, publish, recruit). G5 remains NOT-MET until a blind external party engages the live surface.

### VL-113 - 2026-06-17 - T-governance: Feature 1 increment 1a - impact classification (requires_approval) built-then-wire with review fixes H1+H2

#### What landed
The first increment of the governance-layer build (spec: docs/design/governance_layer_design.md,
corrected). A new orchestration-layer module IMPLEMENTATION/impact.py provides two pure,
manifest-derived functions: safe_high_impact(manifest) validates the new HIGH_IMPACT manifest
field, returning a set of selector tokens or None (the fail-closed sentinel) on any malformation;
requires_approval(ctx, manifest) returns True iff the interaction is high-impact and therefore
needs an out-of-band human approval grant before forward, fail-closed (any doubt -> True).

Two adversarial-review fixes are baked in and pinned by revert-catchers:
- [FIX H1] a MISSING or malformed HIGH_IMPACT fails CLOSED (-> requires approval), never the
  `.get(..., [])` empty-set that would silently disable oversight for the whole deployment. An
  EXPLICIT empty list is the operator's conscious "nothing is high-impact" opt-out (distinct
  from a missing key, which is None).
- [FIX H2] every HIGH_IMPACT selector token must be a member of the manifest's required sets
  (AR u R); a token outside them is a manifest error -> fail closed. Because coverage already
  forces AP>=AR and OP>=R, an ELIGIBLE caller cannot omit a high-impact token to self-declare
  low-impact. Impact is a property of the interaction TYPE (the pinned manifest), not a
  caller-set flag.

#### Placement decision (why impact.py, not evaluator.py as the base design suggested)
envelope.reassert() pins evaluator_sha256 = sha256(IMPLEMENTATION/evaluator.py). Adding the
functions to evaluator.py changed its hash and made every envelope verified against a pinned
published record read as an evaluator-version TRANSITION (canon 12.4 -> RE_EVALUATE_REQUIRED),
which RED-ed 49 verify-against-pinned-record tests in the clean-extraction run. Impact
classification is orchestration-layer logic that lives ABOVE G(I) (the PENDING_APPROVAL layer),
so it belongs in its own module; impact.py reuses evaluator.safe_set and leaves evaluator.py
byte-identical (hash unchanged, verified). This keeps the hash-pinned core predicate stable and
the G(I) boundary clean; recorded as a refinement of design section 1.7.

#### Canon / build-then-wire posture
Canon UNTOUCHED (GR-1); both governance features layer above G(I), no canon hash change.
Build-then-wire: requires_approval has NO caller on the default pep.py path this increment;
evaluator.py and safe_manifest()/evaluate() are byte-identical to HEAD (verified by sha), so the
default decision path is byte-behavior-unchanged. Wiring into pep.governed_call (design 1.3 /
increment 1c) is a later increment; the oversight GUARANTEE is not claimed until Feature 2
(non-bypassable) is built, and no readiness predicate goes green on Feature 1 alone.

#### Tests + revert-catcher discipline
TESTS/adversarial/test_requires_approval.py adds 10 tests; suite 419 -> 429 green in a pristine
`git archive HEAD` extraction. Three starred revert-catchers were each proven to go RED when its
fix is reverted, then GREEN when restored: missing HIGH_IMPACT -> requires approval (RED when
reverted to `.get(...,[])`) [FIX H1]; out-of-band HIGH_IMPACT token -> fail closed (RED when the
AR u R subset check is dropped) [FIX H2]; eligible-and-low-impact-by-omission is unreachable (RED
on the same revert) [FIX H2].

#### Spec-defines-the-change
docs/design/governance_layer_design.md (the uploaded design + the eight review fixes H1-H8 marked
inline) is the spec commit and precedes the build commit, per the project's spec-defines-the-change
pattern.

#### Honest scope / GR-3
Impact is TOKEN-level, not semantic (a benign-labelled call that is semantically high-impact is
out of scope by design). The remaining six review fixes (H3-H8: grant single-use under scale,
binding to decision_sha256 + gate-side pending-state, SoD as custody, the 202 state-machine
placement, grant freshness reuse, and the audit-reconcile extension) are scheduled for increments
1b-1d. WHITE-BOX in-house build; NOT external validation (GR-3); does not enter the attacker pack.

#### Files affected
docs/design/governance_layer_design.md (NEW/corrected - the spec); IMPLEMENTATION/impact.py (NEW);
TESTS/adversarial/test_requires_approval.py (NEW); STATE.md (Last-updated + governance item in
Next open action); EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
IMPLEMENTATION/evaluator.py (byte-identical, hash unchanged), pep.py, envelope.py, verifier.py,
MANIFEST/manifest.json, CANON/*, EVIDENCE/readiness.json - all unchanged.

#### Environment note (Cowork sandbox)
Validated against a pristine `git archive HEAD` extraction because the mount is again truncating
working-tree reads (VL-108 hazard: HEAD STATE.md 1187 lines vs mount 1085; ledger 16270 vs 16139;
authz_sidecar.py 581 vs 309). The commit chain was built from HEAD-intact blobs and written to a
side ref (refs/heads/governance-f1-inc1); main is UNTOUCHED. The AUTHOR MUST, natively: rebuild
the working tree from HEAD (clear the truncation per SESSION_PROTOCOL rule 2), verify the
committed blobs, fast-forward main to the side ref, and push (the sandbox has no push credentials,
rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Feature 1 increment 1b: IMPLEMENTATION/approval.py - the approval grant (build/sign/verify)
reusing envelope.py's Ed25519 + binding to decision_sha256 [FIX H4] + freshness reuse [FIX H7].
Then 1c (pep.py wiring: 202 state machine [FIX H6]; pending-state + grant replay cache
[FIX H3/H4]; REF_APPROVAL_*; approver-key custody/role [FIX H5]) and 1d (issuance-log + reconcile
extension [FIX H8]; approver CLI). The G5 external-readiness road is unchanged and parallel.

### VL-114 - 2026-06-17 - T-governance: Feature 1 increment 1b - the approval grant (approval.py) built-then-wire with review fixes H3/H4/H5/H7

#### What landed
IMPLEMENTATION/approval.py - the approval GRANT (the out-of-band, human-signed object that
releases a held high-impact decision). Three functions mirror envelope.py's Ed25519 +
canonical_json discipline (reuse, not re-implement): build_grant() (unsigned grant bound to
decision_sha256 + approval_request_id + a mandatory grant_id + a tz-aware not_after),
sign_grant() (adds approver_key_id + approver_signature over canonical_json(grant minus the
signature), duck-typed key like sign_envelope), and verify_grant() (a pure verifier returning
{accepted, reason} over the REF_APPROVAL_* vocabulary).

Review fixes baked in and pinned by revert-catchers:
- [FIX H4] the grant binds decision_sha256 (transitively target_url / AP / OP / context /
  manifest pins) AND approval_request_id; an approval of action A cannot release action/args/
  target B, nor a different held request.
- [FIX H3] grant_id is MANDATORY (a grant without it is REFUSED); this guarantees the later
  single-use claim (1c) has a non-skippable key - it forbids the executor_sdk "id is None ->
  skip" replay hole at the grant layer.
- [FIX H5] separation of duties: verify_grant rejects approver_key_id == gate_key_id BEFORE the
  signature check, so a gate-minted approval is refused even if well-signed. This is the
  belt-and-braces id check; the load-bearing custody invariant (the gate cannot resolve the
  approver PRIVATE key; approver provenance/role from the signed key-record chain) is the
  1c/deploy layer.
- [FIX H7] freshness REUSES one primitive: verifier.not_after_valid() was factored out of
  verify_envelope step 1.5b (behavior-preserving; suite green) and is called by both. A grant's
  not_after is MANDATORY (absent -> REFUSE, unlike an envelope where absent = no expiry);
  tz-naive or past -> REFUSE; clock_skew tolerated symmetrically.

#### Scope boundary (1b vs 1c)
verify_grant is PURE - crypto provenance, action/request binding, SoD, freshness - over the trust
inputs the caller passes. It does NOT consume the grant: SINGLE-USE (claim grant_id once via the
VL-076 ReplayCache seam) and the server-side pending-request set are STATEFUL gate concerns wired
in pep.governed_call at 1c. Build-then-wire: approval.py has NO caller on the default pep.py path
this increment.

#### Canon / build-then-wire posture
Canon UNTOUCHED (GR-1); the grant lives ABOVE G(I). evaluator.py and impact.py byte-identical to
the VL-113 tip (verified). verifier.py changed only by the behavior-preserving extraction of
not_after_valid; verifier.py is not hash-pinned (the envelope pins canon.lock, evaluator.py,
manifest.json), so the refactor touches no pinned record. No default pep.py path changed.

#### Tests + revert-catcher discipline
TESTS/adversarial/test_approval.py adds 14 tests over REAL Ed25519 keypairs; suite 429 -> 443
green in a pristine git archive extraction (from the VL-113 tip). Five starred revert-catchers
each proven RED on revert then GREEN restored: action binding [H4], request binding [H4],
mandatory grant_id [H3], SoD [H5], freshness/expired [H7].

#### Honest scope / GR-3
The remaining fixes are 1c/1d: gate-side pending-state + grant single-use claim under scale (the
stateful half of [H3]/[H4]), the 202 state-machine placement ([H6]), approver-key custody/role
via the signed key-record chain (the load-bearing half of [H5]), and the issuance-log + reconcile
extension ([H8]). WHITE-BOX in-house build; NOT external validation (GR-3); does not enter the
attacker pack. The oversight GUARANTEE is still not claimed (needs Feature 2); no readiness
predicate goes green on Feature 1 alone.

#### Files affected
IMPLEMENTATION/approval.py (NEW); IMPLEMENTATION/verifier.py (extract not_after_valid and reuse it
in step 1.5b - behavior-preserving); TESTS/adversarial/test_approval.py (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
IMPLEMENTATION/evaluator.py + impact.py (byte-identical), pep.py, envelope.py, MANIFEST/*,
CANON/*, EVIDENCE/readiness.json - unchanged.

#### Environment note (Cowork sandbox)
Validated against a pristine git archive extraction (mount truncation, VL-108). The commit chain
was built from VL-113-tip-intact blobs on side ref refs/heads/governance-f1-inc2; main is
untouched. The AUTHOR verifies the blobs natively, fast-forwards main, and pushes (no sandbox push
credentials; SESSION_PROTOCOL rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Feature 1 increment 1c: pep.governed_call wiring - the 202 PENDING_APPROVAL state machine as an
explicit early return outside the sign/forward try ([FIX H6]); the requires_approval gate; a
gate-side pending-request set issuing/consuming approval_request_id; grant single-use via the
ReplayCache seam claimed atomically before forward, shared-store-under-scale ([FIX H3]/[FIX H4]);
REF_APPROVAL_* surfaced as 202/403; approver-key trust via the signed key-record chain with an
approver role ([FIX H5]). Then 1d (issuance-log + reconcile extension [FIX H8]; approver CLI).

### VL-115 - 2026-06-18 - T-governance: Feature 1 increment 1c - the pep approval WIRING (the first default-path touch + first stateful gate)

#### What landed
pep.governed_call gains the approval gate that turns the held PENDING_APPROVAL design (1.3) into
running code. This is the first increment that (a) touches the DEFAULT path and (b) makes the gate
STATEFUL, so the prior increments' "default path byte-identical" guarantee now holds by explicit
no-op rather than by absence of a caller.

Manifest groundwork:
- MANIFEST/manifest.json gains an EXPLICIT HIGH_IMPACT: [] - the operator's conscious "nothing is
  high-impact yet" opt-out ([FIX H1]); requires_approval therefore returns False on the default
  manifest, so the default forward path is byte-behavior-unchanged.
- That changed manifest_sha256, so EVIDENCE/published_hashes.json was REGENERATED via
  EVIDENCE/published_hashes_gen.py (constraint i: never hand-copied). No committed SIGNED record
  exists, so no publisher-key re-sign was needed (that remains author-locus if/when a signed
  record is introduced).
- The suite's one hand-coded manifest-sha literal (TESTS/adversarial/test_request_schema.py
  LIVE_MANIFEST_SHA256) was made live-derived via manifest_sha256(), matching the VL-034
  derive-live discipline so the fixture survives manifest changes.

The gate (IMPLEMENTATION/pep.py), placed AFTER the ELIGIBLE+envelope build and BEFORE the
sign/forward try-blocks, as explicit early returns/raises ([FIX H6]):
- requires_approval(normalized_interaction, manifest) - manifest-derived, fail-closed (any
  exception -> treat as high-impact).
- high-impact + NO grant -> 202 PENDING_APPROVAL: issue an approval_request_id bound to this
  decision_sha256, record it in the gate-side pending set, and return WITHOUT sign / issuance-log
  / post_to_target. The envelope is built (unsigned) first only to read decision_sha256; building
  has no side effects.
- high-impact + grant present (off the X-Elyon-Sol-Approval-Grant header): verify_grant
  (provenance / decision+request binding / SoD / freshness), then consume the 202 slot from the
  pending set ([FIX H4]: must be issued, unconsumed, and bound to THIS decision), then claim
  grant_id exactly once via the VL-076 ReplayCache seam ([FIX H3]) - both BEFORE the forward. A
  bad/expired/forged/replayed/unknown grant -> 403 REF_APPROVAL_*. An approved grant falls through
  to the SINGLE existing sign + issuance-log + forward (no second forward).
- Approver trust is an injected/env public-key map (_get_approver_keys) with a gate_key_id SoD
  check ([FIX H5] custody half: the gate holds only PUBLIC approver keys; the private key is never
  resolvable by the gate). Two REF_APPROVAL_* codes added for the wiring layer
  (REF_APPROVAL_REPLAY, REF_APPROVAL_REQUEST_UNKNOWN).

The build/sign split: the old single try (build+sign+log) is split into a build try and a
sign+log try with the approval gate between; for the default path the outcomes are identical (any
build/sign/log exception still -> REF_PEP_FAIL_CLOSED).

#### Canon / build-then-wire posture
Canon UNTOUCHED (GR-1); the new states live ABOVE G(I). evaluator.py and impact.py byte-identical
to the VL-114 tip; approval.py changed only by +2 surfaced codes. The default path (HIGH_IMPACT
empty) is byte-behavior-unchanged: the full pre-existing suite stays green. manifest.json is a
legitimate manifest change (a new pinned field), reflected in the regenerated published record -
NOT a canon change.

#### Tests + revert-catcher discipline
TESTS/test_pep_approval.py adds 9 tests over TestClient (202 hold; approved-forwards-once;
binding/SoD/expired/replay/unknown-request/unknown-key refusals each asserting NO forward;
non-high-impact unchanged). Suite 443 -> 452 green in a pristine git archive extraction (from the
VL-114 tip). The core revert-catcher - high-impact + no grant -> 202 AND requests.post NEVER
called - was proven RED when the approval gate is removed (the high-impact call then forwards
without approval) and GREEN restored. requires_approval is monkeypatched True in the wiring tests
(classification itself is unit-tested at VL-113); these pin the H6 placement, H4 pending binding,
and H3 single-use.

#### Honest scope / GR-3
The pending-request set and the grant single-use cache are IN-PROCESS; under horizontal scale a
202 issued on one instance and approved on another, or a grant replayed across instances, needs a
SHARED store (the same R-02 story as the executor replay cache) - a scheduled wiring, single-
instance is exact. The [FIX H5] LOAD-BEARING half (approver-key provenance + an explicit approver
role via the signed key-record chain) is scheduled; a static/injected pin is the minimal viable
now. The [FIX H8] audit half (issuance-log + reconcile records held requests and grant
consumption, with a predicate that no high-impact forward lacks a recorded grant) is 1d. The
oversight GUARANTEE is still NOT claimed - it requires Feature 2 (non-bypassable); no readiness
predicate goes green on Feature 1 alone. WHITE-BOX in-house build; NOT external validation (GR-3);
does not enter the attacker pack.

#### Files affected
MANIFEST/manifest.json (add HIGH_IMPACT: []); EVIDENCE/published_hashes.json (regenerated);
IMPLEMENTATION/pep.py (approval gate + gate-side state/helpers; build/sign split);
IMPLEMENTATION/approval.py (+2 wiring codes); TESTS/adversarial/test_request_schema.py
(live-derived manifest sha); TESTS/test_pep_approval.py (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
IMPLEMENTATION/evaluator.py + impact.py (byte-identical), envelope.py, verifier.py,
CANON/* (canon untouched), EVIDENCE/readiness.json - unchanged.

#### Environment note (Cowork sandbox)
Validated against a pristine git archive extraction (mount truncation, VL-108). Commit chain built
from VL-114-tip-intact blobs on side ref refs/heads/governance-f1-inc3; main untouched. The AUTHOR
verifies the blobs natively, fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Feature 1 increment 1d: extend IMPLEMENTATION/issuance_log.py + IMPLEMENTATION/envelope_inspector.py
with approval-request and grant-consumption record types and a reconcile predicate that every
forwarded high-impact decision_id has a matching consumed-grant record bound to its decision_sha256
([FIX H8]); plus IMPLEMENTATION/approver_cli.py (the minimal human surface, separate key).
Schedule the H5 load-bearing custody (approver provenance/role via the signed key-record chain)
and the SHARED-store wiring for the pending-set + grant single-use under scale. Then Feature 2
(non-bypassable) + the integration proof.

### VL-116 - 2026-06-18 - T-governance: Feature 1 increment 1d - the audit half ([FIX H8]) + the approver CLI; Feature 1 mechanism complete

#### What landed
The auditable governance trail and the human surface; Feature 1's mechanism (impact -> grant ->
wiring -> audit) is now complete end to end.

- IMPLEMENTATION/issuance_log.py: JsonlApprovalLog + approval_log_from_env() (ELYON_APPROVAL_LOG_PATH),
  mirroring the issuance log's durability discipline. Two record types: approval_request (the 202
  hold) and grant_consumed (the approved release).
- IMPLEMENTATION/pep.py: writes the approval_request record at the 202 hold and the grant_consumed
  record in the approved leg AFTER the grant_id claim and BEFORE the forward. Injected/env, DEFAULT
  None (no records, byte-behavior-identical); fail-closed when CONFIGURED (a hold/release that
  cannot be recorded -> REF_PEP_FAIL_CLOSED; record before you act, canon section 9).
- IMPLEMENTATION/envelope_inspector.py: reconcile_approvals(issued_envelopes, approval_records) with
  the closed violation set FORWARDED_WITHOUT_GRANT (a held AND forwarded high-impact decision with
  no grant_consumed - the governance guarantee broken), ORPHAN_CONSUMPTION (a release with no hold),
  DUPLICATE_GRANT (a grant_id consumed twice), DUPLICATE_REQUEST_CONSUMPTION (a 202 honored twice).
  The existing reconcile() is byte-unchanged.
- IMPLEMENTATION/approver_cli.py: the minimal human surface - a SEPARATE process holding the
  approver PRIVATE key (never the gate's, never in the repo). make_grant() is the testable core
  (wraps approval.build_grant/sign_grant so a grant it emits is exactly what verify_grant accepts);
  main() reads a 202 JSON, shows the human the decision being released, and on confirmation emits a
  signed grant.

#### Canon / build-then-wire posture
Canon UNTOUCHED (GR-1). evaluator.py, impact.py, approval.py BYTE-IDENTICAL to the VL-115 tip.
Default-off: with no approval log configured the full pre-existing suite is unchanged. The approval
trail and reconcile audit a LOG; they add no runtime invariant and refuse nothing (parity with
reconcile()).

#### Tests + revert-catcher discipline
TESTS/adversarial/test_approval_audit.py adds 9 tests; suite 452 -> 461 green in a pristine git
archive extraction. The starred revert-catcher - a held AND forwarded high-impact decision with NO
grant_consumed must be FORWARDED_WITHOUT_GRANT - was proven RED when the predicate is removed (the
gap would be reported clean), and an end-to-end variant (drive pep approved-forward, then drop the
consumption records) is caught the same way. The approver CLI's grant is accepted by verify_grant.

#### Honest scope / GR-3
reconcile_approvals is keyed on decision_sha256 (issuance-invariant), so it proves "every
held+forwarded high-impact decision has at least one recorded grant", NOT a per-issuance 1:1 match
(the grant is claimed before the envelope's decision_id is assigned; per-issuance linkage is a
later refinement). The log is the trustworthy referent (the explicit bound, parity with
reconcile). Feature 1 is now mechanism-complete, but the oversight GUARANTEE is still NOT claimed -
it requires Feature 2 (non-bypassable); a caller that skips the gate skips the human. Two Feature-1
RESIDUALS remain before claiming: R1 ([FIX H5] load-bearing) approver-key provenance + an explicit
approver ROLE via the signed key-record/root-record chain (the gate already holds only public
approver keys; this hardens the trust source); R2 ([FIX H3]/[FIX H4] under scale) a SHARED store
for the grant single-use cache + the pending-request set (reuse the R-02 declare-or-fail guard).
WHITE-BOX in-house build; NOT external validation (GR-3); does not enter the attacker pack. No
readiness predicate goes green on Feature 1 alone.

#### Files affected
IMPLEMENTATION/issuance_log.py (JsonlApprovalLog + approval_log_from_env); IMPLEMENTATION/pep.py
(approval-log wiring, default-off, fail-closed-when-configured); IMPLEMENTATION/envelope_inspector.py
(reconcile_approvals + the violation vocabulary); IMPLEMENTATION/approver_cli.py (NEW);
TESTS/adversarial/test_approval_audit.py (NEW); STATE.md; EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
IMPLEMENTATION/evaluator.py + impact.py + approval.py (byte-identical), envelope.py, verifier.py,
MANIFEST/* + EVIDENCE/published_hashes.json (no manifest change this increment), CANON/* (canon
untouched), EVIDENCE/readiness.json - unchanged.

#### Environment note (Cowork sandbox)
Validated against a pristine git archive extraction (mount truncation, VL-108). Commit chain built
from VL-115-tip-intact blobs on side ref refs/heads/governance-f1-inc4; main untouched. The AUTHOR
verifies the blobs natively, fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Feature 1 residuals then Feature 2. R1: approver-key provenance/role via the signed key-record /
root-record chain (custody hardening of [FIX H5]). R2: a SHARED store (ExternalStoreReplayCache +
a shared pending-set) for single-use + the 202 slot under horizontal scale ([FIX H3]/[FIX H4]),
with the R-02 declare-or-fail guard. Then Feature 2 (non-bypassable: inline body-bound sidecar +
mTLS client-auth + egress topology + the network-layer bypass-refused proof) and the integration
proof. Only after Feature 2 does the oversight guarantee become claimable.

### VL-117 - 2026-06-18 - T-governance: Feature 2 increment 2a - the mTLS client-auth proof (closing A1 at the transport layer)

#### What landed
The load-bearing network-layer property of Feature 2 (non-bypassable enforcement): the target
refuses any client that is not the gate AT THE TLS LAYER, before any app logic. This elevates A1
from "the app refuses bare calls" to "the network refuses to carry a bypassing call at all".

NO IMPLEMENTATION change. The dev-CA leaves already carry the CLIENT_AUTH EKU
(deploy/tls/gen_certs.py gen_leaf) and the transport seam already supports client certs (one-way
TLS by default per the TLS dossier 9.5); this increment PROVES the mTLS property and documents the
deployment, rather than adding gate code.

- TESTS/deploy/test_mtls_required.py (4 hermetic MemoryBIO handshake tests, reusing
  deploy.tls.gen_certs): the bare connection (no gate client cert) is REFUSED at the handshake
  when the target sets CERT_REQUIRED (the design-2.3 star proof); a connection presenting the gate
  cert is HONORED and the target reads the gate's identity; a client cert from an untrusted CA is
  REFUSED; and a CONTRAST test shows that with the target in one-way TLS the same bare connection
  IS accepted - demonstrating mTLS is exactly the layer that closes A1.
- EVIDENCE/proofs/nonbypass_direct_call_refused_runner.py: the same proof over REAL sockets
  (loopback), with the SERVER side authoritative (on TLS 1.3 the client handshake can return
  before the server's client-auth rejection propagates, so the proof reads the target's verdict:
  bare connection REFUSED_AT_TLS, gate connection ACCEPTED). Exit 0.
- deploy/NONBYPASS_TOPOLOGY.md: the three-layer recipe (inline body-bound sidecar; mTLS
  client-auth; network ACL + agent egress) with each layer's status and the bypass-refused
  procedure.

#### Canon / posture
Canon UNTOUCHED (GR-1). No IMPLEMENTATION/ change, so the full pre-existing suite is unaffected;
the 4 new tests are transport-layer proofs. This is a Feature-2 capability proof, not a new
runtime invariant in the gate.

#### Tests + revert demonstration
Suite 461 -> 465 green in a pristine git archive extraction. The bare-call-refused property was
demonstrated as a revert-catcher pair: WITH mTLS (CERT_REQUIRED) the bare call is refused; WITHOUT
it (one-way TLS, the contrast/revert) the bare call is accepted and the bypass reopens - so a
regression of the target to one-way TLS makes the catcher go RED.

#### Honest scope / GR-3
Non-bypassable holds ONLY within the network boundary the operator controls. The mTLS layer
(layer 2) is BUILT + PROVEN in-repo; layer 1 (the inline body binding via Envoy with_request_body;
the extractor was built at VL-111) and layer 3 (the network ACL + agent egress restriction) are
OPERATOR-LOCUS on real hosts and are NOT in-repo-testable. A1 is therefore NARROWED, not
blanket-closed; G4 is NOT marked RESOLVED (docs/restructure/04_current_vs_claimed.md unchanged this
increment - it earns the update when layers 1+3 are wired on a real deployment). The Feature-1
oversight GUARANTEE becomes claimable only inside a deployment that wires all three layers; the
in-repo artifact is the proof + the recipe, not a live non-bypassable deployment. WHITE-BOX
in-house proof; NOT external validation (GR-3); does not enter the attacker pack.

#### Files affected
TESTS/deploy/test_mtls_required.py (NEW); EVIDENCE/proofs/nonbypass_direct_call_refused_runner.py
(NEW); deploy/NONBYPASS_TOPOLOGY.md (NEW); STATE.md; EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/ (no gate code change), MANIFEST/*, CANON/*, EVIDENCE/published_hashes.json,
EVIDENCE/readiness.json - unchanged.

#### Environment note (Cowork sandbox)
Validated against a pristine git archive extraction (mount truncation, VL-108). Commit chain built
from VL-116-tip-intact blobs on side ref refs/heads/governance-f2-inc1; main untouched. The AUTHOR
verifies the blobs natively, fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
The INTEGRATION proof (design 3.3): one runner asserting a high-impact call cannot execute unless
it BOTH routes through the gate (mTLS, Feature 2) AND carries a valid human grant (Feature 1) -
direct bypass TLS-refused; routed-but-unapproved 202 with no execution; routed+approved executes
exactly once and is reconcilable on the issuance + approval logs. Then the OPERATOR-LOCUS Feature-2
layers (Envoy with_request_body inline binding; network ACL + agent egress) on real hosts, and the
Feature-1 residuals R1 ([H5] approver provenance/role via the signed key-record chain) + R2
([H3]/[H4] shared store under scale). Only inside a deployment wiring all three Feature-2 layers
does the oversight guarantee become claimable.

### VL-118 - 2026-06-18 - T-governance: the integration proof (design 3.3) - Feature 1 and Feature 2 compose

#### What landed
The capstone of the governance-substrate build: a single proof that the two features COMPOSE, so
the only path to executing a high-impact action is through-the-gate (Feature 2 mTLS) AND
with-a-valid-human-grant (Feature 1).

- EVIDENCE/proofs/governance_integration_001_runner.py (standalone, exit 0) and
  TESTS/test_governance_integration.py (suite-pinned) assert four legs, all of which must hold:
  A) a direct bypass is refused at the TLS handshake (Feature 2 mTLS; real MemoryBIO handshake);
  B) a routed-but-UNAPPROVED high-impact call returns 202 PENDING_APPROVAL and the target is NEVER
     called (Feature 1 hold, [FIX H6]);
  C) a routed + APPROVED call (the grant minted by approver_cli.make_grant) executes EXACTLY once,
     and the issuance + approval logs reconcile_approvals clean (no FORWARDED_WITHOUT_GRANT,
     [FIX H8]);
  D) a REPLAYED grant_id presented against a fresh 202 is refused with NO second execution
     ([FIX H3] single-use).
- EVIDENCE/proofs/governance_integration_001.{md,log}: the proof note + captured run log
  (RESULT: PASS).

Hermetic: a private dev CA + the real pep ASGI app driven via TestClient with the gate/approver
keys injected in-process. NO IMPLEMENTATION change - the proof composes existing code (impact.py,
approval.py, pep.py, envelope_inspector.py, approver_cli.py, deploy/tls/gen_certs.py).

#### Canon / posture
Canon UNTOUCHED (GR-1). No IMPLEMENTATION/ change; the full pre-existing suite is unaffected and
gains one integration test. This is a composition PROOF, not new runtime behavior.

#### Tests
Suite 465 -> 466 green in a pristine git archive extraction; the runner exits 0 from the committed
tree. Leg B (no execution without a grant) and leg D (no second execution on replay) both assert
the target-call list directly, so a regression that forwarded an unapproved or replayed
high-impact call would fail the proof.

#### Honest scope / GR-3
The proof shows the two mechanisms compose IN-PROCESS. It does NOT stand up the full deployment:
Feature 2 layers 1 (inline body binding via Envoy with_request_body) and 3 (network ACL + agent
egress) remain OPERATOR-LOCUS (deploy/NONBYPASS_TOPOLOGY.md), and single-use + the pending-set are
single-instance until a shared store is wired (R2). The oversight GUARANTEE is claimable ONLY
inside a deployment that wires all three Feature-2 layers plus the R1/R2 hardening; the in-repo
artifact is the composition proof, not a live non-bypassable deployment. WHITE-BOX in-house proof;
NOT external validation (GR-3); does not enter the attacker pack. No readiness predicate goes green
on this proof.

#### Files affected
TESTS/test_governance_integration.py (NEW); EVIDENCE/proofs/governance_integration_001_runner.py
(NEW); EVIDENCE/proofs/governance_integration_001.md (NEW);
EVIDENCE/proofs/governance_integration_001.log (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, MANIFEST/*, CANON/*, EVIDENCE/published_hashes.json,
EVIDENCE/readiness.json - unchanged.

#### Environment note (Cowork sandbox)
Validated against a pristine git archive extraction (mount truncation, VL-108). Commit chain built
from VL-117-tip-intact blobs on side ref refs/heads/governance-f2-inc2; main untouched. The AUTHOR
verifies the blobs natively, fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
The governance-substrate BUILD is in-repo complete (Feature 1 mechanism 1a-1d + Feature 2 mTLS 2a
+ this integration proof). What remains is the path to a DEPLOYABLE oversight guarantee, none of it
new in-repo capability: (i) OPERATOR-LOCUS Feature-2 layers 1 + 3 on real hosts; (ii) Feature 1
residuals R1 ([H5] approver provenance/role via the signed key-record chain) + R2 ([H3]/[H4]
shared store under scale). Only then does the oversight guarantee become claimable, and only an
external attacker on a live deployment (G5, GR-3) certifies it.


### VL-119 - 2026-06-18 - T-governance: Feature 1 residual R1 - approver provenance + role ([FIX H5] load-bearing half)

#### What landed
The load-bearing half of [FIX H5]. verify_grant (VL-114) and the pep wiring (VL-115) already
enforce the CHEAP Separation-of-Duties check (approver_key_id != gate_key_id) over a STATIC
approver-key pin. [FIX H5] requires SoD to be a CUSTODY/PROVENANCE invariant, not a key_id string
compare: the approver public keys the gate trusts must flow through the EXISTING signed
key-record / root-record chain and carry an explicit `approver` ROLE distinct from `issuer`, with
SoD enforced as ROLE-DISTINCTNESS in the SIGNED record. R1 builds exactly that, ABOVE G(I).

- NEW IMPLEMENTATION/approver_trust.py: resolve_approver_keys(validated_key_record_trust_view,
  gate_key_id, now, clock_skew) -> {key_id: public_key}. A key is eligible IFF its signed
  record-role is EXACTLY "approver" (role-distinctness; the load-bearing SoD), it is NOT revoked,
  it is within [not_before - skew, not_after + skew) (mirrors verify_envelope's VL-075 issuer-key
  window), and key_id != gate_key_id (belt-and-braces). Everything else is excluded fail-closed.
  The result is a drop-in for verify_grant's `approver_public_keys`, so approval.py is byte-UNCHANGED.
- IMPLEMENTATION/key_record_source.py: ADDITIVE only - the per-key trust view now surfaces the
  signed entry's OPTIONAL `role` field ("role": entry.get("role")). Because the publisher signs
  canonical_json(record minus signature), which includes every key entry, the role is
  signature-provenanced by construction. A role-less record (pre-VL-119) loads with role None and
  yields NO approver keys (fail-closed). No required-field change; existing membership-based tests
  unaffected.

#### How it composes (build-then-wire)
The gate's existing _INJECTED_APPROVER_KEYS seam (pep.py, VL-115) already accepts exactly the
{key_id: public_key} map resolve_approver_keys returns, so R1 is wireable WITHOUT a pep edit: a
deployment computes resolve_approver_keys(load_key_record_from_bytes(...)) and injects the result.
pep.py is therefore byte-IDENTICAL to HEAD this increment (no default-path touch).

#### Canon / posture
Canon UNTOUCHED (GR-1). evaluator.py / impact.py / approval.py / envelope.py / verifier.py /
pep.py / MANIFEST/manifest.json / EVIDENCE/published_hashes.json all byte-IDENTICAL to HEAD
(verified by hash-object vs HEAD blob). The only changes are the NEW approver_trust.py, the
ADDITIVE role surfacing in key_record_source.py, and the NEW test file.

#### Tests
TESTS/adversarial/test_approver_trust.py adds 15 tests, all driving the REAL chain
(load_key_record_from_bytes) and, where end-to-end, the REAL grant verifier (verify_grant) - never
a stub. Suite 466 -> 481 green in a pristine git archive HEAD extraction. The core revert-catcher
(test_issuer_role_cannot_authorize_revert_catcher) proves an ISSUER-role key that signs a grant is
EXCLUDED -> verify_grant REF_APPROVAL_KEY_UNKNOWN, and asserts the CONTRAST that a role-ignoring
resolver WOULD honor the gate's self-minted approval (GRANT_VALID). With the role gate reverted,
3 tests go RED (the revert-catcher, test_selects_only_approver_role, test_roleless_key_surfaces_role_none);
GREEN on restore. Provenance proven: a tampered key record validates to no trust view -> no
approver key; a key the publisher never signed is KEY_UNKNOWN. Positive composition proven GREEN
end-to-end (signed chain -> resolve -> verify_grant GRANT_VALID).

#### Honest scope / GR-3
This delivers the PROVENANCE + ROLE half of [FIX H5] (WHERE approver trust comes from). The CUSTODY
half - a deployment proof that the gate PROCESS cannot resolve the approver PRIVATE key - remains an
operator/deployment property, not an in-repo artifact. A key record that publishes no roles yields
no approver keys (fail-closed): a deployment using signed-chain approver trust MUST publish an
explicit approver role. WHITE-BOX in-house; NOT a G5 referent; no readiness predicate goes green on
R1. The oversight GUARANTEE is still claimable only inside a deployment wiring all three Feature-2
layers plus R1 AND R2; R2 ([H3]/[H4] shared store under horizontal scale) remains the open in-repo
governance residual after this entry.

#### Files affected
IMPLEMENTATION/approver_trust.py (NEW); IMPLEMENTATION/key_record_source.py (additive role
surfacing); TESTS/adversarial/test_approver_trust.py (NEW); STATE.md; EVIDENCE/verification_ledger.md
(this entry).

#### Files NOT affected
IMPLEMENTATION/evaluator.py, impact.py, approval.py, envelope.py, verifier.py, pep.py;
MANIFEST/manifest.json; CANON/*; EVIDENCE/published_hashes.json - all byte-identical to HEAD.

#### Environment note (Cowork sandbox)
Resume found a dirty mount (VL-108 truncation/stale-index hazard): HEAD == origin/main == 195269e,
but the mount served truncated working-tree reads (ledger 16139/16760, pep.py 354/567, STATE
1023/1201) and a stale index listing present files as deleted. Ruled out as an artifact per the
protocol (HEAD blobs intact; host files match HEAD); NOTHING discarded. All build + validation ran
against a pristine `git archive HEAD` extraction. Commit chain built from HEAD-intact blobs on side
ref refs/heads/governance-f1-r1; main untouched. The AUTHOR verifies the blobs natively,
fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
R2 ([FIX H3]/[FIX H4] under horizontal scale): a SHARED store (ExternalStoreReplayCache + a shared
pending-set) so grant single-use and the 202 slot hold across instances, reusing
replay_cache_from_env's R-02 declare-or-fail guard. Then only the OPERATOR-LOCUS Feature-2 layers 1
(Envoy with_request_body inline body binding) + 3 (network ACL + agent egress) on real hosts remain
before the oversight guarantee is deployment-claimable; an external attacker on a live deployment
(G5, GR-3) certifies it.


### VL-120 - 2026-06-18 - T-governance: Feature 1 residual R2 - shared store for single-use + the pending-set ([FIX H3]/[FIX H4] under horizontal scale)

#### What landed
The shared-store residual that lets grant single-use and the 202 pending-slot hold ACROSS
instances. Before R2, pep hard-coded a per-process pending set (_PendingApprovals dict) and a
per-process grant-replay cache (InMemoryReplayCache()), so a horizontally-scaled gate kept N
independent copies: a 202 issued on instance A was unknown to instance B (approved resubmit ->
REF_APPROVAL_REQUEST_UNKNOWN), and - worse for [FIX H3] - single-consume of both the
approval_request_id and the grant_id held only per-process (one approval -> one execution PER
replica).

- NEW IMPLEMENTATION/pending_store.py: the pending-approval-set seam, a SIBLING of replay_cache.py.
  PendingApprovals Protocol (issue / check_and_consume); PendingStore cross-process primitive
  (put / consume_if_matches = compare-AND-delete); InMemoryPendingApprovals (behavior-IDENTICAL to
  pep's pre-R2 _PendingApprovals); ExternalStorePendingApprovals(store) delegating the global
  atomic consume; RedisPendingStore (SET [EX] + a Lua GET-compare-DEL so a concurrent
  double-consume succeeds at most once and a wrong-decision probe deletes nothing); and
  pending_store_from_env() with the R-02 declare-or-fail guard reused from replay_cache_from_env.
- IMPLEMENTATION/pep.py (the only default-path edit): _PENDING = pending_store_from_env() and
  _GRANT_REPLAY = replay_cache_from_env() (the [FIX H3] requirement: the grant single-use cache now
  rides the shared ExternalStoreReplayCache under scale). _PendingApprovals retained as a
  backward-compatible alias of InMemoryPendingApprovals (three test files import it). DEFAULT (no
  ELYON_* env) is byte-behavior-identical: both builders return their in-memory impls, which are
  behavior-identical to the pre-R2 constructors. A gate that declares ELYON_REPLAY_MULTI_INSTANCE
  without a shared store (ELYON_PENDING_REDIS_URL / ELYON_REPLAY_REDIS_URL) now FAILS CLOSED at
  import/startup rather than handing each replica a per-process set/cache.

#### Canon / posture
Canon UNTOUCHED (GR-1). evaluator.py / impact.py / approval.py / envelope.py / verifier.py /
key_record_source.py / approver_trust.py / replay_cache.py / MANIFEST/manifest.json /
EVIDENCE/published_hashes.json all byte-IDENTICAL to the base (verified by hash-object vs the base
blob). The ONLY default-path change is pep.py (the import line + the _PENDING/_GRANT_REPLAY block),
and its default behavior is byte-behavior-unchanged.

#### Tests
TESTS/adversarial/test_pending_store.py adds 18 tests, mirroring test_shared_replay_cache.py: the
in-memory parity + unknown/wrong-decision refusals; the GAP (two separate sets miss a cross-instance
consume) vs the SEAM (one shared store catches it, single-use across both); the external adapter +
a fake shared store (incl. fail-closed propagation); RedisPendingStore against a fake redis (Lua
compare-and-delete, TTL derivation, no-TTL parity); the protocol-conformance checks; and the
pending_store_from_env default + R-02 guard. Suite 481 -> 499 green in a pristine git archive HEAD
extraction. Two revert-catchers proven RED-on-revert then GREEN: removing the R-02 guard fails
test_from_env_multi_instance_without_store_fails_closed; making consume delete-on-mismatch fails
test_in_memory_wrong_decision_refused_and_not_consumed. The three test files that import
_PendingApprovals from pep and the full pep-approval suite stay green (backward-compat alias +
byte-identical default wiring).

#### Honest scope / GR-3
R2 makes single-use + the pending-set shared-CAPABLE and fail-closed-under-scale; the guarantee
holds across instances ONLY with a shared store actually deployed (ELYON_PENDING_REDIS_URL /
ELYON_REPLAY_REDIS_URL pointing at one Redis). The RedisPendingStore is exercised against a fake
redis in-repo; a real Redis behind N gate processes is a deployment property (G5/operator-locus),
not an in-repo artifact. With R2, the in-repo governance-substrate BUILD is COMPLETE (Feature 1
mechanism 1a-1d + R1 provenance/role + R2 shared store; Feature 2 mTLS layer 2a; the integration
proof). What remains for a DEPLOYABLE, claimable oversight guarantee is purely OPERATOR-LOCUS:
Feature-2 layers 1 (Envoy with_request_body inline body binding) + 3 (network ACL + agent egress)
on real hosts, plus actually wiring the shared store. WHITE-BOX in-house; NOT a G5 referent; no
readiness predicate goes green on R2.

#### Files affected
IMPLEMENTATION/pending_store.py (NEW); IMPLEMENTATION/pep.py (import + _PENDING/_GRANT_REPLAY
wiring + _PendingApprovals alias); TESTS/adversarial/test_pending_store.py (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
IMPLEMENTATION/evaluator.py, impact.py, approval.py, envelope.py, verifier.py, key_record_source.py,
approver_trust.py, replay_cache.py; MANIFEST/manifest.json; CANON/*; EVIDENCE/published_hashes.json
- all byte-identical to the base.

#### Environment note (Cowork sandbox)
Base = c29cb4a (origin/main after the R1 native ff+push). Built/validated against a pristine
git archive extraction (the VL-108 mount-truncation hazard persists). Commit chain built from
base-intact blobs on side ref refs/heads/governance-f1-r2; main untouched. The AUTHOR verifies the
blobs natively, fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
The in-repo governance-substrate build is COMPLETE. The remaining path to a claimable oversight
guarantee is OPERATOR-LOCUS, not new in-repo capability: (i) stand up the shared store (one Redis
behind the gate replicas; set ELYON_PENDING_REDIS_URL + ELYON_REPLAY_REDIS_URL + declare
ELYON_REPLAY_MULTI_INSTANCE); (ii) wire Feature-2 layers 1 (Envoy with_request_body inline
body-binding) + 3 (network ACL + agent egress) per deploy/NONBYPASS_TOPOLOGY.md. Only inside a
deployment wiring all three Feature-2 layers WITH R1 + R2 does the oversight guarantee become
claimable, and only an external attacker on that live deployment (G5, GR-3) certifies it.


### VL-121 - 2026-06-18 - T-governance: governance-substrate DEPLOYMENT artifacts authored (operator-locus; R1 + R2 + Feature-2 wiring)

#### What landed
The operator-locus deployment package that wires the completed in-repo governance build (Feature 1
mechanism 1a-1d + R1 + R2; Feature 2 mTLS 2a; integration proof) into a real, all-layers deployment.
NO IMPLEMENTATION / TESTS / canon change; the full suite is unaffected (499, unchanged). These are
deploy/ artifacts - authored and locally smoke-validated, but UNVALIDATED on real hosts (no docker /
real CA / real Redis / multi-host network in the sandbox).

- deploy/governance/approver_trust_bootstrap.py (NEW): the R1 wiring shim. The gate's stock entry
  (uvicorn IMPLEMENTATION.pep:app) only had a STATIC approver pin (the [FIX H5] weakness). This thin
  ASGI shim loads the SIGNED key record, validates it against the pinned root, resolves the
  ROLE-DISTINCT approver map (approver_trust.resolve_approver_keys, excluding the gate issuer id),
  injects it into pep._INJECTED_APPROVER_KEYS, and re-exposes pep.app. Run the gate as
  `uvicorn deploy.governance.approver_trust_bootstrap:app`. Fail-closed: bad record / no approver
  role -> empty map -> every grant REF_APPROVAL_KEY_UNKNOWN. SMOKE-VALIDATED in-sandbox: a built
  signed record with an approver-role + an issuer-role key injects ONLY the approver-role key.
- deploy/docker-compose.governance.yml (NEW): overlay adding redis (the R2 shared store) + TWO gate
  replicas (gate + gate2) both run via the shim and both pointed at redis with
  ELYON_REPLAY_MULTI_INSTANCE=1 + ELYON_PENDING_REDIS_URL + ELYON_REPLAY_REDIS_URL (so single-use +
  the 202 slot are global, R2), + an approver-cli service (profile "approver") holding the approver
  PRIVATE key in a SEPARATE process (custody). YAML-validated; network aligned to the base/replay
  overlays (default network, reach by service name).
- deploy/governance.env.example (NEW): the full ELYON_* env contract for the governance deployment.
  Every var the shim reads is set here and in the compose overlay (cross-checked); the R2 vars match
  the pending_store/replay_cache reads.
- deploy/GOVERNANCE_DEPLOYMENT.md (NEW): the end-to-end runbook - R1 (signed key-record + approver
  role + CLI custody), R2 (shared store + the declare-or-fail guard), Feature-2 layers 1 (Envoy
  with_request_body inline body-binding) + 2 (mTLS, proven in-repo) + 3 (network ACL + egress, per
  NONBYPASS_TOPOLOGY.md) - each with an acceptance check, the live A-D integration replay (VL-118's
  four legs), and a sign-off checklist. Leads with the HONEST claimability gate: the oversight
  guarantee is claimable ONLY inside a deployment wiring ALL of R1 + R2 + F2 layers 1-3, and only an
  external attacker (G5) certifies it.

#### Canon / posture
Canon UNTOUCHED (GR-1). No IMPLEMENTATION / MANIFEST / TESTS / EVIDENCE-proof change; G(I) core and
every code module byte-identical to the R2 base. Suite 499 unchanged (deploy-only additions).

#### Honest scope / GR-3
These are AUTHORED, locally-smoke-validated deployment artifacts, NOT a live deployment and NOT
external validation. The shim is smoke-validated in-sandbox; the compose/env/runbook are
syntactically validated and consistency-checked against the code's env reads, but the real stand-up
(docker, real CA, a real Redis behind N replicas, multi-host network ACL/egress, Envoy
with_request_body) is the operator's and remains UNVALIDATED here. The oversight GUARANTEE is NOT
claimed; no readiness predicate goes green. G5 stays NOT-MET until a blind external party engages the
live, all-layers-wired surface.

#### Files affected
deploy/governance/approver_trust_bootstrap.py (NEW); deploy/docker-compose.governance.yml (NEW);
deploy/governance.env.example (NEW); deploy/GOVERNANCE_DEPLOYMENT.md (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, TESTS/, MANIFEST/, CANON/, EVIDENCE/published_hashes.json - byte-identical to
the R2 base (c29cb4a..R2-tip).

#### Environment note (Cowork sandbox)
Base = the R2 side-ref tip (built on c29cb4a = origin/main after R1's native ff+push); R2 itself is
not yet on origin (the author's native ff+push lands it). Built/validated against the pristine R2
extraction (VL-108 mount truncation persists). Commit chain on side ref refs/heads/governance-deploy-prep,
which includes R2 as ancestor; main untouched - the AUTHOR verifies the blobs natively, fast-forwards
main (R2 + deploy-prep together, or R2 first then this), and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Operator execution, not in-repo code: (1) stand up redis + the two gate replicas via the governance
overlay and run the R2 acceptance checks (declare-or-fail; cross-instance single-use); (2) publish the
approver-role key record + pin the root, run the gate via the shim, run the R1 acceptance checks
(issuer-role cannot authorize; revocation via the record); (3) wire Feature-2 layers 1 + 3 per
NONBYPASS_TOPOLOGY.md and enable layer 2 mTLS; (4) replay VL-118's A-D integration legs on the live
surface; (5) arrange the external attacker (G5) per BREAK_IT.md + SAFE_HARBOR_DRAFT.md. Only then is
the oversight guarantee deployment-claimable, and only G5 certifies it.


### VL-122 - 2026-06-18 - LIVE-OPS: publisher signing-key ROTATION + byte-anchor->signed correction (VL-108 pre-exposure items 1 & 2 closed)

#### What happened
The VL-108 pre-exposure checklist item 1 - regenerate the publisher signing key (it had been exposed
in a working chat) and re-pin it - was EXECUTED on the live four-node surface, under a strict
no-secret-in-history/never-typed protocol. NO repository code/canon/manifest/test change; the suite
is unaffected. This is a live-ops + record-correction entry.

- ROTATION. A fresh Ed25519 publisher keypair was generated ON the publisher host by an in-process
  generator that writes the PRIVATE key straight to a 0600 EnvironmentFile and prints ONLY the public
  key (never the private). The publisher now signs /published_hashes_signed.json under key id
  `pub-2026-06-18`; the exposed key and every transient throwaway are now trusted by NO node.
- CORRECTION (the load-bearing finding). VL-108 documented the deployment as "target+publisher in
  SIGNED freshness mode", but the live target's ELYON_PUBLISHER_URL pointed at the BYTE-ANCHOR
  endpoint /published_hashes.json (the unsigned record: currency pins only, no publisher_key_id /
  publisher_signature). So the target was actually BYTE-ANCHOR, not signed - no consumer verified the
  publisher signature, and the exposed publisher signing key was not load-bearing for the target. The
  rotation re-pinned the new publisher PUBLIC key on the target AND repointed it at the SIGNED
  endpoint, moving it to GENUINE signed-freshness mode.
- VERIFICATION (live, two ways). (a) A direct on-target check calling the same trust function the
  service uses, published_record_source.fetch_signed_record, returned PASS (key_id=pub-2026-06-18).
  (b) The full live attack suite (EVIDENCE/proofs/attack_suite_live_runner.py) over the public surface
  returned exit 0: positive control HONORED end-to-end (gate admits->signs->forwards to the target IN
  SIGNED MODE->target verifies the new publisher record->acts) and 6/6 gate-2 attacks REFUSED
  (unattested/forged-sig/replay/rebind-tool/rebind-args/target-url-swap). The suite was run
  VERSION-MATCHED at the deployed commit (3343e32), because the laptop's main pins the post-VL-115
  manifest sha (ac18ac78) while the live gate holds the VL-109 manifest (a21dea8b) - a latest-main
  harness is correctly REFUSED by the live gate (expected, not a fault).
- SIDECAR (authz). Confirmed NOT in signed mode (it does not consume the published record), so the
  rotation does not touch it. VL-108 item 2 (live sidecar ALLOW/DENY - only deny-on-junk had been
  confirmed) was closed by a live recheck against authz.elyon-sol.io:9243 /authz: a real gate-signed
  envelope -> 200 ALLOW (REASSERTED_AND_BOUND); a forged envelope -> 403 DENY
  (REF_VERIFY_SIGNATURE_INVALID); an absent envelope -> 403 DENY (REF_VERIFY_ENVELOPE_ABSENT).
- GATE. Signs envelopes; does NOT consume the published record (no publisher pin). Its issuer key
  (ELYON_SIGNING_KEY_*) was never exposed (only the publisher key leaked), so it was not rotated.

#### Deployment fact (for the record)
The live four-node surface (gate.elyon-sol.io:8443, target:9443, pub:9143, authz:9243) runs commit
3343e32 (VL-109), NOT latest main. The governance layer (R1 VL-119 / R2 VL-120) and the post-VL-115
manifest are NOT deployed there; deploying them is the separate operator-locus governance deployment
(deploy/GOVERNANCE_DEPLOYMENT.md). Hosts were also renamed to functional names (pub/target/gate/authz)
for operability - cosmetic, no effect on DNS/TLS/services.

#### Tooling landed
deploy/rotate_publisher_key.py (NEW) - the safe keygen helper: writes the private key to a 0600 file,
prints ONLY the public key + a suggested key id; never prints the private key (unless an explicit
--print-private). deploy/KEY_ROTATION.md (NEW) - the rotation runbook (per-node var table, steps,
live verification, retirement check), env names cross-checked against the code's constants.

#### Canon / posture / honest scope
Canon UNTOUCHED (GR-1). NO IMPLEMENTATION/MANIFEST/TESTS/EVIDENCE-proof change - this is live-ops +
two new deploy/ docs; the in-repo suite is unaffected. The rotation is VERIFIED on the live surface
(direct check + full suite green); WHITE-BOX author self-test, NOT external validation. G5 (a blind
external attacker) remains NOT-MET.

#### VL-108 pre-exposure checklist status
Item 1 (regenerate + re-pin publisher key) - CLOSED (this entry). Item 2 (sidecar live ALLOW/DENY) -
CLOSED (this entry). OPEN: item 3 (cert-renewal deploy-hook - a restart-elyon hook was added on at
least one host; verify across all four), item 4 (counsel safe-harbor sign-off - HARD GATE before
publish), item 5 (bounty tiers / window / reporting channel), item 6 (publish the decontaminated
attacker pack + open the private bounty listing), item 7 (recruit). G5 stays NOT-MET until a blind
external party engages.

#### Files affected
deploy/rotate_publisher_key.py (NEW); deploy/KEY_ROTATION.md (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, MANIFEST/, CANON/, TESTS/, EVIDENCE/proofs/, EVIDENCE/published_hashes.json -
byte-identical to the base.

#### Environment note (Cowork sandbox)
Base = origin/main 2aedb03. Built against a pristine git archive extraction. Commit chain on side ref
refs/heads/keyrotation-vl122; main untouched - the AUTHOR verifies the blobs natively, fast-forwards
main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
The remaining VL-108 pre-exposure items (3-7) are the path to opening the external engagement (G5):
verify cert-renewal hooks on all four hosts; counsel safe-harbor sign-off; set bounty tiers + window +
channel; publish the decontaminated attacker pack; recruit. Separately, the in-repo governance build
(R1+R2) is complete and its operator-locus deployment (Redis shared store + Feature-2 layers 1+3 +
the R1 approver key-record) per deploy/GOVERNANCE_DEPLOYMENT.md remains the other open deployment track.


### VL-123 - 2026-06-18 - T-governance: Cursor white-box review of the governance core - hardening cluster (G-01/03/04/06 FIXED; G-02/05 documented)

#### What happened
A Cursor Mode-A white-box adversarial review (per the CURSOR_REVIEW_governance_core packet) of the
governance core - approval.py, approver_trust.py + key_record_source role surfacing, impact.py,
pending_store.py, replay_cache.py, the pep governed_call approval branch, approver_cli.py, and the
issuance_log/envelope_inspector audit - found NO exploitable bug on a correctly-wired single-instance
gate (the hold -> verify_grant -> consume pending -> claim grant -> forward chain is correctly
ordered and fail-closed). It surfaced six DEPLOYMENT-POSTURE findings; the load-bearing three were
re-verified against the code line-by-line before acting (project rule: do not trust an assertion
without reading the lines). WHITE-BOX = internal hardening evidence, NOT a G5 referent (GR-3, VL-057).

#### Findings + disposition
- G-01 (High, P3) FIXED. The bare static approver pin (ELYON_APPROVER_PUBKEY_HEX) enforces SoD only
  as approver_key_id != gate_key_id, so `uvicorn IMPLEMENTATION.pep:app` lets a gate self-approve
  under a DIFFERENT key_id with its own key material. R1 (role-distinctness from the signed
  key-record chain) is the fix, but nothing forced it.
- G-06 (Low, P3) FIXED. A high-impact gate with an empty resolved approver map starts silently and
  REFUSES every grant at request time (fail-closed but not loud).
- G-04 (Medium, P6) FIXED. The [FIX H8] approval log is optional, so issuance-logged-but-no-approval-
  log forwards an approved high-impact call with no grant_consumed record -> reconcile_approvals
  cannot detect FORWARDED_WITHOUT_GRANT.
- G-03 (High, P4) FIXED. pending_store_from_env and replay_cache_from_env resolve independently, so a
  shared pending store WITHOUT a shared grant-replay store (or vice versa) leaves grant single-use
  per-process under scale.
- G-02 (High, P4) DOCUMENTED, not code-fixed. An UNDECLARED multi-worker gate (no
  ELYON_REPLAY_MULTI_INSTANCE, no Redis URLs, workers>1) gets per-process state. A worker cannot
  observe the worker count, so this is not fully closable from inside the app; the declare-or-fail
  guard + the new G-03 coherence check NARROW it, but the operator's multi-instance declaration
  remains load-bearing (honest residual; named in governance_wiring.py + GOVERNANCE_DEPLOYMENT.md).
- G-05 (Low, P2) DOCUMENTED, ruled out. pep passes verify_grant expected_approval_request_id =
  grant's own field, so that step is a tautology; the request-identity binding is actually carried by
  _PENDING.check_and_consume (server-side compare-and-delete). Redundant defense-in-depth, NOT a
  bypass. Left as-is with a note; a future tightening could pass the server-side pending id.

#### The fix
NEW IMPLEMENTATION/governance_wiring.py: assert_high_impact_wiring() - a single fail-closed startup
check that fires ONLY when the SHA-pinned manifest DECLARES high-impact actions (safe_high_impact
non-empty, or malformed -> fail-closed-declared). It refuses to start when: approver trust is not
R1-injected (G-01), the approver map is empty (G-06), no approval log is configured (G-04), or the
pending/replay shared stores are configured incoherently (one XOR the other, G-03). NO-OP for the
default HIGH_IMPACT:[] manifest, so the non-high-impact deployment is byte-behavior-unchanged.
IMPLEMENTATION/pep.py adds ONE @app.on_event("startup") hook that gathers live gate state
(load_manifest / _get_approver_keys / _INJECTED_APPROVER_KEYS / _get_approval_log / the two Redis
env vars) and calls the pure check. Build-then-wire: the logic is in the pure module (tested
directly); the hook is thin. Declaring HIGH_IMPACT is itself an explicit opt-in, so a deployment that
does so must wire oversight safely or the gate fails closed at startup.

#### Canon / posture
Canon UNTOUCHED (GR-1). evaluator.py / envelope.py / verifier.py / impact.py / approval.py /
approver_trust.py / pending_store.py / replay_cache.py / key_record_source.py / MANIFEST/manifest.json
/ CANON/* / EVIDENCE/published_hashes.json all byte-IDENTICAL to the base. The ONLY default-path file
touched is pep.py, and its sole change is the startup hook (the governed_call request path is
byte-unchanged; the hook no-ops on the default manifest).

#### Tests
TESTS/adversarial/test_governance_wiring.py adds 13 tests: high_impact_declared (empty/non-empty/
malformed); the default-empty path is a no-op even with all-bad wiring; safe wiring passes; a
revert-catcher per finding (G-01/G-06/G-04/G-03, each RED if its check is removed - proven); malformed
HIGH_IMPACT fails closed; multiple-problems-reported-together; and a real-startup-hook test
(`with TestClient(pep.app)`) confirming the default app starts clean. Suite 499 -> 512 green in a
pristine git archive extraction; the existing pep/approval/governance suites are unaffected (they use
TestClient(app) without the context manager, so the startup hook does not fire, and the repo manifest
is HIGH_IMPACT:[] regardless).

#### Honest scope / GR-3
This is in-house WHITE-BOX hardening (the reviewer had the full repo) - internal evidence, NOT
external validation and FORBIDDEN to show a blind reviewer (VL-057). The findings were
deployment-posture, none exploitable on the live surface (HIGH_IMPACT:[], single worker), so the live
four-node deployment is UNAFFECTED. The guard hardens FUTURE high-impact / scaled deployments; no
readiness predicate goes green; G5 (a blind external attacker) remains NOT-MET. Recommended follow-up:
a cross-model convergence round (Grok/OpenAI) on the same packet, discarding any fabricated-citation
run (VL-008 rule b). NOTE: the startup hook uses the deprecated FastAPI on_event API (works on
current FastAPI; a lifespan migration is a future cosmetic).

#### Files affected
IMPLEMENTATION/governance_wiring.py (NEW); IMPLEMENTATION/pep.py (startup hook only);
TESTS/adversarial/test_governance_wiring.py (NEW); STATE.md; EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All G(I) core + governance crypto modules, MANIFEST/*, CANON/*, EVIDENCE/published_hashes.json -
byte-identical to the base.

#### Environment note (Cowork sandbox)
Base = origin/main aa2dea0 (VL-122). Built/validated against a pristine git archive extraction. Commit
chain on side ref refs/heads/governance-wiring-vl123; main untouched - the AUTHOR verifies the blobs
natively, fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Optional: the cross-model convergence round on the governance-core review packet. The in-repo
governance build (Feature 1 + R1 + R2 + this wiring guard) is complete; the operator-locus deployment
(GOVERNANCE_DEPLOYMENT.md - Redis shared store + Feature-2 layers 1+3 + the R1 approver key-record)
and the VL-108 pre-exposure items 3-7 remain the open deployment tracks. G5 NOT-MET.


### VL-124 - 2026-06-18 - T-governance: cross-model convergence round on the governance core (Cursor + OpenAI + Grok) - VL-123 confirmed; two single-model sharpenings named-open

#### What happened
The VL-123 Cursor white-box review was followed by an independent cross-model round on the SAME
governance-core bundle (docs/methodology/xmodel_review_governance_core_request.md - a re-worded packet
that names the properties P1-P6 but NOT the prior findings or line numbers, so each run is independent
rather than an echo). Grok and OpenAI each ran it against the zipped HEAD-6ea0ccd source bundle. Both
are PROCEDURALLY CLEAN per VL-008: scope-bound to the provided files, cited only in-scope path:line,
and gave the explicit scope-confirmation line (NO fabrication - unlike the Gemini runs discarded at
VL-102/VL-106 under rule b). Verbatim transcripts: EVIDENCE/verification_runs/governance_core_{cursor,
openai,grok}_2026-06-18.md. NO repository code/canon/manifest/test change in this entry - it records a
verification round and schedules two refinements.

#### Convergence (the headline)
UNANIMOUS across three independent models: NO exploitable bug on a correctly-wired single-process gate
(the hold -> verify_grant -> consume-pending -> claim-grant -> forward chain is correctly ordered and
fail-closed), and all [FIX H1]-[H8] hold IN CODE, not just docstrings. Every break attempt (tampered/
cross-bound grants, gate self-approval, replay, concurrent resubmit, malformed manifest, missing
record) was refused or ruled out. The only weak paths are DEPLOYMENT-POSTURE: P3 (the bare static
approver pin), P4 (single-use under undeclared multi-instance / no shared store), P6 (no approval
log) - the exact class VL-123's governance_wiring guard was built to catch, which Grok independently
credits as catching them at startup. OpenAI's findings map 1:1 onto the Cursor cluster: GL-01<->G-01
(P3), GL-02<->G-05 (P2, both RULED OUT - the verify_grant request-id check is redundant because the
binding is carried by _PENDING.check_and_consume), GL-03<->G-04 (P6), GL-04<->G-02/03 (P4). The round
therefore CONFIRMS VL-123's gap analysis and that the guard works.

#### Two single-model sharpenings (OpenAI), NAMED-OPEN / scheduled - not yet fixed
- GL-01-refine (P3): VL-123's startup guard requires approver trust to be INJECTED (not the bare
  static pin) but checks injected-ness, NOT signed-chain PROVENANCE - so an injected map of
  gate-controlled keys under a different key_id still passes the guard and verify_grant. Verified real
  on inspection. Deployment-gated (in-process injection is already operator-controlled) and not
  exploitable on the live surface, but it means VL-123 NARROWED G-01, did not fully close it. The
  robust fix is for pep to resolve approver keys from the signed key-record chain ITSELF (env-driven:
  load_key_record_from_bytes + resolve_approver_keys in _get_approver_keys), so the in-process
  injection seam stops being the trust boundary and the approver_trust_bootstrap shim becomes optional.
- GL-03-refine (P6): VL-123's audit-wiring guard is STARTUP-only; it should ALSO be enforced in the
  REQUEST PATH (high-impact + no approval log -> fail closed at governed_call), so it holds even if the
  startup hook does not run. NOTE: this changes the approved-forward contract and the pep approval test
  fixtures must then configure an approval log - hence scheduled as its own increment, not folded here.
Grok did NOT surface either sharpening (it judged the guard sufficient), so both are SINGLE-MODEL
findings, verified-on-inspection, scheduled for a deliberate follow-up increment rather than a reflex.

#### Canon / posture / honest scope
Canon UNTOUCHED (GR-1). NO IMPLEMENTATION/MANIFEST/TESTS/EVIDENCE-proof change - this entry adds the
review request (docs/methodology/) + three verbatim run transcripts (EVIDENCE/verification_runs/) +
this ledger entry. The suite is unaffected. This is an in-house WHITE-BOX cross-model round (every
model had the full bundle) - internal CONVERGENCE / hardening evidence, NOT external validation and
FORBIDDEN to show a blind reviewer (GR-3, VL-057). None of the findings are exploitable on the live
surface (HIGH_IMPACT:[], single worker); the live four nodes are UNAFFECTED. No readiness predicate
goes green; G5 (a blind external attacker) remains NOT-MET.

#### Files affected
docs/methodology/xmodel_review_governance_core_request.md (NEW);
EVIDENCE/verification_runs/governance_core_cursor_2026-06-18.md (NEW);
EVIDENCE/verification_runs/governance_core_openai_2026-06-18.md (NEW);
EVIDENCE/verification_runs/governance_core_grok_2026-06-18.md (NEW); STATE.md;
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, MANIFEST/, CANON/, TESTS/, EVIDENCE/proofs/, EVIDENCE/published_hashes.json -
byte-identical to the base.

#### Environment note (Cowork sandbox)
Base = origin/main 6ea0ccd (VL-123). Built against a pristine git archive extraction. Commit chain on
side ref refs/heads/governance-xmodel-vl124; main untouched - the AUTHOR verifies the blobs natively,
fast-forwards main, and pushes (no sandbox push credentials; rule 7).

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
SCHEDULED follow-up increment (when chosen): GL-01-refine (pep resolves approver keys from the signed
key-record chain in-process, closing the SoD provenance residual + simplifying deployment) and
GL-03-refine (request-path audit fail-closed + the test-fixture updates it requires). Both are
deployment-gated, not exploitable. Otherwise the open tracks are unchanged: the operator-locus
governance deployment (GOVERNANCE_DEPLOYMENT.md) and the VL-108 pre-exposure items 3-7. G5 NOT-MET.

### VL-125 - 2026-07-01 - T-recruiting: private-invite red-team pack + public one-page site + non-monetary recognition model authored (no code/canon/test/verification change)

Recruiting / publication assets for the G5 external-validation engagement (pre-exposure item 6)
were authored and committed at build 816beb8; this entry is the STATE + ledger close. NO
IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof change - the test suite is unaffected.
This is NOT a verification event; it records the authoring of external-facing recruiting material
and its honest-scope framing, per the close protocol's continuity requirement.

#### What was authored
- site/index.html (NEW): a self-contained one-page public site - features, technologies, the
  four-node live surface (gate/target/authz/pub), canon v0.9.8.4 (G(I) = AC^3 ^ T^26 ^ CCS), the
  CURRENT Zenodo record 10.5281/zenodo.20751592, and the red-team challenge. Carries the honest-
  scope note (no external validation yet; G5 is the open finish line).
- deploy/PRIVATE_INVITE_PROGRAM.md (NEW): platform-neutral, invite-only program pack (scope, rules,
  recognition model, SLA, vetting, safe harbor, doc inventory), replacing the YesWeHack-specific pack.
- deploy/SOLICITOR_INTAKE_CHEATSHEET.md (NEW): operator cheat sheet - what to give a researcher who
  solicits at security@elyon-sol.io, in gated order (public vs gated buckets, vetting, signed
  authorization, then the briefing pack), plus a reply template, a never-send list, and curated
  where-to-post venues.
- deploy/BREAK_IT.md + deploy/RED_TEAM_OUTREACH.md: the reward section revised from a CASH bounty to
  a NON-MONETARY recognition/ownership model (permanent named ledger entry, Zenodo co-credit + ORCID,
  CVE where applicable, invited fix-authorship, a founding red-team seat, and a team creative-
  ownership / co-maintainer path).

#### Decisions recorded this session
- The reward model is now recognition + ownership, NOT cash (author decision).
- The engagement is PRIVATE, invite-only, run directly by the team - NO bug-bounty platform. Entry is
  a solicitation to security@elyon-sol.io, then vetting + a signed Authorization-to-Test. YesWeHack
  is retired (deploy/YESWEHACK_PROGRAM.md removed).
- .gitignore line 175 '/site' (an inherited mkdocs build-output ignore) was commented out so the
  published site source under site/ is trackable - the THIRD instance of the inherited-.gitignore
  collision pattern (cf. VL-010, VL-017; a standing candidate audit of .gitignore remains open).

#### Honest scope
Author-authored recruiting material, NOT external validation and NOT a live launch. The program's
HARD GATES (counsel-signed safe-harbor clause, a green live self-test over the four nodes, cert-
renewal hooks, a signed Authorization-to-Test) are UNMET, so nothing is published or open. Publisher-
key rotation (pre-exposure item 1) was already closed at VL-122. G5 (a blind external attacker on the
live surface) remains NOT-MET; no readiness predicate goes green.

#### Files affected
site/index.html (NEW); deploy/PRIVATE_INVITE_PROGRAM.md (NEW); deploy/SOLICITOR_INTAKE_CHEATSHEET.md
(NEW); deploy/BREAK_IT.md; deploy/RED_TEAM_OUTREACH.md; deploy/YESWEHACK_PROGRAM.md (REMOVED);
.gitignore; STATE.md; EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, CANON/, MANIFEST/, TESTS/, EVIDENCE/proofs/, EVIDENCE/published_hashes.json -
byte-identical.

#### Environment note (Cowork sandbox)
The recruiting assets landed natively at commit 816beb8 (build); this STATE + ledger entry is the
follow-up close commit. Authored via the Cowork host file tools. The sandbox mount showed the VL-108-
class artifacts during the session - a stale .git/index.lock and a wedged/ghost deploy/
YESWEHACK_PROGRAM.md (stat present, open/unlink absent) - cleared natively before commit; no work lost.

#### Citation discipline (VL-012)
Does not cite its own hash.

#### Next trajectory action
Unchanged. G5 pre-exposure items 3-7 remain open: cert-renewal hooks (item 3), counsel sign-off on
the safe-harbor clause (item 4, HARD GATE), set the engagement window + reporting channel (item 5),
publish the pack + open the private invite (item 6 - the ASSETS are now drafted; publishing is gated
on counsel + the live hard gates), and the parallel Phase-3.2 rebuild estimator (item 7). G5 NOT-MET.

---

### VL-126 - 2026-07-03 - T-bookkeeping close-repair + T-external Phase-3.2 asset: the 40fb5e6 close repaired (pre-launch pack landed, COPYRIGHT_HEADER retired, session-local files ignored) + the rebuild-estimator commissioning brief authored

#### What the resume found (close-protocol invariant violated)
- Commit 40fb5e6 (2026-07-03, native: preprint md+PDF, LinkedIn profile + Gargoyle banner, Rev6
  Zenodo post, outreach drafts (metzdowd, MCP), ORCID correction, site Rev6 DOI update) landed
  AFTER the VL-125 close with NO STATE.md update and NO ledger entry, and the tree was left dirty:
  docs/COPYRIGHT_HEADER.txt deleted-on-disk but tracked, and 14 untracked files from the
  2026-06-18/19 native sessions.
- The apparent 6-file "modified" set was the VL-108-class mount artifact (stale index + truncated
  mount reads), ruled out per SESSION_PROTOCOL environment rule 2: the host files match HEAD
  (verified via the host file tools - .gitignore's full tail present; STATE.md tail matches the
  HEAD blob). The index was rebuilt from HEAD via a tmpfs GIT_INDEX_FILE; nothing was discarded.
- NEW artifact VARIANT recorded: after host-tool edits, the mount served reads CAPPED AT THE
  PRE-EDIT byte length with the new content mixed in - neither pure-stale nor pure-truncated
  (grep found new strings while wc -c reported the old size and tails were mangled). Consequence:
  no git add through the mount; both build commits were assembled from tmpfs-staged exact content
  via plumbing (hash-object -w + update-index --cacheinfo + write-tree + commit-tree +
  update-ref), per environment rule 5, and every committed blob was hash-verified against the
  staged bytes (all MATCH).

#### What landed (close-repair build, commit 685a907)
- deploy/AUTHORIZATION_TO_TEST.md, deploy/SAFE_HARBOR_CLAUSE.md, deploy/PHASE1_PRELAUNCH_RUNBOOK.md
  COMMITTED. These were already referenced by the COMMITTED deploy/PRIVATE_INVITE_PROGRAM.md doc
  inventory (rows naming AUTHORIZATION_TO_TEST and SAFE_HARBOR_CLAUSE) - i.e., HEAD carried broken
  references until this commit. Their stale YesWeHack-era references were updated to the VL-125
  private-invite model (platform/channel lines; the paste target for the counsel-approved clause is
  now PRIVATE_INVITE_PROGRAM.md's SAFE HARBOR section; the launch line now points at
  SOLICITOR_INTAKE_CHEATSHEET.md; researcher acceptance recorded by counter-signature or written
  acceptance instead of platform terms).
- deploy/PHASE1_PRELAUNCH_RUNBOOK.md annotated with honest STATUS notes: Gate 1 (publisher-key
  rotation) CLOSED at VL-122 (key id pub-2026-06-18; kept for the method of record); Gate 3 green
  runs on record (attack suite exit 0 at VL-108, version-matched signed-mode re-run + sidecar live
  ALLOW/DENY at VL-122; REAL_TRANSPORT flipped at VL-108) with an explicit re-run-inside-the-window
  requirement.
- docs/design/governance_layer_KICKOFF.md COMMITTED (the session-kickoff companion to the committed
  governance_layer_design.md; the governance build it kicked off completed at VL-113..VL-120).
- docs/COPYRIGHT_HEADER.txt deletion COMMITTED - the AUTHOR confirmed this session the deletion was
  intentional.
- .gitignore: 10 session-local/superseded files added to the deliberate private section
  (SESSION_WORK_ASSESSMENT.md, TLS_BOOTSTRAP_DOSSIER.md, check_history.sh, disable_history.sh,
  docs/ZENODO_REV{4,5,6}_ADDENDUM.md drafts - superseded by the committed docs/zenodo/*.md - and
  docs/zenodo/*.pdf upload artifacts). This is the deliberate private-section pattern, NOT a fourth
  instance of the inherited-.gitignore collision pattern (VL-010/VL-017/VL-125).

#### What was authored (Phase-3.2 asset half, commit a2c9f82)
- NEW deploy/REBUILD_ESTIMATOR_BRIEF.md: the commissioning pack for ext-readiness Gate 3
  (docs/methodology/external_verification_readiness.md) / execution-plan Phase 3.2 (artifact 29).
  Carries: the cost question verbatim (assemble the equivalent admission-and-attestation substrate
  from OPA + SPIFFE + a PKI, or the estimator's own component judgment) BOUND to whether it SHIPPED,
  not to an estimate (a model's "1-2 months" is named non-evidential per VL-057); the stake-free
  eligibility filter with the explicit contrast that blindness is Gate 4's filter, not Gate 3's,
  plus the do-not-show-convergence-verdicts rule (VL-057); a functional-equivalence target bound to
  falsifiable_claim_sheet.md Section 1 rows 1-8 (fail-closed pinned admission; signed action-bound
  attestation; replay/freshness; drift refusal; enforcement locus + positive control); the report
  deliverable (shipped-or-not, cost actuals, per-item friction, verdict, up-front estimator-declared
  time-box); both-verdicts-acceptable framing; verbatim ledgering + the VL-125 recognition model;
  and an author-fills engagement-terms block (estimator, time-box, compensation TBD, channel).

#### Honest scope
NO IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof change; the test suite is unaffected
(the session's diff against 40fb5e6 is deploy assets, docs, .gitignore, STATE.md, and this ledger
entry only). These are author-authored ASSETS, not referents: ext-readiness Gate 3 remains NOT MET
until a stake-free person ships the report (whatever it concludes); the pre-exposure items 3-6
remain open (item 3 cert hooks, item 4 counsel HARD GATE, item 5 window/channel, item 6 publish);
G5 (a blind external attacker on the live surface) remains NOT-MET; no readiness predicate goes
green.

#### Files affected
deploy/AUTHORIZATION_TO_TEST.md (NEW), deploy/SAFE_HARBOR_CLAUSE.md (NEW),
deploy/PHASE1_PRELAUNCH_RUNBOOK.md (NEW), docs/design/governance_layer_KICKOFF.md (NEW),
deploy/REBUILD_ESTIMATOR_BRIEF.md (NEW), docs/COPYRIGHT_HEADER.txt (REMOVED), .gitignore,
STATE.md, EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, CANON/, MANIFEST/, TESTS/, EVIDENCE/proofs/, EVIDENCE/published_hashes.json
- byte-identical to 40fb5e6.

#### Environment note (Cowork sandbox)
Ghost .git/HEAD.lock and 235 orphaned .git/objects tmp_obj_* files (debris of the mount's
unlink-block during plumbing) were cleaned after granting file-delete; a Jul-1 ghost index.lock
resists unlink (rule-4 wedge) but does not block the tmpfs-index commit route - a Cowork restart
clears it. The sandbox has no GitHub credentials: HEAD is three commits ahead of origin/main
(685a907, a2c9f82, and this close commit). The AUTHOR verifies the blobs natively (git cat-file -s
/ content spot-checks vs this entry's inventory) and pushes; until then the at-rest invariant is
knowingly open, and pushing is the FIRST task of any session that resumes before it lands.

#### Citation discipline (VL-012)
Prior substantive entry: VL-125. This entry cites VL-125 (the private-invite model and recognition
model the pack was aligned to), VL-122 (Gate-1 closure + signed-mode facts), VL-108 (the mount
hazard family + the pre-exposure list), VL-057 (referent-binding / verdict demotion), VL-012 (the
hash rule), and VL-010/VL-017 (the .gitignore pattern contrast). It cites the two build commits
685a907 and a2c9f82; it does not cite its own hash.

---

### VL-127 - 2026-07-03 - T-recruiting: channel re-alignment - no bug-bounty platform; the site disclaimer + LinkedIn posts are the solicitation channels; residual platform/cash references purged; LinkedIn drafts authored

#### Decision recorded (author, this session)
No bug-bounty platform will be engaged for the G5 red-team recruiting - YesWeHack was
retired at VL-125, and HackerOne / Bugcrowd / Intigriti (still recommended as "Best fit"
in the pre-VL-127 outreach doc) are now explicitly NOT used. The solicitation channels
are: (a) the public one-page site, whose engagement/disclaimer block (committed at
VL-125/40fb5e6) already carries the private invite-only format, the safe-harbor line,
the scope/rules, and the security@elyon-sol.io intake; and (b) LinkedIn posts from the
author's profile. All channels route to the same gated intake + vetting + signed
Authorization-to-Test.

#### What changed (build a8ae52b)
- deploy/RED_TEAM_OUTREACH.md REWRITTEN: a channel preamble (private/invite-only, the two
  channels, the intake path); section A's subject de-cashed ("Paid short engagement" ->
  "Short invited engagement") and its "Compensation: [$X / negotiable]" replaced with the
  VL-125 recognition/ownership model inline; section B retitled "(private, invite-only -
  no platform)" (scope/focus/boundaries/recognition text unchanged); section C's
  "compensation agreed" -> "recognition terms agreed"; section D now leads with LinkedIn
  (PRIMARY) + the public site, keeps GitHub/conferences, r/netsec/OWASP/Discords, and
  Upwork/Toptal cold-briefing, and closes with an explicit NOT-used note naming the
  platforms (the only remaining platform-name mention in the recruiting assets, and it is
  negative). REPAIRS a pre-existing COMMITTED defect: the prior blob ended mid-word
  ("- Upwork / Toptal - c", no trailing newline) - the chat-paste-eats-content family,
  present since the file's VL-107-era commit and unnoticed until this scan.
- deploy/BREAK_IT.md: the submission line drops "(or the program's intake on the
  bug-bounty platform)" - security@elyon-sol.io is the single intake.
- deploy/SOLICITOR_INTAKE_CHEATSHEET.md: the broad-reach venue list now leads with
  LinkedIn as the PRIMARY channel, pointing at the drafts file.
- NEW docs/outreach/linkedin_redteam_posts.md: three paste-ready drafts - Post 1 the
  challenge (claim-to-disprove verbatim from the site, recognition model, intake, DOI
  10.5281/zenodo.21107731), Post 2 mission-aligned for the AI-governance/safety audience
  (leads with the honest no-external-validation-yet status as the reason for the ask),
  Post 3 a short reshare. Each leads with the cheatsheet's three-lead rule; the file
  carries a publishing-is-GATED banner (PHASE1 gates incl. the counsel HARD GATE),
  [SITE URL] fill-fields, and a comment/reply discipline section per artifact 29 4.4
  (answer operational questions only; never explain the design or hint at attacks; no
  scope in comments; never imply external validation exists until a G5 referent is
  ledgered).

#### Honest scope
NO IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof change; the suite is
unaffected. This is a channel DECISION plus author-authored assets, NOT external
validation and NOT a launch: nothing has been posted anywhere; the PHASE1 hard gates
(counsel-signed safe harbor, in-window green self-test, cert hooks, signed
Authorization-to-Test) remain unmet; pre-exposure items 3-7 remain open as ordered in
STATE.md. G5 remains NOT-MET; no readiness predicate goes green. A residue scan of
deploy/ + site/ + docs/outreach/ at the build commit confirms the only platform-name
mention left in the recruiting assets is the explicit NOT-used note.

#### Files affected
deploy/RED_TEAM_OUTREACH.md; deploy/BREAK_IT.md; deploy/SOLICITOR_INTAKE_CHEATSHEET.md;
docs/outreach/linkedin_redteam_posts.md (NEW); STATE.md; EVIDENCE/verification_ledger.md
(this entry).

#### Files NOT affected
site/index.html (its disclaimer/engagement block was already aligned - verified, not
changed); all of IMPLEMENTATION/, CANON/, MANIFEST/, TESTS/, EVIDENCE/proofs/,
EVIDENCE/published_hashes.json - byte-identical.

#### Environment note (Cowork sandbox)
Same session as VL-126; the same tmpfs-staged plumbing route was used (the mount still
serves stale-length reads after host edits), and every committed blob hash-verified
against the staged bytes (all MATCH). The sandbox cannot push: HEAD is now FIVE commits
ahead of origin/main (685a907, a2c9f82, 56b1ea9, a8ae52b, and this close). The AUTHOR
verifies natively and pushes; pushing is the first task of any session that resumes
before it lands.

#### Citation discipline (VL-012)
Prior substantive entry: VL-126. Cites VL-125 (the private-invite/recognition model this
completes), VL-108 (mount hazard family), VL-107 (the era of the repaired truncation),
VL-057 (no-verdicts-shown rule carried into the drafts), and artifact 29 4.4 (the
no-coaching discipline). Cites the build commit a8ae52b; does not cite its own hash.

---

### VL-128 - 2026-07-03 - LIVE currency sweep: all four public nodes verified current; live attack suite green version-matched at 3343e32 (author self-test, NOT external validation)

#### What was done
A four-node currency check of the live public surface, run from the author's laptop against
the deployed Hetzner nodes, prompted by the GitHub Ideas solicitation post (the author wanted
to confirm the surface is current before any responder arrives). Four checks:

1. TRANSPORT + CERTS (openssl s_client per node). All four up; Let's Encrypt leaf certs valid,
   CN-matched, notBefore 2026-06-16, notAfter 2026-09-14 (~73 days out at check time):
   gate.elyon-sol.io:8443, target.elyon-sol.io:9443, pub.elyon-sol.io:9143, authz.elyon-sol.io:9243.
2. SERVICE LIVENESS (curl). authz /healthz -> 200; target /received -> 200;
   pub /published_hashes.json -> 200; gate /governed-call -> 405 (POST-only route answering,
   i.e. the app is up).
3. SIGNED-RECORD CURRENCY. pub /published_hashes_signed.json validated:
   publisher_key_id = pub-2026-06-18 (the VL-122 rotated key; old key retired), serial present,
   issued_at 2026-07-03T20:41:38Z, not_after 2026-07-03T20:46:38Z -> FRESH at check time. The
   ~5-minute window confirms a LIVE publisher actively re-signing on a schedule, not a stale
   committed file.
4. LIVE ATTACK SUITE (EVIDENCE/proofs/attack_suite_live_runner.py over real TLS). GREEN, exit 0:
   positive_control HONORED; unattested -> REF_VERIFY_ENVELOPE_ABSENT; forged_signature ->
   REF_VERIFY_SIGNATURE_INVALID; replay -> REF_VERIFY_REPLAY; rebind_tool / rebind_args /
   target_url_swap -> REF_VERIFY_BINDING_MISMATCH. 6/6 request-tampering attacks defeated over
   real cross-host transport + positive control honored.

#### Version-matching (a process finding, resolved)
The first run of the live runner FAILED (KeyError 'envelope' on the positive control) because the
laptop checkout was on main (HEAD), whose manifest hashes to ac18ac78... (HIGH_IMPACT:[] added at
VL-115), while the DEPLOYED gate runs 3343e32, whose manifest hashes to a21dea8b... . interaction_for
embeds the manifest pin from the local checkout, so a HEAD-pinned request is correctly REFUSED by
the 3343e32 gate (403, no envelope) -> the KeyError. This is the gate doing its job, not a defense
failure. Resolved per VL-122's "run version-matched" rule via a detached worktree at 3343e32
(`git worktree add ../elyon-live 3343e32`), from which the suite ran green. LESSON (reinforces
VL-122): the live runner MUST be run from a checkout at the deployed commit; a manifest/schema skew
between the runner and the deployed gate surfaces as a positive-control failure, not a silent pass.
The runner by design does NOT drive the stale/drifted_state cases over the generic HTTP adapter
(they stay covered in-process); this run covers the request-tampering class over real transport.

#### Honest scope
WHITE-BOX AUTHOR SELF-TEST confirming (a) the four nodes are current and (b) the defenses hold over
real transport at the deployed commit - the same class of evidence as VL-108 and VL-122. This is
NOT external validation and NOT a G5 referent (GR-3/VL-057): the author ran their own scripted suite
against their own surface. No readiness predicate changes; REAL_TRANSPORT was already green at VL-108.
G5 (a blind external attacker on the live surface) remains NOT-MET. The GitHub Ideas post is a
solicitation, not an engagement; the pre-exposure HARD GATES (counsel-signed safe harbor above all,
plus the in-window self-test + cert-renewal hooks + signed Authorization-to-Test) remain UNMET, so
no responder should be pointed at the live hosts yet.

#### Files affected
STATE.md (currency line + a Current-verified-state bullet), EVIDENCE/verification_ledger.md (this
entry). NO IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof change; the suite is unaffected;
no live-run log file is committed (the run was on the author's laptop; this entry is the record).

#### Environment note (Cowork sandbox)
This entry was assembled in the same Cowork session via the tmpfs-staged plumbing route (the mount
serves stale-length reads after host edits); the committed blobs hash-verify against the staged
bytes. The sandbox cannot push; HEAD is now SIX commits ahead of origin/main (685a907, a2c9f82,
56b1ea9, a8ae52b, a7c3593, and this entry). The AUTHOR verifies natively and pushes; pushing is the
first task of any session that resumes before it lands.

#### Citation discipline (VL-012)
Prior substantive entry: VL-127. Cites VL-122 (the rotated key pub-2026-06-18 + the version-matched
run rule + the byte-anchor->signed correction), VL-108 (the prior live green + REAL_TRANSPORT flip),
VL-083 (the live-runner + REAL_TRANSPORT predicate it exercises), VL-115 (the manifest change behind
the version skew), and VL-057/GR-3 (the not-external-validation discipline). Does not cite its own hash.

---

### VL-129 - 2026-07-03 - SITE honest-scope cleanup: four public-site overclaims/contradictions corrected in the repo-canonical site/index.html; live WordPress copy still to update

#### What prompted it
A review of the LIVE public site (https://elyon-sol.io) against repo state. First finding: the
live site is a WordPress deployment (WordPress 6.9.4), a SEPARATE artifact from the committed
site/index.html - so the public-facing claims live OUTSIDE the repo's ledgered honesty controls
and had drifted from them. The committed site/index.html shared the same copy and the same four
problems, so it was corrected here as the canonical source; the same four edits still have to be
applied in the WordPress editor (not repo-reachable from this session).

#### The four items (all corrected in build 01aef29)
1. OVERCLAIM (legal): the engagement block read "Safe harbor - Good-faith research within scope is
   authorized (counsel-finalized clause)". deploy/SAFE_HARBOR_CLAUSE.md is headed "DRAFT for counsel
   review (HARD GATE)" and STATE item 4 (counsel sign-off) is UNMET. A public "counsel-finalized"
   claim is false against our own record and a reliance risk. Corrected to: authorized under a
   clause "currently in counsel review - not yet finalized. No invitations issue and no traffic is
   authorized until it is signed."
2.+3. MISSING honest-scope + live-vs-built drift: the site advertised the human-oversight governance
   (202 PENDING_APPROVAL), mTLS non-bypass, and "512 tests green" alongside "these are the only hosts
   in scope", implying the live nodes enforce them. Per VL-122 the live four nodes run 3343e32
   (pre-governance, ~394-399 tests); the governance/mTLS/512 build is on side refs, NOT deployed. And
   no external validation exists (GR-3). Added a "Honest scope" paragraph in the live-surface section:
   Elyon-Sol has not yet been externally validated (this challenge is how we seek it; a break would be
   the FIRST such result); the public nodes enforce the cryptographic admission core (signing,
   freshness, single-use, binding); the governance + mTLS layers are implemented/tested in the
   codebase but NOT deployed on these public nodes and are OUT OF SCOPE for the live challenge. This
   also corrects a VL-125 overclaim: its entry said site/index.html "carries the honest-scope note"
   - it did NOT until this commit.
4. CONTRADICTION: the canon block read "AGPL-3.0 open-core - repository private, access on request",
   contradicting the repeated "AGPL-3.0 open-core" badge (and the .gitignore's "repo is public"
   comment). Changed to "source available on request", removing the internal contradiction WITHOUT
   asserting a GitHub visibility this session cannot confirm. FLAG (not silently resolved): AGPL-3.0
   sect.13 requires network-service source availability to users of the deployed service; whether
   "on request" satisfies it for the live surface is a counsel question, recorded here.

#### Honest scope
Author-side site copy correction. NO IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof
change; the suite is unaffected. Only site/index.html + STATE + this entry changed. This is a
honesty/currency cleanup, not a capability or validation event; no readiness predicate changes; G5
remains NOT-MET. ACTION STILL OPEN (author-locus, not repo-reachable): apply the same four edits to
the live WordPress site so the public copy matches the corrected canonical source; until then the
live site still carries the four items.

#### Files affected
site/index.html; STATE.md; EVIDENCE/verification_ledger.md (this entry). site/index.html is the
repo-canonical source; the WordPress deployment is a separate artifact updated out-of-band.

#### Files NOT affected
All of IMPLEMENTATION/, CANON/, MANIFEST/, TESTS/, EVIDENCE/proofs/ - byte-identical.

#### Environment note (Cowork sandbox)
Same session/route as VL-126..128 (tmpfs-staged plumbing; mount serves stale-length reads); the
committed site blob hash-verified against the staged bytes (MATCH). The sandbox cannot push; HEAD is
now EIGHT commits ahead of origin/main (685a907, a2c9f82, 56b1ea9, a8ae52b, a7c3593, 12a3bb4,
01aef29, and this close). The AUTHOR verifies natively and pushes; pushing is the first task of any
session that resumes before it lands.

#### Citation discipline (VL-012)
Prior substantive entry: VL-128. Cites VL-122 (the live nodes run 3343e32, governance not deployed),
VL-125 (the recruiting site it corrects + the honest-scope-note overclaim), and GR-3/VL-057 (the
not-externally-validated discipline the added note restores). Does not cite its own hash.

---

### VL-130 - 2026-07-03 - T-recruiting: G5 conversion kit - seven paste-ready assets to convert public solicitation into an engaged blind external red-teamer

#### Why
The author confirmed the safe-harbor / Authorization-to-Test sign-off is in hand and is actively
soliciting externally (GitHub Ideas post live). The remaining barrier to G5 is CONVERSION: a novel,
unknown, no-cash target has a high activation cost for exactly the skilled, stake-free researchers
G5 requires. This kit attacks the two barriers - friction (time-to-first-attempt) and suspicion
(unknown-solo-challenge distrust) - without touching the honesty discipline.

#### What was authored (build 60e7e0c)
- deploy/BREAK_IT_IN_60_SECONDS.md: a no-signup, copy-paste curl quickstart against the LIVE public
  surface. The interaction body carries a PRECOMPUTED args_sha256
  (ee0885070ca8ca1ff7df3e53275c4cadb3fbf747f3e0ea380a002f8c69ab8e9d, = sha256 of canonical_json(
  {"amount":100,"to":"acct-42"})) and the DEPLOYED manifest pins (version "1.0",
  expected_manifest_sha256 a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8) read from
  3343e32 - the commit the live nodes run (VL-122/128) - so the mint call actually succeeds against
  the live gate rather than 403-ing on a manifest-pin skew (the exact failure diagnosed in VL-128).
  Shows the positive control, then five refusable attacks (absent / replay / forge / rebind / sidecar).
- deploy/INSPECT_YOUR_BREAK.md: packages the read-only envelope_inspector CLI (inspect / reevaluate /
  reconcile) as a one-command self-adjudicator, with the explicit adjudication rule (a finding = the
  tool rates the token invalid AND the surface honored it). Removes the "the author will dismiss my
  finding" barrier by making the TOOL the referent.
- deploy/WALL_OF_FAME.md: a first-blood / CTF scoreboard ("nobody has broken it yet"), the capture
  vs not-a-capture rules, mirrored to the ledger; converts the challenge from a features list into a
  puzzle with bragging rights.
- docs/outreach/target_list_and_referral.md: where the novelty-for-credit pools are (protocol/crypto/
  authz researchers, CTF crews + university clubs, AI-safety niche), a 15-20-contact list template,
  and template R (referral cold-mail) whose SECOND ask is a name ("who's the one person you'd point
  at this?") plus template F (a voucher's forward).
- docs/outreach/audience_pitches.md: three motivation-matched variants - university-CTF (puzzle +
  resume), AI-safety (mission), early-career (portfolio/CVE/first) - with placement notes.
- deploy/BREAK_IT_WEEK.md: a time-boxed event (pre-flight gates, run rules incl. the artifact-29 4.4
  no-coaching discipline, honest close) with paste-ready announcement copy; frames a clean week as
  the first bounded EXTERNAL-ATTEMPT referent, explicitly NOT proof of unbreakability.
- docs/outreach/TRUST_THIS_CHALLENGE.md: the honesty-as-credibility lead block - concedes no external
  validation, the tool adjudicates, the claim is falsifiable and narrow, it is all on the public
  record - reusable across posts; reasoning captured (undersell lowers suspicion for stake-free pros).

#### Access model (unchanged, made explicit)
The ATTACKING surface is public and pokeable immediately (no signup) - the invite-only gate governs
only the CREDITED engagement (reward + coordinated disclosure), entered at security@elyon-sol.io with
vetting + the signed Authorization-to-Test. Every asset keeps the honest-scope line and the gated-pack
/ no-coaching discipline (do not send the briefing pack, internal reviews, or cross-model verdicts to
an un-vetted researcher; VL-057).

#### Honest scope
NO IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof change; the suite is unaffected and was
INDEPENDENTLY re-verified this session (python -m pytest -> 512 passed on a clean sandbox extraction,
the first time the count was checked against the code rather than carried from the ledger). These are
recruiting ASSETS, not external validation and not a live event; nothing is posted or scheduled by
this commit. G5 (a blind external attacker engaging the live surface) remains NOT-MET; no readiness
predicate changes.

#### Files affected
deploy/BREAK_IT_IN_60_SECONDS.md (NEW), deploy/INSPECT_YOUR_BREAK.md (NEW), deploy/WALL_OF_FAME.md
(NEW), deploy/BREAK_IT_WEEK.md (NEW), docs/outreach/target_list_and_referral.md (NEW),
docs/outreach/audience_pitches.md (NEW), docs/outreach/TRUST_THIS_CHALLENGE.md (NEW), STATE.md,
EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, CANON/, MANIFEST/, TESTS/, EVIDENCE/proofs/, site/index.html - byte-identical.

#### Environment note (Cowork sandbox)
Same session/route as VL-126..129 (tmpfs-staged plumbing; the mount serves stale/truncated reads after
host edits - re-confirmed when the VL-126 working-tree files were found truncated at the session-close
check and restored from HEAD). All seven blobs hash-verified against the on-disk files (MATCH). The
sandbox cannot push; after VL-129's native push HEAD==origin was restored, and this build+close leaves
HEAD TWO commits ahead of origin/main (60e7e0c build + this close). The AUTHOR verifies natively and
pushes; pushing is the first task of any session that resumes before it lands.

#### Citation discipline (VL-012)
Prior substantive entry: VL-129. Cites VL-128 (the deployed-commit manifest-pin skew the quickstart is
built to avoid), VL-122 (the live nodes run 3343e32), VL-097 (the envelope_inspector the self-adjudication
doc packages), artifact 29 4.4 (the no-coaching rule) and VL-057 (the gated-pack / no-verdicts discipline).
Does not cite its own hash.

---

### VL-131 - 2026-07-03 - SITE build-out of the conversion kit + repair of a pre-existing site/index.html truncation

#### Two things happened
1. The VL-130 recruiting conversion kit was folded into the public site source site/index.html.
2. A PRE-EXISTING truncation of that file was discovered and repaired.

#### The truncation (root cause)
site/index.html had been committed TRUNCATED since at least 40fb5e6 (the 2026-07-03 native session,
before this Cowork session): the blob ended mid-word at "...confirm a break befor" with NO remainder
of the how-to-start/submit list, NO closing </div>/</section> tags, NO <footer>, and NO </body></html>.
This is the VL-108/VL-126-class mount-truncation artifact baked into a native commit. It was carried
forward invisibly through VL-129 (honest-scope cleanup) and 0a4d605 (the quickstart), because those
edits only touched the MIDDLE of the file and preserved the truncated tail. Confirmed pre-existing:
git cat-file -p 40fb5e6:site/index.html ends at the identical byte; the only two "footer" matches in
the file were the CSS rules footer{...}/footer a{...}, not an actual element.

#### What was built (0a4d605, then b21ecc2)
- 0a4d605: the "Break it in 60 seconds" section (id=tryit) between #surface and #canon - a copy-paste
  curl walkthrough (mint -> positive control -> five refusable attacks) carrying the PRECOMPUTED
  args_sha256 (ee0885...8e9d) and the DEPLOYED-manifest pins (version 1.0,
  sha a21dea8b...23b8 from 3343e32) so the mint call actually succeeds against the live gate; a
  pre.code / .step code-block CSS; a nav link; and the hero primary CTA retargeted from #redteam to
  #tryit (send people to a runnable attack, not a wall of text).
- b21ecc2: REPAIRED the truncation AND folded in the rest of the kit: completed the submit list with
  the inspector SELF-ADJUDICATION ("the tool decides, not us" + the one-command inspect) and a submit
  line; added an honest-scope note; a Wall-of-Fame section (id=wall) - a first-blood/CTF board
  ("nobody has broken it yet", the awaiting row, honorable-mentions note); the why-trust-this honesty
  block as a claimbox right after the "claim to disprove"; a real <footer> (project/contact links + the
  "no external validation yet - G5 is the open finish line" line); and #tryit/#wall nav links. The
  document now closes </body></html> and EVERY tag balances (HTMLParser residual 0; section 9/9,
  div 127/127, ul 3/3, table 2/2, footer 1/1, body 1/1, html 1/1) - vs the pre-repair unclosed state.

#### Honest scope
NO IMPLEMENTATION / CANON / MANIFEST / TESTS / EVIDENCE-proof change; the suite is unaffected. These
are public recruiting assets, NOT external validation. CRITICAL DISTINCTION: site/index.html is the
REPO-CANONICAL source; the LIVE site at elyon-sol.io is a SEPARATE WordPress deployment - these repo
edits do NOT change what visitors see until the content is applied in the WordPress editor. G5
(a blind external attacker) remains NOT-MET.

#### Files affected
site/index.html (0a4d605 + b21ecc2); STATE.md; EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
All of IMPLEMENTATION/, CANON/, MANIFEST/, TESTS/, EVIDENCE/proofs/ - byte-identical.

#### Environment note (Cowork sandbox)
Same tmpfs-staged plumbing route; the site blob hash-verified against the staged bytes at each build
(MATCH), and the on-disk working tree was resynced from HEAD after commit. The truncation being
pre-existing (in 40fb5e6, a native commit) shows the mount hazard has bitten the AUTHOR's native
workflow too, not only the sandbox - a reason to prefer the plumbing+verify discipline generally. The
sandbox cannot push; after VL-129's push HEAD==origin, and VL-130 (2) + VL-131 (0a4d605, b21ecc2, this
close) leave HEAD FIVE commits ahead of origin/main. The AUTHOR verifies natively and pushes.

#### Citation discipline (VL-012)
Prior substantive entry: VL-130. Cites VL-130 (the kit it renders), VL-128/VL-122 (the deployed 3343e32
manifest pins baked into the quickstart), VL-129 (the honest-scope edits it builds past), and
VL-108/VL-126 (the mount-truncation family this instance belongs to). Does not cite its own hash.


---

### VL-132 - 2026-07-05 - T-governance typed-impact evaluator increment: per-interaction-type required-set selection; impact lifted from all-or-nothing to per-type. EDITS evaluator.py (G(I)) - evaluator_sha256 re-pinned.

#### What was built
IMPLEMENTATION/evaluator.py gains typed-impact support so eligibility can resolve DIFFERENT required
sets per declared interaction type - which is what lets impact discriminate (some types forward, some
hold): (1) resolve_required_sets(manifest, ctx) selects (AR, R) by the caller's declared
interaction_type, defaulting to the top-level sets for a flat manifest OR an untyped caller, and
FAIL-CLOSED -> (None, None) -> REFUSE on an unknown/malformed type; (2) safe_manifest validates an
OPTIONAL interaction_types map fail-closed - each type's AR/R are string-lists whose union is a SUBSET
of the top-level AR u R (so top-level stays the token vocabulary and impact.safe_high_impact's [FIX H2]
subset check is UNCHANGED), each carries an EXPLICIT boolean high_impact, and a type's flag must be
CONSISTENT with whether its own tokens intersect HIGH_IMPACT (a mislabel -> None); (3) evaluate() uses
resolve_required_sets. IMPLEMENTATION/impact.py is BYTE-UNCHANGED.

#### The finding this corrects
Impact was structurally all-or-nothing. evaluate() compared against a SINGLE flat AR/R and
interaction_for returns a FIXED AP/OP for every tool/args, so every eligible caller declared AR u R;
with [FIX H2] constraining HIGH_IMPACT to a subset of AR u R, any non-empty policy matched EVERY mint
and an empty one matched none. VL-113's "impact is a property of the interaction TYPE" was therefore
realized only DEGENERATELY (a single type). This increment makes the type real: a benign type is
ELIGIBLE while declaring FEWER tokens, so requires_approval can return False for it and True for a
sensitive type on the SAME manifest - a state the flat model could not express.

#### G(I) distinction from VL-113 (recorded honestly)
VL-113 deliberately placed impact classification in its OWN module to keep evaluator.py byte-identical,
because editing evaluator.py changes the pinned evaluator_sha256 and REDs the verify-against-pinned
tests. Per-type required-set SELECTION is intrinsic to eligibility (which AR/R to compare against), so
it CANNOT live above G(I): this increment DOES edit evaluator.py. As expected it changed evaluator_sha256
(89a30ffe... -> e307fab2...) and RED-ed the same 49 verify-against-pinned tests until
EVIDENCE/published_hashes.json was regenerated via its own generator (never hand-copied) - exactly the
VL-115 manifest-pin-regen discipline, applied to the evaluator pin. CANON/canon.md is UNTOUCHED
(canon_sha256 d1c9d18... unchanged); the three invariants (AC^3/T^26/CCS) are unchanged in meaning; the
evaluator still implements canon v0.9.8.4 (evaluator_version stays 0.9.8.4 - the field denotes the canon
version implemented, not the code revision; the code identity is evaluator_sha256, which moved and was
re-pinned). GR-1 (canon-by-increment) is NOT triggered.

#### Backward-compatibility (proven, not asserted)
A flat manifest (no interaction_types) is the degenerate single-type case and is byte-behaviour-identical:
the clean git-archive HEAD baseline (515 passed) is UNCHANGED by the evaluator edit once the pin is
regenerated. TESTS/adversarial/test_typed_impact.py +15 (per-type selection; unknown/mislabeled type
fail-closed; token-outside-vocabulary rejected; [FIX H1]/[FIX H2] preserved on a typed manifest; the
headline "benign ELIGIBLE and low-impact" the flat model cannot express), suite 515 -> 530 green
(working tree; re-verify on a pristine git-archive extraction before finalizing the count). 4
revert-catchers (per-type selection matters; unknown-type fail-close; token-outside-vocabulary; mislabel).

#### Honest scope / build-then-wire
EVALUATOR increment only, DEFAULT-OFF: MANIFEST/manifest.json is UNCHANGED (still flat HIGH_IMPACT:[],
manifest_sha256 ac18ac78... unchanged) and interaction_for STILL returns a fixed AP/OP, so NO production
behavior changes and no mint forwards or holds differently until the typed manifest + real AP/OP
derivation are wired (a subsequent increment). Because manifest_sha256 is unchanged, the target/sidecar
MANIFEST pin is unaffected; but the published-record BYTE-ANCHOR changed (evaluator_sha256 field), so a
real deployment re-pins Host B on the new anchor. No readiness predicate goes green; G5 NOT-MET.
WHITE-BOX in-house build, NOT external validation (GR-3/VL-057).

#### Files affected
IMPLEMENTATION/evaluator.py; EVIDENCE/published_hashes.json (evaluator_sha256 regenerated);
TESTS/adversarial/test_typed_impact.py (new); STATE.md; EVIDENCE/verification_ledger.md (this entry).

#### Files NOT affected
IMPLEMENTATION/impact.py, approval.py, pep.py, verifier.py, envelope.py; MANIFEST/manifest.json;
CANON/ (canon.md/canon.lock byte-identical) - all UNCHANGED.

#### Environment note (Cowork sandbox)
Built in the Cowork sandbox; files written through bash and verified (ast.parse + byte counts) per the
VL-108/VL-126 mount-truncation discipline. The "49 REDs until re-pin" was reproduced and resolved exactly
as VL-113 predicted. Counts are working-tree; the AUTHOR should re-verify on a pristine git-archive HEAD
extraction and push natively.

#### Citation discipline (VL-012)
Prior substantive entry: VL-131. Cites VL-113 (the impact-classification origin + the ABOVE-G(I)
placement this increment consciously departs from), VL-115 (the manifest-pin-regen discipline this
mirrors for the evaluator pin), GR-1/VL-007 (canon-by-increment, NOT triggered), and VL-108/VL-126 (the
mount-truncation family). Does not cite its own hash.


---

### VL-133 - 2026-07-05 - T-governance typed-impact WIRING (step 8.2): request-schema interaction_type + interaction_for per-type derivation + governed_call per-type envelope. Default-off; NO pin change.

#### What was built
The three wiring points a real submission needs for a BENIGN type to forward end-to-end (surfaced
by the VL-132 submission-validation harness), all additive and default-off:
1. IMPLEMENTATION/request_validator.py - `interaction_type` accepted as an OPTIONAL string field
   (new `_OPTIONAL_INTERACTION_FIELDS`; excluded from the step-4d unknown-key set; type-checked;
   passed through to the normalized interaction). Absent -> pre-typed behavior, byte-identical.
2. IMPLEMENTATION/mcp_server.py - `interaction_for` maps a tool to an interaction_type
   (`_BENIGN_TOOLS` -> "read", `_SENSITIVE_TOOLS` -> "transfer", unknown -> None) and, under a
   TYPED manifest, emits that type's REDUCED required sets as AP/OP plus interaction_type. Under a
   FLAT manifest (no interaction_types) it returns the pre-typed hardcoded interaction (full
   tokens, version 1.0, NO interaction_type field) - BYTE-IDENTICAL for every tool.
3. IMPLEMENTATION/pep.py - governed_call stamps the envelope's ac3/t26 from
   `resolve_required_sets(safe_mfst, normalized_interaction)` instead of the top-level AR/R (the
   gap the VL-132 submission found at the envelope-construction step). Flat manifest -> top-level
   (byte-identical).

#### Scope / discipline
DEFAULT-OFF: with the live flat manifest (HIGH_IMPACT:[]) in place, production behavior is
UNCHANGED - interaction_for emits full tokens, resolve_required_sets returns the top-level sets, and
no caller sends interaction_type. NO PINNED FILE is touched: canon_sha256, evaluator_sha256
(e307fab2, from VL-132) and manifest_sha256 (ac18ac78) are all UNCHANGED - request_validator.py /
mcp_server.py / pep.py are not part of the published record - so 8.2 requires NO re-pin and NO Host
B action. canon.md UNTOUCHED (GR-1 not triggered). The typed behavior activates only when a typed
MANIFEST/manifest.json is pinned (the deliberate turn-on step; see deploy/TYPED_IMPACT_DEPLOY.md).

#### The capstone (proven end-to-end)
A BENIGN `read` submission (reduced tokens + interaction_type) is ELIGIBLE and FORWARDS with no
202; a SENSITIVE full-authority submission on the SAME typed manifest is HELD (202) -> a
separately-keyed human grant -> forwards exactly once. The discriminating oversight the flat model
could not express, driven by the REAL requires_approval through the actual gate (not a forced flag).

#### Tests
TESTS/adversarial/test_typed_impact_wiring.py +7 (interaction_for flat byte-identity revert-catcher;
typed benign/sensitive/unknown derivation; schema accepts/rejects/omits interaction_type);
TESTS/test_typed_impact_e2e.py +1 (the benign-forwards-end-to-end capstone). Suite 533 -> 541 green
(working tree; re-verify on a pristine git-archive extraction). The flat byte-identity is proven by
the unchanged 533 baseline plus the explicit revert-catcher.

#### Files affected / NOT affected
Affected: IMPLEMENTATION/request_validator.py, IMPLEMENTATION/mcp_server.py, IMPLEMENTATION/pep.py;
TESTS/adversarial/test_typed_impact_wiring.py (new), TESTS/test_typed_impact_e2e.py (new this VL /
extended); STATE.md; EVIDENCE/verification_ledger.md (this entry). NOT affected: evaluator.py,
impact.py, approval.py, verifier.py, envelope.py; MANIFEST/manifest.json; EVIDENCE/published_hashes.json
(no pin change); CANON/.

#### Honest scope / build-then-wire
WHITE-BOX in-house build, NOT external validation (GR-3/VL-057). No readiness predicate goes green;
G5 NOT-MET. Turning typing on in production is a separate deliberate step: it flips the live manifest
(changes manifest_sha256 -> coordinated re-pin), resolves the everything-holds HIGH_IMPACT policy,
and requires migrating the flat-assuming tests - all enumerated in deploy/TYPED_IMPACT_DEPLOY.md.

#### Environment note (Cowork sandbox)
Files written through bash and verified (ast.parse + byte counts) per the VL-108/VL-126
mount-truncation discipline. Counts are working-tree; the AUTHOR re-verifies on a pristine
git-archive extraction and pushes natively. GR-4 note: this is a code-only WIRING build with no
behavior change under the live manifest; it is recorded as a VL entry for continuity with the
VL-113/VL-132 typed-impact line, but is defensibly a commit+STATE-only event under GR-4 - operator's call.

#### Citation discipline (VL-012)
Prior substantive entry: VL-132. Cites VL-132 (the evaluator increment this wires + the submission
harness that scoped these three points), VL-054 (the request-schema unknown-key vocabulary this
extends with an optional field), and VL-115 (the pep approval-gate wiring this per-type-izes). Does
not cite its own hash.
