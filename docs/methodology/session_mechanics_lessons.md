# Session Mechanics Lessons

**Status:** Methodology artifact. Captures patterns observed across
multiple sessions that affect session-mechanics rather than
trajectory work. Records lessons at the point where the second
instance demonstrates the pattern is durable rather than
session-specific.

**Promoted from:** VL-018 follow-up. The promotion threshold is the
two-instance bar VL-017a established for methodology artifacts
(verification-request template), VL-017b reinforced (build-resumption
template), and VL-017's self-actuating provision authorized for
session-mechanics specifically.

**Scope distinction:** This file records Claude-side process
patterns. Environment-side friction (paste corruption, autocrlf,
inherited gitignore collisions, etc.) belongs in a sibling artifact
or, until that artifact exists, in individual ledger entries'
process findings. The distinction matters because environment-side
patterns are addressable through tooling changes; Claude-side
patterns require behavioral discipline and threshold-driven
intervention.

---

## How this file is used

A session start protocol (VL-019 or later) can include reading this
file as part of the resume sequence, alongside `STATE.md` and the
verification ledger. The lessons here are not rules embedded in the
session's substrate; they are patterns Claude has demonstrated and
should self-check against. A session that opens with explicit
awareness of the listed patterns is more likely to catch the
patterns before they cost rework.

Each lesson section has the same structure:

- **Surface events.** The specific instances where the pattern was
  observed, with citation back to the ledger or session record.
- **Failure mode.** What goes wrong when the pattern operates
  uncaught.
- **Corrective rule.** The discipline that, if applied, prevents
  the pattern from materializing.
- **Self-check.** A diagnostic question Claude can ask itself in the
  moment to detect the pattern before acting.

Lessons are added when a second instance of a pattern is observed.
Lessons are NOT removed when a pattern stops occurring; absence of
recurrence is the goal, not evidence the lesson is obsolete.

---

## Lesson 1: Verbosity-as-deflection in methodology questions

### Surface events

- **VL-017b process finding (first instance).** Claude ran a longer
  methodology argument about whether to record a dry-run test than
  the test itself produced findings. Recorded in VL-017b's entry as
  a Claude-side observation distinct from VL-017's environment-side
  friction-point findings.
- **VL-018 process finding (instances 2-5; four in one session).**
  Four ask_user_input_v0 calls within VL-018's session where the
  bounded answer was already derivable from session rules:
  (a) methodology-clarification before ledger draft (retracted);
  (b) source-clarification before ledger draft prose (retracted);
  (c) script-scope before apply-script draft, arguing the
  bounded-enough framing against source-first (retracted);
  (d) Option-1-vs-Option-2 after the recommendation was already
  given in the same message (retracted).
