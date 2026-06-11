# 29 - External validation execution plan (G5) (VL-103)

Status: SINGLE-SOURCE (drafted in the VL-103 session). Operational plan,
not a code spec. It consolidates work that already exists in scattered
form - the readiness criterion (`docs/methodology/external_verification_readiness.md`),
the falsifiable claim sheet (`docs/methodology/falsifiable_claim_sheet.md`),
the deploy runbooks (`deploy/runbook.md`, `deploy/tls/trust_bootstrap.md`),
and the live attack runner (`EVIDENCE/proofs/attack_suite_live_runner.py`,
artifact 22) - into one ordered procedure for closing G5. It introduces
no claim those documents do not already make; where it would, it defers
to them by reference.

GR-3 honest framing: this plan describes HOW the external validation is
to be run. It does not assert that running it will succeed. A defect
found by the external attacker is the plan working, not failing.

---

## 0. What G5 is, restated as the bar this plan must clear

G5 is closed only by a real EXTERNAL attacker, on a real PUBLIC surface,
who has not absorbed the project's account of itself, failing to break a
falsifiable claim - or breaking it, and the break being recorded. The
four readiness gates that are NOT met by in-house work alone
(external_verification_readiness.md) are the acceptance checklist:

- Gate 1 ATTACKABLE DEPLOYMENT over real public transport - the
  load-bearing gate; engineering.
- Gate 3 REBUILD-COST REFERENT - a stake-free human rebuild attempt.
- Gate 4 STAKE-FREE BLIND REVIEWER - a person with no ledger investment,
  shown no convergence verdicts.
- (Gate 2 claim sheet and Gate 5 named-floors are MET in-house; they are
  carried into the briefing, not re-built.)

This plan sequences the four AUTHOR steps STATE.md already names
(stand up C1+C2 on real hosts; run the live attack suite; flip
REAL_TRANSPORT; arrange the external attacker) and adds the people-and-
process scaffolding those steps assume but do not specify.

---

## Phase 1 - Public surface bring-up (Gate 1)

The deploy artifacts are built and in-sandbox-validated (VL-081/082);
this phase executes them on real, internet-reachable hosts. It is
engineering, the author's, and pure execution of existing runbooks.

1.1 **Two hosts, real network.** Two cloud instances (or two physical
    hosts on different networks - NOT two VMs on one host; that is the
    VirtualBox tier already done, VL-085..096). Gate on host A; reference
    target + publisher on host B. Per `deploy/runbook.md` +
    `deploy/host_setup_*.md`.

1.2 **Real DNS + real CA.** Public DNS names for both hosts; certificates
    from a real CA (Let's Encrypt suffices - the point is a trust root the
    author does not control, retiring the dev-CA caveat that bounds every
    prior live run). Trust bootstrap per `deploy/tls/trust_bootstrap.md`,
    substituting the real CA for the dev CA.

1.3 **Signed mode, freshness + replay wired.** Bring up SIGNED mode (the
    target pins the publisher key; B1 freshness + B3 shared replay active
    per the `.tls.yml` + `.replay.yml` overlays). Set
    `ELYON_ISSUANCE_LOG_PATH` on the gate (VL-099) so the run produces a
    reconcilable issuance log.

1.4 **Self-test before exposure.** Run `attack_suite_live_runner.py`
    against the public surface with the author's own calls (artifact 22 /
    the C3-live run). On green: flip the REAL_TRANSPORT predicate naming
    the run log (C4). This is the author validating the surface is real
    and the defenses transport - NOT the external validation. It is the
    precondition for inviting an attacker, so the attacker meets a working
    system, not a broken demo (the VirtualBox tier found four real bugs
    this way - VL-087/088/089/092; expect the public tier to surface its
    own before any stranger arrives).

1.5 **Acceptance for Phase 1:** a stranger on the internet can reach the
    gate and the target over real TLS and exercise them without reading
    the canon; the author's own attack suite is green over that surface;
    REAL_TRANSPORT cites the public run log. Gate 1 MET.

---

## Phase 2 - The reviewer briefing pack (Gates 4, 5)

