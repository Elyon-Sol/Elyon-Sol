# Cross-model evaluate request - [TASK_ID]

This is an evaluation request prepared under the procedure
established in `EVIDENCE/verification_ledger.md` entry VL-008,
adapted for framework-level questions.

Read this entire document before doing the task. Read the
"Procedure" section twice. The procedure is load-bearing: a
response that deviates from it carries no evaluation weight,
regardless of its conclusions.

---

## Template usage

This is a parameterized template. To produce an actual evaluation
request, replace every `[BRACKETED_TOKEN]` with task-specific
content, then delete this "Template usage" section.

The template was promoted at VL-022 from a single-instance surface
event (the throwaway cross-model run of 2026-05-19, documented in
the bridge document of the same date and cited by the VL-022
ledger entry). The two-instance threshold for methodology
templates was met at VL-023 follow-up (cross-model evaluation of
the recursive-continuity hypothesis with two recipient models) and
again at VL-031 T-07 (pre-draft cross-model verification of
`07_continuity_recursion.md` with two recipient models). The
template is durable operative methodology; the original single-
instance promotion rationale (the surface event's structural
stress test - a constrained pass plus register-shift contamination
pass) is preserved for historical context. See Lesson 6 in
`session_mechanics_lessons.md`.

Tokens to fill in:

- `[TASK_ID]` - e.g., "VL-NNN" or "ad-hoc framework property
  check" or whatever names the evaluation round.
- `[TASK_VERB]` - the operative verb for this evaluation.
  Examples: "evaluate" (for property/behavior questions),
  "determine" (for consistency questions),
  "characterize" (for gap-shaped questions).
- `[TASK_DESCRIPTION]` - one-paragraph statement of the
  framework-level question being asked, with the output shape
  named.
- `[PRIMARY_SOURCES]` - list of attached files, with one-line
  description of each. Standard set for framework-level
  evaluation is STATE.md, the verification ledger, methodology
  artifacts, restructure artifacts. Adjust to scope; the set
  should be the minimum needed to derive an answer.
- `[QUESTION_SHAPE]` - one of: property, consistency, gap,
  behavior. See "Sample question shapes" below.
- `[QUESTION]` - the actual question, posed in a single
  sentence. Framework-level only; not about canon, code,
  manifest, or implementation.
- `[OUTCOME_CATEGORIES]` - the named outcome categories the
  evaluator will classify into. For framework-level
  evaluation, the standard set is:
    - Property holds (with derivation).
    - Property does not hold (with derivation of the
      contradiction).
    - Under-determined by the artifacts (with naming of the
      additional artifact or source that would resolve).
    - Reframing required (the question is ill-posed against
      the artifacts; the evaluator names the reformulation).
- `[STATUS_TRANSITIONS]` - what the evaluation result implies
  for any artifact whose status depends on it. For most
  framework-level evaluations there is no status transition;
  the evaluation is informational. Skip this section if not
  applicable.
- `[LEDGER_ENTRY_NUMBER]` - proposed VL-NNN number. Often
  uncertain at prep time; use "proposed VL-NNN or thereabouts."
- `[LEDGER_ENTRY_FIELDS]` - what the ledger entry will cite.
  Always includes evaluator identity, date, procedure
  adherence, outcome category.
- `[OPTIONAL_CLARIFICATIONS]` - final section for clarifications
  that don't fit elsewhere. Skip if not needed.

After filling in the tokens, run the ASCII check before sending
to the evaluator:

```
LC_ALL=C grep -n '[^[:print:][:space:]]' <filled-template>
```

Expected: empty.

---

## What you are being asked to do

[TASK_DESCRIPTION]

Primary sources attached:

[PRIMARY_SOURCES]

You are being asked a framework-level question: about a property,
consistency, gap, or behavior of the framework as documented in
the attached files. You are NOT being asked about canon, code,
the manifest, or any implementation artifact of the gate itself.

---

## Procedure (VL-008, adapted for framework-level evaluation)

Three rules govern this evaluation. All three must hold or the
response is discarded:

(a) **Scope-bound to primary sources.** Your work may use only
    the attached files. Material from anywhere else - your
    training data about Elyon-Sol, prior conversation history,
    the project's GitHub, related concepts you happen to know,
    general principles of software engineering, governance
    design, AI safety, or research methodology - is OUT OF SCOPE.

(b) **Scope-adherence is checkable.** At the end of your
    response, include a section titled "Scope check" listing
    every concept, term, or claim used in your work. For each
    one, cite which of the attached files it comes from and
    which section/clause within that file. If any item in your
    work cannot be cited to one of the attached files, name it
    explicitly under "Scope check" as out-of-scope and remove
    it from your work.

