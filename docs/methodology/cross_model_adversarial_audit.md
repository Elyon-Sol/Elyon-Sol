# Cross-Model Adversarial Audit (methodology)

Status: framework methodology. Companion to
`docs/methodology/cross_model_evaluate_template.md`, which it does NOT
replace. The evaluate template checks framework-level PROPERTY claims
(convergent, direct-naming, Grok plus OpenAI). This process audits a built
INCREMENT and the author's own assessment of it for proof and stability,
adversarially, with the author treated as an interested party.

Invoke when: an increment makes a claim that matters (a security or
correctness property, a "done" or "non-bypassable" framing), OR the author's
self-assessment is the only check on the work (single-author loop: the same
party designed, judged, and specified the next step). It is optional, not
per-session.

------------------------------------------------------------------------------
CORE STANCE
------------------------------------------------------------------------------
1. Cold is the verdict of record. Every model evaluates blind and
   falsification-first, with no author framing. The cold verdict is what
   counts.
2. Falsification-first. Every proposition asks the model to find where the
   claim FAILS, and must be answerable in any direction (the system claims
   too much, too little, or exactly right).
3. Blind and independent. Models are not told an AI authored the work or the
   audit; no model sees another model's output or the author's
   self-assessment in the cold round. Independence is a precondition, not a
   hope (see Enforcement).
4. The terminal authority is a test, never a model. A finding's output is a
   characterization test that pins current behavior (see Disposition). Model
   reasoning decides how urgently to write the test, not whether the claim is
   true.

------------------------------------------------------------------------------
PROTOCOL
------------------------------------------------------------------------------
Step 0. The human, not the author-under-review, owns the trigger and the
  blinding. If the author is an AI, the AI may draft the propositions but the
  human edits them, may add propositions the author has not seen, and may run
  a model the author is not told about.

Step 1. Neutral packet. Provide the raw files (source, tests, evidence run)
  with authorship and AI attribution stripped. Frame as "a system that does X;
  evaluate these claims." Do not include the author's prose, the ledger, or
  the project's preferred vocabulary.

Step 2. Propositions in three sets:
  - Proof: does the claimed property hold? (correctness, soundness)
  - Stability: does it hold robustly and durably? (perturbation, adversarial
    input, time/reassertion, transport reality, threat-model completeness)
  - Admissions: the author's own claims, each confirmable, downgradable, or
    overturnable.
  Plus one instrument-critique proposition: "This audit's author is the party
  whose work it audits. Identify leading questions, easy-to-pass framings, and
  claims that should be tested but are absent." This is the load-bearing
  safeguard for a self-authored audit.

Step 3. Cold round. At least two INDEPENDENT models answer the packet plus
  propositions, falsification-first. Record verbatim every concrete
  counter-case.

Step 4. Split-resolver round (conditional, directional). Run ONLY to resolve a
  genuine cold split (cold verdicts differ by more than one band:
  holds / partial / fails). Show each dissenting model the opposing view and
  ask whether it revises.
  - A model that HOLDS its dissent under pressure -> the dissent is
    strengthened; treat as a high-confidence finding and write the test now.
  - A model that FOLDS toward the author -> discard that agreement as
    anchoring; the split is UNRESOLVED; route to a test anyway.
  The resolver can only downgrade or hold. It can NEVER upgrade a claim or
  count folding as confirmation. Agreement that appears only after anchoring
  is weak by construction; disagreement that survives anchoring is strong.

Step 5. Disposition. Every finding becomes a characterization test that pins
  current behavior and passes green, so closing the gap later is a deliberate
  change that breaks the named test (convention: `TESTS/.../test_findings_NNN.py`,
  one test per finding, docstring stating the finding and what flipping it
  means). The test is the framework's record of the finding; the audit
  transcript is not committed.

------------------------------------------------------------------------------
ENFORCEMENT (lessons from the first run, VL-038 audit)
------------------------------------------------------------------------------
- Independence is the precondition the first run partly failed: the two model
  outputs were verbatim-identical across long stretches, so "two-model
  convergence" was really one model wearing two hats. If pass one is not
  genuinely independent, the split-resolver adjudicates an illusion. Enforce:
  separate sessions, no shared context, no paste-through; if outputs overlap
  verbatim, treat them as ONE source.
- The strongest result the first run produced was a model HOLDING a dissent
  against the author under pressure (it overturned a claim the author had
  affirmed in the author's own evaluation). That is why the directional
  resolver is kept: held-against-author is the highest-confidence signal
  available.
- The author will be motivated to read findings as vindicating. When the
  author evaluates the findings, the human holds the author to: report per
  proposition whether the independent reads confirm, soften, or OVERTURN each
  admission, including where the author was wrong, steelmanned not explained
  away; do not discount a real defect as "not a bug"; do not over-credit a
  convenient agreement; do not downgrade a refutation to a wording issue.

------------------------------------------------------------------------------
WHAT IT CAN AND CANNOT ESTABLISH
------------------------------------------------------------------------------
Can: catch overclaims, missed cases, and framing bias; surface concrete
counter-cases that convert to tests; check a self-authored loop from outside.
Cannot: prove code correct. Cross-model agreement is a consistency-and-
plausibility signal. A found defect is high-value (write the test). Unanimous
"found nothing" is weak evidence, and is only trustworthy to the degree the
instrument-critique proposition reports the audit had teeth.

------------------------------------------------------------------------------
ADOPTION
------------------------------------------------------------------------------
This artifact is the process; it carries no per-increment obligation. A session
that invokes it records, in its ledger entry, only: that the audit ran, the
disposition (which findings became which tests), and the verdict-of-record
(cold). The audit transcript and any anchoring round stay off the framework
record, consistent with how the audit was first run.