What the external party is handed. The discipline is decontamination:
the reviewer is bound to referents the author did not frame. This pack
is assembled ONCE and reused for every reviewer.

2.1 **Included:**
    - Live endpoint URLs + a minimal "how to send a request / read a
      response" (the wire shape, the refusal vocabulary) - NOT the canon,
      NOT the rationale.
    - The falsifiable claim sheet (`falsifiable_claim_sheet.md`) as the
      target list: each row is a break-it challenge with its pass/fail
      line. The reviewer succeeds by producing a working exploit.
    - The named floors (claim sheet Section 3 / ext-readiness gate 5)
      stated as boundaries: A1 (non-adopting target), ROOT (key
      compromise recovery), COST. The reviewer is told where the attack
      surface ends, so a "break" of a named-open boundary is not mistaken
      for a finding against a defended claim.
    - The envelope inspector CLI (`docs/TOOLING.md` section 4) so the
      reviewer can decode/verify/reevaluate/reconcile what the surface
      emits - giving them an independent read of every decision, not just
      the gate's say-so.

2.2 **FORBIDDEN in the pack** (claim sheet "Forbidden in any reviewer
    briefing"; ext-readiness gate 4): no cross-model convergence verdicts
    ("SOUND 3-0", the VL-102 CONFIRMED, "N-0"); no "whole canon realized"
    framing; no "non-bypassable" without the routed-and-attested
    qualifier; no ledger, no STATE.md, no this-plan. The reviewer attacks
    a running thing against a claim sheet; they do not read the project's
    self-account. (The VL-102 cross-model result is in-house conformance
    evidence; showing it to a blind reviewer re-inflates exactly the way
    VL-057 demotes.)

2.3 **Acceptance for Phase 2:** the pack exists, contains only referent-
    bound material, and has passed a read for carry-over hazards. Gate 5
    carried; Gate 4 procedurally ready.

---

## Phase 3 - Sourcing the external party (Gates 3, 4)

The hardest gate, because it is people, not engineering. Two distinct
roles; do not conflate them.

3.1 **The blind attacker (Gate 4).** A security-competent person with NO
    investment in the project, who has not been in the build conversations.
    Sourcing options, in rough order of rigor:
    - A paid penetration-test engagement (a firm; maximal independence,
      maximal cost).
    - A bug-bounty-style scope on the public surface (a platform listing;
      breadth, variable rigor).
    - An individual security researcher engaged directly (cheaper than a
      firm; vet for no prior project exposure).
    The decontamination requirement (gate 4) is the binding filter: prior
    exposure to the project's framing disqualifies, exactly as it would
    have for a model under VL-008 (c) - except here there is no
    task-to-source binding to rescue a contaminated reviewer, so the
    filter is exclusionary, not procedural.

3.2 **The rebuild estimator (Gate 3).** A SEPARATE person, an engineer
    with no stake, asked the COST question only: attempt to assemble the
    equivalent admission-and-attestation substrate from OPA + SPIFFE + a
    PKI (or their judgment of the right components) and report whether it
    was cheaper - bound to whether it shipped, not to an estimate. A
    model's "a small team could do it in 1-2 months" is explicitly NOT
    this (ext-readiness gate 3; non-evidential per GR-3). This gate can
    run in parallel with Phase 1-2 and does not depend on the live
    surface.

3.3 **Acceptance for Phase 3:** a vetted-blind attacker is engaged with
    the Phase-2 pack; a stake-free rebuild attempt is commissioned. Gate 4
    met on engagement; Gate 3 met on the rebuild report (whatever it
    concludes).

---

## Phase 4 - Rules of engagement

The contract with the attacker. Stated so a finding is unambiguous and
the run is safe and legal.

4.1 **Scope:** the two named hosts + their endpoints, for the engagement
    window. Explicitly in scope: forging/replaying/rebinding/swapping
    envelopes; presenting stale or drifted state; attempting A1 bypass at
    the target; key/record manipulation within what the surface exposes.
    Explicitly OUT of scope: attacking the cloud provider, the CA, the
    author's other infrastructure, or denial-of-service against
    availability (the gate's fail-closed posture trades availability for
    safety by design - DoS is conceded, not a finding; claim sheet does
    not list an availability claim).

4.2 **Success definition:** a finding is a working exploit that causes the
    TARGET to ACT (the side effect fires) on a call the gate's claim sheet
    says it must refuse - OR causes the gate to ADMIT a call the claim
    sheet says it must refuse - with reproduction steps. Reaching a
    named-open boundary (A1 at a non-adopting target, ROOT compromise,
    DoS) is NOT a finding against a defended claim; it confirms a stated
    limit. The inspector CLI is the shared adjudication tool: a disputed
    "break" is settled by running inspect/verify_issuer/reevaluate/
    reconcile on the artifacts and reading the verdict.

4.3 **Intake:** findings go to a channel the attacker controls the timing
    of (so the author cannot massage them); each finding is reproduced by
    the author independently before classification. Legal: a written
    authorization-to-test for the named hosts/window (so the engagement is
    lawful access, not intrusion).

4.4 **No coaching:** during the window the author answers operational
    questions (is the endpoint up, what is the wire shape) but does NOT
    explain the design, defend a refusal, or hint at intended attacks.
    The claim sheet is the only guidance.

---

## Phase 5 - Intake, classification, and the ledger

Every outcome lands in the project's existing discipline.

5.1 **A confirmed break** (target acted / gate admitted against a
    defended claim): reproduced by the author, then recorded as a ledger
    entry that NAMES the defeated claim-sheet row, the exploit, and the
    fix-or-concession. A break is the most valuable output the project can
    produce; the four VirtualBox-tier bugs (VL-087/088/089/092) are the
    precedent for recording defects as first-class progress, not as
    embarrassment. If the break is fixable, it becomes a new build
    increment; if it reveals a trust-model limit, it becomes a new
    named-open boundary on the claim sheet.

5.2 **A clean run** (no break against the defended rows over the window):
    recorded as a ledger entry stating exactly what was attempted, by
    whom (role, not necessarily name), over what window, against which
    claim-sheet rows - bounded as "this attacker did not break these
    claims on this surface in this window", NOT as "unbreakable". G5
    transitions from NOT-MET to MET-bounded: the bound is the engagement's
    scope and duration, stated honestly, the same way every prior live run
    carries its ceiling.

5.3 **The rebuild report** (Gate 3): recorded as-is, whatever it concludes
    - cheaper, costlier, or didn't ship. The COST claim on the sheet
    resolves to whatever the referent says, including "the substrate was
    not worth assembling", if that is the honest result.

5.4 **STATE.md + the gap tracker** (`04_current_vs_claimed.md`) updated to
    reflect G5's new status. Until 5.1/5.2 produce a real referent, G5
    stays NOT-MET and the project stays NOT-READY for an external-
    validation claim, by its own discipline.

---

## 6. What this plan deliberately does not do

- It does not promise the surface survives. The honest posture is that
  the external tier, like the VirtualBox tier, will likely surface
  defects; the plan is built to record them, not to avoid them.
- It does not turn a clean run into "unbreakable". A clean engagement is
  bounded by its scope and window and is stated that way (5.2).
- It does not resolve the named floors (A1, ROOT, COST-as-trust). Those
  are boundaries; the plan briefs them as limits (Phase 2.1) and scopes
  them out of "finding" (Phase 4.2).
- It does not address semantic binding (the substrate guarantees process
  legitimacy, not that an admissible request is wise) - that is a layer
  above this one and out of canon section 14 scope; named here only so a
  reviewer's "I described a harmful action in admissible vocabulary and
  it passed" is correctly classified as out-of-scope-by-design, not a
  break.

---

## 7. Sequencing summary

Phase 1 (public surface) and Phase 3.2 (rebuild estimator) can run in
parallel; both are independent of the attacker. Phase 2 (briefing pack)
depends on Phase 1's live URLs. Phase 3.1 (attacker) depends on Phases 1
and 2. Phase 4-5 are the engagement and its aftermath. The critical path
to a G5 referent is: public surface up (1) -> pack (2) -> blind attacker
engaged (3.1) -> run (4) -> recorded (5). Everything before Phase 1 is
done; everything from Phase 1 on is the author's, and is people-and-
deployment, not in-house code.