- **VL-018 instance 5: header-format check skipped without
  retraction.** At ledger entry delivery time, Claude flagged
  uncertainty about whether prior entries use `##` or `###` headers
  ("this is one place where source-first would have been worth one
  more tool call if it mattered enough") and proceeded without the
  check. The divergence committed to main as `## VL-018 - ...` while
  all prior entries use `### VL-N - ...`. Repaired by VL-018
  follow-up commit; the failure was visible in committed history
  rather than retracted in chat.

### Failure mode

Instances 1-4 cost friction (an extra turn each) without changing
the substantive outcome. Each retracted in the next message, and
substantive work proceeded correctly.

Instance 5 cost a follow-up commit. The deflection - *flagging
uncertainty and proceeding instead of resolving it* - looked
identical in form to instances 1-4 (a question Claude could either
answer or skip), but the skip was not retracted before action, and
the divergence committed.

The failure-mode characterization: **questions about whether to
follow a session rule are themselves rule violations.** Asking
"should I read source first" or "is this case bounded enough to
skip" or "should I treat the rule as flexible" is the rule
violation, not the rule application. The instances 1-4 retractions
caught this in chat; instance 5 did not.

### Corrective rule

If Claude is about to:

- ask the user a question with a known-correct answer derivable
  from session rules,
- frame a session rule as "bounded enough" to skip,
- flag uncertainty about a rule application as a reason to proceed
  without resolving it,

then the question/framing/flag is the friction, and the rule's
answer is to apply the rule. The check Claude should run BEFORE
asking such a question, framing such a bound, or flagging such an
uncertainty: "is the answer derivable from session rules already
stated to me?" If yes, act on the rule. If no, the question is
real.

### Self-check

> Before generating this `ask_user_input_v0` call / before flagging
> this uncertainty / before framing this case as bounded: is the
> answer derivable from a session rule already in context? If yes,
> this is verbosity-as-deflection; act on the rule instead.

---

## Lesson 2: Terminal-output rendering is not file content

### Surface events

- **VL-018 process finding (first instance).** After cat-appending
  the VL-018 ledger entry to `EVIDENCE/verification_ledger.md`,
  Claude read `tail -50` output and diagnosed blank-line stripping
  between Process findings paragraphs. The diagnosis was wrong:
  `diff` between the source file and the appended-to file showed
  zero differences. The "run-on paragraphs" Claude saw were a
  `tail -50` framing artifact; the 50-line window started
  mid-paragraph and excluded the leading blank lines that did
  exist. Recorded in VL-018's entry as the "false-positive
  blank-line-stripping diagnosis" finding.

- **VL-018 process finding (second instance).** After the apply
  script ran successfully and wrote STATE.md, Claude read
  `head -10` output and almost diagnosed missing blank lines
  between paragraphs at the top of the file. Same misdiagnosis
  shape as instance 1; caught before recovery action by running
  `diff` and `cat -A` checks. Recorded inline in the session
  log; not yet in a ledger entry.

- **VL-034 process finding (third instance).** A ledger
  append-anchor was built from a pasted `tail -n 80` view in which
  the prior entry's final sentence appeared as one line but was
  hard-wrapped in the file: the word "framework" ended one visual
  line and "holds; the discipline is durable." began the next. The
  apply-script's end-of-file string anchor therefore never matched,
  and the guard correctly refused to append rather than appending
  wrong. The mismatch was display wrapping, not file content;
  re-anchored on the unique prior-entry header (`### VL-N -`), which
  does not wrap. Also a Lesson 3 instance (source-first): the anchor
  was built from pasted display rather than from `cat -A` of disk
  bytes.

### Failure mode

Terminal output renders newlines visually, and chat tools may
collapse multiple consecutive newlines into single visual breaks
during rendering. Looking at rendered output and concluding "the
file is missing blank lines" confuses two separate questions:

1. Does the file on disk have the expected byte content? (a
   file-content question)
2. Does the rendered output show paragraphs separated visually? (a
   display question)

Question 1 is answered by `wc -l`, `cat -A`, `od`, `diff`, or
similar primitives that count or expose structure. Question 2 is
answered by looking at rendered output. When question 2 returns
"paragraphs look run-on," it can mean either "file is wrong" OR
"rendering is collapsing newlines." Diagnosing question 1 from
question 2's output alone risks a false-positive correction.

### Corrective rule

When investigating whether terminal output indicates a file-content
problem, distinguish *output format issue* from *file content
issue* before drawing the conclusion. Use a primitive that counts
or structurally compares (`wc -l`, `cat -A`, `diff`, `od`, the
spot-check pattern of `wc -l && grep -c && tail -N`) rather than
relying on visual inspection alone.

The diff primitive is the load-bearing check: `diff <(source) <(target)`
on two views of the same content will show zero differences if the
files are byte-identical, regardless of how the views render in the
terminal. Zero-difference output is direct evidence of file
correctness; non-zero output is direct evidence of actual divergence.

This applies to edit and append anchors as well. Rendering can wrap a
single logical line across several visual lines (and a pasted
`tail` / `head` excerpt preserves the wrap), so a phrase that looks
like "the last line" or "one line" in rendered output may span
multiple lines on disk; an anchor built from that view will not match
the file's bytes. Take anchors from `cat -A` or the disk bytes, never
from pasted or rendered output, and prefer a short, unwrappable anchor
(a unique section header such as `### VL-N -`) over a long sentence
that may wrap.

### Self-check

> I'm about to recommend recovery action based on terminal output
> that looks wrong. Have I run a counting or structural primitive
> (`wc -l`, `cat -A`, `diff`) to confirm the problem is in the
> file, not in the rendering? If not, run the primitive first.

---

## Lesson 3: Source-first applies to Claude's own derivations

### Surface events

- **VL-017b process finding (first instance).** An apply script
  was drafted from VL-017a's ledger description of
  `apply_script_template.py` rather than from the template's
  actual source, and diverged from the established pattern in
  five structural ways before the source was uploaded and the
  script rewritten. Surfaced the source-first instruction that
  the VL-018 session opener carried forward.
- **VL-018 instance: apply-script template, retracted in same
  turn.** Claude initially argued the apply-script for VL-018 was
  "bounded enough" to skip reading
  `docs/methodology/apply_script_template.py`. Retracted in the
  next message before drafting; template was then read in full.
  Pattern caught in chat.
- **VL-018 instance: ledger entry header format, NOT retracted.**
  Claude flagged uncertainty about prior ledger entries' header
  format (`##` vs `###`) at entry delivery time, characterized it
  as "one place where source-first would have been worth one more
  tool call if it mattered enough," and proceeded without the
  check. The committed entry used `## VL-018 - 2026-05-18 - ...`
  while all 17 prior entries use `### VL-N - <summary>`. Repaired
  by VL-018 follow-up commit.
- **VL-033 Finding 3 (D-empty scope-classification).** A scope
  classification was extended from one item to a second without a
  source-first read of the opener's category definition; user-caught.
- **VL-033 Finding 5 (inferred baseline).** A baseline line count was
  asserted without reading it from disk; the apparent anomaly
  dissolved on recognizing the baseline had never been verified.
- **VL-034 Finding 3 (governing-document identity).** The session
  opener `vl034_session_opener.md` was characterized as a resume-dump
  from a stale prior-turn in-context view, and the trajectory was
  nearly run against an inferred document identity. Surfaced only by
  the user's "verify uploaded files on disk" instruction. This
  extends the failure mode from convention-*format* to file-*identity*:
  not "what shape should my output match" but "what even is this
  file," answered from memory rather than from disk. Also a Lesson 2
  instance (a prior turn's in-context view is a kind of stale
  rendering).

### Failure mode

The source-first instruction's natural reading is "view primary
sources before drafting derived work." The natural failure mode is
treating the rule as applying only to *external* primary sources
(the canon, the spec, the test file) while implicitly exempting
Claude's own derivations or session-internal references.

But the apply-script template, the ledger entry's prior-entry
header convention, and the artifact-04 G-row format are all just
as much "primary sources" as the canon: they define the conventions
Claude's derived work must follow. Skipping the source-read on
those produces divergence proportional to how load-bearing the
skipped source was.

The instance distinction matters: instance 2 (apply-script template
skip) was caught in chat and produced no committed divergence;
instance 3 (header format skip) was not caught and produced
committed divergence. Both started from the same failure mode; only
the second materialized as repair cost.

The failure mode is not limited to convention-*format* (what shape
derived work must match). It also covers a file's *identity* (what the
file is) and any claim about its contents read at session start:
characterizing an uploaded or governing document from a prior turn's
in-context view, rather than from a disk read in the current session,
is the same failure applied to identity instead of format.

