# G5 go-live - clean-context session kickoff

Purpose: bootstrap a NEW session to EXECUTE G5 Phase 1 (stand up the real public
surface) and kick off Phase 3.1 (solicit a blind attacker). Read this and the
cited sources first; do not rely on chat history. Mirrors the SESSION_PROTOCOL
resume discipline. This session is EXECUTION (deploy + people), not a code build.

---

## 0. Objective (one sentence)
Stand up the four real, internet-reachable nodes (gate, target, publisher,
sidecar) at *.elyon-sol.io under a real CA, get the author self-test GREEN over
that surface, flip the REAL_TRANSPORT predicate naming the public run log, then
publish the decontaminated "break it" pack and begin recruiting a blind attacker.

## 1. Resume first (SESSION_PROTOCOL)
       git pull origin main
       git log --oneline -6      # HEAD should be at the VL-106 line or later
       git status                # working tree clean, up to date with origin
- Read STATE.md - "Next open action" is "execute artifact 29 Phase 1." THIS
  session is that action (no scope creep).
- Read the ledger tail: VL-104 (sidecar), VL-105 (sidecar TLS), VL-106 (the
  sidecar claim set cross-model-verified at conformance scope).

## 2. Read first (primary sources - do not skip)
1. `deploy/G5_GO_LIVE.md` - the concrete execution sheet (instances, bring-up
   order, self-test gate, recruiting kickoff, the forks). AUTHORITATIVE for today.
2. `docs/restructure/29_external_validation_execution_plan.md` - the G5 plan
   (phases, gates, acceptance criteria).
3. `deploy/LIVE_BRINGUP_RUNBOOK.md` + `deploy/runbook.md` + `deploy/host_setup_*.md`
   - bring-up mechanics.
4. `deploy/tls/trust_bootstrap.md` (Path B, real CA) + `deploy/tls/gen_certs.py`.
5. The attacker pack (what a stranger receives - nothing else): `deploy/BREAK_IT.md`,
   `deploy/HOW_TO_INTERACT.md`, `deploy/RED_TEAM_BRIEFING.md`, `deploy/RED_TEAM_OUTREACH.md`.
6. The self-tests: `EVIDENCE/proofs/attack_suite_live_runner.py` (gate/target) and
   the sidecar matrix (the `mint_and_present` pattern /
   `EVIDENCE/proofs/authz_sidecar_tls_001_runner.py` over the public surface).

## 3. Scope
IN: provision two hosts on different networks; real DNS (*.elyon-sol.io) + real CA
(Let's Encrypt); bring up gate/target/publisher/sidecar under TLS in SIGNED mode;
author self-test GREEN; flip REAL_TRANSPORT naming the public run log; publish the
decontaminated attacker pack; open recruiting channels for a BLIND attacker;
(parallel) commission the stake-free rebuild estimator (Phase 3.2).
OUT: any change to gate / verifier / crypto / sidecar CODE (this is execution); the
universal-PDP track (separate, concurrent); showing canon / ledger / the VL-106
result / any convergence verdict to an attacker (FORBIDDEN - Gate 4).

## 4. Execution order (from G5_GO_LIVE.md sections 2-5)
1. Provision host A (gate) + host B (target/publisher/sidecar), different networks;
   open the four ports; set DNS A-records for gate/target/authz/pub.elyon-sol.io.
2. Issue real certs (Let's Encrypt) for the four names.
3. `bootstrap_config.py` ONCE; distribute the PUBLIC key + anchor to host B; the
   private signing key stays on host A.
4. Host B: publisher + target + sidecar under TLS, SIGNED mode (the compose
   overlays); set `ELYON_ISSUANCE_LOG_PATH` on the gate.
5. Host A: gate under TLS, pointed at `https://target.elyon-sol.io:9443`.
6. SELF-TEST GREEN before exposure: `attack_suite_live_runner.py` + the sidecar
   matrix over the public surface. EXPECT to find bugs here first - fix them (a real
   fix is a build increment with its own VL). On green: flip REAL_TRANSPORT naming
   the public run log.
7. Publish `BREAK_IT.md` (strip the operator header, fill placeholders, link
   `HOW_TO_INTERACT.md` + the inspector usage). Hand `RED_TEAM_BRIEFING.md` to
   vetted-BLIND attackers only.
8. Open channels (`RED_TEAM_OUTREACH.md`); commission the rebuild estimator
   (Phase 3.2) in parallel - it does not need the live surface.

## 5. Decisions to lock before executing (the forks)
- Two hosts: which providers/regions (different networks). [domain elyon-sol.io is set.]
- Recruiting tier + reward (bounty pool vs credit-only); engagement window
  (<START>/<END>); reporting channel you control the timing of.
- Counsel sign-off on the `BREAK_IT.md` safe-harbor / authorization clause BEFORE
  publishing.

## 6. Guardrails
- EXECUTION, not build: do not touch gate / verifier / crypto / sidecar code. If a
  self-test surfaces a real bug, that IS a build increment - fix it, ledger it,
  re-run the self-test - then continue the go-live.
- Decontamination (Gate 4): attackers get the BREAK_IT / HOW_TO_INTERACT /
  RED_TEAM_BRIEFING pack ONLY. Canon, ledger, VL-106, convergence verdicts FORBIDDEN.
- Honest posture: a break is first-class progress (a fix or a new named-open
  boundary); a clean run is bounded by scope + window, NEVER "unbreakable." G5 is
  MET only when a blind external party has actually engaged the surface.

## 7. Definition of done (this session)
Four nodes live under real-CA TLS; author self-test GREEN over the public surface;
REAL_TRANSPORT flipped naming the public run log (Gate 1 MET); the decontaminated
attacker pack published; at least one recruiting channel open and the rebuild
estimator commissioned (Gates 3/4 in motion). Then run the CLOSE PROTOCOL: update
STATE "Next open action" to G5's new status and append a VL entry recording the
bring-up, the self-test result, and the recruiting kickoff.

## 8. Honest framing (carry it intact)
Standing this up does NOT make the claim true. It makes the claim TESTABLE by
someone who is not you. That is the whole point of today.
