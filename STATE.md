# Elyon-Sol - Project State

**This file is the entry point. A fresh session - the author, a new Claude
session, Grok, or any collaborator - should read this file first.**

**Session start/end:** see `docs/SESSION_PROTOCOL.md` for the resume and close protocols.
**Governance rules:** see `docs/MAINTENANCE_PROTOCOL.md` for the rules under which the repository is allowed to change (GR-N entries).

Last updated: 2026-07-01 (VL-125: T-recruiting - the G5 external-validation recruiting/publication assets authored + committed (build 816beb8): a self-contained public one-page site (site/index.html - features, technologies, the four-node live surface, canon v0.9.8.4, the CURRENT Zenodo record 10.5281/zenodo.20751592, and the red-team challenge, carrying the honest-scope note that no external validation has occurred and G5 is the open finish line); a platform-neutral PRIVATE, invite-only program pack (deploy/PRIVATE_INVITE_PROGRAM.md, replacing the RETIRED YesWeHack pack); a solicitor-intake cheat sheet (deploy/SOLICITOR_INTAKE_CHEATSHEET.md - the gated what-to-send flow, a reply template, a never-send list, and curated where-to-post venues); and a reward-model change across deploy/BREAK_IT.md + deploy/RED_TEAM_OUTREACH.md from a CASH bounty to a NON-MONETARY recognition/ownership model (permanent named ledger credit, Zenodo co-credit + ORCID, CVE where applicable, invited fix-authorship, a founding red-team seat, and a team creative-ownership / co-maintainer path). The engagement is now PRIVATE, invite-only, run directly by the team - NO bug-bounty platform; entry is a solicitation to security@elyon-sol.io followed by vetting + a signed Authorization-to-Test. .gitignore line 175 '/site' (an inherited mkdocs build-output ignore) was commented out so the published site source under site/ is trackable - the THIRD instance of the inherited-.gitignore collision pattern (cf. VL-010, VL-017). NO IMPLEMENTATION/CANON/MANIFEST/TESTS/EVIDENCE-proof change; the suite is unaffected. Author-authored recruiting material, NOT external validation and NOT a live launch: the program HARD GATES (counsel-signed safe harbor, a green live self-test over the four nodes, cert-renewal hooks, a signed Authorization-to-Test) are UNMET, so nothing is published or open. Advances G5 pre-exposure item 6 (the asset half). G5 (a blind external attacker on the live surface) remains NOT-MET; no readiness predicate goes green. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-124: T-governance - a cross-model convergence round (Cursor + OpenAI + Grok) on the governance core. NO repo code/canon/test change; records a verification round + schedules two refinements. UNANIMOUS across three independent, VL-008-clean models (scope-bound, in-scope citations, scope-confirmation line; no fabrication): NO exploitable bug on a correctly-wired single-process gate, all [FIX H1]-[H8] hold IN CODE, and the only weak paths are DEPLOYMENT-POSTURE (P3 static pin, P4 undeclared scale, P6 no approval log) - the class VL-123's governance_wiring guard was built to catch, which Grok independently credits as catching them at startup. OpenAI maps 1:1 onto the Cursor cluster (GL-01<->G-01, GL-02<->G-05 both RULED OUT, GL-03<->G-04, GL-04<->G-02/03), CONFIRMING VL-123. Two SINGLE-MODEL (OpenAI) sharpenings, verified-on-inspection, NAMED-OPEN/scheduled: GL-01-refine (the VL-123 guard checks approver-trust INJECTED-ness, not signed-chain PROVENANCE - an injected gate-controlled map still passes; robust fix = pep resolves approver keys from the signed key-record chain itself, making the bootstrap shim optional) and GL-03-refine (the audit guard is startup-only; add a request-path fail-closed). Both deployment-gated, not exploitable; deferred to a deliberate follow-up. Transcripts under EVIDENCE/verification_runs/. WHITE-BOX convergence evidence, NOT external validation (GR-3/VL-057); live nodes UNAFFECTED; G5 NOT-MET. Commit chain on side ref refs/heads/governance-xmodel-vl124, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-123: T-governance - a Cursor WHITE-BOX review of the governance core found NO exploitable bug on a correctly-wired gate (the hold->verify->consume->claim->forward chain is sound) + six DEPLOYMENT-POSTURE findings; the hardening cluster G-01/03/04/06 is FIXED, G-02/05 documented. NEW IMPLEMENTATION/governance_wiring.py assert_high_impact_wiring(): a single fail-closed STARTUP check that fires ONLY when the SHA-pinned manifest DECLARES high-impact actions - refuses to start if approver trust is not R1-injected (G-01: the bare static pin's SoD is only a key_id compare a gate can defeat), the approver map is empty (G-06), no approval log is configured (G-04), or the pending/replay shared stores are incoherent (one XOR the other, G-03). NO-OP for the default HIGH_IMPACT:[] manifest -> non-high-impact deployment byte-behavior-UNCHANGED. pep.py adds ONE @app.on_event('startup') hook (the only default-path touch; governed_call request path byte-unchanged). G(I) core + impact/approval/approver_trust/pending_store/replay_cache/key_record_source + manifest + canon + published_hashes all byte-IDENTICAL. TESTS/adversarial/test_governance_wiring.py +13 (revert-catcher per finding, default-app-starts-clean), suite 499 -> 512 green on a pristine extraction; revert-catchers RED-on-revert. G-02 (undeclared multi-worker - a worker cannot see the worker count) is NARROWED not closed (operator declaration load-bearing); G-05 (verify_grant request-id step is redundant - binding carried by check_and_consume) is defense-in-depth, not a bypass. HONEST SCOPE: in-house WHITE-BOX, internal hardening evidence NOT external validation (GR-3/VL-057); all findings were posture, NONE exploitable on the live surface (HIGH_IMPACT:[], single worker), so the live nodes are UNAFFECTED; no readiness predicate goes green; G5 NOT-MET. Commit chain on side ref refs/heads/governance-wiring-vl123, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-122: LIVE-OPS - publisher signing-key ROTATION + a byte-anchor->signed CORRECTION on the live G5 surface; VL-108 pre-exposure items 1 & 2 CLOSED. NO repo code/canon/manifest/test change (suite unaffected). The exposed publisher signing key (VL-108) was regenerated on the publisher host under a never-typed/no-secret-in-history protocol (in-process keygen -> 0600 EnvironmentFile; only the PUBLIC key printed); the publisher now signs under id pub-2026-06-18 and the old key is trusted by NO node. CORRECTION: VL-108 documented 'signed freshness mode', but the live target's ELYON_PUBLISHER_URL pointed at the BYTE-ANCHOR /published_hashes.json - it was actually byte-anchor, so no consumer verified the publisher signature. The rotation re-pinned the new public key on the target AND repointed it at the SIGNED endpoint -> genuine signed mode, VERIFIED live two ways: a direct fetch_signed_record check (PASS key_id=pub-2026-06-18) and the full attack suite over the public surface (positive control HONORED end-to-end through the target IN SIGNED MODE + 6/6 gate-2 attacks REFUSED, exit 0), run version-matched at the deployed commit 3343e32. Sidecar (authz) confirmed NOT in signed mode; VL-108 item 2 closed via a live ALLOW/DENY recheck (200 ALLOW / 403 DENY REF_VERIFY_SIGNATURE_INVALID / 403 DENY REF_VERIFY_ENVELOPE_ABSENT). Gate signs envelopes, does not consume the record (no publisher pin), issuer key never exposed -> not rotated. DEPLOYMENT FACT: the live four nodes run 3343e32 (VL-109), NOT latest main - the governance layer (R1/R2) and the post-VL-115 manifest are NOT deployed; that is the separate operator-locus deployment. NEW deploy/KEY_ROTATION.md + deploy/rotate_publisher_key.py (the runbook + safe keygen helper). VL-108 items 3-7 (cert-renewal hooks, counsel sign-off, bounty/window/channel, publish, recruit) remain OPEN; G5 NOT-MET. WHITE-BOX author self-test, NOT external validation. Commit chain on side ref refs/heads/keyrotation-vl122, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-121: T-governance DEPLOYMENT artifacts authored (operator-locus) - the package that wires the completed in-repo governance build (Feature 1 mechanism 1a-1d + R1 + R2; Feature 2 mTLS 2a; integration proof) into a real all-layers deployment. NO IMPLEMENTATION/TESTS/canon change; suite 499 unchanged. NEW deploy/governance/approver_trust_bootstrap.py (the R1 wiring shim: loads the SIGNED key record, resolves the ROLE-DISTINCT approver map via approver_trust, injects pep._INJECTED_APPROVER_KEYS, re-exposes pep.app; fail-closed; SMOKE-VALIDATED in-sandbox - only the approver-role key is injected, issuer/role-less excluded); deploy/docker-compose.governance.yml (redis + TWO gate replicas on the shared store with the R-02 multi-instance env + an approver-cli custody process; YAML-validated); deploy/governance.env.example (the full ELYON_* contract, cross-checked vs the code's reads); deploy/GOVERNANCE_DEPLOYMENT.md (the R1+R2+F2-layers-1/2/3 runbook with acceptance checks, the live A-D integration replay, and a sign-off checklist, leading with the honest claimability gate). HONEST SCOPE: AUTHORED + locally-smoke-validated artifacts, NOT a live deployment and NOT external validation; the real stand-up (docker/CA/Redis/multi-host ACL+egress/Envoy with_request_body) is operator-locus and UNVALIDATED here; no readiness predicate goes green; G5 NOT-MET. Base = the R2 side-ref tip (on c29cb4a after R1's native push); commit chain on side ref refs/heads/governance-deploy-prep (includes R2 as ancestor), main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-120: T-governance Feature 1 residual R2 BUILT - the [FIX H3]/[FIX H4] shared-store residual so grant single-use AND the 202 pending-slot hold across instances. Before R2, pep hard-coded a per-process pending set (_PendingApprovals dict) + a per-process grant-replay cache (InMemoryReplayCache()), so a horizontally-scaled gate kept N independent copies (a 202 issued on replica A unknown to B; single-consume only per-process -> one approval -> one execution PER replica). NEW IMPLEMENTATION/pending_store.py is the pending-set seam, a SIBLING of replay_cache.py: PendingApprovals/PendingStore protocols; InMemoryPendingApprovals (behavior-IDENTICAL to pep's pre-R2 _PendingApprovals); ExternalStorePendingApprovals(store); RedisPendingStore (SET [EX] + a Lua GET-compare-DEL: concurrent double-consume succeeds at most once, a wrong-decision probe deletes nothing); pending_store_from_env() with the R-02 declare-or-fail guard reused from replay_cache_from_env. pep.py (the only default-path edit): _PENDING = pending_store_from_env() and _GRANT_REPLAY = replay_cache_from_env() (the [FIX H3] requirement - grant single-use now rides the shared cache under scale); _PendingApprovals kept as a backward-compat alias (3 test files import it). DEFAULT (no ELYON_* env) byte-behavior-IDENTICAL; a gate declaring ELYON_REPLAY_MULTI_INSTANCE without a shared store FAILS CLOSED at startup. G(I) core/canon/manifest/published_hashes + R1 modules all byte-IDENTICAL to base. TESTS/adversarial/test_pending_store.py +18 (gap-vs-seam cross-instance, compare-and-delete, fake-redis Lua, R-02 guard), suite 481 -> 499 green in a pristine git archive extraction; 2 revert-catchers (R-02 guard removed; consume delete-on-mismatch) proven RED-on-revert, GREEN on restore; the 3 _PendingApprovals importers + the pep-approval suite stay green. Canon UNTOUCHED (GR-1). HONEST SCOPE: shared-CAPABLE + fail-closed-under-scale; the guarantee holds across instances only with a shared store actually deployed (Redis); the in-repo governance-substrate BUILD is now COMPLETE (Feature 1 mechanism 1a-1d + R1 + R2; Feature 2 mTLS 2a; integration proof), and what remains is OPERATOR-LOCUS (Feature-2 layers 1+3 on real hosts + wiring the shared store). WHITE-BOX, NOT a G5 referent; no readiness predicate goes green on R2. Base c29cb4a (origin/main after R1's native ff+push); built/validated against a pristine git archive (VL-108 mount truncation persists). Commit chain on side ref refs/heads/governance-f1-r2, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-119: T-governance Feature 1 residual R1 BUILT - the [FIX H5] LOAD-BEARING half: approver provenance + role via the signed key-record chain. NEW IMPLEMENTATION/approver_trust.py resolve_approver_keys(validated_key_record_trust_view, gate_key_id, now, clock_skew) -> {key_id: public_key}: a key is eligible IFF its SIGNED record-role is EXACTLY 'approver' (ROLE-DISTINCTNESS, the load-bearing SoD - an issuer/role-less key is structurally excluded, so a gate-minted approval is never honored even though a bare key_id != gate_key_id check would pass it), NOT revoked, in [not_before-skew, not_after+skew) (mirrors verify_envelope VL-075), and key_id != gate_key_id (belt-and-braces). The result is a drop-in for verify_grant's approver_public_keys, so approval.py is byte-UNCHANGED. key_record_source.py is ADDITIVE only - the per-key trust view surfaces the signed entry's OPTIONAL role (role: entry.get('role')); the publisher signs the whole record so role is signature-provenanced; a role-less record yields NO approver keys (fail-closed). Build-then-wire: the existing _INJECTED_APPROVER_KEYS seam already accepts exactly the map resolve_approver_keys returns, so R1 is wireable WITHOUT a pep edit - pep.py byte-IDENTICAL to HEAD (no default-path touch). evaluator/impact/approval/envelope/verifier/pep/manifest/published_hashes all byte-IDENTICAL to HEAD. TESTS/adversarial/test_approver_trust.py +15 (all drive the REAL chain + REAL verify_grant), suite 466 -> 481 green in a pristine git archive extraction; the core revert-catcher (issuer-role key cannot authorize; contrast shows a role-ignoring resolver WOULD honor the gate's self-approval) proven RED on revert (3 RED), GREEN on restore; provenance proven (tampered record -> no approver; unsigned key -> KEY_UNKNOWN); positive composition GREEN end-to-end. Canon UNTOUCHED (GR-1). HONEST SCOPE: this is the PROVENANCE+ROLE half of [FIX H5]; the CUSTODY half (a deployment proof the gate cannot resolve the approver PRIVATE key) is operator-locus. WHITE-BOX, NOT a G5 referent; no readiness predicate goes green on R1. R2 ([H3]/[H4] shared store under scale) remains the open in-repo governance residual. Resume found the VL-108 mount-truncation artifact (HEAD==origin/main==195269e; mount served truncated reads + a stale index) - ruled out per protocol, nothing discarded; built/validated against a pristine git archive HEAD. Commit chain on side ref refs/heads/governance-f1-r1, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-118: T-governance INTEGRATION PROOF (design 3.3) - Feature 1 and Feature 2 shown to COMPOSE: the only path to executing a high-impact action is through-the-gate (mTLS) AND with-a-human-grant. EVIDENCE/proofs/governance_integration_001_runner.py (+ the suite test TESTS/test_governance_integration.py) asserts four legs, all of which hold (exit 0): A) a direct bypass is refused at the TLS handshake (Feature 2 mTLS, real BIO); B) a routed but UNAPPROVED high-impact call returns 202 PENDING_APPROVAL and the target is NEVER called (Feature 1 hold, H6); C) a routed + APPROVED call (grant minted by the approver CLI) executes EXACTLY once and the issuance+approval logs reconcile clean (no FORWARDED_WITHOUT_GRANT, H8); D) a REPLAYED grant_id against a fresh 202 is refused with NO second execution (H3 single-use). Hermetic: a private dev CA + the real pep ASGI app via TestClient with gate/approver keys injected in-process. NO IMPLEMENTATION change (the proof composes existing code). Proof note + log at EVIDENCE/proofs/governance_integration_001.{md,log} (RESULT: PASS). Suite 465 -> 466 green. Canon UNTOUCHED (GR-1). HONEST SCOPE: this proves the two mechanisms COMPOSE in-process; the full non-bypassable property is deployment-gated (Feature 2 layers 1 inline-body + 3 network-ACL/egress are operator-locus, deploy/NONBYPASS_TOPOLOGY.md), and single-use + the pending-set are single-instance until a shared store is wired (R2). The oversight GUARANTEE is claimable ONLY inside a deployment that wires all three Feature-2 layers and the R1/R2 hardening; the in-repo artifact is the composition proof, not a live deployment. WHITE-BOX, NOT a G5 referent (GR-3). Commit chain on side ref refs/heads/governance-f2-inc2, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-117: T-governance Feature 2 increment 2a BUILT - the mTLS client-auth proof, the load-bearing network-layer property that closes A1 (design 2.3). NO IMPLEMENTATION change: the dev-CA leaves already carry the CLIENT_AUTH EKU (deploy/tls/gen_certs.py) and the transport seam supports client certs; this PROVES the property and documents the deployment. TESTS/deploy/test_mtls_required.py adds 4 hermetic MemoryBIO handshake tests: a direct connection WITHOUT the gate client cert is REFUSED at the TLS handshake (the target never reaches app logic - the star proof); the gate cert is honored and the target sees the gate identity; a wrong-CA client is refused; and a CONTRAST test shows that under one-way TLS the same bare connection WOULD be accepted - so mTLS is exactly the layer that closes A1, not TLS alone. EVIDENCE/proofs/nonbypass_direct_call_refused_runner.py is the real-socket, server-side-authoritative version (bare connection REFUSED_AT_TLS; gate connection ACCEPTED; exit 0). deploy/NONBYPASS_TOPOLOGY.md gives the three-layer recipe and marks each layer's status: layer 2 (mTLS) BUILT+PROVEN in-repo; layer 1 (inline body-bound sidecar via Envoy with_request_body - extractor built VL-111, inline wiring) and layer 3 (network ACL + agent egress restriction) are OPERATOR-LOCUS. Suite 461 -> 465 green; the bare-call-refused catcher demonstrated (with mTLS refused; one-way TLS accepted -> bypass reopens). Canon UNTOUCHED (GR-1). HONEST SCOPE: non-bypassable holds ONLY within the network boundary the operator controls; A1 is NARROWED, NOT blanket-closed; G4 is NOT marked RESOLVED. The oversight GUARANTEE (Feature 1) becomes claimable only WITHIN a deployment that wires all three layers; the in-repo proof is the mTLS layer + the recipe, not a live non-bypassable deployment. WHITE-BOX, NOT a G5 referent (GR-3). Commit chain on side ref refs/heads/governance-f2-inc1, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-116: T-governance Feature 1 increment 1d BUILT - the AUDIT half ([FIX H8]) + the approver CLI; Feature 1's MECHANISM is now complete (1a-1d). IMPLEMENTATION/issuance_log.py gains JsonlApprovalLog + approval_log_from_env (JSONL records: approval_request at the 202 hold, grant_consumed in the approved leg). pep.governed_call writes both (injected/env, DEFAULT None = no records, byte-behavior-identical; fail-closed when CONFIGURED - do not acknowledge a hold or forward a release you cannot record). IMPLEMENTATION/envelope_inspector.py gains reconcile_approvals(issued, approvals) with the governance predicate FORWARDED_WITHOUT_GRANT (a held AND forwarded high-impact decision with no grant_consumed) plus ORPHAN_CONSUMPTION / DUPLICATE_GRANT / DUPLICATE_REQUEST_CONSUMPTION; the existing reconcile() is untouched. IMPLEMENTATION/approver_cli.py is the minimal human surface (separate process, separate PRIVATE key never in the repo; make_grant() wraps approval.build_grant/sign_grant so its output is exactly what verify_grant accepts). TESTS/adversarial/test_approval_audit.py adds 9 (synthetic reconcile incl. the revert-catcher; an end-to-end pep-writes-records-then-reconciles-clean; the dropped-consumption-is-caught case; the CLI grant accepted by verify_grant); suite 452 -> 461 green. The FORWARDED_WITHOUT_GRANT predicate proven RED on revert. Canon UNTOUCHED (GR-1); evaluator.py/impact.py/approval.py byte-identical; default path byte-behavior-unchanged (logs off). HONEST SCOPE: reconcile_approvals is keyed on decision_sha256 (issuance-invariant), so it proves 'every held+forwarded high-impact decision has at least one recorded grant', NOT a per-issuance 1:1 match (the grant is claimed before the envelope's decision_id is assigned); the log is the trustworthy referent (parity with reconcile). The oversight GUARANTEE still requires Feature 2 (non-bypassable); no readiness predicate goes green on Feature 1 alone. WHITE-BOX, NOT a G5 referent (GR-3). Commit chain on side ref refs/heads/governance-f1-inc4, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-18 (VL-115: T-governance Feature 1 increment 1c BUILT - the pep approval WIRING; the first default-path touch and the first STATEFUL gate. MANIFEST/manifest.json gains an explicit HIGH_IMPACT: [] (the conscious 'nothing high-impact yet' opt-out, [FIX H1]); this changed manifest_sha256, so EVIDENCE/published_hashes.json was regenerated via its own generator (never hand-copied) and the suite's one hand-coded manifest-sha literal (TESTS/adversarial/test_request_schema.py) was made live-derived. pep.governed_call gains an approval gate placed AFTER ELIGIBLE+envelope-build and BEFORE sign/forward, as explicit early returns ([FIX H6]): requires_approval (manifest-derived, fail-closed) -> if high-impact and no grant, 202 PENDING_APPROVAL with no sign/log/forward; if a grant rides the X-Elyon-Sol-Approval-Grant header, verify_grant (provenance/binding/SoD/freshness) then consume the 202 slot from a gate-side pending-request set ([FIX H4]) then claim grant_id once via the VL-076 ReplayCache seam BEFORE the forward ([FIX H3]); bad grant -> 403 REF_APPROVAL_*; approved -> falls through to the single existing sign+forward (no second forward). Approver trust is an injected/env public-key map with a gate_key_id SoD check ([FIX H5] custody half: the gate holds only PUBLIC keys; provenance/role via the signed key-record chain is the scheduled H5 refinement). Default path (HIGH_IMPACT empty -> requires_approval False) is byte-behavior-unchanged: existing 443 green; TESTS/test_pep_approval.py adds 9; suite 443 -> 452. The core revert-catcher (high-impact + no grant -> 202 AND requests.post never called) proven RED when the gate is removed. Canon UNTOUCHED (GR-1); evaluator.py/impact.py byte-identical; approval.py only +2 surfaced codes (REPLAY, REQUEST_UNKNOWN). HONEST SCOPE: the pending-set and grant single-use are in-process -> multi-instance needs a SHARED store (the R-02 story); the oversight GUARANTEE still requires Feature 2 (non-bypassable) and no readiness predicate goes green on Feature 1 alone; the H8 audit-log/reconcile extension is 1d. WHITE-BOX, NOT a G5 referent (GR-3). Commit chain on side ref refs/heads/governance-f1-inc3, main untouched - the AUTHOR verifies blobs, ff main, pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-17 (VL-114: T-governance Feature 1 increment 1b BUILT - the approval grant. IMPLEMENTATION/approval.py with build_grant/sign_grant/verify_grant mirroring envelope.py's Ed25519 + canonical_json (reuse, not re-implement). verify_grant is a pure {accepted,reason} verifier over REF_APPROVAL_* enforcing review fixes: [H4] binds decision_sha256 (transitively target_url/AP/OP/context/manifest pins) AND approval_request_id - an approval of A cannot release B or another held request; [H3] grant_id is MANDATORY (absent -> REFUSE) so the later single-use claim has a non-skippable key; [H5] SoD rejects approver_key_id == gate_key_id BEFORE the signature (a gate-minted approval is not oversight); [H7] freshness REUSES verifier.not_after_valid (factored out of verify_envelope step 1.5b, behavior-preserving) - a grant's not_after is mandatory, tz-naive/past -> REFUSE, clock_skew tolerated. Scope: single-use claim + the pending-request set are STATEFUL pep wiring (1c); verify_grant is pure. Canon UNTOUCHED (GR-1); the grant lives above G(I); evaluator.py and impact.py byte-identical; verifier.py changed only by the behavior-preserving extraction (not hash-pinned); no default pep.py path changed (build-then-wire/unwired). TESTS/adversarial/test_approval.py adds 14 tests (real Ed25519); suite 429 -> 443 green in a git archive extraction; 5 revert-catchers (H3 / H4 action + request / H5 / H7) proven RED-on-revert then GREEN. WHITE-BOX, NOT a G5 referent (GR-3). Commit chain on side ref refs/heads/governance-f1-inc2, main untouched - the AUTHOR verifies blobs, ff main, and pushes natively. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-17 (VL-113: T-governance Feature 1 increment 1a BUILT - impact classification. New orchestration-layer module IMPLEMENTATION/impact.py with safe_high_impact() + requires_approval() (pure, manifest-derived, fail-closed), folding in adversarial-review fixes [FIX H1] (missing/malformed HIGH_IMPACT fails CLOSED, never the .get(...,[]) empty-set that would silently disable oversight; an EXPLICIT [] is the conscious opt-out) and [FIX H2] (every HIGH_IMPACT selector token must be in AR u R, so an ELIGIBLE caller cannot omit one to self-declare low-impact; impact is a property of the interaction TYPE, not a caller flag). Placed in its OWN module, NOT evaluator.py: editing evaluator.py changes its pinned evaluator_sha256 and RED-ed 49 verify-against-pinned-record tests in the clean-extraction run, so impact classification lives ABOVE G(I) and leaves evaluator.py byte-identical (hash unchanged; safe_manifest/evaluate unchanged - build-then-wire). The corrected spec docs/design/governance_layer_design.md (uploaded design + the 8 fixes H1-H8, marked inline) precedes the build (spec-defines-the-change). TESTS/adversarial/test_requires_approval.py adds 10 tests; suite 419 -> 429 green in a pristine git archive HEAD extraction; 3 revert-catchers proven RED-on-revert then GREEN. Canon UNTOUCHED (GR-1); both features layer above G(I). requires_approval has NO caller yet (build-then-wire/unwired); the oversight guarantee is NOT claimed until Feature 2, and no readiness predicate goes green on Feature 1 alone. WHITE-BOX in-house, NOT a G5 referent (GR-3). Mount truncation hazard recurred (VL-108: HEAD STATE 1187 vs mount 1085; ledger 16270 vs 16139; authz_sidecar 581 vs 309); commits built from HEAD-intact blobs on side ref refs/heads/governance-f1-inc1, main untouched - the AUTHOR MUST rebuild the working tree from HEAD, verify the blobs, fast-forward main, and push natively (no sandbox push creds). Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-17 (VL-112: F-01 BUILT - optional SIGNED-record (freshness) mode wired into the ext-authz sidecar. config_from_env gains ELYON_PUBLISHER_KEY_ID / ELYON_PUBLISHER_KEY_HEX / ELYON_SIGNED_RECORD_PATH; when a publisher key is pinned the sidecar validates a LOCAL signed record per request (publisher signature + freshness + serial via published_record_source.load_signed_record_from_bytes) and uses the validated record as the gate's record_source, so a stale/invalid record fails closed (REF_VERIFY_PUBLISHED_RECORD_STALE / _INVALID) - the freshness the byte-anchor path lacks. Mirrors reference_target's VL-091 signed mode but reads a LOCAL file instead of HTTP-fetching. Build-then-wire: absent a publisher key the byte-anchor record_bytes+pinned_root path is byte-behaviour-unchanged. TESTS/adversarial/test_authz_sidecar_freshness.py adds 8 tests (fresh ALLOW; stale DENY; tampered + wrong-publisher-key INVALID; byte-anchor default unchanged; 3 config_from_env resolve/fail-closed paths); TESTS suite 411 -> 419 green, validated against a pristine `git archive HEAD` extraction (the Cowork mount is still truncating working-tree reads, VL-108 hazard - the AUTHOR MUST verify the committed blobs natively before pushing). K-01 (key_record_view on the default enforce path) is now the last scheduled sidecar/posture build item. WHITE-BOX in-house build, NOT a G5 referent; G5 unchanged. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-17 (VL-111: B-01 build-order step 4 BUILT - IMPLEMENTATION/authz_sidecar.py gains `build_request_body_extractor`, the CUSTOM (declarative-mapping) extractor that derives the live interaction from the ext_authz REQUEST BODY (context.args_sha256 = sha256(canonical_json(args)) over the forwarded body, reproducing interaction_for's shape byte-identically) instead of the client-controllable X-Elyon-Sol-Interaction header. This closes the IN-HOUSE half of B-01: an envelope minted for args X presented with a different executed body is REFUSED at binding (REF_VERIFY_BINDING_MISMATCH). Build-then-wire: the DEFAULT decision path stays header-read and OFF (no default path changed); the only decision-path edit is an inspect.isawaitable await for the async body extractor, byte-behavior-identical for the sync default. TESTS/adversarial/test_authz_sidecar_body_binding.py adds 10 tests (allow-on-matching-body incl. reordered-keys; deny-on-tampered-body; the inline-rebind DEFEATED + a contrast test showing the default header extractor would ALLOW the rebind; tool-from-path/header + args-from-body-field; 3 fail-closed paths); TESTS suite 401 -> 411 green, validated against a pristine `git archive HEAD` extraction because the Cowork mount served TRUNCATED working-tree reads (VL-108 stat-cache/ghost hazard recurred - the AUTHOR MUST verify the committed blobs natively before pushing). HONEST CEILING: safe INLINE operation still requires wiring this extractor AND Envoy `with_request_body` so the sidecar digests the same bytes the upstream executes; until that, the default header-read mode must not go inline. F-01 (sidecar signed-record freshness) and K-01 (key_record_view on the default enforce path) remain scheduled. WHITE-BOX in-house build, NOT a G5 referent; G5 unchanged. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-16 (VL-110: a cross-model white-box round (3 procedurally-clean runs - 'cursor', Grok, OpenAI; no fabrication) UNANIMOUSLY re-confirmed R-01 + P-01 SOUND and the crypto enforce path holds (no new protocol break). The BREAK-FOUND verdicts all pointed at already-named DEPLOYMENT-POSTURE gaps, none exploitable on the current single-worker/standalone surface: B-01 (sidecar binds the interaction header, not the executed body - CONVERGENT across 2 models, one rating it High), R-02 (per-process replay cache), F-01 (sidecar lacks signed-record freshness), K-01 (issuer-key revocation not on the default static-pin path - spot-checked accurate vs HEAD). APPLIED here: an R-02 fail-closed multi-instance guard in replay_cache_from_env (ELYON_REPLAY_MULTI_INSTANCE without a shared store now refuses at startup; single-instance unchanged) + a revert-catcher test; a B-01 security-scope docstring on the sidecar extractor + a deploy-posture note. SCHEDULED named-open build items: B-01 step-4 (derive the sidecar interaction from the ext_authz request body), F-01 (wire sidecar signed-record freshness), K-01 (pass key_record_view on the default enforce path). WHITE-BOX / in-house, NOT a G5 referent. Does not cite its own hash (VL-012).)

PREVIOUS: 2026-06-16 (VL-109: a Cursor white-box adversarial code review (Mode A) of IMPLEMENTATION/ found TWO real bugs, now FIXED + deployed. R-01: InMemoryReplayCache.check_and_claim was a lock-free check-then-set and the ext-authz sidecar runs gate.check in a threadpool, so two concurrent POST /authz could both claim one decision_id (a single-use bypass on the live sidecar); fixed with a threading.Lock (replay_cache.py), single-threaded behavior byte-identical. P-01: a duplicate X-Elyon-Sol-Envelope / X-Elyon-Sol-Interaction header was first-wins; now treated as absent -> fail closed (authz_sidecar.py + reference_target.py). Tests TESTS/adversarial/test_findings_002.py; full suite 391 -> 394 green (native run); committed 3343e32, redeployed to all four nodes, live sidecar ALLOW/DENY re-passed. NAMED-OPEN (not blocking the single-process surface): B-01 (the sidecar binds the interaction HEADER not the upstream's executed body - build-order step 4, unbuilt - do not front a body-carrying upstream until built), F-01 (the sidecar lacks signed-record freshness; the target has it), R-02 (per-process replay cache; a fail-closed guard is wanted for workers>1 without Redis). WHITE-BOX, in-house hardening only: the reviewer had the full repo, so this is internal evidence FORBIDDEN to show a blind reviewer (VL-057), NOT a G5 referent. G5 remains NOT-MET. Does not cite its own hash (VL-012).)






---

## How to use this repository as continuity

This repository is the continuity layer. It does not depend on any model's
memory. To orient in a fresh session, read in this order:

1. **`git log --oneline`** - what has happened, in order.
2. **`EVIDENCE/verification_ledger.md`** - how each claim about the project
   became trusted. This is the highest-order evidence: the record of what has
   been independently verified, by whom, against what sources.
3. **`docs/restructure/`** - the Rev. 2 restructure package: the reasoning
   behind the current structure, the gap analysis, the envelope spec, and the
   spec-to-code traceability map. Artifact 01 (`01_repository_structure.md`)
   is the reconciled diff against the real repository tree; artifact 04
   (`04_current_vs_claimed.md`) is the living gap document.
4. **This file's "Next open action" section** - the ordered starting point.

Pass *artifacts*, never *verdicts*. A rating or an approval is not evidence;
a derivation from primary sources (canon, code) is.

---

## What Elyon-Sol is

Elyon-Sol is a deterministic, fail-closed HTTP admission gate, derived from a
formal specification (the v0.9.8.4 canonical whitepaper). Given a request and
a SHA256-pinned manifest, it returns ELIGIBLE only if the caller's authority
set and operation set each satisfy the manifest's required sets and the
manifest hash and version match; otherwise REFUSE. On ELIGIBLE the request is
forwarded to the target; on REFUSE or any exception the target is not called.

The canon defines three invariants: Authority (AC^3), Coverage (T^26), and
Continuity (CCS). The implementation faithfully realizes AC^3 and T^26 and the
manifest layer. CCS has drifted - see G0 below.

---

## Current verified state

- **Recruiting & publication assets authored (VL-125).** The G5 recruiting pack + a public one-page site are drafted and committed (build `816beb8`): `site/index.html` (features, technologies, the four-node live surface, canon v0.9.8.4, the current Zenodo record `10.5281/zenodo.20751592`, and the red-team challenge, with the honest-scope note); `deploy/PRIVATE_INVITE_PROGRAM.md` (platform-neutral, invite-only, replacing the retired YesWeHack pack); `deploy/SOLICITOR_INTAKE_CHEATSHEET.md` (the operator intake flow + where-to-post venues). The reward model across `deploy/BREAK_IT.md` + `deploy/RED_TEAM_OUTREACH.md` changed from a CASH bounty to a NON-MONETARY recognition/ownership model (named ledger credit, Zenodo co-credit + ORCID, CVE, invited fix-authorship, a founding red-team seat, a team co-maintainer/ownership path), and the engagement is now PRIVATE invite-only via `security@elyon-sol.io` (no platform; YesWeHack retired). NO code/canon/manifest/test change; suite unaffected. Author-authored recruiting material, NOT external validation; the program's HARD GATES are UNMET and nothing is published. Advances G5 pre-exposure item 6 (asset half); G5 NOT-MET.
- **Governance-core white-box review + hardening cluster (VL-123).** A Cursor Mode-A white-box review of the governance core found NO exploitable bug on a correctly-wired gate; six deployment-posture findings. FIXED G-01/03/04/06 via NEW `IMPLEMENTATION/governance_wiring.py` `assert_high_impact_wiring()` - a fail-closed startup check that fires ONLY when the manifest declares HIGH_IMPACT (refuses a bare static approver pin / empty approver map / missing approval log / incoherent pending-vs-replay Redis). NO-OP on the default HIGH_IMPACT:[] manifest, so the non-high-impact path is byte-unchanged; pep's only change is one startup hook. G-02 (undeclared multi-worker) narrowed-not-closed; G-05 (redundant request-id check) defense-in-depth. 13 tests (revert-catcher per finding), suite 499 -> 512. White-box internal evidence, NOT a G5 referent; findings were all posture, none exploitable on the live surface, which is UNAFFECTED.
- **LIVE publisher-key ROTATION done + byte-anchor->signed correction (VL-122).** The VL-108-exposed publisher signing key was rotated on the live surface (new id `pub-2026-06-18`; old key trusted by no node) under a never-typed/no-history protocol. The live target was found to be running BYTE-ANCHOR (not 'signed mode' as VL-108 claimed) and was moved to genuine SIGNED mode + re-pinned to the new key, VERIFIED live by a direct `fetch_signed_record` PASS and a full attack-suite green run (exit 0, version-matched at the deployed commit 3343e32). Sidecar ALLOW/DENY confirmed live (VL-108 item 2 closed). Live nodes run 3343e32 (VL-109), NOT latest main. No repo code change; suite unaffected. VL-108 pre-exposure items 1 & 2 CLOSED; items 3-7 open; G5 NOT-MET.
- **Governance DEPLOYMENT artifacts authored - operator-locus (VL-121).** The package that wires R1 + R2 + Feature-2 into a real deployment: `deploy/governance/approver_trust_bootstrap.py` (the R1 shim - resolves role-distinct approver keys from the signed record and injects them; smoke-validated), `deploy/docker-compose.governance.yml` (redis + two gate replicas on the shared store + a custody approver-cli), `deploy/governance.env.example` (the env contract), and `deploy/GOVERNANCE_DEPLOYMENT.md` (the R1/R2/F2-layers runbook + acceptance checklist + the honest claimability gate). NO IMPLEMENTATION/TESTS/canon change; suite 499 unchanged. HONEST SCOPE: authored + locally smoke-validated, NOT a live deployment and NOT external validation; the real stand-up is operator-locus and unvalidated here; G5 NOT-MET.
- **R2 BUILT - shared store for grant single-use + the 202 pending-set, the [FIX H3]/[FIX H4] under-scale residual (VL-120).** NEW `IMPLEMENTATION/pending_store.py` is a SIBLING of `replay_cache.py`: `PendingApprovals`/`PendingStore` protocols, `InMemoryPendingApprovals` (behavior-identical to pep's pre-R2 `_PendingApprovals`), `ExternalStorePendingApprovals`, `RedisPendingStore` (SET + a Lua compare-and-delete), and `pending_store_from_env()` reusing the R-02 declare-or-fail guard. pep now builds `_PENDING = pending_store_from_env()` and `_GRANT_REPLAY = replay_cache_from_env()` (the [FIX H3] shared single-use wiring); default (no env) is byte-behavior-identical, and a declared multi-instance gate without a shared store fails closed at startup. 18 tests (gap-vs-seam cross-instance, compare-and-delete, fake-redis Lua, R-02 guard), suite 481 -> 499 green on a pristine extraction; 2 revert-catchers proven RED-on-revert. G(I) core / canon / manifest / published_hashes + R1 modules byte-identical; pep is the only default-path edit (byte-behavior-unchanged default). HONEST SCOPE: shared-capable + fail-closed-under-scale; the cross-instance guarantee holds only with a shared store actually deployed. With R2 the in-repo governance build is COMPLETE; the remainder is operator-locus. White-box, NOT a G5 referent.
- **R1 BUILT - approver provenance + role, the [FIX H5] load-bearing half (VL-119).** NEW `IMPLEMENTATION/approver_trust.py` `resolve_approver_keys()` turns a VALIDATED signed key-record trust view into the `{key_id: public_key}` approver map `verify_grant` consumes, enforcing SoD as ROLE-DISTINCTNESS in the SIGNED record: only a key whose signed role is exactly `approver` (non-revoked, in-window, `key_id != gate_key_id`) is eligible. An issuer/role-less key is structurally excluded, so a gate-minted self-approval is never honored - the guarantee a bare `key_id` compare cannot give. `key_record_source.py` is ADDITIVE-only (surfaces the signed entry's optional `role`; the publisher signature already covers it). Drop-in for the existing `_INJECTED_APPROVER_KEYS` seam, so `approval.py`/`pep.py` are byte-IDENTICAL to HEAD (no default-path touch). 15 tests on the REAL chain + REAL `verify_grant`, suite 466 -> 481 green on a pristine git-archive extraction; the issuer-cannot-authorize revert-catcher proven RED-on-revert. HONEST SCOPE: this is the provenance+role half; the custody half (gate cannot read the approver PRIVATE key) is operator-locus. White-box in-house, NOT a G5 referent; R2 is the remaining in-repo governance residual.
- **F-01 BUILT - sidecar signed-record freshness (VL-112).** The ext-authz sidecar gains an optional SIGNED-record mode (env: ELYON_PUBLISHER_KEY_ID/HEX/SIGNED_RECORD_PATH): with a pinned publisher key it validates a LOCAL signed record (publisher signature + freshness + serial, via `published_record_source.load_signed_record_from_bytes`) and uses it as the gate's record_source; a stale/invalid record fails closed (REF_VERIFY_PUBLISHED_RECORD_STALE/_INVALID). Mirrors the reference target's VL-091 signed mode, reading a local file rather than fetching. Build-then-wire: no publisher key -> the byte-anchor path is unchanged. TESTS/adversarial/test_authz_sidecar_freshness.py (+8) green; TESTS suite 411 -> 419 (validated against a pristine git-archive of HEAD; Cowork mount truncation persists, author verifies blobs natively). K-01 is the last remaining scheduled build item. White-box in-house build, NOT a G5 referent; G5 unchanged.
- **B-01 build-order step 4 BUILT (VL-111).** `build_request_body_extractor` (IMPLEMENTATION/authz_sidecar.py) derives the sidecar interaction from the ext_authz REQUEST BODY (context.args_sha256 over the forwarded body) instead of the client-controllable header, closing the in-house half of B-01: a valid envelope presented with a different executed body is refused at binding (REF_VERIFY_BINDING_MISMATCH). Build-then-wire - the default decision path stays header-read and off; the body extractor is injectable, and safe INLINE use additionally requires wiring it together with Envoy `with_request_body`. TESTS/adversarial/test_authz_sidecar_body_binding.py (+10) green; TESTS suite 401 -> 411 (validated against a pristine git-archive of HEAD - the Cowork mount truncated working-tree reads, VL-108 hazard; author verifies committed blobs natively). Remaining scheduled: F-01 (sidecar signed freshness), K-01 (key-record on the default enforce path). White-box in-house build, NOT a G5 referent; G5 unchanged.
- **Cross-model round + two hardening fixes (VL-110).** Three independent models (incl. Grok, OpenAI) unanimously re-confirmed R-01/P-01 sound and the crypto core; their findings were the already-named posture gaps (B-01 convergent/High, R-02, F-01, K-01), none exploitable on the current deployment. Applied: a fail-closed `ELYON_REPLAY_MULTI_INSTANCE` guard in `replay_cache_from_env` (R-02) + test, and a B-01 security-scope docstring + deploy note. Scheduled build items: B-01 step-4 (sidecar body-binding), F-01 (sidecar signed freshness), K-01 (key-record on the default enforce path). In-house white-box, not a G5 referent.
- **Cursor white-box review fixes landed (VL-109).** A Mode-A white-box review (Cursor over the full repo) found, and the project fixed, two real bugs: R-01 (a concurrent single-use bypass on the in-memory replay cache under the sidecar's threadpool -> a `threading.Lock`) and P-01 (an ambiguous duplicate attestation/interaction header -> now treated as absent, fail closed). Suite 391 -> 394 green; committed 3343e32 and redeployed to all four live nodes (sidecar ALLOW/DENY re-verified). Named-open, non-blocking: B-01 (sidecar header-vs-body binding = build-order step 4), F-01 (sidecar signed freshness), R-02 (multi-worker replay guard). In-house hardening, internal evidence only - NOT a G5 referent (the reviewer had the whole repo); G5 unchanged.
- **G5 Phase 1 EXECUTED - public surface LIVE, author self-test GREEN (VL-108).** Four nodes are live on Hetzner under real-CA (Let's Encrypt) TLS across two continents: `gate.elyon-sol.io:8443` (Helsinki), `target.elyon-sol.io:9443` (Hillsboro), `pub.elyon-sol.io:9143` (Helsinki), `authz.elyon-sol.io:9243` (Ashburn); target+publisher in SIGNED freshness mode. `attack_suite_live_runner` is GREEN over the public surface (positive control honored + 6/6 adversarial refused, exit 0; proof `EVIDENCE/proofs/attack_suite_live_run_2026-06-16.log`), and `readiness.json` REAL_TRANSPORT is upgraded from the VirtualBox/dev-CA tier to this real public surface. HONEST CEILING: author's own scripted attack, 6 gate-2 cases + positive control only; claims 8-13 (incl. sidecar live-ALLOW) are in-house-tested, not yet live-exercised; publisher key exposed in chat (regenerate before non-POC); counsel + bounty/window + pack publication pending. G5 (a real EXTERNAL attacker) remains NOT-MET.
- **G5 Phase-1 forks locked; recruiting pack consistent + publish-ready pending counsel (VL-107).** An execution session (deploy + people, not code) locked the section-6 forks - hosts Hetzner + DigitalOcean (two networks); recruiting via a private bug-bounty listing; reward a small bounty pool (amounts TBD); counsel safe-harbor sign-off a HARD GATE before publishing BREAK_IT.md - and repaired attacker-pack consistency: deploy/RED_TEAM_OUTREACH.md (stale [EXAMPLE.COM] + ports 8000/9000/9100 -> canonical four hosts) and deploy/LIVE_BRINGUP_RUNBOOK.md (ports -> 8443/9443/9143 + a sidecar-gap note), both previously untracked, now committed; deploy/BREAK_IT.md determinable placeholders filled (bounty $ / window / channel / counsel clause left as marked TODO). Decontamination re-verified clean (Gate 4); the live-runner env-var contract matches the runbook. No code/canon/test change; nothing went live - the bring-up, self-test over the public surface, REAL_TRANSPORT flip, publish, and recruiting remain AUTHOR-locus. G5 unchanged - NOT-MET, the only open ROAD item.
- **OPA sidecar claim set cross-model verified (VL-106) - conformance.** The VL-104/105 sidecar claims are CONFIRMED at conformance scope (faithful-to-design) by two procedurally-clean independent runs (Grok, OpenAI): 18/19 Supported, CA-9 a named gap, 0 Contradicted; a third run (Gemini) was discarded for fabricated citations (VL-008 rule b; second such in the project after VL-102). Verbatim responses + request committed under EVIDENCE/verification_runs/ and docs/methodology/. This is internal conformance evidence, NOT external validation - it confirms the sidecar is built as designed, not that the gate defeats attacks on a live surface; G5 unchanged.
- **Sidecar TLS test path (VL-105).** The VL-104 sidecar runs under real TLS: `deploy/tls/gen_certs.py` emits an `elyon-authz` leaf; `TESTS/deploy/test_authz_sidecar_tls.py` (4) verifies the leaf via a strict in-memory handshake (CI-safe); `EVIDENCE/proofs/authz_sidecar_tls_001_runner.py` serves the sidecar over a real loopback TLS socket and gets ALLOW/DENY over a CA-verifying HTTPS client (exits 0, CI-excluded); `deploy/docker-compose.authz.tls.yml` + `deploy/elyon-authz/VM_TLS_TEST.md` carry the TLS overlay + the two-VM manual runbook. Suite 387 -> 391; real cross-host TLS, not an external attacker (G5 unchanged).
- **OPA ext-authz sidecar shipped (VL-104).** `IMPLEMENTATION/authz_sidecar.py` wraps the shipped `ExecutorGate` as a thin HTTP ext_authz service answering ALLOW/DENY over the X-Elyon-Sol-Envelope + X-Elyon-Sol-Interaction header contract (the reference_target consume-path refactored into an authorizer). 15 in-container tests green (allow + each REF_* deny class + fail-closed config + cross-instance replay); `deploy/` carries the Mode A two-filter Envoy example. REUSE-only (no new admissibility/crypto/refusal-code/invariant); build-then-wire (no default path changed, suite 372 -> 387); container/`envoy --mode validate` is the author's locus. A deliberately-inserted in-house DERIVATIVE track, not a G5 road item.
- **Canon locked.** v0.9.8.4 is locked: `CANON/canon_v0.9.8.4.pdf` (immutable
  source of record), `CANON/canon.md` (ASCII-safe transcription, verified
  against the PDF - see ledger VL-006), `CANON/canon.lock` (sha256 of canon.md).
- **Verification ledger established.** `EVIDENCE/verification_ledger.md`,
  entries VL-001 through VL-019.
- **G0 confirmed (anchor finding).** Canonical CCS (whitepaper sections 12-13)
  is a temporal invariant over state transitions; the implemented `ccs_valid()`
  is a point-in-time manifest-integrity check. They are not the same invariant.
  Confirmed by three independent derivations from primary sources: Claude,
  Grok (clean pass), and OpenAI (ledger VL-002, VL-008).
- **Method on record.** `scripts/establish_ledger.sh`, `scripts/lock_canon.sh`,
  `scripts/append_vl008.sh`, `scripts/append_vl009.sh`, and
  `scripts/append_vl010.sh` - the scripts that built the ledger, the lock, and
  the VL-008/VL-009/VL-010 entries - are committed.
- **Cross-model verification procedure established (VL-008).** A valid
  verification requires the task scoped to primary sources and confirmation the
  response stayed within that scope. A model's prior exposure to the project
  does not disqualify it, provided those hold. Two failed and one successful
  OpenAI attempt are documented in VL-008.
- **Cross-model verification method applied deliberately and repeatedly
  (VL-014 -> VL-015 -> VL-016).** VL-014 drafted SPEC/request_schema.md as
  SINGLE-SOURCE. VL-015 ran cross-model verification of the schema with
  Grok and OpenAI (both procedurally clean), surfaced two new gaps (G12,
  G13), and transitioned VL-014 to DISPUTED. VL-016 ran a second cross-
  model verification on the *premises* beneath proposed corrections
  (Grok and OpenAI both procedurally clean; all three premises classified
  unanimously) and applied the resulting corrections, transitioning
  VL-014 to CORRECTED. Four verifier-runs in back-to-back rounds, all
  procedurally clean; methodology artifact recorded as candidate for
  durability commit.
- **Rev. 2 restructure package committed.** The seven planning artifacts
  (`00_README.md` through `06_spec_to_code_traceability.md`) are in
  `docs/restructure/`. The ASCII-safe standard (VL-006) has been applied
  repo-wide (VL-009). Artifact 01 has been revised to reconcile against the
  real repository tree; artifact 04 has been updated through G13 (VL-016
  session: G12 and G13 added with PARTIALLY ADDRESSED status).
  Artifacts 05 and 06 brought current to VL-012 in the VL-013 freshness
  pass; artifact 05 freshness pass to absorb `context` and `target_url`
  is proposed VL-020.
- **MANIFEST/manifest.json committed (VL-010).** Previously hidden by a
  `.gitignore` rule inherited from a Python-project template. Both the
  manifest and the `.gitignore` correction landed at commit c0867a6;
  corrective ledger entry VL-010. VL-003's derivation is now reproducible
  from a fresh clone.
- **EVIDENCE/ reorganized (VL-011).** Six proof-style files split into
  `EVIDENCE/proofs/` (three current proofs plus the raw pytest log
  backing the AC^3 mutation experiment) and `EVIDENCE/archive/` (two
  interception proofs of the dead flat-key API, plus the truncated
  stability proof). Each archived file carries a prepended NON-CURRENT
  header citing the gaps that retired it (G2/G5/G9). `EVIDENCE/tmp/`
  removed. `EVIDENCE/verification_ledger.md` is unchanged at
  `EVIDENCE/` root. The honest-base track is now complete.
- **G0/G6/G10 disambiguation pass complete (VL-012, commit 8ba88cf).**
  Function `ccs_valid()` renamed to `manifest_integrity_valid()`; the
  redundant caller-asserted `ctx["ccs_valid"]` input removed; the load-
  bearing pinning fields (`expected_manifest_version`,
  `expected_manifest_sha256`) retained and their caller-assertion
  semantics documented in the function docstring. The name "CCS" is
  reserved in code and in test IDs until envelope.py implements
  section 12. Test surface: four `ccs_flag_*` cases deleted; one new
  `manifest_sha256_missing` added to preserve coverage; four
  `ccs_version_*` renamed to `manifest_version_*`. Suite size: 37 -> 34.
  EVIDENCE/proofs/manifest_integrity_continuity_001.md renamed to
  manifest_integrity_001.md and body rewritten. New gap G11 surfaced
  (manifest-source asymmetry: `manifest_sha256()` reads from disk,
  ignoring the manifest argument). The hash citation in the VL-012
  ledger entry was corrected from the pre-amend hash to the actual
  commit hash in follow-up commit f0df14c; process finding on
  self-referencing-hash workflow recorded there.
- **Planning artifacts 05 and 06 brought current to VL-012 (VL-013,
  commit 606ddc1).** Forward-tense references to `ccs_valid()` in
  `docs/restructure/05_admissibility_envelope_spec.md` updated to
  past tense citing VL-012. In
  `docs/restructure/06_spec_to_code_traceability.md`, canonical CCS
  reclassified from DRIFTED (one row, the function in the wrong slot)
  to UNIMPLEMENTED (no code implements it; the rename half of G0
  closed in VL-012; the build half is the G0 build track). DRIFTED
  count: 1 -> 0. UNIMPLEMENTED count: 6 -> 7. The artifacts'
  substantive content was preserved; only statements about current
  state that became false after VL-012 were touched. No code, canon,
  manifest, or test change.
- **SPEC/request_schema.md committed (d7eddd5; VL-014 follow-up).**
  First artifact of the G0 build track. Canon-derived from sections
  11, 12, 13. Locks the on-the-wire request shape; maps the
  canonical interaction tuple I = (A, S, C, t) and the caller-supplied
  sets AP, OP to wire fields; names AR(I) and R(I) as manifest-derived
  (not caller-supplied); documents the load-bearing caller-asserted
  manifest-pinning fields per VL-012's convention; reserves "CCS" and
  defines a refusal rule for caller attempts to assert it
  (REF_SCHEMA_RESERVED_CCS); names the flat-key payload from
  EVIDENCE/archive/interception_* as REFUSED (REF_SCHEMA_FLAT_KEYS,
  the schema-layer half of G2). Status SINGLE-SOURCE at the time
  of VL-014.
- **VL-014 cross-model-verified (VL-015, commit 846b97a).** Grok and
  OpenAI both ran procedurally-clean derivations under VL-008. Core
  field set (AP, OP, manifest-pinning) agreed by all three
  derivations. Three-way divergence at three loci surfaced two new
  gap candidates: G12 (canon under-specifies wire-origins of `I`'s
  components) and G13 (manifest-pinning field provenance is mixed
  canon + envelope, not pure canon). VL-014 transitioned
  SINGLE-SOURCE -> DISPUTED. Three corrective decisions parked for
  VL-016 (1A, 2B, 3B), recorded in VL-015's entry.
- **VL-014 corrections applied (VL-016).** The three decisions
  parked in VL-015 (1A: `context` stays caller-supplied required
  with G12 rationale; 2B: `t` stays NOT caller-supplied with G12
  fail-closed rationale; 3B: manifest-pinning fields gain explicit
  layered-provenance note with G13 rationale) were applied to
  `SPEC/request_schema.md`. Prior to application, the *premises*
  beneath the decisions were cross-model-verified (Grok and
  OpenAI, both procedurally clean, unanimous classifications:
  premise 1 Under-specified, premise 2 Supported, premise 3
  Supported). OpenAI's argument-from-contrast framing of G12
  (canon's silence is meaningful because canon elsewhere
  demonstrates capacity to specify wire-origins for AR/R) was
  carried forward into G12's artifact-04 entry. G12 and G13
  added to artifact 04 with PARTIALLY ADDRESSED status (schema-
  layer half closed; canon-layer half open pending canon-version
  event under GR-1). VL-014 transitioned DISPUTED -> CORRECTED.
  The premise verification and the corrections are recorded in
  the single VL-016 entry; combined-entry rationale documented
  there.
- **Methodology artifacts promoted (VL-017a).** Two templates
  extracted from proven session patterns now committed to
  `docs/methodology/`: the verification-request template
  (extracted from `verification_request_vl014.md` and
  `verification_request_vl016_premises.md`; captures the
  VL-008-procedure-bound common structure across both) and the
  apply-script template (extracted from
  `apply_vl016_followup.py`; captures the uniqueness-check +
  atomic-write + per-edit-delta pattern, including the
  CRLF-on-read normalization fix and the always-write-LF
  convention learned from VL-017a's first-run abort). Both
  artifacts close methodology-debt candidate actions from
 VL-015 and the VL-016 follow-up. Classification: efficiency
  move, not trajectory move; recorded in VL-017a's entry with
  explicit framing of the distinction.
- **Failing schema-shape tests committed (VL-017).**
  `TESTS/adversarial/test_request_schema.py` adds 27 tests
  derived from `SPEC/request_schema.md` (post-VL-016,
  CORRECTED) - one per refusal class named in "Rejected
  shapes" plus a positive accepting-shape case. Against
  `IMPLEMENTATION/pep.py` at HEAD, all 27 fail. Uniform-422
  finding: every test fails at the same Pydantic wire-shape
  gate because the schema's `interaction` envelope is
  incompatible with the current `context` top-level field.
  The tests collectively prove wire-shape incompatibility
  but do not, today, discriminate between refusal classes;
  discrimination requires VL-019's wire-shape change.
  Evidence committed as
  `EVIDENCE/proofs/g2_schema_failing_tests_001.log` (raw
  pytest) and `EVIDENCE/proofs/g2_schema_failing_tests_001.md`
  (prose proof). Regression footprint clean:
  `TESTS/test_adversarial_evaluator.py` still 23/23 passing.
  The first artifact of the G2 build track's code half;
  the honest G2 signal that the schema's build-order step
  2 specifies. Classification: trajectory move per VL-017a's
  distinction.
- **Build-resumption invocation tested against two models
  (VL-017b).** A dry-run test of the invocation artifact for
  VL-018 (`IMPLEMENTATION/request_validator.py` per
  `SPEC/request_schema.md` build-order step 3) was run against
  Grok and OpenAI with identical six-file primary-source
  bundles. Both models produced procedurally-clean output per
  VL-008-adapted-for-build (scope confirmation, spec-citation
  maps, no out-of-scope artifacts). Both validators converged
  on six refusal codes (`REF_SCHEMA_TOP_LEVEL`,
  `REF_SCHEMA_BAD_URL`, `REF_SCHEMA_FLAT_KEYS`,
  `REF_SCHEMA_MANIFEST_PINNING_MISSING`,
  `REF_SCHEMA_TYPE_MISMATCH`, `REF_SCHEMA_RESERVED_CCS`) with
  identical trigger semantics. They diverged on a seventh code
  (parse-error: Grok handles externally, OpenAI names but does
  not trigger). Three candidate spec-gap findings recorded:
  seventh-code disambiguation, generic-unknown-key handling,
  parse-order API-vs-procedure separation. Build-resumption-
  request template extracted from the test prompt and promoted
  to `docs/methodology/build_resumption_request_template.md`,
  paralleling VL-017a's verification-request-template
  promotion. Classification: test result with incidental
  trajectory findings (new category; distinct from VL-017a's
  pure-efficiency and VL-017's pure-trajectory). The three
  candidate findings carry explicit citation discipline: they
  may be confirmed, superseded, or revised by VL-018's
  live-build commit, but must not be cited as established spec
  gaps without that confirmation.
- **Schema validator committed (VL-018).**
  `IMPLEMENTATION/request_validator.py` lands per
  `SPEC/request_schema.md` build-order step 3. The validator
  accepts an already-parsed Python dict and returns either a
  normalized interaction dict (AP/OP sorted and deduplicated)
  or one of six refusal codes (`REF_SCHEMA_TOP_LEVEL`,
  `REF_SCHEMA_BAD_URL`, `REF_SCHEMA_FLAT_KEYS`,
  `REF_SCHEMA_MANIFEST_PINNING_MISSING`,
  `REF_SCHEMA_RESERVED_CCS`, `REF_SCHEMA_TYPE_MISMATCH`). The
  seventh code (`REF_SCHEMA_PARSE_ERROR`) is named at module
  level but emitted by `pep.py` at the PEP boundary in
  VL-019. All three VL-017b candidates were resolved with
  explicit rationale per the citation discipline: Candidate 3
  (parse-order API contract) superseded by spec+test direct
  read (parsed-dict contract); Candidate 1 (seventh code
  status) superseded by Candidate-3 coupling (named-but-not-
  emitted approach taken); Candidate 2 (generic unknown keys
  inside `interaction`) upgraded to real spec gap (G14) with
  provisional `REF_SCHEMA_TYPE_MISMATCH` mapping pending spec
  edit. Validator verified in-container against 26/27
  discriminating tests plus the positive case; the 27th
  (parse-error) is structurally VL-019's domain. Validator
  does NOT touch `pep.py`; G2 closes on VL-019.
- **PEP wired to validator; G2 closed in code (VL-019).**
  `IMPLEMENTATION/pep.py` replaced wholesale per
  `SPEC/request_schema.md` build-order step 4. The endpoint
  reads the raw JSON body (no Pydantic body model), parses
  with `json.loads` (emitting `REF_SCHEMA_PARSE_ERROR` on
  decode failure), calls `validate_request()` on the parsed
  dict, and passes the normalized interaction to
  `evaluate()` only after schema acceptance. The seven-code
  schema vocabulary is fully realized: six codes emitted by
  the validator (VL-018), the seventh
  (`REF_SCHEMA_PARSE_ERROR`) emitted by the PEP boundary.
  Architectural deviation from the VL-019 session intent
  documented in the ledger entry: the planned
  Pydantic-model-with-RequestValidationError-handler
  architecture failed 4/27 tests because Pydantic silently
  drops extra top-level keys, making the validator's flat-
  key and top-level-CCS-shaped-key refusals structurally
  unreachable. Raw-body architecture sidesteps the
  Pydantic-as-filter concern. In-container verification:
  27/27 schema tests passing; 23/23 evaluator regression
  passing; TESTS/test_pep.py migrated to new wire shape (4/4
  passing; three of four previously passing-by-accident at
  schema-layer 403 rather than at the evaluator/upstream
  behavior they were written to test); 54/54 in-container,
  61/61 in repo. Evidence at
  `EVIDENCE/proofs/g2_pep_wiring_001.log` (raw pytest
  output). The evaluator-layer refusal payload is preserved
  from pre-VL-019 pep.py (`{terminal_state: REFUSE}` without
  a `refusal_reason_code`) because VL-019's scope is
  schema-layer wiring; evaluator-layer refusal vocabulary is
  not specified by SPEC/request_schema.md and is not
  introduced here.
- **VL-020 artifact 05 freshness pass; methodology Lesson 5
  promoted; schema stale forward-reference corrected
  (commit d81de1d).** `docs/restructure/05_admissibility_envelope_spec.md`
  absorbs the canonical wire shape locked by VL-014..VL-019.
  The envelope's `request_context` block gains `context`
  (canon section 11.1 `C`) between `OP` and
  `expected_manifest_version`; the envelope top level gains
  `target_url` between `decision` and `canon`. Two
  field-rationale bullets appended in JSON-block-order.
  Two queue-drain items bundled per VL-013's freshness-pass
  scope rule: `docs/methodology/session_mechanics_lessons.md`
  gains Lesson 5 (set-exhaustiveness claims require explicit
  enumeration; three VL-019 surface events: Pydantic
  architecture skip, 23/23 regression-set scope claim,
  `grep -P` MINGW64 flag-set rejection; failure mode
  characterized distinctly from Lesson 3 source-first);
  `SPEC/request_schema.md` "Build order (schema-internal)"
  closing paragraph corrected from pre-VL-015 numbering plan
  (VL-014..VL-018) to actual numbering (VL-014..VL-020).
  Single focused str_replace in the schema per session intent;
  second stale forward-reference at the schema's line 457
  surfaced as a process finding and deferred to a separate
  small commit. No code/canon/test change. Repo test set
  61/61, unchanged from VL-019.
- **VL-020 follow-up STATE.md and ledger append; delivery-
  omission repair (this commit).** VL-020's commit d81de1d
  landed the three structural-edit files but omitted the
  STATE.md update and the ledger entry append; the Step 8
  paste contained comment-form action items for both that
  were silently skipped at execution. This follow-up commit
  applies the STATE.md edits and appends both the VL-020 and
  VL-020 follow-up ledger entries. Third instance of the
  chat-paste-eats-content failure mode named in
  `docs/methodology/session_mechanics_lessons.md` (VL-016
  follow-up lessons (a) and (b)). No code/canon/test change.
- **VL-021 schema line-457 stale forward-reference
  correction (commit cbb428b).** The second stale
  forward-reference in `SPEC/request_schema.md`, surfaced
  by VL-020's source-read pass and deferred per
  strict-scope discipline, is corrected. The "Decided
  downstream tasks / Feed-back to envelope spec
  (Deliverable 05)" section's parenthetical reference is
  rewritten from forward-tense pre-VL-020 numbering
  ("proposed VL-018, after the VL-014..VL-017 schema-work
  entries below") to past-tense citing the actual landing
  ("recorded at VL-020, after the VL-014..VL-019
  schema-work entries"). Single focused str_replace; same
  family as VL-020's closing-paragraph correction. No
  code/canon/test/structural-doc change. Repo test set
  61/61, unchanged from VL-020 follow-up.
- **VL-021 follow-up STATE.md and ledger append;
  delivery-omission repair (commit 79feab9).** VL-021's
  commit cbb428b landed the schema edit but omitted the
  STATE.md update and the ledger entry append. This
  follow-up commit applies the STATE.md edits with
  anchors verified against the actual file content and
  appends both the VL-021 and the VL-021 follow-up ledger
  entries. Items 15 and 16 of "Next open action" landed
  in 79feab9; this current-verified-state bullet pair and
  the last-updated parenthetical landed in a separate
  follow-up commit after edits 1 and 2 of the original
  apply-script were observed to apply to disk but not
  survive to staging in 79feab9 (mechanism undiagnosed;
  treated as a session-mechanics finding for a future
  ledger entry). Fifth instance of the chat-paste-eats-
  content failure mode family. No code/canon/test change.
- **VL-022 throwaway-session methodology promotion (this
  commit).** Two deliverables from the bridge document of
  2026-05-19: (1) new file
  `docs/methodology/cross_model_evaluate_template.md` - a
  fourth methodology template for framework-level
  evaluation under derivation discipline, paralleling the
  three existing methodology templates and incorporating
  the constraint-bounding caveat Lesson 6 motivates; (2)
  Lesson 6 appended to
  `docs/methodology/session_mechanics_lessons.md` - the
  presentation-indistinguishability failure mode
  (constraint enforcement in cross-model output is
  prompt-bounded, not model-bounded) and its corrective
  rule (verify scope discipline within the response body,
  not just at its opening confirmation). Both deliverables
  promoted on single-instance basis with explicit
  acknowledgment; rationale recorded in the VL-022 ledger
  entry. Finding 3 from the bridge (recursive-continuity
  hypothesis) NOT in this commit's scope; parked for
  VL-023, which requires fresh artifact reading without
  reference to the bridge document or surface-event model
  phrasing per the bridge's prescription. This entry also
  absorbs the audit trail for commit 37a4390 (the VL-021
  follow-up 2 recovery) per option B of the VL-022
  scoping decision; the disappearance mechanism that
  necessitated 37a4390 is documented in the VL-022 ledger
  entry as an open methodology investigation.
  Classification: efficiency move per VL-017a's
  distinction. No code/canon/test/spec/structural-doc
  change. Repo test set 61/61, unchanged from 37a4390.
- **VL-023 recursive-continuity hypothesis derivation:
  PARTIAL HOLDS (this commit).** Finding 3 from the bridge
  document of 2026-05-19, deferred to VL-023 by VL-022 per
  the bridge's prescription that the model's phrasing not
  be imported. Derivation conducted in a fresh session
  without the bridge document, the throwaway chat
  transcript, or the outside model's output in working
  context. A four-part abstract shape extracted from canon
  section 12 (state + enumerated transitions +
  invalidation/revalidation mechanism + fail-closed on
  unverified continuation) applied to the five candidate
  layers the session opener named: decision layer
  (definitionally; build half open per G0), manifest layer
  (with the transition-shape being part of canonical CCS,
  not a separate invariant), methodology layer (procedural
  detector via ledger discipline plus no-prose-promotion
  rule), and session layer (procedural detector via close
  + resume protocols) all fit. Request layer does NOT fit:
  no transition concept; it is a precondition layer, not a
  continuity layer. Hypothesis closes with PARTIAL HOLDS;
  downstream-artifact candidate
  (`docs/restructure/07_continuity_recursion.md` naming
  the four fitting layers) flagged in process findings,
  NOT committed in this entry, with recommendation to
  schedule post-G0-build. Classification: methodology /
  analysis entry per VL-017a's distinction. No
  code/canon/test/spec/structural-doc change. Repo test
  set 61/61, unchanged from 37a4390 (VL-022).
- **VL-023 follow-up cross-model evaluation: convergent
  on PARTIAL HOLDS; one supplementary finding (this commit).**
  First framework-level cross-model evaluation under the
  VL-022 template (drafted from inference about the template
  structure; Lesson 3 inference flag at top of the request).
  Recipient model produced a procedurally-clean response per
  VL-008 + Lesson 6 within-body discipline. Four-part abstract
  shape extracted independently from canon section 12 matches
  VL-023's extraction exactly in components and citations. All
  five original per-layer verdicts converge: decision fits
  definitionally, manifest fits with CCS-application
  refinement, request does NOT fit, methodology fits via
  procedural detector, session fits via procedural detector.
  Outcome classification: PARTIAL HOLDS, matching VL-023.
  One supplementary divergence finding: evaluator versioning
  layer added as a sixth fitting layer per artifact 05's
  `evaluator` block field rationale citing canon section
  12.4-class transition, with one minor inference caveat on
  its fail-closed component (artifact-recoverable from the
  envelope's overall fail-closed posture; flagged for
  precision). VL-023's PARTIAL HOLDS strengthened from
  single-model to two-model converged derivation; the
  `07_continuity_recursion.md` artifact candidate (if/when
  eventually drafted post-G0-build) should incorporate the
  evaluator versioning layer per this entry's recommendation.
  Classification: methodology / analysis entry per VL-017a's
  distinction. No code/canon/test/spec/structural-doc change.
  Repo test set 61/61, unchanged from 83fa5a7 (VL-023).
- **VL-024 strengthening derivation: STRENGTHENS bounded to
  layers B and C (this commit).** Methodology / analysis entry
  deriving whether the cross-model run at VL-023 follow-up
  strengthens the framework's claim of recursive continuity
  discipline. Four-step structure per session opener: Step 1
  decomposed `strengthen` against VL-023 follow-up's stated
  accomplishments (Passages A, B, C of that entry) per Lesson 5
  set-exhaustiveness, producing three load-bearing sub-meanings
  (confidence, scope, methodology-pattern durability) after
  collapsing opener-(iii) risk-reduction into (i) and deferring
  opener-(iv) external defensibility to Step 4. Step 2 derived
  each sub-meaning with citations: (i) confidence strengthens
  materially on the abstract shape and the load-bearing
  request-layer exclusion, bounded by the shared-bundle caveat
  which is the strongest test the framework's methodology
  specifies; (ii) scope expands by one fitting layer (evaluator
  versioning) with one artifact-recoverable inference caveat,
  PARTIAL HOLDS verdict unchanged with fitting set now five;
  (iii) methodology-pattern durability strengthens with two
  effects - cross-model evaluate template now meets two-instance
  threshold per session_mechanics_lessons.md line 47, and the
  methodology layer's recursive-continuity instance is now
  operative rather than merely observable. Step 3 synthesized
  via Layer A/B/C decomposition of framework purposes (Layer A
  = declared purpose per canon sections 1, 6, 14; Layer B =
  epistemic discipline per VL-008 plus the no-prose-promotion
  rule plus SESSION_PROTOCOL.md lines 84-86; Layer C =
  reading-aid track per the `07_continuity_recursion.md`
  candidate and STATE.md's entry-point role). Verdict:
  STRENGTHENS, bounded to layers B and C; explicitly does NOT
  extend to layer A. The verdict refines VL-023 follow-up's
  unqualified `strengthened` framing (entry line 5237) to an
  explicit layer-bounded form. Step 4 recorded five implications:
  (1) `07_continuity_recursion.md` composition to include
  evaluator-versioning as fifth fitting layer with detector-type
  distinction made explicit; (2) VL-025 envelope.py build
  attention to `reassert()`'s handling of `evaluator_sha256` as
  load-bearing for the evaluator-versioning layer's fit; (3)
  external defensibility strengthens in proportion to current
  readership scope (bounded), becomes load-bearing contingent on
  G3 status change; (4) cross-model evaluate template's
  single-instance language now removable per two-instance
  threshold met, efficiency move queue-drain candidate; (5)
  derivation-over-absorption verdict-refinement as first
  instance of candidate methodology pattern (VL-024 itself is
  the first instance), two-instance threshold not yet met.
  Classification: methodology / analysis entry per VL-017a's
  distinction. No code/canon/test/spec/structural-doc change.
  Repo test set 61/61, unchanged from 49b797a (VL-023 follow-up).
- **VL-025 G0 build half: canonical CCS implementation via envelope.py (this commit).** `IMPLEMENTATION/envelope.py` lands per
  `docs/restructure/05_admissibility_envelope_spec.md` build-order
  step 3. Two functions: `build_envelope()` constructs the envelope
  dict matching artifact 05's Envelope structure section, with every
  field cited to a specific artifact 05 passage or canon clause (see
  VL-025's Spec-citation map). `reassert()` implements the five-row
  Reassertion protocol table with each branch cited to its table row
  in table order (see VL-025's Reassertion-protocol mapping).
  Integration boundary one-sided per opener risk-reduction observation
  1: envelope.py imports `manifest_sha256` from evaluator.py and is
  not imported by evaluator.py or pep.py in this commit. Option A
  integration locked pre-build: condition booleans (ac3, t26,
  manifest_integrity) are caller-supplied parameters; envelope.py
  does NOT call the condition functions itself. `reassert()` is pure
  with respect to the envelope (reads live file hashes, does not
  modify input). `ensure_ascii=True` per VL-009 with divergence from
  receipt.py's `ensure_ascii=False` recorded as gap candidate 4 (second
  instance of the VL-012 receipt.py finding; methodology two-instance
  threshold now met). `condition_results.ccs` is None on first issuance
  per artifact 05 open question 1, locked by opener constraint (e);
  the reassert-time ccs boolean's owner is recorded as gap candidate 1
  for spec edit before VL-027. **VL-024 Implication 2 converted from
  inference to direct citation in code**: reassert() Row 3 (evaluator
  _sha256 mismatch -> RE-EVALUATE-REQUIRED, canon basis section 12.4)
  resolves the evaluator-versioning fail-closed inference flag from
  VL-023 follow-up lines 5200-5210; the inference caveat dissolves on
  direct read of artifact 05's reassertion table and the build
  instantiates the exact mapping. Five gap candidates total recorded
  (none blocking): (1) condition_results.ccs reassertion semantic, (2)
  evaluate aggregate return shape vs condition_results needs, (3)
  canon section 12.3 c_{t+1} vs T^26 relationship, (4) ensure_ascii
  divergence from receipt.py, (5) canon_sha256 lockfile-read vs
  canon.md hash recomputation design choice. Pre-commit smoke test
  exercised the integration boundary end-to-end (validator ->
  evaluator condition functions -> build_envelope -> reassert across
  all 5 table rows plus determinism plus timestamp-invariance plus
  purity); 7/7 checks passed; smoke test not committed (VL-026 owns
  test artifacts). Repo test set 61/61, unchanged from c944a76
  (VL-024); envelope.py has no callers in pep.py yet so no test
  regression possible. Build-resumption template's second behavioral
  instance and first with Claude as executing agent; two-instance
  threshold per session_mechanics_lessons.md line 47 met for
  build-resumption-as-protocol (paralleling VL-024's threshold met
  for cross-model evaluate template). G0 build half transitions from
  OPEN to PARTIALLY RESOLVED with the envelope-construction-and-
  reassertion portion landed; pep.py wiring remains open for VL-027.
  Canonical CCS in 06_spec_to_code_traceability.md transitions from
  UNIMPLEMENTED to PARTIALLY IMPLEMENTED for the envelope.py portion;
  structured artifact 06 update deferred to a follow-up commit
  paralleling VL-018's pattern. Layer A change per VL-024's bridge
  proposition; canon section 12 has a deterministic implementation
  in code for the first time in the project's history. Classification:
  trajectory move per VL-017a's distinction.
- **VL-025 follow-up cross-model verification of envelope.py against artifact 05 and canon section 12-13 (this commit).** Two-bundle, two-recipient cross-model verification of VL-025 under VL-008 + Lesson 6 with Grok and OpenAI as recipients. Bundle A verifies
  envelope.py's structural fidelity to
  `docs/restructure/05_admissibility_envelope_spec.md`; Bundle B
  verifies `reassert()`'s behavior against `CANON/canon.md`
  sections 12.1-12.4 and 13. Four verifier-runs total; all
  procedurally clean per VL-008 (a)+(b) and Lesson 6 within-body
  discipline. One re-request for response-mechanism truncation
  (OpenAI Bundle A first run truncated mid-section-4; re-requested
  with explicit "respond in full" instruction; re-run clean).
  **Substantive convergence across all four runs**: no Divergence
  and no Code-absent classifications anywhere; envelope.py honors
  the intent of both artifact 05 and canon section 12-13. **VL-024
  Implication 2 fully confirmed**: Row 3 (evaluator_sha256
  mismatch -> RE-EVALUATE-REQUIRED) directly authorized by canon
  section 12.4 per both Bundle B verifiers; the inference flag at
  the methodology layer on evaluator-versioning's fail-closed
  component (VL-023 follow-up lines 5200-5210) is now two-model-
  converged and can be retired in any subsequent
  `07_continuity_recursion.md` draft. **Classification divergence**:
  Grok's Match outcomes (both bundles) vs. OpenAI's Different-set
  outcomes (both bundles) reflect a Match-criterion divergence,
  not a substantive divergence: Grok treats authorization-by-
  design-space as Match; OpenAI treats only authorization-by-
  direct-naming as Match. The pattern is structural across both
  bundles; two-instance threshold per session_mechanics_lessons.md
  line 47 met for a verification-request-template Match-criterion
  clarification. **Six gap candidates surfaced**, none blocking:
  (1) artifact 05 should specify `ensure_ascii=True` per VL-009 -
  this is VL-025 gap candidate 4 confirmed by OpenAI Bundle A; (2)
  artifact 05 should specify `reassert()` purity contract - new,
  not in VL-025's gap-candidate list; (3) artifact 05 could specify
  defensive AP/OP copy semantics - new, minor; (4) module-level
  path constants `CANON_LOCK_PATH`/`EVALUATOR_PATH` recorded as
  deliberate non-spec choice per VL-012 discipline pattern; (5)
  artifact 05's Canon-mapping table Row 2 (tamper detection) needs
  rewording to acknowledge artifact-05-layer mechanism rather than
  direct canon-clause instantiation - new, load-bearing; (6)
  first-issuance ccs initialization semantic is canon-underdetermined
  - overlaps with VL-025 gap candidate 1 and resolvable via same
  spec edit. **Four methodology process findings**: (i) verification
  request template Match-criterion ambiguity is load-bearing across
  both bundles; (ii) absence-of-Divergence and absence-of-Code-absent
  are themselves derivation outcomes worth elevating in the template's
  rubric language; (iii) response truncation handling needs explicit
  length instruction in submission-format wording; (iv) scope check
  enumeration discipline (per-concept vs grouped) needs clarification.
  **Status implications**: no code-correction needed (envelope.py is
  verified correct); one spec-clarification batch needed before
  VL-027, combining VL-025 gap candidate 1 plus this entry's gap
  candidates 1, 2, 3, 5, 6 into a single artifact 05 spec-revision
  commit; VL-026 (canon-derived tests) is not blocked and may use
  Bundle B verifier-runs' per-branch canon citations as the
  authoritative source for `test_ccs_canonical.py` docstrings.
  Verifier responses recorded by reference per VL-015/VL-016/VL-023
  follow-up precedent (not committed as standalone artifacts).
  Classification: methodology / analysis entry per VL-017a's
  distinction. No code/canon/test/spec/structural-doc change in
  this commit. Repo test set 61/61, unchanged from 096c933
  (VL-025).
- **VL-026 artifact 05 spec revision: four edits resolving VL-025 +
  VL-025 follow-up gap candidates (this commit).** Pre-VL-027
  spec-revision commit per Order B of the VL-026 opener's pre-session
  ordering decision. Four edits to
  `docs/restructure/05_admissibility_envelope_spec.md` applied in a
  single atomic write (9747 -> 11309 bytes, +1562). Edit 1 adds
  `ensure_ascii=True` clause to the `decision_sha256` field
  rationale with VL-009 citation and brief receipt.py-divergence
  parenthetical (resolves VL-025 gap candidate 4 + VL-025 follow-up
  Bundle A finding 1). Edit 2 inserts the `reassert()` purity
  contract paragraph between the Reassertion protocol table and the
  "REASSERTED is the only state" paragraph (resolves VL-025
  follow-up Bundle A finding 2, new). Edit 4 rewrites Reassertion
  protocol table Row 2 Canon basis cell from descriptive
  "tampered/corrupt envelope" to citation "sections 12.3/12.4
  fail-closed semantics, operationalized via artifact-05-layer
  tamper detection," bringing Row 2 into citation-discipline parity
  with the other four rows (resolves VL-025 follow-up Bundle B
  finding 5, load-bearing). Edit 5 rewrites Open question 1 as
  resolution: Python `None` first-issuance sentinel; canon section
  12.3 inapplicable on first issuance; forward-looking
  ccs-derivation rule at reassertion (True on REASSERTED, False on
  INVALIDATED or RE-EVALUATE-REQUIRED per canon section 12.4);
  explicit envelope.py implementation-gap note (resolves VL-025 gap
  candidate 1 + VL-025 follow-up Bundle B finding 6 jointly). Edit
  3 (defensive AP/OP copies) recorded as deliberate non-spec
  choice in the ledger entry per VL-025 follow-up's module-level
  path constants precedent. Apply-script discipline corrective from
  VL-025 fully applied: read-only diagnostic
  (`diagnose_anchors_vl026.py`) ran first against pre-edit file
  (9747 bytes, pure LF; 8/8 anchor needles unique); byte-exact
  anchors copied to apply-script (`apply_vl026_specrev.py`);
  synthetic-fixture verification step performed pre-real-file-run
  with delta-match exactly (+230/+295/+71/+966 bytes); negative-path
  corrupted-fixture verification confirmed abort-no-write behavior
  (exit code 3, no disk change). The synthetic-fixture verification
  step is a new methodology pattern (first instance; two-instance
  threshold per session_mechanics_lessons.md line 47 not yet met).
  Ledger numbering shift under Order B: VL-026 = spec revision
  (this commit), VL-027 = canon-derived tests (was VL-026 in the
  opener), VL-028 = pep.py wiring (was VL-027). G0 build half
  remains PARTIALLY RESOLVED post-VL-026: the spec is now
  self-consistent on the purity contract and the ccs-derivation
  rule, but envelope.py at HEAD does not yet implement Edit 5's
  ccs-derivation rule (recorded as forward-looking commitment;
  envelope.py update deferred to VL-027a or VL-028-prelim; the
  VL-027 author should make the test-vs-code timing decision
  explicit at session start per Finding 4 of the VL-026 ledger
  entry). Canonical CCS in
  `docs/restructure/06_spec_to_code_traceability.md` remains
  PARTIALLY IMPLEMENTED. No G-row movements in
  `docs/restructure/04_current_vs_claimed.md`. Classification:
  methodology / analysis entry per VL-017a's distinction
  (structural-doc edits to artifact 05; no code, canon, manifest,
  test, or schema change). Repo test set 61/61, unchanged from
  f0c76cd (VL-025 follow-up).
- **VL-027 envelope.py import fix (this commit).** One-line fix
  to `IMPLEMENTATION/envelope.py` line 96: `from evaluator import
  manifest_sha256` -> `from IMPLEMENTATION.evaluator import
  manifest_sha256`. The fix brings envelope.py into convention
  parity with every other file in the repo (`TESTS/test_adversarial_evaluator.py`
  line 3 and `TESTS/adversarial/test_request_schema.py` use
  `from IMPLEMENTATION.evaluator import ...`; envelope.py at
  VL-025 was the only file using the prefix-less form). The bug
  was latent at VL-025 because nothing in the repo had imported
  envelope.py before the planned VL-028 (canon-derived tests)
  session: VL-025 was a build-only commit; VL-025 follow-up's
  two-bundle cross-model verification was static-reading-based
  and did not exercise the runtime import. The bug surfaced at
  the planned VL-028 session when `python -m pytest TESTS/`
  failed at collection with `ModuleNotFoundError: No module
  named 'evaluator'`. Per VL-027 opener (originally drafted as
  the VL-028 opener) constraint (l) bug-fix discipline, the
  planned-VL-028 session was halted before any commit; the
  import fix is being committed first as a separate trajectory
  action under VL-026's Order B renumbering precedent (this
  commit = VL-027 import fix; was-VL-027 canon-derived tests
  becomes VL-028; was-VL-028 pep.py wiring becomes VL-029).
  envelope.py file size delta is +15 bytes (16641 -> 16656).
  Sandbox verification: with the patched envelope.py and the
  two test files at `/home/claude/work/vl028_archived/`,
  `python -m pytest TESTS/adversarial/` runs without
  `PYTHONPATH=IMPLEMENTATION` and produces 19 passed + 3
  xfailed in 0.05s (the same result the now-archived VL-027
  draft produced under the masking PYTHONPATH; the patched
  envelope.py reproduces it under the user's real
  environment's PYTHONPATH conditions). The original VL-025
  cross-model verification's classification was Match (Grok)
  / Spec-undetermined (OpenAI) on the `from evaluator import`
  line; neither classification fires on a runtime-only
  failure that requires actually importing the module.
  **One process finding recorded**: "every module in
  `IMPLEMENTATION/` should be import-tested" - a Lesson 5
  set-exhaustiveness candidate at the test-coverage layer.
  The fact that `import IMPLEMENTATION.envelope` was never
  exercised by any test until the planned VL-028 surfaced
  the bug is itself the coverage gap that allowed the bug
  to ship at VL-025. The bug-detection mechanism (running
  pytest in the user's real environment as the first
  practical test of envelope.py's runtime importability)
  is the corrective the framework already has; the
  candidate methodology refinement is to make
  import-cleanliness an explicit test rather than a
  side-effect of other tests' module-loading. Deferred to
  a future bookkeeping commit; not in VL-027 scope.
  G0 build half remains PARTIALLY RESOLVED with envelope.py
  now import-clean and the canon-derived tests + pep.py
  wiring still open for VL-028 and VL-029 respectively.
  Canonical CCS in
  `docs/restructure/06_spec_to_code_traceability.md`
  remains PARTIALLY IMPLEMENTED. No G-row movements in
  `docs/restructure/04_current_vs_claimed.md`.
  Classification: bug-fix trajectory move per VL-017a's
  distinction (single-line code change in
  `IMPLEMENTATION/`, with structural-doc updates only in
  STATE.md and the ledger). No canon/manifest/spec/test/
  structural-doc change in this commit.
- **VL-028 canon-derived tests for envelope.py (this commit).**
  Two new test files at `TESTS/adversarial/`:
  `test_envelope.py` (13 spec-derived tests against post-VL-026
  `docs/restructure/05_admissibility_envelope_spec.md`) and
  `test_ccs_canonical.py` (6 non-xfail canon-derived tests citing
  CANON/canon.md sections 11.9, 12.1-12.4, 13 + 1 Row-2 test with
  artifact-05-layer acknowledgment per VL-028 opener Decision B + 3
  xfail tests for the post-VL-026 forward-looking ccs-derivation
  rule per Decision A). Rebase from archived VL-027-drafted work
  onto post-VL-027 state: substring-rename pass per opener rules
  (test_envelope.py: 7 occurrences of VL-027 -> VL-028 for
  current-opener references, all same-length; test_ccs_canonical.py:
  11 occurrences of VL-028 -> VL-029 for forward-references then 9
  occurrences of VL-027 -> VL-028 for current-opener references,
  order load-bearing because two-pass-reversed would over-convert
  current-opener refs to VL-029). All renames same-length (6
  chars); zero byte-delta in both files. Synthetic-fixture
  pre-verification confirmed rename math exactly (counts and
  byte-delta-zero invariant) before real-file run per VL-026
  Finding 1 / VL-027 Finding 2 / this entry's Finding 3
  methodology. Post-rename verification: 0/7/0 (VL-027/VL-028/VL-029)
  in test_envelope.py; 0/9/11 in test_ccs_canonical.py; both files
  ASCII-clean (zero non-ASCII bytes); both compile cleanly under
  Python 3. G7 (tests are code-derived, not canon-derived) partially
  closes for the envelope domain via the canon-derived test file;
  full G7 closure requires canon-derived tests for the evaluator
  domain (AC^3, T^26, manifest-integrity) which remain code-derived
  at TESTS/test_adversarial_evaluator.py and
  TESTS/adversarial/test_request_schema.py. Canonical CCS in
  `docs/restructure/06_spec_to_code_traceability.md` remains
  PARTIALLY IMPLEMENTED; full transition to IMPLEMENTED at VL-029
  with pep.py wiring + envelope.py ccs-derivation-rule update.
  xfail registry: three tests
  (`test_canon_12_3_ccs_derived_true_on_REASSERTED`,
  `test_canon_12_4_ccs_derived_false_on_INVALIDATED`,
  `test_canon_12_4_ccs_derived_false_on_RE_EVALUATE_REQUIRED`) all
  marked `@pytest.mark.xfail(strict=True, reason=XFAIL_REASON_DICT_SHAPE)`
  asserting provisional dict-shaped `reassert()` return
  `{"outcome": ..., "ccs": ...}`. When VL-029 implements the
  ccs-derivation rule, strict=True will fire xpass and the markers
  must be removed plus the result-indexing shape reconciled with
  VL-029's chosen interface in the same commit. Two gap candidates
  recorded: (1) envelope.py docstring drift, five references to
  VL-027 in envelope.py lines 36, 43, 77, 79, 319 now refer
  historically-incorrectly to the now-VL-029 pep.py wiring session,
  load-bearing for VL-029 (which is already in scope for envelope.py
  changes per Decision A); (2) apply-script template extension typo
  in VL-028 opener line 94 (`.md` vs canonical `.py`), cosmetic.
  Five process findings recorded: (1) opener-prediction-vs-file-
  content surface divergence as a Lesson 3 / Lesson 5 second-instance
  candidate at the rebase layer (opener predicted ~0 + 4 renames;
  actual was 7 + 20 string-replacements); (2) apply-script template
  extension typo (single-instance, traceability only); (3)
  synthetic-fixture verification methodology threshold met formally
  with this run as third instance after VL-026 and VL-027 (queue-
  drain candidate to promote into apply_script_template.py's
  docstring); (4) zero-byte-delta-rename invariant as candidate
  template addition for rename-shape edits where every old_str and
  new_str are same-length (queue-drain candidate); (5) VL-027's
  import-fix session was the first practical test of envelope.py's
  runtime importability, validating VL-027 Finding 1's
  "every module in IMPLEMENTATION/ should be import-tested"
  candidate at the methodology layer; VL-028's two test files are
  the de-facto import-test for envelope.py but the dedicated
  TESTS/test_module_imports.py artifact remains a queue-drain
  candidate. The recursion is honest: VL-027 was triggered by
  VL-028's drafting; VL-028's commit validates VL-027 Finding 1 by
  closing the import-coverage gap for envelope.py. Pytest
  verification deferred to user's real environment per constraint
  (m) sandbox discipline; expected at session-close per opener
  line 226: 80 passed + 3 xfailed (61 pre-existing + 19 new
  non-xfail + 3 xfail). Classification: trajectory move per
  VL-017a's distinction (two new test files in `TESTS/`, with
  structural-doc updates only in STATE.md and the ledger). No
  canon/manifest/spec/implementation change in this commit.
- **VL-029 G0 build half closes completely: pep.py wires to emit
  envelopes + envelope.py ccs-derivation rule + xfail-to-xpass
  transition + artifact 04/06 F1 bundle (this commit).**
  `IMPLEMENTATION/envelope.py` updated: `reassert()` now returns
  dict `{"outcome": <str>, "ccs": <bool>}` per VL-028 Decision A;
  6 return points each carry the derived ccs (True on REASSERTED,
  False on INVALIDATED or RE-EVALUATE-REQUIRED per post-VL-026
  Edit 5 + canon section 12.4); module + reassert() docstrings
  honestly reflect the new behavior (3 minimal VL-027 -> VL-029
  renames at lines 36/43/77 zero-byte-delta + C-honest substantive
  rewrites at lines 74-77/79/316-319 per the R1 self-discipline
  recovery from a session-internal scope-expansion). `IMPLEMENTATION/pep.py`
  wires envelope emission on ELIGIBLE: after `evaluate()` returns
  ELIGIBLE, pep.py calls `safe_manifest()` + three condition functions
  (`ac3_valid`, `t26_valid`, `manifest_integrity_valid`) per Decision C1
  to derive the booleans independently, then calls `build_envelope()`
  to construct the envelope, then returns `{"decision": "ELIGIBLE",
  "envelope": <envelope>}` per Decision E SD-3-a. The envelope-
  construction block is wrapped in try/except per W2 fail-closed
  discipline (post-N3-review fix): any exception in the condition
  functions or in build_envelope() raises REF_PEP_FAIL_CLOSED,
  matching the symmetric protection around evaluate() and the
  upstream POST. Test surface: `TESTS/adversarial/test_ccs_canonical.py`
  3 xfail markers removed (Decision A-extended strict=True discipline)
  + XFAIL_REASON_DICT_SHAPE constant removed + module-docstring B'
  light-edit (past-tense + landing-note) + honest rewrite of xfail-
  section comment block + 5 non-xfail callers updated to dict-shape
  `["outcome"]` indexing (Option alpha: opener-prediction-vs-file-content
  surface divergence second-instance per VL-028 Finding 1; two-instance
  threshold met for Lesson 5 surface-event sub-pattern); 4 callers in
  `test_envelope.py` likewise updated; `test_pep.py` gains
  `test_pep_eligible_response_contains_envelope` verifying response
  shape + 10 envelope top-level keys + ELIGIBLE-path invariants
  (ac3/t26/manifest_integrity all True per Decision C1) + ccs=None on
  first issuance + decision_sha256 format (no value pinning per
  inherited constraint (i)). F1 bundle applied:
  `docs/restructure/04_current_vs_claimed.md` G0 row PARTIALLY
  RESOLVED -> RESOLVED + G7 row gets Status: PARTIALLY ADDRESSED
  (VL-028 + VL-029) + priority-order polish (G0 anchor RESOLVED + G7
  PARTIALLY ADDRESSED); `docs/restructure/06_spec_to_code_traceability.md`
  7 row promotions to FULL (section 3 CCS, section 12.1, section 12.2
  PARTIAL -> FULL since u/c/d now stored in envelope, section 12.3,
  section 12.4, section 13 per R-trajectory reading) + Appendix D.3
  stays UNIMPLEMENTED with refined note (D.3's literal in-evaluate
  CCS-isolated failure case doesn't occur on first issuance since
  envelope.condition_results.ccs=None; the CCS-isolated failure does
  occur at reassertion via section-12.4 path) + summary status counts
  updated (FULL 8->15 with pre-existing miscount fix where the "8"
  listed 9 sections; PARTIAL 6->4; DRIFTED 0 note update naming
  VL-029 build-half closure; UNIMPLEMENTED 7->3) + read-of-the-whole-
  picture paragraph full rewrite ("All three canonical invariants
  (AC^3, T^26, CCS) are FULL post-VL-029"). Per-file apply-script
  + synthetic-fixture discipline applied (5 apply-scripts: test_ccs_canonical,
  test_envelope, pep, test_pep, artifact04, artifact06; envelope.py
  via str_replace direct with one R1 self-discipline recovery for
  mid-edit scope-expansion + one apply-script halt-and-restore for
  str_replace old_str/new_str argument confusion in test_ccs_canonical.py,
  recovered via copy-from-pristine + apply-script promotion). N3
  source-first re-read after pep.py wiring caught one spec divergence
  (envelope construction not fail-closed; fixed via W2 + governed_call
  docstring step-6 extension before commit). Layer A inflection point
  per VL-024's bridge proposition: canon section 12 has a deterministic
  implementation in code wired into the gate for the first time in
  project history. The `07_continuity_recursion.md` artifact candidate
  is now eligible to schedule per VL-023's post-G0-build recommendation.
  Pytest verification deferred to user's real environment per constraint
  (m) sandbox discipline; expected at session-close: 84 passed + 0
  xfailed (80 pre-existing - 3 xfail + 3 xpass-now-pass + 1 new
  test_pep envelope coverage). Trajectory move per VL-017a's distinction
  (two implementation files + three test files + two structural docs +
  STATE.md + ledger; eight files modified, one untouched at evaluator.py
  per Decision C1 preserving evaluator's contract).
- **VL-030 T-G3 trajectory close: public framing reframe completed via Zenodo addendum Revision 2 + repo-internal evidence commit (this commit).** Two-part substantive trajectory. Part 1 (substantive, completed at prior session-close): README rewrite at commit `5f833fb` (logged via VL-029 follow-up entry at commit `89ff2f9`) brought public framing to post-VL-029 honest state. Part 2 (substantive, completed at the bridge session): Zenodo addendum Revision 2 published at DOI `10.5281/zenodo.20387278`, title `Elyon-Sol v0.9.8.4 - Enforcement Evidence Addendum (Revision 2)`, attached PDF `zenodo_addendum.pdf` (md5 `b750a803eb31a44248dd5fa89b4c273b`, 57.8 kB, 7 pages). The publication's evidence section is anchored to snapshot commit `89ff2f9c02871d8641cebd3eb043d6c3c0d8471a` and reports 204-call enforcement evidence (102 REFUSE producing 0 external POSTs, 102 ELIGIBLE producing exactly 102 external POSTs, 0 unexpected, webhook.site inbox 53 -> 155 verifying delta = exactly the ELIGIBLE-call count via SD-1 baseline-arithmetic discipline) plus pytest 84/84. Part 3 (this commit, repo-internal): `EVIDENCE/proofs/g3_enforcement_evidence_001.log` (verbatim script log, md5 `4281341ec10088766d78f59b87917fa6`, 843 bytes) and `EVIDENCE/proofs/g3_enforcement_evidence_001.md` (prose proof, md5 `adf458a0f3b4840b67152ebc2d37423f`, 4351 bytes) committed as durable internal record of the run that produced the DOI's evidence section. `docs/restructure/04_current_vs_claimed.md` G3 row gains Status: RESOLVED bullet citing VL-030 with README + Zenodo + EVIDENCE/proofs/ resolution criteria + DONE annotation on existing Action bullet + priority-order item 5 RESOLVED annotation. README line 414 forward-tense corrected to past-tense citing VL-030. G3 closes completely; T-G3 trajectory done. Five process findings recorded including Finding 1 Zenodo description-field plain-text rendering (Lesson candidate), Finding 2 webhook.site stale-inbox baseline-arithmetic discipline (methodology candidate), and Finding 5 session-close two-commit pattern (substantive at VL-029 follow-up + this commit's bridge session; ledger at this commit; first explicit instance of deferred-ledger workflow). Carry-forward gap candidate: STATE.md never received a VL-029 follow-up bullet (the `5f833fb` README commit) before VL-030; the VL-030 bullet folds the VL-029 follow-up narrative as Part 1 per alpha scope-bound decision; resolution candidate is a focused str_replace refreshing STATE.md for prior follow-up bullets in a future bookkeeping commit. The `07_continuity_recursion.md` artifact candidate remains eligible to schedule per VL-023's post-G0-build recommendation; no further G-resolution active. Classification: trajectory move per VL-017a's distinction.

- **VL-031 T-07 trajectory close: `docs/restructure/07_continuity_recursion.md` drafted and landed; pre-draft cross-model verification pattern's first instance (this commit).** Per VL-023's PARTIAL HOLDS verdict + VL-024's STRENGTHENS-bounded-to-layers-B-and-C refinement + VL-025 follow-up's convergent confirmation + post-VL-029 implementation evidence: the artifact names the recursive-continuity discipline pattern visible at five layers of the framework (decision, manifest, methodology, session, evaluator-versioning), the request-layer non-fit, the per-layer detector mechanisms (functional vs. procedural), and the layer A/B/C bounding per VL-024. Reading-aid track only per artifact's own scope statement; introduces no new invariant, claim, or vocabulary. Pattern-first structure (s2) for parity with the restructure package's existing artifacts (00_README, 04, 05, 06); inline citations (beta1) for parity with VL-023's derivation entry. Artifact stats: 19349 bytes, 381 lines, ASCII-clean, md5 `0ea94e694dfe3725776aaef12a9be412`. **T-07 verification (first pre-draft cross-model verification in project history)** ran with Grok and OpenAI as recipients, bundle of 7 files (canon + VL-023 + VL-024 + artifact 05 + artifact 06 + envelope.py + pep.py), four questions covering: Q1 four-part shape extraction from canon section 12, Q2 per-layer recursion-fit across five fitting layers + request non-fit, Q3 VL-024 layer A/B/C bounding re-derivability, Q4 evaluator-versioning fail-closed dissolution post-VL-029. Both verifiers procedurally clean within-body per Lesson 6; substantive convergence on all four questions; OpenAI's source-bound caveats on methodology/session layers (mediated through VL-023 excerpts) dissolved at artifact level via direct attachment of `docs/SESSION_PROTOCOL.md` and `docs/methodology/*` as citations. **VL-024 Implication 1's instruction to "carry the inference flag on evaluator-versioning's fail-closed component" is dissolved** per Q4 two-model convergence: post-VL-029 envelope.py reassert() Row 3 (lines 387-392) explicitly returns `{"outcome": RE_EVALUATE_REQUIRED, "ccs": False}` on evaluator_sha256 mismatch with canon section 12.4 direct basis; artifact cites Row 3 code verbatim without inference caveat. Bundled per scope: `docs/restructure/00_README.md` updated to list seven artifacts (item 7 added with the new artifact's framing). Five process findings recorded including the pre-draft verification pattern as two-instance threshold candidate (alongside VL-016 premise-verification) + bundle-plus-request co-upload prompt-recognition surface event (OpenAI's initial response was descriptive rather than derivational; required explicit "execute the procedure" re-prompt before shifting to derivational mode) + SESSION_PROTOCOL.md citation drift from VL-023 (VL-023 cited "lines 119-126" which no longer exist on disk; the file is now 87 lines; all substantive citations resolve to current lines but at different positions; same family as VL-029 gap candidates 1+2) + Lesson-7-candidate ASCII-pre-write-check discipline held cleanly for third consecutive artifact + carry-forward gap candidates absorbed from VL-030. Per-file apply-script + synthetic-fixture discipline applied throughout (3 apply-scripts: 00_README, statemd, ledger). Classification: trajectory move per VL-017a's distinction.

- **VL-032 T-methodology trajectory close: methodology backlog from VL-025 through VL-031 absorbed into durable artifacts via 5 sub-edits across 3 methodology files (this commit).** `docs/methodology/apply_script_template.py` gains a new SYNTHETIC-FIXTURE PRE-VERIFICATION docstring section codifying the pattern operative since VL-026 (three-plus-instance threshold met) with VL-031's load-bearing refinement that fixtures must be built from `cat -A` (or equivalent disk-byte inspection) of actual disk regions, not from inferred structure (+2717 bytes; 9587 -> 12304). `docs/methodology/session_mechanics_lessons.md` gains a Lesson 5 refinement (five new surface events from VL-028 through VL-031 demonstrating the opener-packaged-prediction timing variant of the set-exhaustiveness failure mode; failure-mode subsection refined with in-session-vs-opener-packaged distinction; corrective rule extended; self-check extended) plus two new lessons: Lesson 7 (typographic-drift discipline, two-stage: ASCII pre-write check at apply-script-write time + explicit byte-sweep at Claude-drafting time; three-instance threshold from VL-027, VL-029 Finding 4, VL-031 Finding 4) and Lesson 8 (pre-draft cross-model verification as premise-testing pattern distinct from post-draft artifact-reproduction-testing; two-instance threshold from VL-016 premise verification + VL-031 T-07 pre-draft verification) (+12064 bytes; 26580 -> 38644). `docs/methodology/cross_model_evaluate_template.md` gains three revisions: single-instance-language removed (two-instance threshold met at VL-023 follow-up + VL-031 T-07); new Outcome-classification criteria section codifying VL-025 follow-up's authorization-by-design-space vs. authorization-by-direct-naming Match-criterion clarification; new Co-upload format note section codifying VL-031 Finding 2's recipient-recognition surface event with two correctives (filename convention OR explicit inline turn after upload) (+3703 bytes; 15975 -> 19678). Decision recorded for sub-edit 4: Option B (Lesson 5 refinement) over Option A (new Lesson 9); rationale: file's own "How this file evolves" clause explicitly authorizes refinement when third or later instance reveals sharper characterization, and the new surface events demonstrate a sharper characterization of the same failure mode (set claim without enumeration) rather than a structurally different pattern. Per-file apply-script + synthetic-fixture discipline applied per the very Lesson 7 + apply_script_template.py refinement being promoted in this commit; Lesson 7 stage-2 byte-sweep validated session-internally during draft construction (2 em-dash drifts caught in draft files before apply-script construction - the very failure mode Lesson 7 addresses). One opener-prediction surface event at the byte-prediction layer (Lesson 5 fired once: lessons-file delta predicted approximately +8000, actual +12064; the +50% underestimate is a prediction-error not a content-error; substantive content correct). Classification: efficiency move per VL-017a's distinction (no code/canon/test/spec/structural-doc change). Repo test set 84 passed + 0 xfailed, unchanged from `6369eac` (VL-031).

- **VL-033 citation-currency audit: SESSION_PROTOCOL.md citations annotated; STATE.md known-items pruned (parent commit `fc15d1b`; this commit is the VL-033 follow-up appending the ledger entry + this current-verified-state bullet + item 27).** Audit per VL-033 opener with four categories. Category A: 6 bracket annotations applied to stale `docs/SESSION_PROTOCOL.md` line citations in VL-023 (5 sites) + VL-024 (1 site) Layer B passage. Form: `[VL-033 cite-currency: now lines N-M at HEAD 7f41615]` appended inline after original citations; original text preserved verbatim. Sites: VL-023 lines 84-86 -> 63-64; lines 119-122 -> 81-83; lines 64-100 close protocol -> 45-74; lines 20-58 resume protocol -> 10-41; lines 124-126 fail-closed -> 85-87; line 86 "continuity purposes" phrase -> 64. Net +512 bytes ledger. VL-031 gap candidate 6 closes. Category D: 9 closed items removed from STATE.md "Known items open but not scheduled" subsection under Decision T-cite-C conservative discipline (closure-event citable per removal). Removed items: VL-015/VL-016 verification-request artifacts (closed VL-017a); VL-016 premise-testing (closed VL-032 Lesson 8); VL-016 follow-up session-mechanics-lessons promotion (closed VL-018 follow-up); VL-017 stale forward-reference (closed VL-020); VL-017b candidate findings 1, 2, 3 (closed VL-018: SUPERSEDED + upgraded to G14); VL-017b build-resumption template revision (closed VL-017b own session); VL-020 second stale forward-reference at line 457 (closed VL-021). Subsection compacts 19 -> 10 items remaining. Net -3832 bytes. VL-029 gap candidate 2 closes. Category B: empty. STATE.md citation discipline already uses stable item-N references; line-N appears only in self-describing source-first records (correctly out of scope). Category C: empty. Disk verification at ledger lines 5237, 5159-5176, 5212-5224, 5331-5339, 5079-5086, 4501, 5002 confirmed every ledger-to-ledger line citation resolves correctly under append-only discipline. Step 0 Decision T-cite-E: VL-029 gap candidate 1 classified Type 2 (content drift at lines 1116-1152 / post-Category-D lines 1163+); out of VL-033 scope; new T-prose-drift candidate. Pre-session locked decisions applied: T-cite-A pause-and-split threshold (~30 drift instances) not triggered; T-cite-B content-phrase preference applied to Category A phrase-anchored citations; T-cite-C conservative bias applied per-item in Category D; T-cite-D batch-size discipline in this entry. In-session: Option B annotation form (preserves history); Strategy B apply-script structure (5 edits for 9 removals via merged adjacent clusters); commit cadence Option b (single trajectory commit at session-close; subsequently required follow-up commit due to STATE.md/ledger delivery omission, recorded as session-mechanics finding in this follow-up entry's process findings). Seven process findings in VL-033 ledger entry: MINGW64 path translation surface event (single instance); Greek-letter leak in Claude-side prose (fourth instance of Lesson 7 stage 2 failure; user-caught); D-empty reversal triggered by user's "is D-empty in violation of scope definitions?" question (scope-classification drift caught at user-as-final-arbiter layer); byte-delta prediction errors in both apply-scripts (Lesson 5 recurrence; predictions off by 5% / 3.4%; substantive content correct); inferred-baseline assertion without source verification (line count claimed at 8568 without disk read; trace observation); out-of-order category execution (A-B-D-C rather than A-B-C-D; opener-permitted); Lesson 7 stage 2 catching this entry's own em-dash in draft (fifth instance of operative discipline). The session's audit demonstrated two of the four citation categories (B and C) were already structurally drift-resistant under existing framework discipline; the other two absorbed real drift accumulation. Classification: efficiency move per VL-017a's distinction. No code/canon/test/spec/implementation/structural-doc change. Pytest 84 passed + 0 xfailed unchanged from HEAD `7f41615`.
- **VL-034 T-G7-eval trajectory close: canon-derived tests for the evaluator domain; G7 closes completely (this commit).** `TESTS/adversarial/test_evaluator_canonical.py` adds 22 tests whose lineage runs from canon section 11 to assertion: 8 for AC^3 (canon 11.7 `AP superset-or-equal AR`), 8 for T^26 (canon 11.8 `OP superset-or-equal R`), and 6 for manifest-integrity (canon 11.9 via artifact-05-layer per Decision C). The tests call the predicate functions directly (`ac3_valid`, `t26_valid`, `manifest_integrity_valid`) to mirror canon section 11's per-clause structure, the different-shape complement to the 23 code-derived tests in `TESTS/test_adversarial_evaluator.py` which drive `evaluate()` end-to-end (Decision D: augment, not replace). Per constraint (i) no test pins a literal hash value; the manifest group derives the expected sha live via `manifest_sha256()`, surviving GR-1 events. G11 (manifest-source asymmetry) is documented in the manifest section's intro comment and B-parked per Decision F. Decision-C artifact-05-layer acknowledgment is carried by the manifest group plus the duplicate-handling and type-violation tests for both predicates (canonical basis: set semantics canon 11.5/11.6 and fail-closed canon section 9; mechanism: safe_set()). Checkpoint B surfaced no halt-class spec gap; the opener's anticipated canon-vs-code gap-candidate materialized as acknowledgment-class. Checkpoint C: 106 passed + 0 xfailed in the author's real environment (84 pre-existing + 22 new), no implementation bug surfaced. G7 transitions from PARTIALLY ADDRESSED (VL-028 + VL-029, envelope domain only) to RESOLVED (VL-028 + VL-029 + VL-034, both domains). Artifact 04 G7 row + priority-order line + two nested G0-section G7-status references updated to RESOLVED; artifact 06 rows 11.7/11.8/11.9 (already FULL) gain canon-derived-test cross-references per maintenance rule 3, closing the spec-map-test-code loop for the evaluator domain as the CCS rows did at VL-028/VL-029. Four process findings recorded (Lesson 7 stage 2 section-sign leak, new character class, user-caught; count-anchor-over-source drift, Lesson 5, user-caught; source-first near-miss on the opener's identity, Lesson 3, user-caught; verify-on-disk catching the hash-pinning error, positive). Classification: trajectory move per VL-017a's distinction. No code/canon/manifest/spec change. Pytest 84 -> 106 passed + 0 xfailed.
- **VL-035 methodology refinement: Lessons 2 and 3 of `docs/methodology/session_mechanics_lessons.md` sharpened from the VL-033/VL-034 source-first findings (this commit).** Refinement, not a new lesson, per the file's "How this file evolves" clause (a third or later instance reveals a sharper corrective; lesson count unchanged at 8). Lesson 2 (terminal-output rendering is not file content) gains the VL-034 fragile-anchor as its third surface event and a corrective addition: edit and append anchors must come from `cat -A` or disk bytes, never pasted or rendered output, because rendering can wrap a single logical line across visual lines (the line-wrap variant alongside the existing blank-line-collapse variant). Lesson 3 (source-first applies to Claude's own derivations) gains three surface events (VL-033 Finding 3 D-empty, VL-033 Finding 5 inferred baseline, VL-034 Finding 3 governing-document identity), a failure-mode sharpening (the rule covers a file's identity and session-start contents, not only convention-format), a corrective list bullet (the identity and contents of uploaded or governing documents), the precondition-not-disposition corrective paragraph (binary precondition; the `[unread]` flag; treat the opener's pre-session checklist as a hard gate), and a matching self-check extension. Cross-references between the two lessons embedded inline per the evolves-clause. Seven str_replace edits (+4029 bytes) applied via a synthetic-fixture-verified apply-script with fixture cleanup on every exit path (the VL-034 carry-forward-2 corrective). A from-memory draft had mis-located the content as one lesson / a possible new Lesson 9; the disk read corrected the placement - the precondition lesson catching its own drafting. Classification: methodology-artifact update, efficiency move per VL-017a's distinction. No code/canon/test/spec/structural-doc change. Pytest 106 passed + 0 xfailed unchanged.
- **VL-036 T-G4-design: `docs/restructure/08_enforcement_design.md` drafted; G4 designed, build pending VL-037 (this commit).** Design + spec session per Decision A; no code/canon/manifest/test/spec change. The artifact states a threat model for G4 (bypass = the target acts without a valid current decision; two routes: non-coverage A1 and non-attestation A2/A3; adversary set A1-A5 derived by construction over the participant set per canon section 11.1, not asserted; non-bypassability framed as canon-permitted and reader-expected per artifact 04 G4, not canon-mandated), enumerates G4 sub-questions Q1-Q8, evaluates the artifact-05 open-question-3 mechanism (attach envelope + target verifies) and its delivery variants (push deepens the pre-existing section-14 tension; caller-carry/proxy-removal relieve it), checks section-14 compatibility (no new invariant; the tension pre-exists in pep.py's forward), addresses the G4/G5 boundary at E1 (target-side `reassert()` reuse needs a durable published hash source = G5, named as precondition; design fully stateable without resolving G5), and recommends a VL-037 increment (delivery-agnostic target-side verifier reusing `reassert()` plus a `request_context`-vs-live-interaction binding check; minimal push delivery flagged for its section-14 cost; A1 named as the gate-unreachable floor closeable only by target-side policy). Two Checkpoint-B-derived sharpenings landed in the artifact: T0's adversary-set exhaustiveness upgraded from asserted to derived-by-construction (the cross-model under-determined finding), and Q5 split into envelope-authenticity (closed by the mechanism via `decision_sha256` over `request_context`) versus interaction-binding (a separate verifier obligation; `reassert()` checks repo-state hashes, not `request_context`, so same-state replay A3 is not closed by `reassert()` alone). Pre-draft cross-model verification (Grok + OpenAI, framework-level evaluate procedure under VL-008 + Lesson 8): T0/P1 procedurally clean; P1 convergent Property-holds under direct-naming; T0 split (Grok holds, OpenAI under-determined on exhaustiveness) logged as a Match-criterion / derivation finding, resolved in-artifact by deriving exhaustiveness by construction. P2 (section-14) and P3 (G4/G5 boundary + `reassert()` replay gap) derived source-first per Checkpoint C scope rather than cross-model, per the source-read finding that `cross_model_evaluate_template.md` is framework-level-only and excludes canon/code questions (opener-internal tension with Decision B's named targets; recorded as a methodology finding). `docs/restructure/04_current_vs_claimed.md` G4 row gains a design-landed-VL-036/build-pending-VL-037 bullet; G4 does NOT transition to RESOLVED. Classification: trajectory move per VL-017a's distinction (a new restructure artifact). Pytest 106 passed + 0 xfailed unchanged from HEAD `cdeeb25`.
- **VL-037 T-G4-build: target-side envelope verifier landed; first G4 build increment; G4 enforcement status unchanged (this commit).** `IMPLEMENTATION/verifier.py` lands per `docs/restructure/08_enforcement_design.md` section 8 step 1: `verify_envelope(envelope, interaction, target_url)` returns `{"accepted", "reason"}` after a structural presence guard, then `envelope.reassert()` for currency plus integrity (any outcome other than REASSERTED rejects, closing forgery A2 and detecting canon/evaluator/manifest transitions), then a symmetric `request_context`-vs-live-interaction binding check (AP/OP as canon section 11.5/11.6 sets normalized on both sides, `context` by `canonical_json` equality, manifest-pinning and `target_url` by string equality; closes same-state replay A3, which `reassert()` alone does not per artifact 08 sections 4.2/7). Closed REF_VERIFY_ reject set (parallel to REF_SCHEMA_): REF_VERIFY_ENVELOPE_ABSENT, REF_VERIFY_REASSERT_INVALIDATED, REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED, REF_VERIFY_BINDING_MISMATCH; accept reason REASSERTED_AND_BOUND. Canon basis: section 13 revalidation (the verifier is the target-side revalidation step) plus section 11.1 interaction identity; no new invariant (artifact 08 section 5); non-executing (canon section 14 holds). `TESTS/adversarial/test_verifier.py` adds 11 canon-derived tests (accept; the four reassert() rows; absent; malformed; replay-binding-mismatch A3; target_url-mismatch; AP/OP normalization parity; context binding) and `TESTS/adversarial/test_bypass.py` adds 2 honest A1-bypass tests (direct-to-target reaches the target with no envelope; a target running the verifier would reject the un-attested call) per Decision E. Build-then-wire per VL-025 to VL-029: the verifier has NO caller; `pep.py` is untouched (Decision A) and delivery (push vs caller-carry vs target-pull) is VL-038. G5 named as the deployment precondition in the module docstring, NOT built (Decision F; artifact 08 section 6); A1 named as closeable only by a target-side policy, not by the gate (artifact 08 section 4.4); the verifier is necessary-but-not-sufficient. Checkpoint-C finding: the sandbox smoke caught an asymmetric AP/OP normalization in the first draft (live side normalized, envelope side raw, so a valid envelope false-rejected), fixed to symmetric set normalization per canon 11.5/11.6 and Decision C; an implementation bug, not a spec gap, so no Checkpoint B halt. The `context` canonical_json equality is flagged [INFERENCE] (artifact 08 gap candidate 1). `docs/restructure/04_current_vs_claimed.md` G4 row gains a verifier-built-VL-037/delivery-pending-VL-038 bullet; `docs/restructure/06_spec_to_code_traceability.md` section-13 row gains a target-side-verifier note (the verifier consumes `reassert()`, implements no new canon section, so a note, not a new row). G4 does NOT transition to RESOLVED (the verifier has no caller; enforcement is unchanged). Classification: trajectory move per VL-017a distinction (a new `IMPLEMENTATION/` module plus two new `TESTS/` files; structural-doc updates only). Pytest 106 -> 119 passed + 0 xfailed (real environment).
- **VL-037 follow-up: working scratch files removed; STATE/ledger bookkeeping (commit `251b44b` plus this bookkeeping commit).** `git add -A` at the VL-037 close (`a959680`) swept three repo-root scratch files into the commit: `apply_vl037_docs.py` (the apply-script), `vl037_commit_msg.txt` (the commit message), and `vl037_ledger_entry.md` (the standalone ledger entry, already appended to `EVIDENCE/verification_ledger.md` at `a959680`, so a duplicate). Commit `251b44b` removed all three via `git rm`; no repo content lost, the seven intended VL-037 deliverables unaffected, pytest 119 passed + 0 xfailed and import clean unchanged, lessons 8. Recovery via follow-up commit per the VL-020/VL-021 precedent (no history rewrite). Process finding (this entry in the ledger): scratch-in-repo via `git add -A` from the repo root, first named instance of a new session-mechanics family distinct from chat-paste-eats-content; correctives are work-outside-the-repo per `apply_script_template.py` and stage-only-intended-paths, with a `.gitignore` guard for `apply_vl*.py`/`vl*_commit_msg.txt`/`vl*_ledger_entry.md` deferred pending a source-first read of the current `.gitignore`. No code/canon/manifest/test/spec change. G4 remains OPEN; next trajectory action unchanged (VL-038 G4-delivery).
- **VL-038 T-G4-enforce: push delivery + enforcing target verifying against the published record; the first gate state (this commit).** `IMPLEMENTATION/pep.py` pushes the envelope on the ELIGIBLE forward as the out-of-band header `X-Elyon-Sol-Envelope` (canonical JSON; forwarded body unchanged, so a routed call and a direct call differ only by the header)  -  2 edits, the rest of `pep.py` and all of `verifier.py`/`envelope.py`/`evaluator.py`/`request_validator.py`/`CANON`/`MANIFEST` byte-unchanged (Decision A; constraint l). `EVIDENCE/published_hashes.json` (new) extends `CANON/canon.lock`'s discipline to the evaluator and manifest hashes, derived live by `EVIDENCE/published_hashes_gen.py` (never hand-copied; constraint i). `TESTS/adversarial/test_enforcement.py` (new, 7 tests) builds an enforcing target that honors iff the envelope's pins match the committed published record (the Decision-C anchor, not local disk) AND `verify_envelope()` accepts (integrity A2 + binding A3, reused as-is per Decision D; no new REF_VERIFY_ code; the single new harness reason is `REF_TARGET_PUBLISHED_RECORD_MISMATCH`); a missing or unparseable header maps to `verify_envelope(None, ...)` reusing `REF_VERIFY_ENVELOPE_ABSENT`. `TESTS/test_pep.py` migrated: all five `fake_post` stubs accept the new `headers` kwarg, the ELIGIBLE-forward test asserts the envelope rides in the header with the body left bare, and the response-envelope test asserts the pushed envelope equals the returned envelope (still 5 tests). Refused-bypass evidence at `EVIDENCE/proofs/g4_refused_bypass_001.{log,md}` (g3 format) plus runner: 1 honored and acted (`REASSERTED_AND_BOUND`), 5 refused 403 and not acted (A1 `REF_VERIFY_ENVELOPE_ABSENT`; A2 `REF_VERIFY_REASSERT_INVALIDATED`; A3 replay and target_url `REF_VERIFY_BINDING_MISMATCH`; `REF_TARGET_PUBLISHED_RECORD_MISMATCH` for an envelope that passes local-disk `reassert()` and binding but mismatches the published record  -  the defensibility case). Checkpoint B: no `SPEC/request_schema.md` edit (the forwarded shape is the unchanged body plus one out-of-band header carrying the already-artifact-05-specified envelope; candidate GR-2 not triggered). Section 14 re-read: the gate still does not verify (it decides and delivers); the target verifies; push deepens the pre-existing section 14 tension without the gate executing; caller-carry is the section-14-faithful later architecture. `docs/restructure/04_current_vs_claimed.md` G4 gains a VL-038-build-increment-2 bullet and G5 a committed-published-record partial-progress bullet; `docs/restructure/06_spec_to_code_traceability.md` section 13 and section 14 rows updated. **G4 defensibly non-bypassable for routed-and-attested traffic; NOT blanket RESOLVED**  -  A1 (the declining caller, closeable only by target-side policy) and cross-host TRANSPORT of the published record (the G5 hardening) remain, named not built (Decision F; artifact 08 sections 4.4 / 6). Pytest 119 -> 126 passed + 0 xfailed (real environment). Classification: trajectory move per VL-017a's distinction (a delivery edit plus a new published record, a new test file, and a new evidence run).

- **Post-VL-038 audit disposition (commit `15c53cb`; board-clear, not a trajectory move).** An off-framework parallel cross-model adversarial audit of VL-038 pinned five confirmed findings as green characterization tripwires in `TESTS/adversarial/test_findings_001.py` (F1 `timestamp_utc` outside `decision_sha256`; F2 verbatim replay honored; F3 no `target_url` allowlist / SSRF surface; F4 ELIGIBLE independent of upstream outcome; F5 order-dependent duplicate `X-Elyon-Sol-Envelope` header). Each test pins current behavior, so closing any gap must break its test. The audit process is recorded at `docs/methodology/cross_model_adversarial_audit.md`; the VL-039 G5 opener at `docs/methodology/vl039_session_opener.md`. Pins, does not fix: capability unchanged from VL-038; pytest 126 -> 131 passed + 0 xfailed. Per the audit methodology's ADOPTION clause, the audit's cold verdict-of-record is recorded by the invoking session (VL-039), not here; this bullet is board-clear bookkeeping only.

- **VL-040 T-signing: issuer signing landed (opt-in); the forgery finding closed on the signed path (this commit).** Per VL-039's conclusion that issuer signing is the increment under A1 and freshness (an attestation that does not authenticate its issuer cannot be the floor under either), the gate now signs the envelope and a target verifies the signature. `IMPLEMENTATION/envelope.py` gains `sign_envelope(envelope, signing_key, key_id)` (Ed25519 via a duck-typed key object; envelope.py does NOT import `cryptography`) returning a NEW envelope with `issuer_key_id` + `issuer_signature`; the signature covers `canonical_json(envelope minus issuer_signature and timestamp_utc)`, which includes `decision_sha256` and `issuer_key_id`. `decision_sha256`'s region and `reassert()` Row 2 now exclude the two issuer fields (`_HASH_EXCLUDED_KEYS`), a confirmed no-op on the unsigned path, so a signed envelope's `decision_sha256` is identical to the unsigned one and reasserts unchanged. `IMPLEMENTATION/verifier.py` gains `verify_envelope(..., pinned_public_keys=None)`: when supplied, the issuer signature is REQUIRED and verified (duck-typed `public_key.verify`) BEFORE `reassert()`, fail-closed to `REF_VERIFY_SIGNATURE_INVALID` (missing/malformed/verification-failed) or `REF_VERIFY_SIGNATURE_UNKNOWN_KEY` (key_id not pinned), canon section 9; with `pinned_public_keys=None` the unsigned path is byte-behavior-unchanged. The VL-039 follow-up 2 three-model forge (from-scratch, correct unkeyed `decision_sha256`, no signature) is now REFUSED on the signed path and ACCEPTED on the unsigned path (the honest opt-in boundary), pinned in `TESTS/adversarial/test_signing.py` (10) and demonstrated in `EVIDENCE/proofs/signing_forgery_defeated_001.{runner.py,log,md}` (runner exits 0). Spec commit `b9ca90a` (artifact 05 'Issuer signature (opt-in)') precedes this build commit (spec-defines-the-change; GR-2 candidate not formalized). Docs: artifact 08 section 4.2 corrected (the A2 'closed by decision_sha256' claim split into TAMPER-closed / FORGERY-closed-by-signing), artifact 04 G4 bullet, artifact 06 section 8.2 UNIMPLEMENTED -> PARTIAL. Canon basis: section 8.2 PoE + 11.9 integrity; no new invariant; no new reassertion row; section 14 holds. New dep `cryptography==44.0.0` (duck-typed; only tests/runner import it). pytest 139 -> 149 + 0 xfailed (real env + in-container). **Opt-in: forgery closed only on the signed path; `pep.py` default unsigned; the mandatory cutover is the named follow-on. CLAIM-TRACK GATE: 'forgery-resistant' is bounded, NOT settled - the key-governance cross-model evaluate RAN at VL-040 follow-up 2 (3-0 convergent: provenance is what pinning buys; key lifecycle is named-not-built; the decisive failure is private-key compromise, trust-model not construction). The bound is evaluate-confirmed and load-bearing; revocation/compromise-recovery (B-prime-2) is the floor it rests on; the word enters no Zenodo deposit until that floor exists.** Classification: trajectory move per VL-017a's distinction.

- **VL-041 T-key-lifecycle: issuer-key EXPIRY built (opt-in); an undetected key compromise is now time-bounded (this entry).** `IMPLEMENTATION/envelope.py::sign_envelope(..., not_after=<tz-aware datetime>)` stamps a `not_after` ISO-8601 field INSIDE the signed region (covered by `issuer_signature`, so it is tamper-proof - a captured signed envelope's window cannot be extended) and OUTSIDE `decision_sha256`'s region (`_HASH_EXCLUDED_KEYS`, like `issuer_key_id`, so a signed-with-expiry envelope's `decision_sha256` is byte-identical to the unsigned one and `reassert()` Row 2 is unchanged - the Checkpoint B decision). `IMPLEMENTATION/verifier.py::verify_envelope(..., now=None)` enforces `now < not_after` at a new Step 1.5b after the signature check, fail-closed (canon section 9) to `REF_VERIFY_SIGNATURE_EXPIRED`; a malformed or tz-naive `not_after` also fails closed; absent `not_after` = no expiry (VL-040 byte-behavior). Canon basis: section 8.2 PoE + 11.9 integrity; no new invariant; verifier-layer, orthogonal to `reassert()`/CCS; section 14 holds (the window bounds the ISSUER's attestation, not actor identity). `TESTS/adversarial/test_signing_expiry.py` (11, canon/spec-derived); `EVIDENCE/proofs/signing_expiry_001_runner.py` (live Ed25519 keypair; expired refused while the same live-window decision honored; exit 0). pytest 149 -> 160 + 0 xfailed (real env, against live `reassert()`). Spec commit `abdb9e0` (artifact 05 `not_after`) precedes build commit `807ccfe` (spec-defines-the-change). Build-then-wire: NO `pep.py` change; the gate's default forward is unchanged; emitting expiring envelopes is the integrator-posture cutover. **Closes the UNDETECTED-compromise sub-case of the VL-040 follow-up 2 decisive failure, time-bounded, WITHOUT depending on detecting the leak - the highest-value first key-lifecycle increment. Does NOT close revocation (detected-compromise instant kill) or the trust root; the published signed key record (B-prime-2) carrying revocation/rotation introduces a publisher/root key that owes its own framework-level evaluate before 'forgery-resistant' moves further. The word stays BOUNDED, not settled; the compromise floor is now PARTIALLY addressed (expiry), revocation + the trust-root evaluate still required.** Classification: trajectory move per VL-017a's distinction.

- **VL-042 T-key-record (B-prime-2): published signed key record built (opt-in); revocation closes the detected-compromise instant-kill case; the new publisher/root trust floor (this entry).** `EVIDENCE/published_keys_gen.py` generates a live publisher-signed `EVIDENCE/published_keys.json` (generated at runtime, not a committed repo artifact) listing currently-valid issuer keys (each with a window + explicit `revoked` flag) plus the record's own freshness bound; only `publisher_signature` is outside the signed region, so serial/window/revoked are tamper-proof. `IMPLEMENTATION/key_record_source.py` (new; MIRRORS `published_source.py`, does not extend it - B-prime-1 pins record BYTES, B-prime-2 pins a root PUBLIC KEY so the record may change under a stable pin) is the reader: pure `load_key_record_from_bytes(..., pinned_root_keys, now, last_seen_serial)` (pinned-root signature -> freshness (`not_after` + opt-in `serial`) -> per-key trust view) + thin `fetch_key_record()` transport, discriminating `REF_VERIFY_KEY_RECORD_INVALID` from `REF_VERIFY_KEY_RECORD_STALE`. `IMPLEMENTATION/verifier.py::verify_envelope(..., key_record_view=None)` consults the validated view RECORD-EXCLUSIVELY (decision 3; the static `pinned_public_keys` map is ignored when a record is supplied, so a record revocation cannot be undone by the map): absent -> `REF_VERIFY_KEY_UNKNOWN`, revoked -> `REF_VERIFY_KEY_REVOKED`, `now` outside `[not_before,not_after)` -> `REF_VERIFY_KEY_OUT_OF_WINDOW`, else the record-sourced key feeds the unchanged Step 1.5 signature check + VL-041 Step 1.5b expiry. Canon 8.2/9/11.9/13; no new invariant; verifier-layer; section 14 holds only under the narrowed reading (the root is now THE trusted identity; identity is not an admissibility substitute). `TESTS/adversarial/test_key_record.py` (15) + `EVIDENCE/proofs/key_record_001_runner.py` (live root+issuer keypairs; revoked refused + stale refused while current honored; `python -m EVIDENCE.proofs.key_record_001_runner`, exit 0); pytest 160 -> 175 + 0 xfailed (real env, win32/Python 3.13). Build-then-wire: NO `pep.py` change. Spec commit `c323b65` (artifact 09, standalone, spec-defines-the-change) + build commit `5e9fbf6`. First `IMPLEMENTATION/` module to import `cryptography` (envelope/verifier stay duck-typed; the dep is unchanged since VL-040). **Honest-recovery test MET: a deployment can now INSTANTLY refuse a revoked key (`REF_VERIFY_KEY_REVOKED`) and a stale pre-revocation key record (`REF_VERIFY_KEY_RECORD_STALE`); the residual cached-record window is the transport/G5 surface. The compromise floor's complement to VL-041 expiry is now built (undetected = expiry; detected = revocation). But the publisher/ROOT key is a NEW, SINGULAR, LOAD-BEARING trust floor (root compromise is total) that OWES its own framework-level cross-model evaluate (VL-042 follow-up) before 'forgery-resistant' moves further off its bound. The word stays BOUNDED, not settled, and out of any Zenodo deposit.** Classification: trajectory move per VL-017a's distinction.

- **VL-043 T-readiness: the WIRING-track drift gate built; machine-checked deployment-readiness, fail-closed on dishonesty; 0 of 3 predicates green by design (this entry).** A GR-track INSTRUMENT, not a capability move - it adds nothing to the admission path (no `verifier.py` / `evaluate()` / canon change, no new invariant; VL-017a: neither substantive nor trajectory - process hardening that happens to be executable, kin to the `.gitignore` guards and VL-009). It adds the un-tracked THIRD axis: the project already runs CAPABILITY (built? - adversarial tests) and CLAIM (defensible? - the evaluates); prototype-drift lives in WIRING (on the DEFAULT path? exercised END-TO-END with no test-only shortcut? TRANSPORTED?). `EVIDENCE/readiness.json` is the single source of readiness truth (per-capability `built/wired_to_default/exercised_e2e/transported`, each `{value,proof,blocked_by}`; a true flag MUST name a proof test, a false flag MUST name a reason); `IMPLEMENTATION/readiness.py` validates; `TESTS/readiness/test_readiness.py` fails the build on a dishonest manifest (flag-true-without-proof, green-while-unwired, missing proof file - all demonstrated caught) but NOT for red predicates; `TESTS/readiness/test_deployment_predicates.py` carries DEFAULT_SECURE + END_TO_END_NO_SHORTCUT as declared xfail (green-with-declared-xfail; reds visible, never skip-hidden). The one principle: no readiness fact is human-attested; every flag is derived from a named proof test or it is false. pytest 175 -> 178 + 2 xfailed (real env). Spec `efeb8ba` (artifact 10, spec-defines-the-change) + build `753e978`. **Honest initial state is 0 of 3 green (see `EVIDENCE/readiness.json`) - CORRECT, not failure: a guardrail green on day one is the theater it prevents. The CAPABILITY track is green; the WIRING track is red; the gate stops the former masking the latter. NO follow-up evaluate (the gate makes no claim about the world - the first build-adjacent entry with none, by design). The honest ceiling, stated: the gate catches claim-vs-wiring drift and reds the build when docs and system diverge; it does NOT do the wiring (cutover / transport / root-recovery are real engineering it cannot perform). Carry-forward: the two predicate ANCHORs are scaffold-reds not yet exercising `pep.py`; finalizing needs a source read.** Classification: GR-track instrument (no capability advance); the three reds (DEFAULT_SECURE = cutover, END_TO_END_NO_SHORTCUT = G5, ROOT_RECOVERY = VL-044) are the finite road to a working system.
- **VL-044 T-root-recovery: planned root rotation + per-root status built (B-prime-3); opt-in, build-then-wire; ROOT_RECOVERY stays RED by design (this entry).** A capability/trajectory move (VL-017a): the rotation primitive is a real capability advance, but NOT on the admission path (`verify_envelope` logic unchanged; no new invariant; canon 8.2/9/11.9/13/14, section 14 under the narrowed reading one layer up). A current root signs its successor's designation, so a target pinning only R1 trusts a designated R2 in-band (transitive root trust, bounded by status + freshness, conservative single hop); per-root status (active/retired/revoked) gates the signing root at the record-validation layer. Built: `EVIDENCE/published_roots_gen.py` (live signer; `published_roots.json` is a runtime artifact, never committed, per artifact 11 section 4); `IMPLEMENTATION/root_record_source.py` (B-prime-3 sibling reader -> per-root status view); a `root_status_view` gate on `key_record_source.py` (revoked -> REF_VERIFY_ROOT_REVOKED; retired NEW record -> REF_VERIFY_ROOT_RETIRED via issued_at<retired_at, past records age via freshness; None -> exact VL-042 byte-behavior); four `REF_VERIFY_ROOT_*` constants in verifier.py (no `verify_envelope` logic change; the stale Step 1.5 comment fixed). Tests `TESTS/adversarial/test_root_record.py` (18; record validation + the cross-record gate + two documented boundaries: cross-signer conflict is NOT loader-resolved, sole-root revocation is out-of-band only). Proof `EVIDENCE/proofs/root_record_001_runner.{py,log}` (live R1->R2 in-band rotation; target pins only R1 and never re-pins; designated R2 honored; R1 self-retires; a NEW key record signed by retired R1 refused while its PAST one ages out; exit 0). Readiness: `root_rotation` capability built-but-unwired; `ROOT_RECOVERY` predicate RED with a named proof anchor + narrowed blocked_by (Decision F; green-on-built would be the masking the gate prevents); gate stays 0 of 3 green (see `EVIDENCE/readiness.json`). The honest ceiling: root-key COMPROMISE recovery is irreducibly out-of-band (artifact 11 section 2); only PLANNED rotation is built. Decision H locked (ii): the transitive-designation evaluate is drafted and run off-framework AFTER this build, folds as VL-044 follow-up; `forgery-resistant` unchanged (constraint l). NO `pep.py` change (build-then-wire). Spec `7cfc699` + `9e5181b`; build `aec58ee`. pytest 178 -> 196 + 3 xfailed (real env).
- **VL-044 follow-up - transitive-root-designation cross-model evaluate: SOUND, 3-0 convergent; the forgery-resistant bound does NOT move (this entry).** Framework-level evaluate (VL-008 + cross_model_evaluate_template) of the one new trust relationship VL-044 introduced - transitive root designation (a pinned R1 vouches in-band for a successor R2 a target never pinned). Grok, OpenAI, Gemini; blind, off-record; all derive-before-grade, all within-body scope-clean (Lesson 6). Verdict: SOUND as built; the bound on `forgery-resistant` is UNMOVED (stays signed-path-under-uncompromised-root, VL-040-follow-up-2 / VL-042-follow-up form, out of any deposit). 3-0 convergent ACCURATE on the load-bearing questions: Q1 (in-band single-hop rotation), Q3 (NO adversary-reach expansion - a compromised root was already total; designation is an honest-root capability, adding lifecycle ambiguity not adversarial authority), Q4 (canon clean, no new invariant, section-14 narrowed reading REQUIRED). One Match-criterion divergence (second instance of the VL-042-follow-up authorization-by-construction-vs-by-direct-naming pattern): OpenAI graded the prompt's stated `overlap-conflict fail-closed` phrasing OVERSTATED (the loader fail-closes only the WITHIN-record analog; cross-signer is the named out-of-band hazard), Grok/Gemini ACCURATE-by-construction while drawing the same split - a stated-answer phrasing finding, not a defect; the code + spec (post-`9e5181b`) already draw it. Two deferred gap candidates: (1) retirement clock-skew (Gemini, load-bearing; a post-retirement root compromise can backdate `issued_at` under clock skew - the artifact-09-section-5 clock note's sibling one layer up; artifact 11 should state the verifier-clock assumption); (2) per-root-window enforcement is consumer-layer (minor spec note). Both deferred to the doc/spec pass. No code/canon/spec/manifest change. Evaluate build `aec58ee`; raw responses off-repo (VL-008).

- **VL-045 T-prose-drift + T-bookkeeping: doc-freshness, spec-clarification, and methodology catch-up; NO capability or admission-path change (this entry).** A catch-up-and-record pass bringing the stale narrative artifacts current with the code that outran them, folding three named spec gaps, and promoting two at-threshold methodology candidates; three content commits, each prose-only. (1) Doc-freshness `3555dc1`: `docs/restructure/04_current_vs_claimed.md` folds VL-041 (issuer-key expiry), VL-042 (key record / revocation, B-prime-2), VL-043 (the readiness instrument, 0 of 3 green by design), and VL-044 (planned root rotation, B-prime-3, plus the SOUND-3-0 transitive-designation evaluate) into the G4 cluster after VL-040, plus a G5 transport-surface note after VL-039; no G-row status transitions (G4 NOT resolved, G5 open; the bullets record CAPABILITY, not deployment). `docs/restructure/00_README.md` heading seven->eleven, intro Six->Eleven, artifacts 08/09/10/11 listed. (2) Spec-clarification `919bc40`: `11_root_record_spec.md` section 6.1 gains a clock-and-window note - the retirement gate `issued_at < retired_at` trusts the verifier clock exactly as the section 5 freshness ceiling does (VL-044 follow-up finding 1, load-bearing; a post-retirement root compromise can backdate a forged `issued_at` within clock skew; not closeable without a trusted time source, stated not fixed), and per-root WINDOW enforcement is consumer-layer (parsed at section 7 step 7; the section 8 status gate consults status, not the window); `09_key_record_spec.md` section 5 gains the mirrored freshness-clock note, closing the long-carried artifact-09-section-5 item; artifact-11 overlap-conflict phrasing (3.3) VERIFIED clean on disk (section 6.3 / section 7 step 6 / section 9 already draw the within-record-vs-cross-signer split), no edit; per-artifact-mirroring chosen over a consolidated clock statement (the opener fork). (3) Methodology `00f5709`: `session_mechanics_lessons.md` new Lesson 9 (session scratch belongs outside the repo tree / run-cwd discipline; three instances VL-037/041/044; the corrective is behavioral because the existing .gitignore guards are root-anchored by design and cannot catch subdirectory scratch); `cross_model_evaluate_template.md` new requester-discipline pre-narrowing section (the mirror of the recipient-discipline outcome-classification section; two instances VL-042-followup/VL-044-followup). The .gitignore scratch guard (4.3) was found ALREADY present (VL-037 follow-up + VL-042) and is NOT edited - the opener-prediction-vs-disk divergence the source-first precondition catches (second instance after VL-042 finding 3). NO follow-up evaluate (no claim about the world). Classification: process/record hardening per VL-017a - neither a capability nor a trajectory move. The board is unchanged: 0 of 3 deployment predicates green; VL-044's capability remains built-but-unwired. Findings recorded: the duplicate VL-042 ledger entry (byte-identical, the two `### VL-042` blocks; de-dup deferred to a separate micro-commit, append-only discipline preserved here); the section-sign leak in Claude-side chat prose (Lesson 7 stage-2, user-caught, no deliverable affected - the .encode("ascii") guard and spelled-out section kept every committed file clean); the .gitignore-already-present divergence. Content commits `3555dc1` + `919bc40` + `00f5709`; this STATE + ledger commit does not cite its own hash (VL-012). Repo test set 196 passed + 3 xfailed unchanged.

- **VL-046 T-bookkeeping: ledger integrity - the duplicate VL-042 build entry removed (this entry).** A single-purpose corrective named in VL-045 finding 1: the VL-042 build entry appeared TWICE as adjacent byte-identical blocks (254 lines / 16502 bytes each, verified identical by the apply-script before removal); the second copy removed, the first retained verbatim, the VL-042 follow-up untouched. The rare justified deletion from the append-only ledger - it removes a verified exact DUPLICATE (changes multiplicity, not recorded content) and is logged in its own appended VL-046 entry so the deletion is itself on the append-only record. Classification: process/record hardening per VL-017a (neither capability nor trajectory); no follow-up evaluate. No code/test/canon/manifest/spec change; the board is unchanged at 0 of 3 deployment predicates green; 196 passed + 3 xfailed unchanged. This commit does not cite its own hash (VL-012).

- **VL-047 T-default-secure: the mandatory signing cutover; DEFAULT_SECURE goes green, the first of three readiness reds (this entry).** A WIRING / trajectory move per VL-017a, not a new capability: signing was built and evaluated at VL-040 (issuer signing), VL-041 (expiry), and VL-042 (key record / revocation); VL-047 puts the already-built signing capability on `pep.py`'s DEFAULT forward, so the secure path is the only forward path. `IMPLEMENTATION/pep.py` gains a module-level `_get_signing_key()` provider (resolves a process-injected key then the `ELYON_SIGNING_KEY_HEX` + `ELYON_SIGNING_KEY_ID` env pair; `cryptography` imported lazily; the private key is never in the repo) and signs the envelope (`sign_envelope`) INSIDE the existing envelope-construction try/except, so a missing key FAILS CLOSED (`REF_PEP_FAIL_CLOSED`), never a downgrade to an unsigned forward (constraint i). The canary `test_unsigned_path_unchanged_forge_still_accepted` is RETIRED and renamed to `test_verifier_unsigned_mode_accepts_forge_non_default` (the verifier's unsigned mode legitimately remains for the enforcement / A1-bypass demos; it is just no longer the gate's default path). New `TESTS/conftest.py` autouse `gate_signing` fixture injects an ephemeral Ed25519 keypair into the provider (private key in-process only); `TESTS/test_pep.py` gains `test_default_path_is_signed_and_forge_refused` (the canary's replacement AND the `issuer_signing.wired_to_default` proof) + `test_default_forward_no_key_fails_closed` (constraint i); `TESTS/readiness/test_deployment_predicates.py` drops the DEFAULT_SECURE xfail and wires ANCHOR 1 (a real regression gate). `EVIDENCE/readiness.json`: `issuer_signing.wired_to_default` -> true + `DEFAULT_SECURE.green` -> true with a cross-host-excluded scope note in `blocked_by` (cross-host transport is END_TO_END_NO_SHORTCUT / G5, NOT asserted here); `validate_manifest` clean; summary now 1 of 3 green. `EVIDENCE/proofs/default_secure_cutover_001_runner.py` is the single-process evidence (default forward signs / co-located key-pinning target honors the signed envelope and refuses the unsigned forge / no-key gate fails closed; exit 0). Canon 8.2/9/11.9; no new invariant; section 14 holds (signing proves issuance, not actor identity). NO follow-up evaluate (no new world-claim; signing's claim-track gate already ran at VL-040 follow-up 2). pytest 196 + 3 xfailed -> 199 + 2 xfailed (real env; the DEFAULT_SECURE xfail becomes a real pass, +3 new tests, -1 retired canary). Spec commit `82648dd` precedes build commit `56fd4f1`; this STATE + ledger commit does not cite its own hash (VL-012). **Honest frame: 1 of 3 green is the START of the road, not "secure"; the cutover closes forgery on what is now the only default path, but the decisive failure (root / issuer key compromise, recovery out-of-band) is unchanged, so "forgery-resistant" stays BOUNDED and out of any deposit.** Classification: trajectory / wiring move per VL-017a's distinction.

- **VL-039 T-G5-transport: cross-host transport of the published record; trust bootstrapped at one pinned anchor (commit `c964612`; post-VL-038 audit disposition at `15c53cb`).** `IMPLEMENTATION/published_source.py` (new): `anchor_sha256()`, `load_record_from_bytes(record_bytes, pinned_root)` (anchor-verify then parse; network-free; fail-closed on mismatch / parse / missing-pin), and `fetch_published_record()` (loopback transport, fail-closed on any transport error). A target on a separate process with a divergent local tree fetches the record over loopback, verifies it against a single pinned root anchor, and checks a delivered envelope's currency against the FETCHED record rather than local disk - correct verdict despite the divergent tree. `TESTS/adversarial/test_cross_host.py` + `EVIDENCE/proofs/g5_cross_host_001_runner.{py,md}`. No `pep.py` / canon / manifest / SPEC change. The post-VL-038 off-framework cross-model adversarial audit folds here (`15c53cb`): five confirmed findings pinned as green characterization tripwires in `TESTS/adversarial/test_findings_001.py` (each pins current behavior, so closing any gap must break its test); audit process at `docs/methodology/cross_model_adversarial_audit.md`. Trust is reduced to one pinned anchor, NOT eliminated; freshness is load-bearing (VL-039 follow-up: Decision G evaluate PARTIAL; VL-039 follow-up 2: the envelope is tamper-evident, not forgery-resistant - the finding signing closed at VL-040). Classification: trajectory move per VL-017a's distinction.

- **VL-048 T-end-to-end: the signed cross-host chain; END_TO_END_NO_SHORTCUT goes green (2 of 3) (spec `2b48336` + build `a89c9b1`).** `EVIDENCE/proofs/g5_signed_cross_host_001_runner.py` composes VL-047 default-path signing with VL-039 transport: the gate signs via the production env-var key path (NOT the conftest in-process fixture), pushes, and a target subprocess with a byte-divergent `evaluator.py` fetches the published record over a real `http.server` socket and verifies signature + currency-from-record + binding; honors signed-valid despite the divergent disk, refuses keyless forge / tamper / anchor-fail / absent (exit 0). `IMPLEMENTATION/readiness.py::_consistency` narrowed to `END_TO_END_CAPABILITIES = (issuer_signing, enforcement_push)` (the `validate_manifest` honesty loop preserved over all capabilities); `TESTS/readiness/test_deployment_predicates.py::test_end_to_end_no_shortcut` drops xfail and wires ANCHOR 2. GR-2 (readiness is test-derived, never human-attested) formalized in `docs/MAINTENANCE_PROTOCOL.md`. Canon 8.2/9/11.9/13/14; no new invariant; `verify_envelope` logic unchanged; section 14 holds. NO follow-up evaluate. pytest 199 + 2 xfailed -> 200 + 1 xfailed. **2 of 3 green = the full signed chain runs over real transport with no shortcut, NOT 'deployed' (true multi-machine/TLS is the named G5 floor) and NOT A3b-freshness-closed; 'forgery-resistant' stays bounded and out of any deposit.** Classification: wiring / trajectory move per VL-017a's distinction.

- **VL-049 T-root-recovery-wire: planned root rotation consulted target-side over the signed cross-host chain; ROOT_RECOVERY goes green (3 of 3) (spec `52d3764` + build `7b0f258`).** The VL-044 rotation primitive is wired onto the VL-048 transport, consulted TARGET-SIDE on the live chain - the gate's default forward is unchanged (reading (A)). `EVIDENCE/proofs/root_recovery_cross_host_001_runner.py`: a target pinning ONLY R1 on a byte-divergent disk fetches published + root + key records over real sockets via the production fetch path, honors a gate-signed envelope vouched by the designated-active R2 with no re-pin, and refuses keyless-forge / revoked-root / retired-root / fetch-failure / stale (exit 0; KILLER PROPERTY holds: honored despite divergent disk while a local-disk verify would refuse). `IMPLEMENTATION/key_record_source.py::fetch_key_record` gains an additive `root_status_view=None` passthrough to the unchanged `load_key_record_from_bytes` (the only seam; default None = VL-042 byte-behavior; `verify_envelope` + validation logic byte-unchanged, constraint g). `readiness.py` `ROOT_RECOVERY_CAPABILITIES = (root_rotation, issuer_key_revocation)` + a `_consistency` ROOT_RECOVERY clause (green = those two `exercised_e2e` + `transported`, mirrors END_TO_END, NOT `wired_to_default` since the gate forward is unchanged); `test_root_recovery_wired` drops xfail (option alpha; the runner owns the no-shortcut transport). NO follow-up evaluate. pytest 200 + 1 xfailed -> 201 + 0 xfailed. **3 of 3 deployment predicates green - the finite road the readiness gate named is walked; NOT 'deployed' or 'secure' (out-of-band root/issuer COMPROMISE recovery and true multi-machine/TLS (G5) remain named floors; 'forgery-resistant' stays bounded (signed-path-under-uncompromised-root) and out of any deposit).** Classification: wiring / trajectory move per VL-017a's distinction.

- **VL-051 T-server-retire: `IMPLEMENTATION/server.py` retired; `pep.py` is the sole gate (this commit).** The parallel un-enveloped FastAPI gate (`/governed-call` calling `evaluate()` then forwarding with no envelope / signing / verifier) is removed by `git rm`. It was kept deliberately through VL-038+ (ledger VL-040 carry-forward, ~line 10409: "a parallel un-enveloped gate, named not retired"); retired post-3-of-3 because a second, weaker gate beside `pep.py` in `IMPLEMENTATION/` is the live-code ambiguity the readiness gate's premise argues against. Checkpoint B confirmed DELETE over deprecate: the G2 narrative in `docs/restructure/01_repository_structure.md` does not teach through server.py as a live contrast (line 152 names it only incidentally beside `pep.py`; line 165 is a presence annotation). Doc reconciliation: artifact 01 tree line removed, the G2-PENDING prose de-referenced (its separate G2-PENDING staleness left for a future T-prose-drift), the structural annotation flipped PRESENT -> RETIRED(VL-051); `README.md` tree line removed. No code-behavior / canon / manifest / SPEC / test change; nothing imports or tests server.py. pytest 201 + 0 xfailed unchanged. Classification: bookkeeping / trajectory move per VL-017a's distinction (a tracked-artifact delete owing an explicit ledger record; the VL-046 family).

- **VL-052 T-prose-bookkeeping-sweep: the Tier-1 honesty sweep (this commit).** One efficiency commit removing the highest-value record-debt. (1) The actively-false claim in `docs/restructure/01_repository_structure.md` that `SPEC/request_schema.md` is PENDING / "does not exist in any form" is corrected to PRESENT / RESOLVED-at-G2 (the schema exists, the validator is `IMPLEMENTATION/request_validator.py` (VL-018), wired into `pep.py` at VL-019); both the reconciliation bullet and the downstream "Pending under the honest-base track" item 3 moved so the two sites agree (closes VL-051 finding 1). (2) `docs/restructure/04_current_vs_claimed.md`: G1 flipped to RESOLVED (VL-052; README count-discipline verified on disk per VL-050 finding 3) with the priority-order line; G8 and G9 given NEAR-CLOSED status notes (executable runners supersede narration; the stability proof is archived non-current) with no proof rewrite. (3) STATE "Known open gaps" summary mirrored (G1 RESOLVED; G8/G9 near-closed). (4) STATE "Known items open but not scheduled" closure-prune: the candidate-GR-2 spec-defines-the-rename item removed (moot - GR-2 was formalized at VL-048 as the readiness rule); the `.gitignore` audit-candidate item KEPT (source read: the opener's "guard present" basis is the scratch guard, a different concern than that item's domain-directory collision audit, which has no citable closure - conservative bias per VL-033 T-cite-C). Carried finding: artifact 01's "Pending under the honest-base track" items 1 and 2 (maintenance-protocol artifact; EVIDENCE/proofs+archive) are also stale-landed but left out of scope - a future dedicated artifact-01 pass (Checkpoint A: not a G2-narrative rewrite). No code / canon / manifest / SPEC / test change; pytest 201 + 0 xfailed unchanged. No follow-up evaluate (no claim about the world). Classification: efficiency move per VL-017a's distinction.

- **VL-053 T-G11-manifest-source: the manifest-source asymmetry closed via path (b)-with-guard (this commit).** G11 (surfaced VL-012) is the split-source integrity verdict: `manifest_integrity_valid()` read the version from its passed `manifest` argument but the sha256 from the on-disk `MANIFEST/manifest.json` via `manifest_sha256()`, so a caller passing a manifest that diverged from disk could get a True verdict whose version came from the argument and whose sha came from a different file. Path (a) (hash the passed dict) was rejected at Checkpoint B because it changes the VALUE `manifest_sha256()` returns (file-bytes -> canonical-dict), rippling into the envelope's `manifest_sha256` field, `decision_sha256`, artifact 05's line-51 contract, and the literal manifest-SHA test pins. Path (b)-with-guard keeps the on-disk file as the single pinned source of truth and adds a fail-closed divergence guard (`manifest != load_manifest() -> False`, canon section 9) in `IMPLEMENTATION/evaluator.py::manifest_integrity_valid()`, leaving the `manifest_sha256` value unchanged so those stay true. Masked-bug check (Checkpoint B): the only divergent-manifest callers were the inline `TEST_MANIFEST`/`MUTABLE_MANIFEST` fixtures in `TESTS/test_concurrency.py` (which had been collecting masked-ELIGIBLE results since written; no production path diverges, `pep.py` uses `load_manifest()`); repointed to the on-disk manifest with the authorized/unauthorized contrast rebuilt on the on-disk `AR=[identity, role]` / `R=[session, request]` sets and `SHA` derived live. New canon-derived characterization test `test_manifest_integrity_rejects_divergent_manifest` (canon 9 + 11.9; fails on the old True, passes on the guard's False; no literal hash, constraint i). Spec commit (artifact 06 8.1/11.9 rows) precedes the build commit (evaluator.py guard + the characterization test + the test_concurrency repoint + the live-regenerated `EVIDENCE/published_hashes.json`); artifact 04 G11 -> RESOLVED. Editing evaluator.py rolled `evaluator_sha256` forward in the published record (regenerated via `EVIDENCE/published_hashes_gen.py`; the canon-12.4 consequence of any evaluator change; `canon_sha256` / `manifest_sha256` byte-identical), so the build commit stays green. No canon/MANIFEST/SPEC change; the manifest bytes are unchanged. Classification: capability/correctness trajectory move per VL-017a. pytest 201 + 0 xfailed -> 202 + 0 xfailed. This STATE + ledger commit does not cite its own hash (VL-012).

- **VL-054 T-G14-unknown-key: the unknown-key refusal code resolved; G14 closes completely (spec `a2c5d41` + build `5df3918`).** An unknown non-CCS key directly inside `interaction` was refused fail-closed but mislabeled `REF_SCHEMA_TYPE_MISMATCH` (the provisional VL-018 mapping - the key IS refused, only the reason was wrong). Option A adds a new `REF_SCHEMA_UNKNOWN_KEY` code that names the cause. Spec commit `a2c5d41` adds the "Unknown key inside `interaction`" rejected shape to `SPEC/request_schema.md`; build commit `5df3918` flips `IMPLEMENTATION/request_validator.py` step 4d to emit it (the single emission point; the step-5 type-check `REF_SCHEMA_TYPE_MISMATCH` returns and the `REF_SCHEMA_PARSE_ERROR` boundary are byte-unchanged), de-provisionalizes the validator docstring / validation-order / ordering-rationale references, updates the test scope-note, and adds the spec-derived reject case `unknown_key_inside_interaction`. No existing test pinned the provisional mapping (the VL-017 author left it deliberately untested), so the fix is additive: schema suite 27 -> 28, repo 202 -> 203 + 0 xfailed. No canon / MANIFEST / evaluator / envelope / pep change; no `published_hashes.json` roll (no hashed-file edit); no new invariant; section 14 holds. `docs/restructure/04_current_vs_claimed.md` G14 PARTIALLY ADDRESSED -> RESOLVED (the moot "(candidate GR-2)" label dropped; GR-2 was formalized at VL-048). Lower-severity than G11: vocabulary honesty, no silent-wrong-answer. Classification: trajectory move per VL-017a's distinction. This STATE + ledger commit does not cite its own hash (VL-012).

- **VL-055 T-prose-drift: the prose tail of G11 (closed VL-053) cleared - the stale `reassert()` comment + the three literal-SHA pins (this entry).** A record-hygiene sweep, no behavior change. (1) `IMPLEMENTATION/envelope.py`'s `reassert()` Row-4 comment still described the manifest-source asymmetry as a LIVE flagged-open pattern ("flagged as G11 ... uses it as-is, matching the existing-pattern boundary"); rewritten to record the VL-053 closure (the divergence guard in `manifest_integrity_valid()`; `manifest_sha256()` hashes the on-disk `MANIFEST/manifest.json`, the single pinned source of truth, and Row 4 reads it as-is). Comment text only; no logic line touched (+180 bytes). (2) The three literal manifest-SHA pins named in VL-053 finding 5 - module-level `SHA = "a21dea8b..."` in `TESTS/test_adversarial_evaluator.py`, `TESTS/test_pep.py`, `TESTS/test_replay_receipts.py` - converted to live `SHA = manifest_sha256()` (with the `from IMPLEMENTATION.evaluator import manifest_sha256` import added where absent), mirroring `TESTS/test_concurrency.py` and `TESTS/adversarial/test_evaluator_canonical.py`. Behavior-preserving and value-identical (live `manifest_sha256()` == the old literal, confirmed before conversion - the Checkpoint B negative result), so no test flips; the pin is now constraint-(i) / GR-1-safe (survives a manifest-version event without a silent break). The flagged VL-029/047 module-docstring drift was read in full and found already current on disk (lines 42-46 correctly describe VL-029 wiring + VL-047 default forward); deferred, no edit. Two content commits (the comment fix cannot touch tests; the SHA-pin conversion must leave the count identical) + this STATE + ledger close. No gap-status transition (G11 already RESOLVED at VL-053); no canon / MANIFEST / SPEC / evaluator / `published_hashes.json` change (nothing here edits a hashed-file source, so no `evaluator_sha256` roll - contrast VL-053). Classification: efficiency / record-hardening per VL-017a's distinction; no follow-up evaluate. pytest 203 + 0 xfailed unchanged.
- **VL-056 T-cross-signer-phrasing: the within-record-vs-cross-signer split verified clean on disk; no spec edit (this entry).** The last Tier-1 spec item resolved as VERIFY-CLEAN (fork b). The VL-053/VL-054 next-action lines still listing `11_root_record_spec.md` section 6.3 as owing a cross-signer-phrasing tighten were stale forward-references from the pre-VL-045 backlog; VL-045's "verified clean" holds on a fresh source-first read. Every prose site draws the within-record-vs-cross-signer split exactly as `IMPLEMENTATION/root_record_source.py` does: the loader fail-closes the WITHIN-record analog (a duplicate `root_key_id` in one record's `roots[]` -> `REF_VERIFY_ROOT_RECORD_INVALID`, the `seen_ids` step performed before the view build), while CROSS-signer conflict (two roots' contradictory records) is a NAMED OUT-OF-BAND hazard resolved by re-pin, NOT a loader function. Sites confirmed clean: artifact 11 section 6.3 (heading + body), section 7 step 6, section 9 reject code, section 12 test list, section 14 properties; artifact 09 (no cross-signer language - correct, cross-signer is a root-record concept; its loader step list claims no within-record duplicate-key guard, matching the key reader); STATE's VL-044 / VL-044-follow-up / VL-045 bullets; artifact 04 / README clean on the grep. Checkpoint B clean (no code-vs-spec defect; the loader fail-closes the within-record analog and the spec claims no cross-signer resolution). Out-of-scope observation named not chased: `key_record_source.py` has no duplicate-`key_id` `seen_ids` guard (artifact 09 does not claim one; benign asymmetry, not a gap). NO follow-up evaluate (the transitive-designation evaluate ran SOUND 3-0 at VL-044 follow-up; VL-056 only confirms the description matches the code). STATE + ledger only; no `11`/`09`/`04`/`README`/code/canon/MANIFEST/`published_*` change. pytest 203 + 0 xfailed unchanged. Classification: methodology / verify-clean entry per VL-017a. Does not cite its own hash (VL-012).
- **VL-057 T-referent-binding: external-verification-readiness artifact landed; cross-model convergence demoted from evidence to framing stress-test (this entry).** New artifact `docs/methodology/external_verification_readiness.md` states the referent-bound criterion for outside HUMAN verification (an attackable real-transport deployment + a falsifiable claim sheet + a stake-free rebuild referent + a blind reviewer; NOT polished docs) and records the honest current verdict: NOT READY, the binding reason being referent quality (loopback transport, no rebuild referent), not documentation - the G5 real-transport floor is the load-bearing gate. The insight behind it: when the artifact, its framing, and the evaluate prompt share one build surface, cross-model judgments of soundness/value measure framing, not the world; convergence is correlated error, not independence. This entry DEMOTES the prior convergence verdicts (VL-023 f/u, VL-040 f/u 2, VL-042 f/u, VL-044 f/u, this session's comparative evaluate) from evidence to framing stress-test; the referent-bound results (tests, runners, pytest, readiness predicates) are untouched. Forward teeth - Lesson 10 + GR-3 - named as companions DEFERRED to a VL-057 follow-up (live-disk anchors). No code/canon/MANIFEST/SPEC/published_* change; pytest 203 + 0 xfailed unchanged. Classification: governance / methodology-rule per VL-017a. Does not cite its own hash (VL-012).
- **VL-057 follow-up: the forward teeth landed - Lesson 10 + GR-3 (this entry; teeth in commit 14291d9, this STATE + ledger repair after the four-file script aborted mid-apply on a false-positive guard).** The referent-binding rule the VL-057 artifact commit recorded-but-deferred is now ENFORCED forward. `docs/methodology/session_mechanics_lessons.md` gained Lesson 10 (model judgments of value are not evidence when artifact and evaluate prompt share one build surface; convergence is correlated error, not independence; contamination is upstream of procedure; a model claim is evidence only when bound to a referent - execution or adversarial-by-construction - the framing cannot move; lesson count 9 -> 10). `docs/MAINTENANCE_PROTOCOL.md` gained GR-3 (evidence is referent-bound; no model evaluative judgment is evidence or may move a claim; cross-model runs only as adversarial break-it or explicitly-labeled framing stress-tests; the evaluate-side analog of GR-2; ACTIVE, originating VL-057). A future opener proposing a soundness/value evaluate is now caught by GR-3, not by memory. Named-not-chased: GR-2's honest-ceiling bullet is stale post-VL-049 (ROOT_RECOVERY green, 3 of 3); a GR-2 amendment-entry deferred. No code/canon/MANIFEST/SPEC/published_* change; pytest 203 + 0 xfailed unchanged. Classification: governance / methodology per VL-017a. Cites 14291d9 + b1330cd; does not cite its own hash (VL-012).
- **VL-057 second follow-up: demotion completed - the 5 missed convergence verdicts demoted (this entry).** VL-057 demoted 4 verdicts; a pre-push grep found 5 more that used cross-model convergence as confirmation of soundness/value and were missed: VL-025 follow-up, VL-031, VL-036, VL-039 follow-up, VL-040 follow-up 1. All 5 demoted from evidence to framing stress-test, completing the set to 9. Principle restated as the core: the referent for soundness/value comes from OUTSIDE the authored loop (external attack on a live surface; a stake-free rebuild), never from the IDE, the tests, the canon, or another model reading the framing. Precision so the rule is not over-broad: execution facts (any source, including IDE-authored tests) CHARACTERIZE behavior - given input X, output Y - and survive; they simply do not certify `secure`/`sound`/`valuable`, because the attacks a test checks are the ones the author thought of. Two bounding notes: (a) downstream citations of any demoted verdict inherit the demotion (named, not chased); (b) VL-008 is bounded by GR-3 - a procedural-cleanliness check, never sufficient to make an evaluative verdict evidence (the prior-exposure clause was the seam the contamination slipped through). Product framing: dev + dev-side verification done; the cross-model evaluates were dev reviewing dev's own work mislabeled as QA; real QA = external validation is blocked on the G5 real-transport build (a loopback simulation is not a QA-able product). NOT demoted by scope: VL-039 follow-up 2, VL-024. No code/canon/MANIFEST/SPEC/published_* change; pytest 203 + 0 xfailed unchanged. Classification: governance / methodology per VL-017a. Cites VL-057 b1330cd; does not cite its own hash (VL-012).
- **VL-058 T-G5-transport: the G5 real-transport design artifact (12) landed plus the first build increment - the transport-config seam (this entry).** `docs/restructure/12_g5_transport_design.md` is the G5 build plan: it separates the two finish lines - (A) a G5-ready build (real cross-host TLS + a real downstream policy + an attack harness; fully buildable by author+model) and (B) G5 closed (the predicate green because the system WITHSTOOD attack on a real surface run by an EXTERNAL attacker; not promptable, GR-3 catches in-loop self-QA) - states the build order steps 1-5 grounded in code on disk (the two HTTP clients, the gate push and the record fetch, are already real; the two servers, an enforcing target and a record publisher, exist only as runner/test scaffolding; `IMPLEMENTATION/target.py` is an 8-line stub), and carries a verified env-capability note from a spike (real TLS between distinct OS processes with fail-closed cert verification; docker NOT available in the build sandbox; single host, so step 2's compose is a deploy-target artifact, not greened in-env). `IMPLEMENTATION/transport.py` is the step-1 transport-config seam: `post_to_target` / `get_published` resolve the TLS `verify` policy + an optional client cert from args or the `ELYON_TLS_*` env (out-of-band, never in repo), fail-closed by default; the load-bearing property is that with no args/env the default request is BYTE-IDENTICAL to the current direct `requests.post` / `requests.get` calls, so a later wiring step changes `pep.py` / `published_source.py` without changing default behavior. Build-then-wire (VL-025 / VL-037 precedent): the seam has NO callers; `pep.py` and `published_source.py` are byte-unchanged. Proven referent-bound by `EVIDENCE/proofs/g5_transport_seam_001_runner.py` (real TLS between distinct OS processes, no monkeypatch - contrast the VL-048 runner's `fake_post`; byte-identical default resolution + push (header + body intact) + fetch (record bytes intact) + fail-closed `SSLError` on an untrusted self-signed peer; 7/7, exit 0). G5 stays OPEN (the seam is build-then-wire with no caller; capability unchanged until wired); GR-3 bounds any in-loop attack to characterization, never certification, and `external_verification_readiness.md` keeps the (B) gate as the G5 real-transport floor. No canon / MANIFEST / SPEC / published_* change; no `evaluator_sha256` roll; no `readiness.json` change; no new invariant (canon section 14); NO follow-up evaluate (GR-3). The reserved deposit-readiness audit renumbers VL-058 -> VL-059. pytest 203 + 0 xfailed unchanged. Cites design `37f9ab7` + build `7894c5d`; does not cite its own hash (VL-012).
- **VL-058 follow-up: Lesson 11 promoted - Cowork-mount file + git mechanics (this entry).** `docs/methodology/session_mechanics_lessons.md` gains Lesson 11: write tracked repo files LF from the Linux side (not the Cowork desktop Write/Edit tools, which emit CRLF on Windows - the VL-058 artifact-12 phantom-modified, resolved by `git checkout --`); and do not drive git over the sandbox mount (it cannot unlink, so locks/temp leak and the index can corrupt - the VL-058 unlink-EPERM, recovered by `git read-tree HEAD`). If git must run over the mount: rename-not-unlink lock clear + read-tree repair + explicit-path staging. Lesson count 10 -> 11. Efficiency move per VL-017a; no code/canon/test/spec change; pytest 203 + 0 xfailed unchanged. Cites VL-058 chain (37f9ab7 / 7894c5d / 31da5ec); does not cite its own hash (VL-012).
- **VL-060 T-G5-transport-wire: the transport seam wired onto the default path; step 1b done; byte-identical (this entry).** `IMPLEMENTATION/pep.py`'s ELIGIBLE upstream forward now calls `post_to_target(...)` and `IMPLEMENTATION/published_source.py`'s record fetch calls `get_published(...)` (the VL-058 seam), each with DEFAULT args, so the request issued on the wire is byte-identical to the prior direct `requests.post` / `requests.get` (the seam defaults to verify=True, cert=None, timeout=10). The build-then-wire seam (VL-058, no caller) now has its two callers; `pep.py` keeps `import requests` (the monkeypatch surface `pep.requests.post` that TESTS/ + EVIDENCE/proofs/ patch), `published_source.py` drops its now-unused `import requests`. 17 `fake_post(url, json, timeout, headers=None)` stubs (TESTS/test_pep.py x7, test_enforcement, test_findings_001 x2, test_deployment_predicates x3, and the four proof runners default_secure_cutover / g4_refused_bypass / g5_signed_cross_host / root_recovery) migrated to `(..., verify=None, cert=None)` per the VL-038 `headers`-kwarg precedent; the lone `_fake_post(*args, **kwargs)` in test_request_schema needed none. Byte-identity proven by no-change: pytest 203 + 0 xfailed UNCHANGED, and `g5_signed_cross_host_001_runner` + `root_recovery_cross_host_001_runner` (the named regression referents) + `g5_transport_seam_001_runner` all exit 0, killer property holds. G5 NOT resolved - single-host loopback/TLS only; cross-host + external attack is artifact 12 steps 2-5 / finish line (B), the author's to arrange (GR-3 bounds in-loop attack to characterization). No canon/MANIFEST/SPEC/published_*/readiness change; no evaluator_sha256 roll; no new invariant (section 14: transport is verification I/O); NO follow-up evaluate (GR-3). Classification: wiring / trajectory move per VL-017a. Cites build b814ca0; does not cite its own hash (VL-012).
- **VL-061 T-G5-transport: artifact 12 step 4 - the standalone reference enforcing target landed (this entry).** `IMPLEMENTATION/reference_target.py` supersedes the 8-line `target.py` stub: a deployable FastAPI service (`uvicorn IMPLEMENTATION.reference_target:app`) that resolves out-of-band config from the environment (target_url / publisher_url / pinned anchor / gate key-id + public-key-hex), reads the `X-Elyon-Sol-Envelope` header, fetches + anchor-verifies the published record via the production `fetch_published_record` over a real socket, and honors iff `verify_envelope` accepts against the FETCHED record AND the pinned gate signature verifies (the reference policy, NOT authored-to-pass; A1 closed by the target's own un-attested-call refusal; fail-closed when unconfigured). Promotes the `TARGET_DRIVER` + `_build_cross_host_target_app` / `build_enforcing_target_app` scaffolding into one service. Build-then-wire: no change to pep.py's default path or the target.py stub (no code importer). New `TESTS/adversarial/test_reference_target.py` 8/8 (full suite 203 -> 211); new `EVIDENCE/proofs/g5_reference_target_001_runner.py` (conftest-free, real publisher socket + real env-config + production signing path) ALL INVARIANTS HOLD; the four G5 regression runners exit 0. G5 stays OPEN (single-host loopback; real cross-host TLS is steps 2-3; (B) external attacker author-arranged). No canon/MANIFEST/SPEC/published_*/readiness change; no new invariant (section 14). Cites the artifact-12 design (37f9ab7); does not cite its own hash (VL-012).
- **VL-062 evidence/publication: external-interception evidence committed; Zenodo addendum -> Revision 3 (this entry).** `EVIDENCE/proofs/external_interception_webhook_001_runner.py` (+ `.log` / `.md`) promotes the addendum Section-2 interception run to a committed, reproducible artifact: 204 calls at c756f8f against the webhook.site third-party receiver - 102 REFUSE -> 403 -> 0 external POSTs and 102 ELIGIBLE -> 200 -> 102 external POSTs (inbox 155 -> 257), 0 unexpected; gate-signed forwards (VL-047). `docs/zenodo/enforcement_evidence_addendum_rev3.md` records the Rev. 3 publication (supersedes Rev. 2 / VL-030): snapshot c756f8f, suite 211, the built-since-Rev-2 capabilities, and an explicit honest-scope section (third-party observation, author-driven, loopback transport - NOT an external pen-test; finish line (B) open per GR-3 / external_verification_readiness.md). No code/canon/SPEC/published_*/readiness change; no new invariant; pytest 211 unchanged.
- **VL-063 T-G5-transport: multi-process + real-TLS chain (artifact 12 steps 2-3, in-env) (this entry).** Gate, reference target, and a new standing publisher (`IMPLEMENTATION/publisher.py`) run as three separate OS processes over real TLS (local test CA); gate->target and target->publisher are CA-verified real sockets via the VL-058/060 seam (`ELYON_TLS_CA_BUNDLE`). `reference_target` gains a read-only `/received` endpoint (observability; not policy). `EVIDENCE/proofs/g5_multiprocess_tls_001_runner.py` proves honor over the real gate->target->publisher chain (target acts exactly once) plus forge / replay / target_url-swap / absent-envelope direct-to-target refusals, exit 0. Pytest `test_publisher.py` (2) + a `/received` test; suite 211 -> 214. No canon/MANIFEST/SPEC/published_*/readiness change; no new invariant (section 14). G5 stays OPEN (single host; docker-compose / two-VM / real-CA are deploy artifacts; finish line (B) external-attacker author-arranged). Cites the VL-063 build files; does not cite its own hash (VL-012).
- **VL-064 governance/relicense: MIT -> proprietary (this entry).** The repository `LICENSE` was replaced (MIT -> proprietary, all rights reserved; commit 47926cf) and the README rights section updated. Rationale: the MIT grant let anyone use/modify/SELL the code; this repo and all future releases are now proprietary. Honest history: prior public MIT releases remain MIT for those released copies (irrevocable for distributed copies); this file governs the repo + subsequent releases. `Elyon-Sol` trademark pending. Per-file headers deliberately omitted - adding one to the hashed `evaluator.py` would roll `evaluator_sha256` and break the published-record anchor + suite; the root `LICENSE` covers the repo without touching a hashed file. No code/canon/SPEC/published_*/readiness change; no new invariant; pytest 214 unchanged. Trajectory unchanged (artifact 12 step 5).
- **VL-065 T-G5-continuity: decision freshness - A3b sub-case (a) closed (this entry).** The default ELIGIBLE forward (`pep.py`) now stamps a signed `not_after` (decision max-age; `ELYON_DECISION_MAX_AGE_SECONDS`, default 300s) and `verify_envelope` refuses a captured, validly-signed decision presented beyond it (step 1.5b). Canon-safe: verification-layer policy, no new CCS invariant, no `reassert()` change; `not_after` signed + excluded from `decision_sha256` (wire hash unchanged); `pep.py` not hashed (no `evaluator_sha256` roll / no published-record regen). New `TESTS/adversarial/test_decision_freshness.py` (2); `TESTS/test_pep.py` key-set migrated (+`not_after`). Suite 214 -> 216. Honest open: replay-within-window (needs nonce + stateful verifier), record freshness (A3b sub-case b), cross-host clock-skew. Cutover like VL-047.
- **VL-066 T-G5-continuity + wedge: replay/exactly-once closed; wedge demonstrated end-to-end (this entry).** The gate stamps a signed, hash-excluded `decision_id` on every default forward; new executor-layer `REF_VERIFY_REPLAY`; the reference enforcing target gains a TTL-bounded `decision_id` seen-set (pruned by `not_after`) refusing already-honored admissions (`verify_envelope` stays pure). `EVIDENCE/proofs/wedge_agent_toolcall_001_runner.py` shows on an MCP-shaped tool-call surface that a side-effecting tool fires ONLY when admitted and is refused on replay / un-attested / rebind / drift / stale (7/7, fired exactly once). Tests: replay + decision_id-signed; test_pep key-set +decision_id. Suite 216 -> 218. The falsifiable wedge claim - admitted + exactly-once + bound + drift-invalidated + fresh, executor-verified independently - now holds in-process end-to-end. Honest open: per-instance seen-set (multi-instance needs a shared cache); record freshness (A3b sub-case b); in-process demo (real MCP / latency / external attacker unproven). No new canon invariant; no hashed-file change.
- **VL-067 directive: road to external readiness committed (this entry).** `docs/restructure/13_road_to_external_readiness.md` orders all remaining LOCAL work to the external-start line: Phase A clean-base (target.py + server.py retirement, gap-tracker refresh, prose-drift, CI, deposit-readiness audit), Phase B wedge-hardening (record freshness A3b-b, clock-skew, shared-replay-cache seam, real MCP server, latency budget), Phase C external scaffolding (deploy packaging, real TLS/cert + bootstrap, attack harness + claim sheet, real-transport readiness predicate) - each with acceptance criteria + validation locus. Canon-blocked G12/G13 and the section-14 fork explicitly out of scope. Doc-only; suite 218 unchanged. Each item lands as its own VL increment.
- **VL-068 A1 (artifact 13): `target.py` stub retired (this entry).** The non-verifying downstream stub (superseded by `reference_target.py`, VL-061) is removed; no code importer (grep-clean). `README.md` + artifact-01 tree refs updated to `reference_target.py` + `publisher.py`; artifact-01 entry marked RETIRED. Suite 218 unchanged. First Phase-A item done.
- **VL-069 A2 (artifact 13): `server.py` retirement was already done at VL-051 - no action (this entry).** The directive (VL-067) and the prior Next-open-action listed A2 "retire `server.py`" as open, but `IMPLEMENTATION/server.py` has been absent since VL-051 (`10e5078`, `git rm`; `pep.py` the sole gate) - retired before the directive named it, carried in error from the stale "server.py retirement" T-bookkeeping note. Confirmed: absent from HEAD, no importer (grep-clean), `README.md` + artifact-01 references already reconciled at VL-051 (only residue a gitignored stale `.pyc`). Artifact 13 A2 annotated ALREADY DONE so a top-down session does not re-attempt it; Next-open-action advanced to A3. Suite 218 unchanged. A prose-drift correction (A4 class), surfaced early.
- **VL-070 directive: Cowork sandbox recovery folded into `docs/SESSION_PROTOCOL.md` (this entry).** A new "Environment / sandbox recovery" appendix (8 rules) codifies the VL-069 resume recovery so future sessions boot cleanly without re-deriving it: host-vs-sandbox truth, the file-delete grant for the no-unlink mount, ghost `index.lock`/ref handling, plumbing-commit around a wedged lock via a sandbox-local index, the stat-cache `touch`, the no-push-from-sandbox handoff, and restart-to-remount as prevention; a pointer is added to resume step 1. Tool-specific appendix; the protocol body stays tool-agnostic (native checkouts skip it). Doc-only; suite 218 unchanged; Next open action unchanged (A3).
- **VL-071 A3 (artifact 13): gap-tracker refresh - artifact 04 G4/G5/A3b brought current to VL-061/063/065/066 (this entry).** `docs/restructure/04_current_vs_claimed.md` had been current only through VL-044 for G4 and G5 and carried no A3b-sub-case tracking. Per the directive's acceptance criterion (statuses match the ledger), it gains: a G4 VL-061/VL-063 increment (the deployable reference enforcing target closes A1 for any adopting target; VL-063 builds the real-TLS multi-process cross-host-transport precondition; both single-host fidelity, no external attacker, so G4 still not blanket RESOLVED); a G5 VL-061 (finish line A, step 4) + VL-063 (steps 2-3, single-host) increment, both still OPEN; and a new A3b continuity block - sub-case (a) decision freshness CLOSED (VL-065), replay/exactly-once CLOSED (VL-066; per-instance seen-set, multi-instance shared cache named-not-built), sub-case (b) record freshness OPEN (Phase-B B1). Each status transcribed from the named ledger entry read from disk. ASCII-safe; no code/canon/test change; suite 218 unchanged. Third Phase-A item done (A1 VL-068, A2 no-action VL-069); Next open action advances to A4. Build + close landed around a stale ghost `.git/index.lock` via plumbing per SESSION_PROTOCOL rules 3-5; push is the author's (rule 7). Does not cite its own hash (VL-012).
- **VL-072 A4 (artifact 13): STATE.md prose-drift cleared - the historical numbered list retired to a pointer; stale gap labels fixed; a pre-existing EOF truncation repaired (this entry).** The ~45-item historical "Next open action" build-track log (long-since-done increments, each trailing stale forward "Next:" guidance and the now-false "T-bookkeeping (G1/G8/G9/G11/G14)" label) is replaced by a pointer to `git log --oneline` + `EVIDENCE/verification_ledger.md` (the repo's stated provenance layers; the pointer option was chosen). The stale "bookkeeping batch" bullet (G1/G8/G9 + G11) in "What is locked vs. open" is corrected to record G1/G11/G14 RESOLVED (VL-052/053/054) and G8/G9 NEAR-CLOSED. A pre-existing mid-sentence EOF truncation (the committed file ended at "- **G12** - canon section 11.1 u", verified identical across the HEAD git blob and the mount, 204192 bytes) is repaired: the full G12/G13 "Known open gaps" bullets are restored and the missing G14 bullet added, sourced from artifact 04. Doc-only; suite 218 unchanged; Next open action advances to A5 (CI; locus AUTHOR). All edits done in-sandbox from the committed blob via plumbing (the VL-071 mount-truncation lesson). Does not cite its own hash (VL-012).
- **VL-073 A5 (artifact 13): CI wired; the g4 runner the gate surfaced repaired (this entry).** `.github/workflows/ci.yml` runs `python -m pytest TESTS/` + every exit-coded EVIDENCE/proofs runner on push/PR (PYTHONPATH=repo root; `cryptography==44.0.0` pinned; the non-hermetic `external_interception_webhook_001` excluded with reason). Prerequisite the CI surfaced and fixed: `g4_refused_bypass_001_runner.py` crashed standalone post-VL-047 (no signing key -> `REF_PEP_FAIL_CLOSED` before the forward; standalone runners skip `conftest.py`'s autouse key); an ephemeral gate key is injected (mirrors `default_secure_cutover`), and its stale committed `.log` regenerated to the current published record (89a30ffe..., matches the live evaluator). A probe disproved an earlier vacuous-pass worry: `pep.requests.post` and `transport.requests.post` are the same shared module object, so the patch is effective. Verified in-sandbox (Py 3.10): suite 218; 13/13 hermetic runners exit 0; webhook skipped. The workflow pins 3.13 (author env); the first real CI run (locus AUTHOR) is what closes the G8 CI residual. Doc/infra + evidence-runner repair; no code/canon/test-logic change. Does not cite its own hash (VL-012).
- **VL-073 follow-up A5: the first real CI run made green (this entry).** The CI run VL-073 enabled failed at `g5_multiprocess_tls_001_runner.py` (`SERVICES NOT READY`, exit 2) - its three uvicorn+TLS subprocesses missed the ~40s wait window on the slower GitHub runner, with stderr discarded. Hardened the runner (150s time-based readiness budget; early `poll()` dead-process detection; per-service stdout+stderr captured and dumped on failure; tz-aware `datetime.now(UTC)` replacing the deprecated `utcnow()`), and changed `.github/workflows/ci.yml` to run every hermetic runner and report all failures in one job (was stop-on-first, which hid any failures after the first). Verified in-sandbox (Py 3.10): suite 218; 13/13 hermetic runners pass under the new loop. The 3.13 CI run is the author's referent; G8's CI residual closes on the first green run. No code/canon/test-logic change. Does not cite its own hash (VL-012).
- **VL-073 follow-up 2 A5: de-flaked the concurrent-mutation test the second CI run surfaced (this entry).** `test_manifest_mutation_during_concurrent_evaluation` asserted `eligible==50` but a CI run got 48: under that runner's thread scheduling, 2 of 50 authorized tasks snapshotted the manifest AFTER the concurrent mutation and were correctly guard-refused (VL-053) - correct concurrent behaviour, an over-strict timing assumption the docstring already flagged. Replaced the `time.sleep(0.001)` race with a `threading.Event` (each task signals after snapshotting; the mutation waits for all 50), so the intended property (pre-mutation snapshots all ELIGIBLE) holds deterministically; the guard's REFUSE-on-post-mutation path stays covered by `test_manifest_integrity_rejects_divergent_manifest`. Assertions unchanged. Verified in-sandbox (Py 3.10): 60/60 standalone, suite 218 passed 8/8. No canon/evaluator/SPEC change. Does not cite its own hash (VL-012).
- **VL-073 follow-up 3 A5: green CI reached; the multi-process-TLS runner excluded from the gate (this entry).** The third CI run confirmed the suite passes and 12/13 hermetic runners pass (all cross-host runners included); only `g5_multiprocess_tls_001_runner.py` fails - the follow-up-1 diagnostics show three empty per-service logs and no process death, i.e. its three uvicorn+TLS OS-process servers start cleanly but are unreachable over loopback TLS within 150s on GitHub's hosted runner (an environment incompatibility, not a logic bug; not reproducible in the 3.10 sandbox, where it passes). Excluded from the CI gate with a documented reason, like the external webhook runner; it stays a local evidence runner (VL-063), and the cross-host evidence class remains CI-gated by g5_cross_host, g5_signed_cross_host, and root_recovery_cross_host (all pass in CI). CI now: suite 218 + 12 gated runners + 2 documented skips. The author's next CI run is expected green; that green run is what closes the G8 CI residual. Does not cite its own hash (VL-012).
- **VL-073 follow-up 4 A5: the green CI run confirmed; G8 CI-half closed (this entry).** The author confirmed the GitHub Actions run is GREEN at `c519f34` - suite 218 + the 12 gated hermetic runners, with the external-webhook and multi-process-TLS runners documented-excluded. That green run is the locus-AUTHOR referent A5 required, so A5 (wire CI) is complete and the CI half of G8's residual is closed (`docs/restructure/04_current_vs_claimed.md` G8 + the Known-open-gaps summary updated; the residual narrows to `STATE.md` auto-regenerability; G8 stays NEAR-CLOSED). Next open action unchanged: A6 (deposit-readiness audit VL-059). Does not cite its own hash (VL-012).

- **VL-059 A6 (artifact 13, Phase A): the deposit-readiness audit recorded (this entry).** `docs/methodology/deposit_readiness_audit.md` fills the long-reserved VL-059 slot (reserved at VL-058 when VL-058 renumbered from VL-057): the GR-3-bound classification of every claim into Section A deposit-ready (named referent each: suite 218/0 confirmed live in-sandbox + CI-green c519f34, the 12 hermetic runners, the 3 green deployment predicates, resolved gaps G0/G1/G2/G3/G7/G11/G14), Section B bounded (bound-in-the-same-breath; "forgery-resistant" held out of any deposit), Section C named-open (A1 declining-caller; the G5 real-transport floor + external attacker; A3b record freshness; G12/G13 canon halves; the G8 STATE.md auto-regen residual; the rebuild-cost ratio - no referent, model estimate non-evidential per GR-3), Section D forbidden framings (VL-057-demoted convergence verdicts; "whole canon realized"), plus an operational deposit gate. Honest ceiling: the audit constrains what may COUNT as deposit-ready; it produces no new referent, and the binding limit on the deposit surface stays the G5 real-transport floor (external_verification_readiness NOT READY). Phase A "clean the base" (A1-A6) is fully walked; next is Phase B / B1. No code/canon/SPEC/evaluator/MANIFEST/published_*/readiness/test change; pytest 218 + 0 xfailed unchanged (confirmed live in-sandbox at HEAD). Locus SANDBOX (analysis). Does not cite its own hash (VL-012).

- **VL-074 B1 (artifact 13, Phase B): record freshness - the signed published-record reader; A3b sub-case (b) closed in the reader (this entry).** Mirrors `key_record_source.py` as a sibling: new `IMPLEMENTATION/published_record_source.py` validates a publisher-signed published record (`format`/`version`/`publisher_key_id`/`serial`/`issued_at`/`not_after` + the three currency pins; signature over `canonical_json(record minus signature)`) and enforces freshness - `now < not_after` (strict) + monotonic `serial` - refusing a stale record with `REF_VERIFY_PUBLISHED_RECORD_STALE` (new code in `verifier.py`, mirroring the key/root-record codes) and a bad / unknown-key / unsigned one with `REF_VERIFY_PUBLISHED_RECORD_INVALID`. Signer `EVIDENCE/published_hashes_signed_gen.py` wraps the LIVE `published_hashes_gen.build_record` pins (constraint i) under a stable pinned publisher key (RUNTIME artifact, never committed, parity with the key record). Spec `docs/restructure/14_published_record_freshness_spec.md`. Build-then-wire: the byte-anchor reader `published_source.py`, the committed `EVIDENCE/published_hashes.json`, and `reassert()`/`verify_envelope()`/`reference_target`/`pep.py` are byte-unchanged (no `evaluator_sha256` roll), so the g4/g5 runners and pinned-anchor tests are unaffected; wiring the signed reader onto the default consult path is a later increment (parity with the VL-039 seam -> VL-060 wire). Acceptance (artifact 13 B1): `TESTS/adversarial/test_published_record_freshness.py` (10) - a stale record flips honored -> refused, with a contrast test pinning the byte-anchor model's absent freshness dimension. pytest 218 -> 228 + 0 xfailed (confirmed live in-sandbox). Honest open: cross-host clock-skew (B2, next); default-path wiring (named, not built). Classification: capability / trajectory move per VL-017a. Does not cite its own hash (VL-012).

## What is locked vs. open

- **Locked:** canon v0.9.8.4. Corrected only by version increment, never by
  in-place edit (governance rule GR-1, ledger VL-007).
- **Open:** the honest-base track is complete, the disambiguation pass
  (G0/G6/G10) is complete, and the G0 build track is underway with
  the first artifact (SPEC/request_schema.md) drafted (VL-014),
  cross-model-verified (VL-015), and corrected (VL-016). Known
  items recorded but not yet scheduled:
    - VL-009 ASCII-safe standard is violated by pre-existing content
      in the three `EVIDENCE/archive/` files (VL-011 process finding);
      resolution deferred to a follow-up decision (normalize / preserve
      verbatim / repo-wide pass).
    - The former bookkeeping batch is discharged: G1 (VL-052), G11
      (VL-053), and G14 (VL-054) are RESOLVED; G8 and G9 are NEAR-CLOSED
      (VL-052: executable runners supersede the narrated proofs; the
      stability proof is archived non-current); the CI residual is the
      A5 item. G2 has its own closed track (VL-014..VL-019). See
      `docs/restructure/04_current_vs_claimed.md`.
    - G12 and G13 (the canon-layer halves) remain open; both
      require canon-version events under GR-1 to fully resolve.
      Not currently scheduled.
    - Latent VL-009 inconsistency: `IMPLEMENTATION/replay/receipt.py`'s
      `canonical_json` uses `ensure_ascii=False` (VL-012 process
      finding); not a current problem (no receipt currently contains
      non-ASCII bytes) but warrants documentation if scope-creep into
      a follow-up is desired.
    - VL-015 and VL-016 process findings on verification-request
      artifact durability: `verification_request_vl014.md` and
      `verification_request_vl016_premises.md` both prepared in
      chat and used directly without committing. The candidate
      action (commit a generalized verification-request template
      to `docs/`) is reinforced by the second instance but not
      actioned.
    - VL-016 process finding on premise-testing as a distinct
      verification shape (versus artifact verification). Worth
      naming in a methodology-artifact addition; not actioned.

---

## Next open action

**GOVERNANCE TRACK (opened VL-113, 2026-06-17) - turn the admission gate into a governance substrate per `docs/design/governance_layer_design.md` (corrected: the uploaded design + the 8 review fixes H1-H8).** A new capability trajectory, parallel to the G5 external-readiness road below (which is unchanged). Feature 1 (human oversight / PENDING_APPROVAL) is built in increments ABOVE G(I); canon stays locked (GR-1). DONE: increment 1a (VL-113 - impact classification: IMPLEMENTATION/impact.py, fixes H1+H2, suite 429, 3 revert-catchers RED) and 1b (VL-114 - IMPLEMENTATION/approval.py: build/sign/verify the approval grant; fixes H3 mandatory grant_id, H4 bind decision_sha256 + approval_request_id, H5 SoD belt-and-braces, H7 freshness via the factored-out verifier.not_after_valid; build-then-wire/unwired, suite 443, 5 revert-catchers RED) and 1c (VL-115 - the pep approval WIRING: manifest HIGH_IMPACT: [] + published_hashes regen; the 202 PENDING_APPROVAL state machine [H6]; gate-side pending-request set [H4] + grant single-use via the ReplayCache seam claimed before forward [H3]; approver public-key trust + SoD [H5]; REF_APPROVAL_* as 202/403; FIRST default-path touch + first stateful gate; default path byte-unchanged, suite 452, core revert-catcher RED) and 1d (VL-116 - the AUDIT half [H8]: JsonlApprovalLog + reconcile_approvals (FORWARDED_WITHOUT_GRANT predicate) + approver_cli.py; default-off, suite 461, predicate proven RED). FEATURE 1 MECHANISM COMPLETE (1a-1d). NEXT: Feature 2 increment 2a (mTLS client-auth proof) is DONE (VL-117). Remaining to a claimable oversight guarantee: the INTEGRATION proof (design 3.3) is DONE (VL-118 - the two features compose, exit 0). What remains is NOT new in-repo capability - it is the path to a DEPLOYABLE, claimable oversight guarantee: (i) OPERATOR-LOCUS Feature-2 layers 1 (Envoy with_request_body inline body binding) + 3 (network ACL + agent egress) on real hosts (deploy/NONBYPASS_TOPOLOGY.md); (ii) Feature 1 residuals: R1 ([H5] approver provenance/role via the signed key-record chain) is DONE (VL-119 - IMPLEMENTATION/approver_trust.py resolve_approver_keys enforces SoD as role-distinctness in the signed record; suite 481; pep/approval byte-identical); R2 ([H3]/[H4] shared store for single-use + the pending-set under horizontal scale) is DONE (VL-120 - IMPLEMENTATION/pending_store.py + pep wires _PENDING/_GRANT_REPLAY through the *_from_env builders with the R-02 declare-or-fail guard; suite 499; G(I)/canon/manifest byte-identical, pep default byte-behavior-unchanged). The in-repo governance-substrate build is COMPLETE (Feature 1 mechanism 1a-1d + R1 + R2; Feature 2 mTLS 2a; integration proof); the REMAINING path to a claimable oversight guarantee is OPERATOR-LOCUS only - wire the shared store (Redis) and Feature-2 layers 1+3 on real hosts. Only inside a deployment wiring all three Feature-2 layers, with R1 AND R2, does the oversight guarantee become claimable; no readiness predicate goes green until then. The governance-substrate BUILD (Feature 1 mechanism 1a-1d + Feature 2 mTLS layer 2a + the integration proof) is in-repo complete. Residual R1 ([FIX H5] load-bearing) is DONE (VL-119) - approver-key provenance + an explicit approver ROLE via the signed key-record / root-record chain, enforced as role-distinctness in the signed record (the gate already holds only public approver keys; this hardens WHERE that trust comes from). Residual R2 ([FIX H3]/[FIX H4] under scale) - a SHARED store (ExternalStoreReplayCache + a shared pending-set) so single-use and the 202 slot hold across instances; reuse replay_cache_from_env's R-02 declare-or-fail guard. Then Feature 2 (non-bypassable: inline body-bound sidecar + mTLS client-auth + egress topology + the network-layer bypass-refused proof) and the integration proof. The oversight GUARANTEE is NOT claimed and no readiness predicate goes green until Feature 2 lands. Then Feature 2 (non-bypassable) + the integration proof. Do NOT claim the oversight guarantee until Feature 2 lands; no readiness predicate goes green on Feature 1 alone.

**DERIVATIVE TRACK (added VL-104) - OPA ext-authz sidecar: built + in-container green; next is AUTHOR validation.** The in-house sidecar (IMPLEMENTATION/authz_sidecar.py + TESTS/adversarial/test_authz_sidecar.py + the deploy/ Mode A example) is shipped build-then-wire (suite 372 -> 387; no existing default path changed). It now also runs under real TLS (VL-105: hermetic + real-loopback-TLS in-sandbox referents + a two-VM manual runbook `deploy/elyon-authz/VM_TLS_TEST.md`). Its next steps, both AUTHOR-locus: (1) run VM_TLS_TEST.md on the two VMs (real cross-host TLS) and/or validate the container stand-up + `envoy --mode validate -c deploy/envoy.example.yaml`; (2) bring it to a first OPA-shop design partner. The named next in-house sidecar increment is build-order step 4 (the declarative CUSTOM interaction-mapping format for gate-less deployments; OUT of VL-104 scope per the kickoff). This track is upstream-of-OPA integration BREADTH; it is NOT a G5 referent and does not change G5's status - the road item below is unchanged.


**NEXT (updated at VL-103 close, 2026-06-10) - execute artifact 29 (the G5 execution plan); AUTHOR locus.** The path is now one followable procedure: docs/restructure/29_external_validation_execution_plan.md. Phase 1 (public surface bring-up - two real hosts, real DNS, real CA, author self-test green, REAL_TRANSPORT flipped) and Phase 3.2 (the stake-free rebuild estimator) can start in parallel and are independent of each other; Phase 2 (briefing pack) depends on Phase 1's live URLs; Phase 3.1 (blind attacker) depends on 1+2; Phases 4-5 are the engagement and its ledgering. All of it is deployment-and-people, not in-house code. G5 stays NOT-MET until Phase 5 produces a real referent (a recorded break, or a scope-and-window-bounded clean run). In-house backlog is the standing non-blocking process-finding list below.

**Forks locked at VL-107 (2026-06-16).** Hosts: Hetzner CX22 (host A, gate) + DigitalOcean (host B, target/publisher/sidecar) - two providers, different networks (pricing re-verified at execution time; Hetzner + Oracle-Free is the cheaper alternative). Recruiting (Phase 3.1): a private, time-boxed bug-bounty platform listing (specific platform TBD). Reward: a small bounty pool, per severity/novelty, plus credit (per-tier amounts TBD). Counsel: the BREAK_IT.md safe-harbor / authorization clause is a HARD GATE - the one-pager does not go public until counsel signs it. The recruiting pack (BREAK_IT / HOW_TO_INTERACT / RED_TEAM_BRIEFING / RED_TEAM_OUTREACH) is now consistency-clean and publish-ready pending those decisions + counsel. The author's next concrete step is the live bring-up per deploy/LIVE_BRINGUP_RUNBOOK.md + deploy/G5_GO_LIVE.md: provision the two hosts, set the four DNS A-records, issue Let's Encrypt certs, bring the four nodes up under TLS, run the self-test GREEN over the public surface, then flip REAL_TRANSPORT naming the run log. In parallel: commission the Phase 3.2 rebuild estimator. (The host plan changed at execution: SINGLE carrier - four Hetzner DCs across two continents - rather than two providers; see VL-108.)

**DONE at VL-108 (2026-06-16): the public surface is LIVE and the author self-test is GREEN over it** (four Hetzner nodes under Let's Encrypt across two continents, signed freshness mode; attack_suite_live_runner 6/6 + positive control, exit 0; REAL_TRANSPORT upgraded to the public-surface log). The NEXT open action is the PRE-EXPOSURE checklist, then publish + recruit: (1) REGENERATE the publisher signing key (it was exposed in the working chat) and re-pin it on the target; (2) live-verify the authz sidecar (mint -> present ALLOW; forged -> DENY) - only DENY-on-junk is confirmed so far; (3) backfill the cert-renewal deploy-hook on gate + pub; (4) counsel sign-off on the BREAK_IT.md safe-harbor clause (deploy/SAFE_HARBOR_DRAFT.md) - HARD GATE before publish; (5) set bounty tiers + engagement window + reporting channel; (6) publish the decontaminated pack + open the private bug-bounty listing; (7) (parallel) commission the Phase 3.2 rebuild estimator. G5 stays NOT-MET until a blind external party engages the live surface.

**At VL-109 (2026-06-16): the Cursor white-box round's two real bugs (R-01, P-01) are fixed, tested (suite 394 green at the VL-109 commit; 399 after the follow-up-1..3 test hardening), committed (3343e32), and deployed to all four live nodes.** Added to the build backlog as named-open (none blocking the current single-process surface): B-01 (build-order step 4 - bind the sidecar to the upstream's executed body, not just the interaction header; until then do NOT front a body-carrying upstream, and say so in the attacker pack's sidecar scope), F-01 (wire signed-record freshness into the sidecar), R-02 (fail-closed guard when workers>1 without a shared replay store). The pre-exposure path is otherwise unchanged: counsel sign-off, bounty/window/channel, publish, recruit. G5 stays NOT-MET until a blind external party engages.


**The local road to external readiness is now a committed directive: `docs/restructure/13_road_to_external_readiness.md` (VL-067).** It orders all remaining in-house work into Phase A (clean the base), Phase B (harden the wedge), and Phase C (external-readiness scaffolding), each item with an acceptance criterion and validation locus. The wedge property holds in-process end-to-end (VL-066). Execute artifact 13 top-down. **A1 (retire `target.py`) is DONE (VL-068); A2 (retire `server.py`) needed NO ACTION - already retired at VL-051 (`10e5078`), before the directive listed it (corrected VL-069; artifact-13 A2 annotated ALREADY DONE); A3 (refresh the gap tracker) is DONE (VL-071 - `docs/restructure/04_current_vs_claimed.md` G4/G5 and a new A3b continuity block brought current to VL-061/063/065/066); A4 (clear the prose-drift) is DONE (VL-072 - the ~45-item historical numbered "Next open action" list retired to a `git log` + ledger pointer; the stale "T-bookkeeping (G1/G8/G9/G11/G14 ...)" / "bookkeeping batch" labels fixed, G1/G11/G14 RESOLVED; and a pre-existing EOF truncation of the G12/G13 "Known open gaps" bullets repaired); A5 (wire CI) is DONE (VL-073 - `.github/workflows/ci.yml` runs the suite + the hermetic EVIDENCE runners on push/PR (the external-webhook and multi-process-TLS runners excluded as CI-incompatible, the cross-host class still gated by three other runners); the g4 runner repaired; CONFIRMED GREEN on GitHub Actions at `c519f34` (VL-073 follow-ups 1-3), closing the CI half of the G8 residual).** A6 (deposit-readiness audit) is DONE (VL-059 - `docs/methodology/deposit_readiness_audit.md` records the GR-3-bound classification of every claim into deposit-ready / bounded / named-open with an operational deposit gate, so no overclaim enters a deposit; Phase A "clean the base" A1-A6 is now fully walked). B1 (record freshness, A3b sub-case b) is DONE (VL-074 - the signed published-record reader `IMPLEMENTATION/published_record_source.py` + signer `EVIDENCE/published_hashes_signed_gen.py` + spec `docs/restructure/14_published_record_freshness_spec.md`; a stale signed record is refused with `REF_VERIFY_PUBLISHED_RECORD_STALE`; build-then-wire, the byte-anchor default unchanged, suite 218 -> 228). B2 (cross-host clock-skew tolerance) is DONE (VL-075 - a configurable non-negative `clock_skew` window (timedelta, default 0) on the decision-freshness check (verifier `not_after`), the issuer-key validity window (symmetric `not_before`), and the three signed-record readers' record-level `not_after`; spec `docs/restructure/15_clock_skew_tolerance_spec.md`; build-then-wire, default 0 byte-behavior-identical, no hashed-file / default-path change, suite 228 -> 249). B3 (shared-replay-cache seam) is DONE (VL-076 - the seam `IMPLEMENTATION/replay_cache.py`: a `ReplayCache.check_and_claim` contract (True=honor / False=replay), an `InMemoryReplayCache` behavior-identical to the VL-066 inline `app.state.seen` dict, and an `ExternalStoreReplayCache` delegating the atomic claim to an injected shared `ReplayStore` (Redis `SET NX EX` / Memcached `add` / unique-key INSERT shape); spec `docs/restructure/16_shared_replay_cache_spec.md`; build-then-wire, the seam unwired and reference_target.py byte-unchanged, suite 249 -> 260). B4 (real MCP server) is DONE (VL-077 - `IMPLEMENTATION/mcp_server.py`, a JSON-RPC 2.0 MCP server over stdio: the `initialize` handshake + `tools/list` + `tools/call` with the production admissibility gate on tool execution, reusing `verify_envelope` + the VL-076 `ReplayCache` seam; the tool fires exactly once and un-attested / rebound / drifted / stale / replayed calls are refused unfired; spec `docs/restructure/17_mcp_server_spec.md`, real-stdio proof `EVIDENCE/proofs/mcp_server_001_runner.py` (subprocess, 11/11, exit 0), suite 260 -> 274; build-then-wire, no caller on the default pep.py path, byte-unchanged). B5 (latency budget + executor SDK) is DONE (VL-078 - `IMPLEMENTATION/executor_sdk.py`, the thin `ExecutorGate` factoring load+verify+replay into `check() -> Decision`, a few-line integration; harness `EVIDENCE/proofs/latency_budget_001_runner.py` measuring p50/p99 + throughput, INDICATIVE sandbox VERIFY p50 ~0.14 ms (author re-runs for the hardware budget of record); spec `docs/restructure/18_latency_budget_and_sdk_spec.md`; suite 274 -> 284; build-then-wire, no default-path caller, byte-unchanged). **Phase B is fully walked (B1-B5).** C3's SANDBOX scaffolding is DONE (VL-079 - the attack harness `EVIDENCE/proofs/attack_harness.py` + suite runner (8 gate-2 attacks defeated + positive control honored on the in-process surface, exit 0) and the falsifiable claim sheet `docs/methodology/falsifiable_claim_sheet.md`; the HttpSurface adapter is shape-tested against a real reference target, ready to run the SAME suite over real transport). The remaining Phase-C work is AUTHOR-locus (the sandbox has no docker / real CA / real hosts): C1 (deploy packaging) ARTIFACTS are authored (VL-081 - `deploy/` Dockerfile + docker-compose + bootstrap_config + runbook; the config bootstrap round-trips admit->verify in-sandbox, but the container stand-up is UNVALIDATED - no docker - and remains the author's), C2 (real TLS/cert + trust bootstrap) ARTIFACTS are authored (VL-082 - `deploy/tls/` gen_certs + the `docker-compose.tls.yml` overlay + the trust_bootstrap runbook; the cert material is validated in-sandbox by a real in-memory TLS handshake (verified / wrong-CA-refused), but a real two-host TLS run + a real CA are AUTHOR). **All in-house-authorable Phase-C artifacts (C1 packaging + C2 TLS) are now done; the remainder is pure AUTHOR execution on real hosts.** C3's LIVE run + C4 are STAGED (VL-083 - the AUTHOR-executed `EVIDENCE/proofs/attack_suite_live_runner.py` runs the VL-079 attack suite over real transport via HttpSurface, CI-excluded; and a RED `REAL_TRANSPORT` readiness predicate naming that run as its proof-to-be). **The entire in-house artifact-13 road is complete (A1-A6, B1-B5, C1-C4 scaffolding).** What remains is NOT authoring - it is the author's execution on real hardware: (1) stand up C1+C2 on two real hosts / cloud (real or dev CA); (2) run `attack_suite_live_runner.py` over that real TLS surface (configure the ELYON_LIVE_* env); (3) on a green run, flip the `REAL_TRANSPORT` predicate to green naming the run log (C4); (4) arrange a real EXTERNAL attacker on the surface - the only thing that certifies G5 (GR-3). Until step 4, the project stays NOT READY for an external-validation / production claim, by the project's own referent discipline (the four AUTHOR steps are enumerated above; VL-074..VL-083 record the completed in-house build, and `docs/restructure/04_current_vs_claimed.md` carries the G5 NOT-CLOSED status). Out of scope (not local code): G12/G13 canon-layer halves (canon-version event under GR-1); the section-14 caller-carry/proxy-removal fork (optional). Finish line **(B)** - an EXTERNAL attacker on a real surface - remains the author's to arrange and is the only thing that certifies G5 (GR-3). Standing, none blocking: A1 target-side policy (closed by the reference target). **VL-096 (three-domain synthetic POC) is a CHARACTERIZATION demonstration, not a road item: it shows the one unchanged chain admits/refuses domain-shaped inputs (medical/legal/finance) the way each domain's reviewer would expect - 39/39 in-process; live mode is the author's per `EVIDENCE/proofs/three_domain_poc/RUNBOOK_live.md`. It adds breadth of CONTENT, not a new validation; G5 remains the only open item.**

The build-track provenance that this section used to enumerate (a numbered log of every completed VL increment, G0/G2 schema work through the G4/G5/A3b track) is not duplicated here. The authoritative record of what has been done, in order, is `git log --oneline`; the record of how each claim became trusted is `EVIDENCE/verification_ledger.md` (VL-001..VL-071). This section now carries only the current next action (above). The standing process-finding backlog, which does not block trajectory work, follows.

Known items open but not scheduled (non-blocking; the entire artifact-13 build is done. The RECURRING process-finding patterns are now captured as Lessons 1-12 in `docs/methodology/session_mechanics_lessons.md` - chat-paste-eats-content, typographic drift, source-first, set-exhaustiveness, and environment-hermeticity (Lesson 12, VL-080 follow-up). What remains below is the residual INFRASTRUCTURAL backlog not covered by a lesson):
- VL-011 process finding on pre-existing non-ASCII bytes in
  `EVIDENCE/archive/` files.
- VL-012 latent inconsistency on `receipt.py` `canonical_json`.
- VL-013 commit 606ddc1 contains one incidental whitespace-only edit
  to `docs/restructure/05_admissibility_envelope_spec.md` (the line
  ending "Lock and envelope are mutually reinforcing -") introduced
  by terminal-paste reconstruction during the session. VL-013
  enumerates three semantic edits to artifact 05 but the commit
  contains four diff-level changes. Same family as VL-012's em-dash
  normalization in `manifest_integrity_001.md`. Acknowledged here
  rather than as a new ledger entry because the ledger documents
  verification claims, not cosmetic process artifacts. No action.
- VL-014 process finding: chat-pasted multi-line `git commit -m`
  blocks have now failed twice. Operational lesson recorded in
  the VL-014 entry; the VL-016 commit uses `git commit -F <file>`
  per the handoff's lesson #1.
- VL-017 process findings (eight session friction points; false
  stop signal on line count; ledger-entry blank-line stripping
  in VL-017a's committed text). The session-mechanics-lessons
  promotion candidate is now reinforced by a quantified
  threshold per VL-017's entry: if VL-018's session opens with
  three or more friction points in the first hour before
  substantive work begins, pause trajectory work and promote
  the session-mechanics-lessons file as that session's
  deliverable. The threshold is the first attempt in this
  project at making a process-finding candidate self-actuating
  rather than perpetually-deferred.
- VL-017 process finding: inherited-`.gitignore` pattern,
  second instance (after VL-010). The Python-template
  `.gitignore` hid `EVIDENCE/proofs/g2_schema_failing_tests_001.log`
  via the `*.log` rule at line 61; corrected with an explicit
  un-ignore `!EVIDENCE/proofs/*.log` landing in the same commit
  as the file it was hiding (structurally parallel to VL-010).
  Two instances is a pattern. Candidate action: a focused
  audit-commit of `.gitignore` against the repo's actual
  domain directories (`CANON/`, `MANIFEST/`, `EVIDENCE/`,
  `SPEC/`, `IMPLEMENTATION/`, `TESTS/`, `docs/`), adding
  explicit un-ignore rules or comments for every name that
  could collide with a template assumption. Efficiency move
  per VL-017a's classification; not blocking. Not actioned.
- VL-020 process finding: Lesson 3 fire pre-commit. The first
  draft of `apply_vl020.py` was written from inference about
  the apply-script template pattern, without viewing the
  actual template source. The template was uploaded
  mid-session; comparison surfaced eight structural
  divergences from the established pattern. The script was
  rewritten from scratch against the template; the rewritten
  script preserves the template's signature and calling
  convention. Did not materialize as committed divergence
  (caught pre-commit). Adding the VL-020 surface event to
  Lesson 3's "Surface events" subsection of
  `docs/methodology/session_mechanics_lessons.md` is deferred
  per VL-020's strict-scope discipline; the ledger entry's
  process findings hold the authoritative record until a
  future methodology-file update lands.
- VL-020 follow-up process finding: third instance of the
  chat-paste-eats-content failure mode (VL-012, VL-014,
  VL-016 follow-up are the prior instances; this is the
  third named in session-mechanics terms). VL-020's Step 8
  paste contained two comment-form action items (apply
  STATE.md edits; cat ledger entry) that were silently
  skipped at execution. The commit d81de1d landed with the
  three structural-edit files but without STATE.md or the
  ledger entry. Recovery via follow-up commit per VL-018 /
  VL-019 follow-up precedent (no history rewrite). The
  lessons in `docs/methodology/session_mechanics_lessons.md`
  on this failure mode (VL-016 follow-up lessons (a) and
  (b)) fired correctly when the divergence was diagnosed
  post-commit but did not prevent the divergence at execution
  time. Calibration finding: lessons currently structured as
  "don't paste multi-step blocks with comment-form action
  items" require Claude-side discipline in *generating* the
  Step 8 instructions; a complementary discipline (workflow
  steps that fail loud if skipped, not silently) would catch
  the case where the discipline is forgotten. Candidate
  methodology update: when generating multi-step recovery
  or workflow instructions, prefer apply-scripts (which
  exit nonzero on skip) over prose comments in pasted shell
  blocks. Not actioned in this commit per strict-scope.

---

## Known open gaps

See `docs/restructure/04_current_vs_claimed.md` for the full list. Summary:

- **G0** - CCS specification/implementation drift. **RESOLVED**
  (VL-012 + VL-029): rename half closed at VL-012 (function renamed;
  name "CCS" reserved in code and test IDs); build half closed at
  VL-029 (envelope.py `build_envelope()` + `reassert()` implement
  canonical CCS per artifact 05 + canon section 12; pep.py wires
  envelope emission on every ELIGIBLE response per artifact 05
  build-order step 5). The post-VL-026 ccs-derivation rule
  implemented in `reassert()`'s dict return per Decision A; 3 xfail
  markers in `test_ccs_canonical.py` xpassed and removed in the
  same commit.
- **G1** - README test count stale / no commit-pinned source of truth.
  **RESOLVED** (VL-052): `README.md` hardcodes no counts and pins `STATE.md` plus
  the latest `VL-NNN` ledger entry as the authoritative count for the current commit
  (VL-050 finding 3). See `docs/restructure/04_current_vs_claimed.md`.
- **G2** - request schema drift (interception proofs document a dead API).
  **RESOLVED** (VL-014 + VL-015 + VL-016 + VL-017 + VL-018 + VL-019):
  SPEC/request_schema.md names the rejected and accepting
  shapes at the schema layer (VL-014), has been
  cross-model-verified (VL-015), and the disputed interpretive
  loci have been corrected (VL-016). VL-017 added 27 failing
  schema-shape tests at
  `TESTS/adversarial/test_request_schema.py` per the schema's
  build-order step 2. VL-018 added the schema validator at
  `IMPLEMENTATION/request_validator.py` per step 3, emitting
  six refusal codes. VL-019 wired the validator into
  `IMPLEMENTATION/pep.py` per step 4, emitting the seventh
  refusal code (`REF_SCHEMA_PARSE_ERROR`) at the boundary;
  the 27 discriminating tests transition from uniform-422
  (VL-017) to per-code discrimination (27/27 passing). The
  artifact-04 update reflecting G2's RESOLVED status is
  deferred to a follow-up commit (paralleling VL-018's
  artifact-04-as-separate-commit choice).
- **G3** - public framing overclaims relative to implementation. **RESOLVED** (VL-030): README rewrite at VL-029 follow-up (`5f833fb`) brought public framing to post-VL-029 honest state; Zenodo addendum Revision 2 (DOI `10.5281/zenodo.20387278`) published with corrected title, short prose abstract, and attached PDF evidence anchored to snapshot commit `89ff2f9`; enforcement-evidence run at HEAD captured to `EVIDENCE/proofs/g3_enforcement_evidence_001.{log,md}`.
- **G4** - the gate is bypassable (opt-in, not enforced).
- **G5** - "external" verification is not durable (ephemeral webhook).
- **G7** - tests are code-derived, not canon-derived.
  **RESOLVED** (VL-028 + VL-029 + VL-034): envelope domain closed
  via `TESTS/adversarial/test_ccs_canonical.py` which derives 9 tests
  from canon sections 11.9, 12.1, 12.3, 12.4, 13 with explicit
  citations in each docstring (the post-VL-029 envelope.py + pep.py
  wiring exercise those tests on every ELIGIBLE response); evaluator
  domain closed via `TESTS/adversarial/test_evaluator_canonical.py`
  (VL-034) which derives 22 tests from canon sections 11.7 (AC^3),
  11.8 (T^26), and 11.9 (manifest-integrity via artifact-05-layer).
  Both domains now have tests whose lineage runs from canon to
  assertion.
- **G8** - evidence proofs are narrated, not executable.
  **NEAR-CLOSED** (VL-052; CI half closed VL-073): executable runners in `EVIDENCE/proofs/`
  supersede the narrated proofs (VL-050 finding 4), and CI now runs the suite + the hermetic
  runners on every push (`.github/workflows/ci.yml`, green on GitHub Actions at `c519f34`); the
  residual narrows to `STATE.md` auto-regenerability. See artifact 04.
- **G9** - `stability_proof_001.md` is truncated.
  **NEAR-CLOSED** (VL-052): archived with a NON-CURRENT header (VL-011); preserved-
  marked-non-current rather than finished or deleted (VL-050 finding 4). See artifact 04.
- **G11** - manifest-source asymmetry: `manifest_sha256()` read from
  disk while `manifest_integrity_valid()` read the version from its
  passed manifest argument (surfaced by VL-012). **RESOLVED** (VL-053)
  via path (b)-with-guard: `manifest_sha256()` keeps hashing the on-disk
  `MANIFEST/manifest.json` (the single pinned source of truth), and
  `manifest_integrity_valid()` fails closed when its passed manifest
  diverges from that source. See
  `docs/restructure/04_current_vs_claimed.md`.
- **G12** - canon section 11.1 under-specifies the wire-origins of `I`'s
  components (`C`, `t`) (surfaced by VL-015). **PARTIALLY ADDRESSED**: the
  schema-layer half is closed (VL-016 - `context` caller-supplied required,
  `t` not caller-supplied, each with rationale); the canon-layer half is open
  and resolvable only by a canon-version event under GR-1 (not scheduled).
  See `docs/restructure/04_current_vs_claimed.md`.
- **G13** - manifest-pinning field provenance is mixed canon + envelope
  (surfaced by VL-015). **PARTIALLY ADDRESSED**: the schema-layer half is
  closed (VL-016 - `expected_manifest_version` / `expected_manifest_sha256`
  re-attributed to layered provenance: canon-required manifest properties +
  envelope-spec operationalization); the canon-layer half is open and
  resolvable only by a canon-version event under GR-1 (not scheduled). See
  `docs/restructure/04_current_vs_claimed.md`.
- **G14** - unknown-key refusal code under-determination inside `interaction`
  (surfaced VL-017 / VL-017b). **RESOLVED** (VL-054, Option A): an unknown
  non-CCS-shaped key inside `interaction` is refused with the cause-naming
  `REF_SCHEMA_UNKNOWN_KEY`, replacing the provisional `REF_SCHEMA_TYPE_MISMATCH`
  mapping. See `docs/restructure/04_current_vs_claimed.md`.