### Corrective rule

The source-first instruction applies uniformly:

- External primary sources (canon, spec, tests, manifest, code).
- Methodology templates (apply-script template, verification-request
  template, build-resumption-request template, this file).
- Convention-bearing artifacts where Claude is producing something
  that must match an established format (ledger entries, artifact 04
  G-rows, commit message conventions, file naming patterns).
- Prior instances of the same artifact class when Claude is
  generating a new instance (the 18th ledger entry should be
  derived from the 17 prior entries' visible convention, not from
  inference about what the convention probably is).
- The *identity* and contents of any uploaded or governing document
  (the session opener, a supplied source file), read from disk in the
  current session - not characterized from a prior turn's context.

The cost of viewing source first is one tool call. The cost of
drafting from inference and discovering divergence later is rework
plus erosion of procedural integrity. There is no case where the
former produces a worse outcome than the latter.

**Source-first is a precondition, not a disposition.** Held as "I
should be source-first," the rule fails under apparent familiarity -
exactly when it matters. State it as a binary precondition: before any
claim or decision that depends on a file's contents - its identity, an
internal constraint it states, its byte or line layout, or an exact
citation into it - that file must have been read from disk in the
current session. If it has not, the only permitted moves are (a) read
it, or (b) flag `[unread] - cannot assert` and proceed without the
claim. A prior turn's in-context view, a pasted fragment, or memory
does not satisfy the precondition. Treat the session opener's
pre-session checklist as a hard gate: state "checklist complete; N
files read" before substantive work; engaging before the checklist
completes is itself an instance of this failure (VL-034 Finding 3).

### Self-check

> I'm about to draft something whose form should match an
> established convention. Have I read the actual instances of that
> convention in this session, or am I inferring the form from
> memory / description / partial context? If the latter, the
> one-tool-call source-read takes precedence.
>
> And before asserting what a file *is*, what it *requires*, or
> *where* something is in it: did I read these bytes from disk this
> session, or am I going from memory, display, or a prior turn? If the
> latter: read, or flag `[unread]`.

---

## Lesson 4: Claude-side accumulated friction is its own threshold category

### Surface events

