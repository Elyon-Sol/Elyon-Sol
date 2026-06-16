# G5 go-live - tomorrow's real-world instances + recruiting kickoff (DRAFT)

Status: DRAFT for review, uncommitted. The concrete, do-it-tomorrow execution of
`docs/restructure/29_external_validation_execution_plan.md` Phase 1 (public
surface bring-up) and the kickoff of Phase 3.1 (sourcing a blind attacker). Folds
in the VL-104/105 ext-authz sidecar, which artifact 29 predates. Builds on
`deploy/LIVE_BRINGUP_RUNBOOK.md`, `deploy/RED_TEAM_BRIEFING.md`,
`deploy/RED_TEAM_OUTREACH.md`, `deploy/host_setup_*.md`, and the TLS stack.

Honest framing (unchanged): standing this up does NOT make the claim true. A
break is first-class progress (becomes a fix or a named-open boundary); a clean
run is bounded by scope and window, never "unbreakable." G5 is MET only when a
blind external party has actually engaged the surface (Gate 4).

---

## 1. The instances (what goes live)

Two real, internet-reachable hosts on DIFFERENT networks (two cloud instances,
ideally different providers/regions - NOT two VMs on one host; that tier is done).
Real DNS, real CA (Let's Encrypt), dev CA retired.

| Host | Service | Public name | Port (TLS) | Role |
| --- | --- | --- | --- | --- |
| A | gate (`pep`) | gate.elyon-sol.io | 8443 | mints + signs admissibility envelopes |
| B | reference target | target.elyon-sol.io | 9443 | the thing that ACTS - primary attack target |
| B | publisher | pub.elyon-sol.io | 9143 | serves the signed published record |
| B | elyon-authz sidecar | authz.elyon-sol.io | 9243 | ext-authz admissibility surface (VL-104/105) |

All four served under real-CA TLS. Optionally front each on 443 via a reverse
proxy; the service ports above are the minimum.

Trust material (out-of-band, NOT on the served hosts' web roots): the pinned
publisher key, the gate signing key (private on host A only), the pinned root
anchor. Per `deploy/tls/trust_bootstrap.md` Path B (real CA -> `ELYON_TLS_CA_BUNDLE`
unset; clients trust the system store).

## 2. Bring-up order (the sequence to run tomorrow)

1. Provision host A and host B; open the four ports; set the four DNS A-records.
2. Issue real certs (Let's Encrypt) for the four names on their hosts.
3. `python bootstrap_config.py` ONCE (the gate keypair + anchor); distribute the
   PUBLIC half + anchor to host B out-of-band. Private signing key stays on A.
4. Host B: bring up publisher, target, and sidecar under TLS in SIGNED mode
   (`docker-compose.yml` + `.tls.yml` + `.replay.yml` + `docker-compose.authz.yml`
   + `docker-compose.authz.tls.yml`). Set `ELYON_ISSUANCE_LOG_PATH` on the gate
   (host A) so the run produces a reconcilable issuance log (VL-099).
5. Host A: bring up the gate under TLS, pointed at `https://target.elyon-sol.io:9443`.
6. Liveness: `/healthz` green on the sidecar; `/received` reachable on the target;
   gate mints an envelope end-to-end across the two hosts.

## 3. Self-test gate - GREEN before any stranger arrives

Run the author's own attack suite against the PUBLIC surface (you, not an
attacker - this proves the surface is real and the defenses transport):

- `attack_suite_live_runner.py` configured against the public gate/target
  (`ELYON_LIVE_*` env) - every adversarial case DEFEATED, positive control honored.
- The sidecar matrix over the public surface (`mint_and_present.py` pointed at
  `authz.elyon-sol.io`): ALLOW on a valid attested request; DENY on forged / rebound /
  replayed / un-attested.

On all-green: flip the `REAL_TRANSPORT` predicate naming the public run log (C4).
Expect this step to surface its own bugs first - the VirtualBox tier found four
(VL-087/088/089/092). Fix them before exposure. The attacker must meet a working
system, not a broken demo.

## 4. The exposed attack surface (what a hacker gets, and what "win" means)

Public endpoints handed to the attacker: `target.elyon-sol.io:9443`,
`gate.elyon-sol.io:8443`, `authz.elyon-sol.io:9243`, `pub.elyon-sol.io:9143`.

Two crisp break definitions (success = reproduce either against a DEFENDED claim):
- TARGET break: get `target.elyon-sol.io` to ACT (record an executed action on
  `/received`) on a call that is un-attested, forged, replayed, rebound, stale, or
  bound to a different target.
- SIDECAR break: get `authz.elyon-sol.io` to return ALLOW (200) for any request that
  is not a current, bound, single-use, validly-signed admissibility envelope.

NOT a finding (brief them as limits, Phase 2.1 / scope them out, Phase 4.2):
reaching a named-open boundary (A1 un-routed caller closed only by target policy;
root/publisher key compromise; the cost floor); DoS / availability (fail-closed by
design); "I described a harmful action in admissible vocabulary and it passed" (the
semantic-binding question is out-of-scope-by-design, canon section 14).

## 5. Recruiting kickoff (Phase 3.1 - the blind attacker)

The binding rule (Gate 4): the attacker must be BLIND - security-competent, with
NO prior exposure to the project's framing and NOT in the build conversations.
Prior exposure disqualifies (there is no task-to-source binding to rescue a
contaminated reviewer, unlike a model under VL-008(c)). What they receive is the
DECONTAMINATED pack only (`deploy/RED_TEAM_BRIEFING.md`): live URLs, the falsifiable
claim sheet, the named floors, the inspector CLI. FORBIDDEN to show: the canon, the
ledger, the VL-106 cross-model result, any convergence verdict (VL-057 / ext-
readiness gate 4).

The "break it" one-pager (publish at a stable URL; this is the recruiting asset):
- the claim, in one sentence (what the surface refuses, by construction);
- the live endpoints + the two break definitions above;
- scope in/out + the "not a finding" list;
- rules of engagement: only the listed hosts, no DoS, no social engineering, no
  out-of-scope systems; coordinated disclosure; explicit authorization + safe
  harbor for good-faith testing of THESE endpoints only;
- how to submit a break (repro steps -> the inspector CLI as the shared adjudicator);
- the reward (decide tier in section 6).

Channels (decontamination-aware - pick people who have NOT seen the framing):
- a bug-bounty-style public listing on an established platform (breadth);
- direct outreach to individual security researchers (vet for no prior exposure);
- security communities where red-teamers gather (a "break my fail-closed gate"
  challenge reads well); the OPA/policy-as-code and agent-security crowds are the
  on-target audience for the sidecar angle specifically;
- a "Show HN / show the community" post pointing at the one-pager.
Lead the sidecar angle for the policy/OPA audience ("get my ext-authz layer to
allow an inadmissible request"); lead the target angle for general red-teamers.

## 6. Decisions to lock before you execute (the real forks)

1. Hosts + domain: which two providers/regions, and the domain. (Need a domain and
   two instances on different networks. Verify provider pricing at execution time.)
2. Recruiting tier (cost vs. rigor, artifact 29 3.1): paid pentest firm (max rigor,
   max cost) / bug-bounty platform listing (breadth) / individual researcher
   (cheapest). For a solo budget, a small bounty pool + public credit + direct
   researcher outreach is the realistic start; a paid engagement is the high-rigor
   upgrade once there is signal.
3. Reward: bounty amount per break tier, or credit-only. Decide before publishing
   the one-pager.
4. Parallel track (Phase 3.2): a SEPARATE stake-free engineer asked only the COST
   question (assemble the equivalent from OPA + SPIFFE + a PKI; report whether it
   shipped cheaper). Independent of the live surface; can start tomorrow too.

## 7. Intake -> ledger (Phase 5, when a report lands)

A break: reproduce it, then record it as a defeated-claim ledger entry that becomes
either a fix or a new named-open boundary (the VL-087..092 precedent - a break is
progress, not failure). A clean run: record it bounded by scope + window, never as
"unbreakable." The rebuild report: record as-is, including an unfavorable result.
Then update STATE + artifact 04 with G5's new status.
