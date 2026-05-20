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

The cost of viewing source first is one tool call. The cost of
drafting from inference and discovering divergence later is rework
plus erosion of procedural integrity. There is no case where the
former produces a worse outcome than the latter.

### Self-check

> I'm about to draft something whose form should match an
> established convention. Have I read the actual instances of that
> convention in this session, or am I inferring the form from
> memory / description / partial context? If the latter, the
> one-tool-call source-read takes precedence.

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

The cost of enumeration is bounded (one primitive call, one
view); the cost of a wrong claim about a set is the rework when
the claim turns out to cover non-existent members or miss real
ones.

### Self-check

> I'm about to claim that a set is complete / characterized /
> exhaustive / covered. Have I enumerated the set's members
> against a source-of-truth primitive, or am I asserting the
> characterization from memory or inference? If the latter,
> run the enumeration first.

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

Changes to this file are recorded in the ledger as
methodology-artifact updates, classified as efficiency moves rather
than trajectory moves per VL-017a's distinction.

The file's promotion to `docs/methodology/` does NOT confer
canonical status. The canon is `CANON/canon.md`. This file records
process observations; the canon defines the system specification.
The two operate at different layers and serve different purposes.