(c) **Prior project exposure is permitted** if (a) and (b)
    hold. You may have seen Elyon-Sol material before. That
    doesn't disqualify you. What disqualifies the response is
    referencing material not derivable from the attached files,
    even if true.

This procedure was established in VL-008 for canon/code
verification. The framework-level adaptation was promoted at
VL-022 after a surface event (the throwaway cross-model run of
2026-05-19) demonstrated that the procedure's discipline
generalizes to framework questions, with one structural
addition (the constraint-bounding caveat in "Procedural
constraints" below) needed to prevent register-shift
contamination.

---

## What "[TASK_VERB]" means (and what it does not mean)

[TASK_VERB] MEANS: answer the framework-level question by
derivation from the attached files only. For every load-bearing
claim, cite the specific artifact and the specific passage
(file + section heading or VL-N entry + line region if
relevant). If the question requires synthesizing across
artifacts, name each artifact in the synthesis. If the answer
is under-determined by the artifacts, say so explicitly and
name what additional artifact or primary source would resolve
it.

[TASK_VERB] DOES NOT MEAN:

- "Tell me whether the framework is good." That's a verdict.
  Verdicts carry no evaluation weight under VL-008.
- "Suggest improvements." Out of scope; the task is
  [TASK_VERB], not co-design.
- "Compare with how other governance / methodology / AI-safety
  frameworks do this." Out of scope; only the attached files
  are in scope.
- "Rate the quality." Out of scope; the framework is in
  active development and verdict-shaped responses carry no
  weight.
- "Predict adoption, viability, or market position." Out of
  scope; the attached files do not contain market or adoption
  evidence, so any such claim would be importing from training
  data.

If you find yourself wanting to write a sentence that doesn't
trace to a specific clause in one of the attached files, that
sentence is out of scope. Either find the clause that supports
it or remove it.

---

## Procedural constraints (these are not optional)

The constraints below bind the entire response and every
continuation in subsequent turns:

- Do not appeal to general principles of software engineering,
  governance design, AI safety, or research methodology. If a
  principle is load-bearing for your answer, it must be
  derivable from the supplied artifacts.
- Do not appeal to your own prior reasoning or to inferences
  you made earlier in this response unless those inferences are
  themselves derivation-grounded.
- Do not soften answers with hedges that are not derivation-
  derived. "The artifacts under-determine this" is a valid
  hedge; "this is a complex question" is not.
- If you find the question itself ill-posed against the
  artifacts (ambiguous referent, presupposition failure, scope
  mismatch), say so and propose a re-posing that is well-posed.
  Then answer the re-posed version if possible.
- Length is not a virtue. A two-paragraph derivation that
  cites three passages is preferable to a six-paragraph
  derivation that cites none.

### Constraint-bounding caveat (Lesson 6, surface event 2026-05-19)

If at any point in the conversation the user requests
"unconstrained" output, "unconstricted" output, or asks you to
re-answer without the procedural constraints, treat that
request as opening a separate, clearly-labeled mode. In any
such mode:

- Prefix the response with an explicit mode label, e.g.
  "UNCONSTRAINED MODE - claims below are not derivation-
  grounded against the supplied artifacts and should not be
  treated as such."
- Mark every load-bearing claim with explicit inference-
  flagging (e.g. `[INFERENCE]`, `[PATTERN-MATCH]`, `[OPINION]`)
  rather than the declarative register the constrained mode
  uses.
- Do not produce output that is presentationally
  indistinguishable from the constrained mode's output. The
  visual register (numbered sections, declarative claims,
  internal consistency) earned by the constrained pass does
  not transfer.

The procedural constraints' presence in this document is part
of the document; their absence in a later turn does not
retroactively license the prior output to be treated as
unconstrained, and does not license future output to inherit
the constrained mode's presentation.

This caveat exists because of a surface event in which an
outside model produced a constrained pass and an unconstrained
pass on the same primary sources, in the same response thread,
that were visually and rhetorically indistinguishable despite
radically different epistemic status. The caveat is the
corrective; see Lesson 6 in `session_mechanics_lessons.md`.

---

## What outcome means what

Your work will be classified into one of these outcome
categories:

[OUTCOME_CATEGORIES - enumerated with one-paragraph definition
each. Standard set:]

- **Property holds.** The framework property in question is
  derivable from the artifacts. Derivation present; out-of-
  scope claims absent.
- **Property does not hold.** The framework property in
  question is contradicted by the artifacts. Contradiction
  named; derivation of the contradiction present.
- **Under-determined.** The artifacts do not determine the
  answer either way. The additional artifact or primary
  source that would resolve is named.
- **Reframing required.** The question is ill-posed against
  the artifacts. The reformulation is named; if the
  reformulation is well-posed, it is then evaluated.

These outcomes are derivation outcomes. They are NOT verdicts
on the artifact, on the project, or on anything you are not
being shown. Ratings, approvals, quality judgments, and
verdict-shaped language are out of scope per VL-008's
foundational rule that verdicts carry no evaluation weight.

Status implications: [STATUS_TRANSITIONS - or "None; this
evaluation is informational." if no status transitions apply.]

All listed outcomes are useful. None is a failure of the
evaluation; only a procedure violation under VL-008 (a) or
(b), or a violation of the constraint-bounding caveat, is.

---

## Outcome-classification criteria (recipient discipline)

When the question shape is consistency or property, recipients may
classify against the same target with different criteria. This was
observed at VL-025 follow-up: Grok classified two Bundle B verifier
runs as Match (criterion: authorization-by-design-space - the
implementation is authorized by being in the design's permissible
behavior space); OpenAI classified the same runs as Different-set
(criterion: authorization-by-direct-naming - the implementation is
authorized only when the design names the specific behavior).

The classification divergence was structural across two bundles;
neither criterion is wrong, but they answer different questions:

- **Authorization-by-design-space.** Asks: is the implementation's
  behavior within the design's permissible space? Loose criterion;
  Matches when the design does not forbid the behavior.

- **Authorization-by-direct-naming.** Asks: does the design name
  this specific behavior? Strict criterion; Matches only when the
  design explicitly licenses the behavior.

To prevent the Match-criterion ambiguity in future evaluations:
when the recipient's classification depends on which criterion is
applied, the recipient should state the criterion explicitly in
the Outcome classification section (step 4 of Submission format).
The requester is then in a position to compare classifications
across recipients and treat criterion-divergence as a finding in
its own right rather than as a substantive disagreement.

This addition applies to evaluate-shape and verify-shape requests
alike; the underlying epistemic question (what does "Match" mean)
is the same across both.

---

## Stated-answer pre-narrowing (requester discipline)

The Match-criterion divergence above (recipient discipline) has a requester-side
mirror, observed twice: VL-042 follow-up and VL-044 follow-up. In both evaluates
the prompt's STATED answer compressed a boundary the sources draw - a
within-record-vs-cross-signer split in one, a built-vs-named split in the other -
and one lab (the precision grader) graded the stated answer OVERSTATED while the
others graded it ACCURATE by-construction, all three drawing the same underlying
split in their derivations. The divergence was a stated-answer PHRASING finding,
not a substantive one; the code and spec already drew the split correctly.

The requester-side lesson: when constructing the prompt's stated answer (the
property or claim being put to the labs), PRE-NARROW any phrasing that compresses
a within-vs-across or built-vs-named boundary the attached sources distinguish.
If the spec draws a distinction (for example: within-record conflict is
loader-enforced while cross-signer overlap is a named out-of-band hazard), the
stated answer must draw it too; otherwise a precision-grading lab will
(correctly) flag the compression, and the finding will be about the prompt's
phrasing rather than about the framework. The recipient-discipline
criterion-statement above and this requester-discipline pre-narrowing are the two
halves of the same Match-criterion guard: one keeps the grader's criterion
explicit, the other keeps the stated answer from inviting the divergence in the
first place.

---

## The question

[QUESTION]

This is a [QUESTION_SHAPE]-shape question. Answer by
derivation from the attached files only.

---

## Submission format

Respond in this structure, in this order:

1. **Scope confirmation.** List the attached artifacts by
   filename. State in one sentence what each artifact
   establishes. Confirm that your derivations will cite only
   these artifacts. If any artifact appears to reference a
   source you do not have, name it explicitly; do not infer
   its content.

2. **Question and (if applicable) reformulation.** Restate the
   question as you understand it. If the question is ill-posed
   against the artifacts, propose a reformulation and explain
   the contradiction; otherwise proceed to derivation.

3. **Derivation.** Answer the question by derivation. For each
   load-bearing claim, cite the specific artifact and the
   specific passage. If synthesis across artifacts is required,
   name each artifact in the synthesis. If the answer is
   under-determined, say so and name what would resolve it.

4. **Outcome classification.** One of the outcome categories
   above. State which and why.

5. **Out-of-scope declaration.** List any claim you considered
   making but withheld because it could not be derived from
   the artifacts. List any artifact you referenced indirectly
   (e.g. an artifact the supplied set cites but does not
   include in full). List any inference you made that goes
   beyond strict derivation, with the inference flagged as
   such.

6. **Scope check.** Per VL-008 rule (b): for every concept,
   term, or claim in the sections above, cite which attached
   file and which section/clause it comes from. If any item
   cannot be cited, name it as out-of-scope and remove it
   from the work above.

Do not include sections beyond these. Do not rate, review, or
suggest. Do not reference any artifact you are not being shown -
speculating about it is out of scope.

---

## Attached files

Attached to this request:

[PRIMARY_SOURCES - re-listed here for clarity]

If any file is missing or appears truncated, stop and say so.
Do not work from a partial source.

---

## Co-upload format note (VL-031 Finding 2)

When the verification request and the primary-source bundle are
co-uploaded as files in the same chat turn (rather than the
request as the chat-turn prompt + bundle as attached files), some
recipients may not recognize the request file as the operative
instruction. The recipient may respond with a capability menu
("a bounded technical assessment, a derivation-only analysis,
..."), or with a synopsis of the request file rather than an
execution of it.

Two correctives are admissible; the requester chooses based on
the chat client's affordances:

- **Filename convention.** Name the request file with a load-
  bearing prefix: `REQUEST_<task>.md` or `EXECUTE_<task>.md`. The
  prefix communicates operative-instruction status; primary-source
  files use no such prefix.

- **Explicit inline turn after upload.** Send a one-line follow-up
  turn after the upload: "Execute the procedure in the request
  file." The follow-up signals operative status explicitly even
  when filename convention is ambiguous.

Both correctives address the same failure mode (recipient does
not distinguish operative-instruction file from primary-source
file). Filename convention is preferable when the chat client
displays filenames prominently; explicit inline turn is more
reliable across clients.

This failure mode was observed at VL-031 T-07: OpenAI's initial
response was a capability menu; second response was a synopsis;
only after an explicit "Execute the four-question procedure in
that file" follow-up did OpenAI shift to derivational mode.
Grok recognized the request file immediately. The recognition
variance is recipient-specific and not predictable in advance,
so the corrective is preventive across all recipients.

---

## Sample question shapes

The template is parameterized for four question shapes. Examples
of each:

- **Property**: "Does the framework distinguish efficiency moves
  from trajectory moves, and is the distinction operationalized?"
- **Consistency**: "Are GR-1 (canon lock) and the spec-defines-
  the-rename candidate GR-2 mutually compatible?"
- **Gap**: "What does the framework not currently track about
  its own methodology evolution?"
- **Behavior**: "How does the framework handle a finding that
  surfaces during a strict-scope commit but is out of scope for
  that commit?"

Question shapes the template is NOT for:

- "Is the framework good?" - no derivable property.
- "Will this approach succeed?" - no artifact-grounded answer.
- "What should the framework do next?" - STATE.md is the
  answer; no derivation needed.
- "Is the canon mathematically sound?" - canon-level question;
  use `verification_request_template.md` instead.
- "How does this compare to <external system>?" - imports
  outside knowledge; forbidden by procedure (a).

---

## Ledger context (informational, not part of the task)

This evaluation, if successful under the procedure above,
becomes a new ledger entry (proposed [LEDGER_ENTRY_NUMBER] or
thereabouts in the project's numbering scheme; the exact number
depends on what else has happened in the repository when the
entry is appended). The entry will cite:

[LEDGER_ENTRY_FIELDS - always includes evaluator identity, date,
procedure adherence, outcome category. Task-specific additions
go here.]

Your response is the artifact. The ledger entry is downstream.

---

## When to use this template vs. the verification-request template

Use `verification_request_template.md` when:

- The task is artifact verification (does X derive faithfully
  from canon / code / manifest).
- Primary sources are canon, code, manifest, tests.
- Outcome categories are Match / Same-set-different-attributions
  / Different-set / Procedure violation, or similar derivation-
  outcome shapes.

Use this template (`cross_model_evaluate_template.md`) when:

- The task is framework-level evaluation (a property,
  consistency, gap, or behavior of the framework's own
  operation).
- Primary sources are STATE.md, the ledger, methodology
  artifacts, restructure artifacts, specs.
- Outcome categories are Property holds / does not hold /
  Under-determined / Reframing required.

The two templates share the VL-008 procedure block, the
scope-check requirement, and the verdict-out-of-scope rule.
They differ in subject matter and outcome shape.

For build tasks (produce new artifact Y satisfying spec Z),
use `build_resumption_request_template.md`. That template
shares the procedural skeleton but has a build-shape submission
format.

---

[OPTIONAL_CLARIFICATIONS - optional final section. Skip if not
needed.]