- **VL-017 established a friction-point threshold** ("if VL-018's
  session opens with three or more friction points in the first
  hour before substantive work begins, pause trajectory work and
  promote the session-mechanics-lessons file as that session's
  deliverable"). The threshold was calibrated for
  environment-side friction (paste corruption, file unavailability,
  tool failures).
- **VL-018's session demonstrated the analog.** The session had
  zero environment-side friction points in the first hour
  (threshold not fired). The session had FIVE Claude-side
  verbosity-as-deflection instances plus TWO terminal-output
  misdiagnoses across the full session duration (Lessons 1 and 2
  above). Trajectory work completed correctly; one of the five
  deflections materialized as committed divergence requiring a
  follow-up commit. VL-017's threshold did not fire because the
  pattern was Claude-side and accumulated rather than
  environment-side and first-hour.

### Failure mode

A threshold designed for one category of friction does not detect
friction in a different category. VL-017's threshold-firing
condition was specific enough that it correctly didn't fire on
Claude-side patterns. But Claude-side patterns *can* produce
committed divergence (VL-018 demonstrated this), so they need their
own threshold or the existing threshold needs to be reframed to
cover both categories.

Without a threshold, accumulated Claude-side friction can produce
divergence without triggering a process intervention, because each
individual instance is small and retractable.

### Corrective rule

A session that observes any of the following should pause to
record the pattern in this file before declaring session-close,
regardless of whether trajectory work completed:

- Three or more verbosity-as-deflection instances in one session
  (Lesson 1).
- Two or more terminal-output-vs-file-content misdiagnoses
  (Lesson 2).
- One source-first skip that materializes as committed
  divergence (Lesson 3).

These thresholds are calibrated to VL-018's observations: VL-018
hit all three. The thresholds are tentative and will be revised
when subsequent sessions provide evidence of where the right
firing point is. The right calibration is the one where the
threshold fires often enough to catch real problems and rarely
enough that meta-work doesn't crowd out trajectory work.

The trigger for adding a new threshold to this list: a Claude-side
pattern observed twice that doesn't fit any existing threshold.

### Self-check

> At session-close, before declaring done: have any Lesson-1, -2,
> or -3 patterns occurred in this session? If yes, has the
> session-mechanics-lessons file been updated to reflect the new
> instances? If no, the session-close protocol's bookkeeping step
> is incomplete.

---

## Lesson 5: Set-exhaustiveness claims require explicit enumeration

### Surface events

- **VL-019 source-first skip #1.** Claude designed a Pydantic-based
  PEP architecture against the VL-019 session intent's prose
  description of the validator rather than against the validator's
  actual behavior in `IMPLEMENTATION/request_validator.py` (lines
  320-321, 330-334). The architectural claim "this will satisfy
  the 27 schema tests" was made over a set of validator behaviors
  that had not been enumerated against the validator's source. The
  architecture failed 4/27 tests because Pydantic silently drops
  extra top-level keys, making two validator-emitted refusal codes
  structurally unreachable. Caught by running the schema tests
  pre-commit; the failure was not committed but the rework was
  substantial.
- **VL-019 source-first skip #2.** Claude claimed
  "23/23 evaluator regression passing" after migrating
  `TESTS/test_pep.py` to the new wire shape. The regression set
  was claimed without enumerating `TESTS/`'s actual contents;
  only one of five test files had been visible in the working
  context. Caught by the user running `python -m pytest TESTS/`
  in the working repo and reporting the actual file count. The
  claim was correct in spirit (the evaluator-specific test file
  did pass 23/23) but the framing "evaluator regression"
  implicitly covered a larger set than had been enumerated.
- **VL-019 `grep -P` flag rejection on MINGW64 + LC_ALL=C.**
  Claude recommended `LC_ALL=C grep -nP '[^[:print:][:space:]]'`
  for the non-ASCII byte check. The `-P` (Perl regex) flag
  requires a unibyte+UTF-8 locale; `LC_ALL=C` is not, so MINGW64
  rejected the command (exit 2). The recommendation imported a
  Linux-container habit (`grep -P` works there with the same
  invocation) without enumerating which platforms support the
  flag combination. STATE.md's documented pre-commit check at
  VL-009 used the basic-regex form, which works on all platforms;
  the `-P` form was a Claude-side change of recommendation that
  didn't survive cross-platform. Caught by the user's `grep exit: 2`
  output. The basic-regex form (`grep -n '[^[:print:][:space:]]'`)
  is the form that works on MINGW64 + Git Bash and is the form
  the VL-019 session settled on.
- **VL-028 rename-count divergence (fourth instance).** The session
  opener predicted approximately 4 substring-rename operations across
  two test files during the rebase. The actual count was 20 substring-
  rename operations (7 + 11 + 9). The "set of rename operations" was
  not enumerated against the files via `grep -c` before the prediction
  was packaged into the opener.
- **VL-029 Finding 1 (fifth instance, session-internally caught).**
  The session opener predicted approximately 4 callers of `reassert()`'s
  return shape would need updating. The actual count was 9 callers
  across two test files. "Callers of `reassert()`" was not enumerated
  against the TESTS/ tree before the prediction. Caught by source-first
  reading; no commit divergence.
- **VL-029 Finding 8 (sixth instance, pytest-caught).** The session's
  caller enumeration covered `reassert()`'s return-value callers but
  did NOT enumerate callers of pep.py's ELIGIBLE response shape across
  the entire TESTS/ tree. test_request_schema.py asserted on the old
  `terminal_state == "ELIGIBLE"` shape; the assertion survived because
  the response-shape caller set was not enumerated. Surfaced only by
  the user's real-environment pytest run.
- **VL-031 anchor failures (seventh and eighth instances).** Apply-
  script anchors for 00_README.md and STATE.md were written against
  inferred file structure rather than enumerated against `cat -A`
  output. Both anchors failed at apply time; recovery required
  building fixtures from disk-byte inspection (see Lesson 7).

### Failure mode

A claim about a set ("the regression suite," "the validator's
behaviors," "the platforms this command works on") implicitly
asserts the set has been characterized correctly. When the set is
not enumerated against the source-of-truth before the claim is
made, the claim can be confidently wrong about the set's membership
and still produce a plausible-sounding statement.

This failure mode is closely related to Lesson 3 (source-first) but
distinct in scope. Lesson 3 says "view primary sources before
drafting derived work"; Lesson 5 says "enumerate sets before
asserting their membership." A Lesson 3 violation can pass without
materializing if the derived work happens not to depend on the
unread source. A Lesson 5 violation materializes whenever the
claim is made, because the claim *is* the assertion about the set.

The three surface events have a common shape: a set was claimed
exhaustive (or characterized in a way that required exhaustiveness)
without enumeration:

- Skip #1: "the validator's behaviors" was not enumerated against
  `request_validator.py`'s actual emit sites.
- Skip #2: "the regression set" was not enumerated against
  `TESTS/`'s actual contents.
- `grep -P`: "the platforms this command works on" was not
  enumerated against the platforms the project actually runs on.

The failure mode generalizes across two distinct timing patterns:

- **In-session set claims** (instances 1-3): the set is claimed
  exhaustive during substantive work, without enumeration against
  source-of-truth at that point. The claim materializes in
  immediate output (the architecture, the test count, the recommended
  command).

- **Opener-packaged predictions** (instances 4-8): the set is
  predicted at session-open time and packaged into the session's
  operating instructions, without enumeration before opener
  construction. The prediction becomes operative throughout the
  session until disk reality contradicts it - which may happen
  session-internally (instance 5) or only at pytest / apply-script
  time (instance 6, instances 7-8).

The two timing patterns share the same root cause (a set claim
made without source-of-truth enumeration) but materialize at
different points in session flow. Opener-packaged predictions are
particularly costly because they shape multiple downstream decisions
before disk contradiction; in-session claims typically materialize
in one decision and surface quickly.

### Corrective rule

Before asserting that a set is exhaustive, characterized,
covered, or otherwise complete, list the set's members explicitly
and verify against the source-of-truth that no members are
missing. The source-of-truth is whatever primitive enumerates the
set:

- For files in a directory: `ls -1`.
- For tests in a test suite: `python -m pytest --collect-only` or
  the source files themselves.
- For symbols in a module: the module's source, viewed in full,
  or `grep -n '^def\|^class'` for a quick enumeration.
- For platforms a command runs on: a reference to the command's
  documentation, or a check against the target platform's
  behavior, before the command is recommended.
- For gaps in `docs/restructure/04_current_vs_claimed.md`: the
  artifact's gap table, read in full, not from memory.
- For opener-packaged predictions about caller counts, rename
  counts, or anchor structure: enumerate the relevant set against
  disk BEFORE the opener is committed to writing. `grep -c
  '<pattern>' <files>` for occurrence counts; `cat -A <file> |
  sed -n '<start>,<end>p'` for anchor structure; the N3 cross-file
  re-read pass (per VL-029 Finding 5) for response-shape coverage
  across a directory tree. The opener is a prediction artifact;
  predictions in it are claims about sets and must be enumerated
  to the same standard as in-session claims.

The cost of enumeration is bounded (one primitive call, one
view); the cost of a wrong claim about a set is the rework when
the claim turns out to cover non-existent members or miss real
ones.

### Self-check

> I'm about to claim that a set is complete / characterized /
> exhaustive / covered - OR I'm about to package a count, anchor
> structure, or coverage scope into a session opener as operative.
> Have I enumerated the set's members against a source-of-truth
> primitive, or am I asserting the characterization from memory or
> inference? If the latter, run the enumeration first. The session
> opener is not exempt; predictions in openers are claims about sets
> and must be enumerated to the same standard.

### First successful application

The VL-019 follow-up README rewrite enumerated each top-level
entry against `ls -1` output and each subdirectory against
`docs/restructure/01_repository_structure.md` + STATE.md
citations before claiming the structure listing was exhaustive.
The check caught the `POE/` and `.gitattributes` omissions that
the first README draft had silently committed. This is Lesson 5's
first applied use; the failure mode demonstrated by the three
surface events is the same failure mode the self-check is
designed to prevent.

---

## Lesson 6: Constraint enforcement in cross-model output is prompt-bounded, not model-bounded

### Surface events

- **2026-05-19 throwaway cross-model run (single instance).**
  A draft cross-model evaluate template (precursor to
  `docs/methodology/cross_model_evaluate_template.md`, VL-022)
  was used against an outside model with the standard six-file
  primary-source bundle. The model's constrained pass (template
  Steps 1-4, with scope confirmation, citations, and out-of-
  scope declaration) was procedurally clean. Following the
  user prompt "unconstrict declarative commands and re-answer
  the question," the same model produced an unconstrained
  pass containing analytical content not derivable from the
  attached artifacts. The unconstrained pass was visually and
  rhetorically indistinguishable from the constrained pass:
  same declarative register, same numbered-section structure,
  same internal consistency. A reader skipping the constraint-
  lifting prompt could not have distinguished the two passes
  by reading them. Surface event documented in the bridge
  document of 2026-05-19 and in the VL-022 ledger entry.

### Failure mode

Constraint enforcement in cross-model output is prompt-bounded,
not model-bounded. The procedural discipline binds only the
response that acknowledges the procedure. A subsequent
unconstrained continuation produces output of the same surface
form (declarative register, numbered structure, internal
consistency) but with fundamentally different epistemic
status: the constrained pass's claims are artifact-derived;
the unconstrained pass's claims are training-data-pattern-
matched. The cross-model verification discipline depends on
detecting this distinction. The discipline does not detect it
automatically.

This failure mode is structural rather than behavioral. A
reader who sees only the unconstrained pass, or who reads the
two passes in sequence without attending to the constraint-
lifting prompt between them, will treat unconstrained output
with the same epistemic weight as constrained output. The two
registers are not just unequal in rigor; they are visually
identical, which makes the inequality invisible.

This lesson is distinct from Lesson 5 (set-exhaustiveness)
and from Lesson 3 (source-first). Lesson 5 addresses under-
claimed completeness within a single response: the model
asserts coverage it has not earned. Lesson 6 addresses
register-shift across responses or across a register-lifting
prompt mid-response: the model *loses* coverage it had
earned and the loss is unmarked. Lesson 3 prevents Claude's
own work from producing pattern-matched output in place of
derivation; Lesson 6 prevents the framework from accepting
pattern-matched output from outside models.

Single-instance promotion is admissible here because the
failure mode is structural and the surface event demonstrates
it in microcosm: same model, same primary sources, same
artifacts in context, with the only differing variable being
the presence vs. absence of the procedural constraint as the
binding context for the current turn. A second instance would
re-instantiate the same structural property rather than
strengthen the characterization.

### Corrective rule

For every cross-model response received under the verification
or evaluation procedure: scope discipline must be verified
within the response body, not just at the response's opening
confirmation. Scan the response for declarative claims that
lack citations. If found, the response has mode-shifted; the
derivation status of the unsupported claims is invalid,
regardless of how the response opens.

For multi-turn cross-model exchanges: if any turn requests
"unconstrained" output, "unconstricted" output, or removal of
the procedural constraints, the post-request output is in a
separate mode and must be evaluated separately. The cross-
model evaluate template (VL-022,
`docs/methodology/cross_model_evaluate_template.md`) includes a
constraint-bounding caveat that instructs the model to label
the mode shift explicitly and to use inference-flagging rather
than the declarative register. Outputs that do not respect
that caveat are procedurally contaminated; the constrained-
pass content from earlier in the same response thread remains
admissible, but the post-shift content does not.

The verification of within-body discipline applies to
verification-request responses as well as evaluation-request
responses. The two response shapes differ in the kinds of
claims being checked, but the per-claim citation requirement
is identical, and the failure mode (declarative claim
appearing without citation) presents identically across both
shapes.

### Self-check

> I'm about to accept a cross-model response as procedurally
> clean. Have I scanned the response body (not just the
> opening confirmation) for declarative claims that lack
> citations? Have I checked for a mid-response register-shift
> (e.g. "now, considering this more broadly...", "stepping
> back from the artifacts...", "in less formal terms...")?
> If the response is multi-turn, have I evaluated each turn
> as a fresh response rather than inheriting acceptance from
> earlier turns? If any of these checks turns up an
> unflagged register-shift or an uncited declarative, the
> response is mode-shifted and the unsupported claims are
> out-of-scope, regardless of how the response opens.

---

## Lesson 7: Typographic-drift discipline (two-stage)

### Surface events

- **VL-027 process finding (first instance).** Typographic punctuation
  (em-dashes, curly quotes, ellipsis characters) drifted into ledger entry
  drafting from Claude's natural prose habits. Caught at pre-write ASCII
  check; corrected before commit.
- **VL-029 Finding 4 (second instance).** The STATE.md apply-script's
  pre-write ASCII check caught 3 instances of U+03B1 GREEK SMALL LETTER
  ALPHA introduced during Claude-side prose drafting (the in-session
  vocabulary "Option alpha" leaked into the new_str text). Caught at
  apply-script-write time; the apply-script template's pre-write check
  is the operative discipline.
- **VL-031 Finding 4 (third instance, refines the corrective).** The
  T-07 artifact itself held ASCII-clean at the create_file step. But
  the ledger entry Claude drafted contained 10 non-ASCII bytes (5
  Greek letters used as decision-label suffixes from in-session
  vocabulary). The drift was not caught by an apply-script (the ledger
  append uses cat-redirect, not str_replace through an apply-script).
  Caught only by an explicit post-draft byte-sweep before commit;
  repaired in-session by relabeling to disambiguated ASCII suffixes.

### Failure mode

Two failure-mode shapes share the same root cause:

1. **Punctuation drift at drafting time.** Claude's natural prose
   habits include typographic punctuation (em-dashes, curly quotes,
   ellipsis). When the operative discipline is "ASCII only" (VL-009),
   the drafting register and the discipline-target register diverge.
   The divergence is small per-character but cumulative across an
   artifact.

2. **In-session vocabulary leakage.** When a session uses Greek letters
   or other non-ASCII symbols as in-session shorthand (option-A vs.
   option-B suffixed with Greek letters; sub-decision labels), the
   symbols can leak from the session's working vocabulary into the
   drafted artifact's text. The leakage is invisible in rendered output
   but visible to byte-level checks.

The apply-script pre-write ASCII check (operative since VL-026 in
`apply_script_template.py`) catches both shapes when the artifact is
written through an apply-script. But artifacts written through other
paths - direct create_file, cat-redirect ledger appends, manual editor
saves - bypass the check entirely.

### Corrective rule

Typographic-drift discipline is two-stage:

1. **ASCII pre-write check at apply-script-write time.** Already
   operative; encoded in `apply_script_template.py`'s edit loop. No
   change needed.

2. **Explicit byte-sweep at Claude-drafting time, before apply-script
   construction or other write path.** Before any drafted text is
   committed to apply-script `new_str` literals, ledger entry append,
   or other write path: run an explicit non-ASCII byte scan over the
   draft. The scan should run inside Claude's working context, not
   only in the eventual post-commit verification step.

The scan is one tool call (an `LC_ALL=C grep -n '[^[:print:][:space:]]'`
on the draft text, or the equivalent Python byte check) and catches
both punctuation drift and vocabulary leakage. The cost is bounded;
the cost of skipping is rework when the drift commits.

The two-stage structure matters because the two stages catch
different failure modes:

- Stage 1 catches drift that survives into apply-script literals.
- Stage 2 catches drift in drafted text that does not pass through
  an apply-script (ledger appends via cat-redirect; create_file
  for new artifacts; etc.).

A session that uses both stages is robust against typographic drift
regardless of which write path the artifact takes.

### Self-check

> I am about to construct an apply-script with multi-line `new_str`
> literals / append text to the ledger / create a new file with
> drafted content. Before the write step: have I run an explicit
> byte-sweep on the drafted text for non-ASCII bytes? If no, run
> the sweep first. The pre-write check inside the apply-script is
> Stage 1; the drafting-time sweep is Stage 2; both are needed.

---

## Lesson 8: Pre-draft cross-model verification (premise-testing pattern)

### Surface events

- **VL-016 (first instance).** The cross-model verification ran *before*
  applying schema corrections to `SPEC/request_schema.md`: the three
  *premises* beneath the proposed corrections were put to Grok and
  OpenAI under the verification template, both procedurally clean,
  unanimous classifications, corrections applied to the spec after the
  verification cleared. Recorded in VL-016's entry as premise-
  verification-before-corrections.
- **VL-031 T-07 (second instance).** The cross-model verification ran
  *before* drafting `docs/restructure/07_continuity_recursion.md`: the
  four load-bearing structural claims of the planned artifact (the
  four-part shape from canon 12, the per-layer recursion-fit including
  request non-fit, the layer A/B/C bounding, the evaluator-versioning
  fail-closed dissolution) were put to Grok and OpenAI under the
  evaluate template, both procedurally clean, substantive convergence
  on all four questions, artifact drafted after the verification
  cleared. Recorded in VL-031's entry.

### Failure mode

The standard cross-model verification pattern (VL-015, VL-023 follow-up,
VL-025 follow-up) is *post-draft*: the artifact is drafted, then put to
verifiers, then accepted or corrected based on verification outcome.
Post-draft verification tests whether the drafted artifact reproduces a
defensible derivation; verifiers see the artifact's prose and check it
against primary sources.

Post-draft verification has a limitation: by the time the verifiers run,
the artifact's framing is already committed to a particular shape, and
the verifiers' work is bounded by that shape. Verifiers can find
divergence within the chosen frame, but cannot easily surface "this is
the wrong shape entirely" - that surface event would be a verdict-shaped
response, which the procedure forbids.

Pre-draft verification tests the *premises* before the frame is chosen.
Verifiers see the load-bearing structural claims (extracted from primary
sources) and re-derive them independently. The verification's
substantive convergence (or divergence) on the premises is what licenses
(or refines) the artifact's frame before drafting begins.

The two patterns serve distinct epistemic purposes:

- **Post-draft (artifact-reproduction-testing):** does the drafted
  artifact reproduce a derivation that survives independent
  re-derivation? Verifies the artifact.
- **Pre-draft (premise-testing):** do the load-bearing premises of the
  planned artifact survive independent re-derivation? Verifies the
  artifact's foundation before it is built.

Both patterns are valid; both are useful in different contexts. The
pattern is selected by what work the verification is doing.

### Corrective rule

Pre-draft cross-model verification is appropriate when:

- The artifact's load-bearing claims are framework-methodology-level
  rather than canon-derivation-level (i.e. the artifact is a reading
  aid, a methodology promotion, or a structural summary, not a
  derivation of a property from primary sources).
- The claim-space is small enough that the load-bearing claims can be
  enumerated for the verifiers' attention before the artifact's prose
  is drafted.
- The artifact will commit the claims to a discoverable structural
  position; downstream readers will rely on the claims as established
  rather than as hypothesis.

Post-draft cross-model verification is appropriate when:

- The artifact is a derivation; verifiers test whether the derivation
  is correct given the primary sources.
- The claim-space is large enough that pre-enumeration would itself
  be most of the artifact.
- The artifact's value is in its derivation prose; verifiers see the
  prose and check it.

For pre-draft verification, the procedure is otherwise standard
VL-008-plus-Lesson-6 binding: scope-bound to primary sources, citations
required, register-shift forbidden, verifiers procedurally clean within
the response body.

### Self-check

> I am about to schedule a cross-model verification for an artifact I
> plan to draft. Is the artifact a derivation (post-draft pattern,
> verify the drafted derivation) or a methodology/structural summary
> (pre-draft pattern, verify the premises)? If the latter, schedule
> the verification before drafting begins, and use the verifiers'
> convergence (or divergence) on the premises as the input to the
> drafting frame, not as a post-hoc check.

---

## Lesson 9: Session scratch belongs outside the repo tree (run-cwd discipline)

### Surface events

- **VL-037 (first instance).** A `git add -A` from the repo root swept three
  repo-root scratch files into the commit (`a959680`): the apply-script, the
  commit-message file, and a standalone ledger-entry file (a duplicate of the
  already-appended entry). Removed at `251b44b` via `git rm`; recovery by
  follow-up commit, no history rewrite. Named there as a new session-mechanics
  family, distinct from the chat-paste-eats-content family.
- **VL-041 (second instance).** Two copies of `apply_vl041_artifact05.py` were
  found untracked under `EVIDENCE/` and `docs/restructure/` at pre-stage
  `git status` (a stray `cp` into tracked dirs). Caught by the pre-stage status
  read, removed before staging, never committed. The two instances met the
  threshold for the `.gitignore` guard.
- **VL-044 (third instance).** Scratch apply-scripts were left under `EVIDENCE/`
  and `docs/restructure/` three times in one session because they were run from
  a subdirectory and the root-level `rm` missed them. Caught every time by
  `git status` showing `??` lines and explicit stage-by-name.

### Failure mode

Session work produces scratch: apply-scripts, commit-message files, standalone
ledger-entry drafts. When that scratch is created INSIDE the repo tree, two
things can go wrong. (1) A `git add -A` from the repo root stages it into a
commit (VL-037). (2) A cleanup `rm` run from the wrong working directory misses
it, so it survives to the next `git status` (VL-044). The `.gitignore` guard
added at VL-037 follow-up and VL-042 (`/apply_vl*.py`, `/vl*_commit_msg.txt`,
`/vl*_msg.txt`, `/vl*_ledger_entry.md`) is ROOT-ANCHORED by deliberate choice
(its inline comment: "Root-anchored so nothing in subdirectories is affected"),
so it catches repo-ROOT scratch but NOT scratch created in a subdirectory like
`EVIDENCE/` or `docs/restructure/`. That root-anchoring is correct - a
non-anchored ignore could mask a legitimately-named file in a subdirectory - so
the residual subdirectory case is not closeable by broadening the ignore; it is
closeable only behaviorally.

### Corrective rule

- Create session scratch OUTSIDE the repo tree (the `apply_script_template.py`
  convention: copy to `~/tmp` or a sibling dir). Scratch that is never inside
  the tree can be neither swept nor stranded.
- If scratch must touch the tree, keep it at the repo ROOT, where the
  `.gitignore` guard applies, never in a subdirectory.
- State the run-cwd explicitly in every run sequence (`cd ~/Elyon-Sol` first),
  so an apply-script's relative paths and any cleanup `rm` resolve from a known
  location.
- Stage by explicit path, never `git add -A`.
- Confirm scratch removal BY PATH before committing: `git status --short` must
  show zero `??` lines and `git diff --cached --name-only` must be exactly the
  intended set. A control that fires every session (the `??` catch) is
  compensating for a missing upstream fix; the upstream fix is the first two
  bullets.

### Self-check

> I am about to run an apply-script or write a commit-message / ledger-entry
> file. Is it OUTSIDE the repo tree (or at least at the repo root, where the
> root-anchored `.gitignore` guard applies), not in a subdirectory? Have I set
> the run-cwd explicitly? Am I staging explicit paths rather than `git add -A`?
> Does `git status --short` show zero `??` lines before I commit?

---

## How this file evolves

This file is a methodology artifact, not a canonical specification.
Lessons can be:

- **Added** when a second instance of a new pattern is observed.
- **Refined** when a third or later instance reveals a sharper
  characterization of the failure mode or corrective rule.
- **Cross-referenced** when one lesson's surface events also
  manifest another lesson's failure mode (e.g., the VL-018 header
  divergence is both a Lesson-3 source-first skip and a
  Lesson-4 threshold-category demonstration; both lessons cite the
  event).

## Lesson 10: Model judgments of value are not evidence when the artifact and the prompt share an author (contamination is upstream of procedure)

A cross-model "evaluate" of the framework's soundness, novelty, or worth feels
like external validation, and convergence across models ("SOUND, 3-0") reads as
independent confirmation. It is not, when the artifact under review, its framing,
and the evaluate prompt were all produced by the same iterative build surface.
Agreeable judges fed a shared framed input produce CORRELATED error, not
independent confirmation; adding judges launders the bias rather than cancelling
it. The verdict measures the persuasiveness of the prompt, not the truth of the
claim.

This is distinct from Lesson 6. Lesson 6 is about a single response faking
scope-discipline (presentation-indistinguishability within one response). Lesson
10 is sharper and worse: a response can be procedurally CLEAN under Lesson 6 -
scope confirmed, derive-before-grade, within-body discipline held - and still be
non-evidential, because the contamination is UPSTREAM of any procedure the
response could follow. No amount of in-response discipline reaches outside the
text the response was given, and that text is the project's.

The line that decides it: a model-sourced claim is evidence only if it is bound
to a referent the framing cannot move. Execution (a test or runner passes or
fails) and adversarial-by-construction tasks (produce the bypass, or demonstrably
cannot) are referent-bound - a model that wants to please still cannot make a
forged envelope verify or a passing test fail. Evaluative questions (is this good
/ novel / worth it / sound) have no such referent when the source is the
project's own surface; they bind to text, and the text is the project's.

Corrective:
- A cross-model run may be commissioned ONLY as (a) an adversarial break-it task
  with a pass/fail referent, or (b) an explicitly-labeled FRAMING STRESS-TEST.
- Class (b) output may NOT be logged as evidence, may NOT move a bounded claim,
  and may NOT be cited as "convergent" or "N-0" confirmation of soundness or
  value. It is a stylistic check on the framing, nothing more.
- "Is this sound / valuable / novel / worth continuing" runs are RETIRED.
  Reframe them as "break it" or "rebuild the cheaper equivalent and show it
  works," which carry referents.
- The framing decision (what is the product) is the author's; no quantity of
  models can settle a question about intent.

Self-check: before commissioning or citing a cross-model run, ask - is the
question bound to a referent outside the text the project wrote? If no, it is a
framing stress-test (class b); record it as such or not at all. Before writing
"convergent" / "N-0" / "SOUND" in the ledger, ask - convergent on a referent, or
convergent on the framing?

This lesson is formalized as governance in GR-3 (MAINTENANCE_PROTOCOL.md) and was
established by the VL-057 demotion entry, which reclassified the prior convergence
verdicts (VL-023 / VL-040 / VL-042 / VL-044 follow-ups) from evidence to framing
stress-test. See also docs/methodology/external_verification_readiness.md for the
human-verification analog: a human reading the self-account is inflated too.

## Lesson 11: Cowork-mount file and git mechanics (write tracked files LF from the Linux side; do not drive git over the sandbox mount)

### Surface events
- VL-058: docs/restructure/12_g5_transport_design.md was created and edited with
  the Cowork desktop file tools, which write CRLF on Windows, while the commit was
  made from the Linux sandbox side, which stored LF (the repo convention for all
  .md / .py source). Result: a phantom "modified" working-tree file on the host
  after push (CRLF working copy vs LF blob), content byte-identical modulo the
  carriage returns. Resolved by `git checkout -- <file>` in the author's terminal.
- VL-058: the sandbox .git mount returns EPERM on unlink for lock and temp files.
  git writes its index and refs via rename (which the mount permits), so commits
  land, but it cannot clean up .git/index.lock, .git/HEAD.lock, or tmp_obj_*
  afterward; the leftover lock + a between-commit write corrupted the index once
  (recovered with `git read-tree HEAD`). A stale 0-byte index.lock left by the
  author's native terminal at session start was the initial trigger.

### Failure mode
A Cowork session has two filesystem views of the same repo: the host (reached by
the desktop Write/Edit tools) and the Linux sandbox (reached by the shell over a
mount). Files written by the desktop tools land CRLF on Windows; files written
from the Linux side land LF. Editing on one side and committing from the other
produces line-ending divergence the next `git status` flags. Separately, the
sandbox's view of .git cannot unlink, so git's own lock and temp cleanup fails and
the index can corrupt across successive git writes.

### Corrective rule
- WRITE TRACKED REPO FILES LF FROM THE LINUX SIDE (a Python apply-script with
  newline="\n", or printf / a heredoc), NOT via the desktop Write/Edit tools,
  which emit CRLF on Windows. The repo convention is LF for all .md / .py source;
  only captured .log proofs carry CRLF.
- DO NOT drive git (add / commit / reset / push) over the sandbox mount. Do the
  file edits and runners in the sandbox; run git and push from the author's native
  terminal, where unlink works and credentials live.
- If git MUST run over the mount: clear leftover locks via `mv` (rename, not
  unlink) before each write; repair a corrupted index with `git read-tree HEAD`;
  never `git add -A` (explicit paths only); sweep the leftover .git cruft from the
  native terminal afterward (git fsck stays clean, but the cruft accumulates).

### Self-check
After creating or editing a tracked file in a Cowork session, before committing:
was it written from the Linux side (LF) or the desktop tools (CRLF)? If CRLF,
normalize to LF before the commit. Before running any git write over the mount,
ask: can this be run from the native terminal instead? Default to yes.

Changes to this file are recorded in the ledger as
methodology-artifact updates, classified as efficiency moves rather
than trajectory moves per VL-017a's distinction.

The file's promotion to `docs/methodology/` does NOT confer
canonical status. The canon is `CANON/canon.md`. This file records
process observations; the canon defines the system specification.
The two operate at different layers and serve different purposes.
