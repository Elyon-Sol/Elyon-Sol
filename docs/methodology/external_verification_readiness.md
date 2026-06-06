# External (human) verification readiness - the referent-bound criterion

Repo path: docs/methodology/external_verification_readiness.md

## Why this exists

The project has used cross-model "evaluates" as if convergence (e.g. "SOUND,
3-0") were external validation. It is not, when the artifact under review, its
framing, and the evaluate prompt were all produced by the same iterative build
surface: agreeable judges fed a shared framed input produce CORRELATED error,
not independent confirmation (see the VL-057 referent-binding entry in
EVIDENCE/verification_ledger.md; Lesson 10 / GR-3 are the companion teeth). The
same trap waits one step out: a HUMAN reviewer handed the canon, the README, and
the ledger is read by that same persuasive surface and gets inflated too - more
expensively, and with the false comfort of a human signature.

So "ready for outside human verification" is NOT "the documents are polished and
internally consistent." A reviewer decontaminates the assessment only if they
are bound to a REFERENT the author did not frame: a running thing they can
attack, and a falsifiable claim they can try to break, without first absorbing
the project's own account of itself.

This file states that criterion as a set of pass/fail gates, and records the
honest current verdict against them. It is the readiness analog of the
bounded-claims discipline: state the criterion, then report the true status,
including when the status is NOT MET.

## The criterion (each gate is pass/fail; all must pass)

1. ATTACKABLE DEPLOYMENT. A running gate plus an enforcing target that a reviewer
   can exercise WITHOUT reading the canon, over REAL transport (separate hosts,
   real network, TLS) - not the loopback model the current runners use. The
   referent is the running system, not its description.

2. FALSIFIABLE CLAIM SHEET. Every bounded claim restated as a break-it challenge
   with an explicit pass/fail criterion, each mapped to the test or runner that
   currently defends it. Examples, in the form a reviewer attacks:
   - "Reach the target without a valid current decision." (A1 bypass; defended
     only by a target-side policy, not by the gate - state this honestly.)
   - "Get the target to honor a forged envelope with no issuer signature on the
     signed path." (defended by sign/verify; signing_forgery_defeated runner.)
   - "Get a revoked or out-of-window issuer key accepted." (key-record gate.)
   - "Get a key record signed by a revoked/retired root accepted." (root gate.)
   - "Get the target to act on a verbatim replay or a target_url-swapped
     envelope." (binding check; test_verifier / test_findings_001.)
   - "Mint acceptance despite a byte-divergent target disk." (cross-host fetch;
     the cross-host runners - but over REAL transport per gate 1, not loopback.)
   The reviewer succeeds by producing a working exploit or fails by not - a
   referent no framing can move.

3. REBUILD-COST REFERENT. The "assemble OPA + SPIFFE + PKI instead" claim is
   answered by someone with NO stake actually attempting the assembly and
   reporting whether it was cheaper - bound to whether it shipped, not to an
   estimate. A model's "a small team could do it in 1-2 months" is NOT this; it
   is non-evidential per the referent-binding rule (VL-057). The ratio question
   gets a referent or stays open.

4. STAKE-FREE, BLIND REVIEWER. The reviewer has no investment in the ledger and
   is NOT shown the prior cross-model convergence verdicts (those are demoted at
   VL-057; showing them re-inflates). They are pointed at the running system and
   the claim sheet, not at the project's self-account.

5. NAMED FLOORS ACKNOWLEDGED, NOT DEFENDED. Out-of-band root/issuer COMPROMISE
   recovery is a trust-model limit not closeable by attack; it is stated to the
   reviewer as a boundary, not presented as something the gate defends. The
   reviewer is told where the attack surface ends.

## Honest current verdict

NOT READY.

The binding reason is REFERENT QUALITY, not documentation maturity:

- Gate 1 (attackable deployment over real transport): NOT MET. The current
  transport is loopback-modeled; true multi-machine + TLS is the named-unbuilt
  G5 floor. Attacking a loopback model is partly attacking a simulation, so a
  reviewer's read against it would itself be partly inflated. This is the
  load-bearing gate and it gates the rest.
- Gate 2 (falsifiable claim sheet): the in-process half exists (the adversarial
  tests and the runners pin current behavior); it becomes a REAL attack surface
  only once gate 1 is met. Status: partial, referent-incomplete until gate 1.
- Gate 3 (rebuild-cost referent): NOT MET. No stake-free rebuild attempt exists;
  the only "estimate" on record is model-sourced and therefore not evidence.
- Gate 4 (stake-free blind reviewer): procedural, met when the others are - and
  requires the convergence-verdict demotion (done at VL-057) so the reviewer is
  not shown inflated priors.
- Gate 5 (named floors acknowledged): largely met in the existing docs; carry it
  into the reviewer briefing verbatim.

## Path to ready (each step referent-bound, none a model evaluate)

1. Close gate 1: real cross-host transport + TLS (the G5 floor), so there is a
   genuine running thing to attack. This is the single highest-value step toward
   external readiness and it is engineering, not framing.
2. Publish the claim sheet (gate 2) against that real surface.
3. Obtain a stake-free rebuild attempt (gate 3) - a person, not a model.
4. Brief a blind reviewer (gates 4, 5) and let them attack, with no prior
   verdicts shown.

When these pass, outside human verification is meaningful because the human is
bound to referents the framing cannot move. Until then, "get a human to look at
it" would purchase the same inflation as the cross-model evaluates, at higher
cost. The synthesis's own conclusion: we are not ready, and the reason is the
referent, not the writing.
