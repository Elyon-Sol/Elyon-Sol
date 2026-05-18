# Cross-model verification request - [TASK_ID]

This is a verification request prepared under the procedure
established in `EVIDENCE/verification_ledger.md` entry VL-008.

Read this entire document before doing the task. Read the
"Procedure" section twice. The procedure is load-bearing: a
response that deviates from it carries no verification weight,
regardless of its conclusions.

---

## Template usage

This is a parameterized template. To produce an actual
verification request, replace every `[BRACKETED_TOKEN]` with
task-specific content, then delete this "Template usage"
section.

The template is derived from two completed verification
requests that produced procedurally-clean responses from two
verifiers each:
- `verification_request_vl014.md` (verified the schema-shape
  derivation; produced VL-015)
- `verification_request_vl016_premises.md` (verified the
  premises beneath VL-016's corrections; produced VL-016)

Both followed VL-008's procedure; both produced four total
verifier-runs (Grok x2, OpenAI x2) with unanimous procedural
adherence. The shape below is the genuine common structure.

Tokens to fill in:

- `[TASK_ID]` - e.g., "VL-019" or "VL-016 premises" or
  whatever names the verification round in your ledger.
- `[TASK_VERB]` - the operative verb for this verification.
  Examples: "derive" (for derivation tasks),
  "classify" (for premise-classification tasks),
  "determine" (for boundary-classification tasks),
  "identify" (for gap-surfacing tasks).
- `[TASK_DESCRIPTION]` - one-paragraph statement of what the
  verifier is being asked to do, with the output shape named.
- `[PRIMARY_SOURCES]` - list of attached files, with one-line
  description of each and a note on which is load-bearing vs.
  secondary if applicable.
- `[TASK_BOUNDARY]` - what the verification IS, in terms of
  the specific question(s) being answered. Distinct from what
  the verifier is asked to PRODUCE.
- `[TASK_NEGATIVE_DEFINITION]` - what `[TASK_VERB]` does NOT
  mean, enumerated as bullets. Always includes verdicts,
  ratings, and suggestions as out-of-scope. Other negatives
  are task-specific.
- `[OUTCOME_CATEGORIES]` - the named outcome categories the
  verifier will classify into. Match the categories to the
  task shape:
    - For derivation tasks: Match / Same-set-different-
      attributions / Different-set / Procedure violation.
    - For premise-classification tasks:
      Supported / Contradicted / Under-specified / Reframing
      required.
    - For other tasks: invent the appropriate set; ensure
      "Reframing required" or equivalent is always available
      so verifiers can flag ill-formed premises rather than
      silently substitute.
- `[STATUS_TRANSITIONS]` - what the verification result
  implies for the artifact's ledger status (e.g.,
  "SINGLE-SOURCE -> CONFIRMED on Match;
   SINGLE-SOURCE -> DISPUTED on disagreement").
- `[OUT_OF_SCOPE_BOUNDARIES]` - optional section listing
  specific things the verifier should NOT try to derive,
  classify, or address. Used when the artifact under
  verification covers more ground than the verification
  question. Skip if the verification question is the whole
  scope.
- `[SUBMISSION_STRUCTURE]` - the named sections of the
  required response, in order. Always ends with "Scope
  check" per VL-008 rule (b). The structure should be the
  minimum that lets a future ledger reader trace the
  verification result back to primary sources.
- `[LEDGER_ENTRY_NUMBER]` - the proposed VL-NNN number for
  the ledger entry this verification will produce. Often
  uncertain at request-prep time; use the form "proposed
  VL-NNN or thereabouts."
- `[LEDGER_ENTRY_FIELDS]` - what the ledger entry will
  cite. Always includes verifier identity, date, procedure
  adherence, outcome category. Task-specific additions
  permitted.
- `[OPTIONAL_CLARIFICATIONS]` - a final section for any
  clarifications the verifier needs that don't fit
  elsewhere. Used in VL-016 premises to explain why the
  corrections themselves were withheld. Skip if not needed.

After filling in the tokens, run the ASCII check before
sending to verifiers:
```
LC_ALL=C grep -n '[^[:print:][:space:]]' <filled-template>
```
Expected: empty.

---

## What you are being asked to do

[TASK_DESCRIPTION]

Primary sources attached:

[PRIMARY_SOURCES]

[TASK_BOUNDARY]

---

## Procedure (VL-008)

Three rules govern this verification. All three must hold or
the response is discarded:

(a) **Scope-bound to primary sources.** Your work may use
    only the attached files. Material from anywhere else -
    your training data about Elyon-Sol, prior conversation
    history, the project's GitHub, related concepts you happen
    to know - is OUT OF SCOPE.

(b) **Scope-adherence is checkable.** At the end of your
    response, include a section titled "Scope check" listing
    every concept, term, or claim used in your work. For each
    one, cite which of the attached files it comes from and
    which section/clause within that file. If any item in
    your work cannot be cited to one of the attached files,
    name it explicitly under "Scope check" as out-of-scope and
    remove it from your work.

(c) **Prior project exposure is permitted** if (a) and (b)
    hold. You may have seen Elyon-Sol material before. That
    doesn't disqualify you. What disqualifies the response is
    referencing material not derivable from the attached files,
    even if true.

This procedure was established in VL-008 because earlier
verification attempts ranged outside the supplied artifacts and
reached conclusions that smoothed over gaps rather than
identifying them. The variable that mattered was task-to-source
binding, not memory cleanliness.

---

## What "[TASK_VERB]" means (and what it does not mean)

[TASK_VERB] MEANS: [task-specific positive definition citing
which canon sections, envelope clauses, or other primary-source
locations to consult; what determinations to make; what output
shape to produce].

[TASK_VERB] DOES NOT MEAN:

[TASK_NEGATIVE_DEFINITION - bulleted list. Always includes:]
- "Tell me whether [artifact X] is good." That's code review,
  not [TASK_VERB]. Verdicts carry no verification weight under
  VL-008.
- "Suggest improvements." Out of scope; the task is
  [TASK_VERB], not co-design.
- "Compare with how other systems do this." Out of scope;
  only the attached files are in scope.
- "Rate the quality." Out of scope; canon is locked and
  verdict-shaped responses carry no weight.

[Task-specific negative-definition bullets here.]

If you find yourself wanting to write a sentence that doesn't
trace to a specific clause in one of the attached files, that
sentence is out of scope. Either find the clause that supports
it or remove it.

---

## What outcome means what

Your work will be classified into one of these outcome
categories:

[OUTCOME_CATEGORIES - enumerated with one-paragraph definition
each]

A procedurally-available fallback outcome: **Reframing
required.** If the task as stated is ambiguous, ill-formed, or
contains an implicit claim you cannot evaluate without
reformulation, name the reformulation and then evaluate the
reformulated task. Do not silently substitute a different
question.

These outcomes are derivation outcomes. They are NOT verdicts
on the artifact, on the project, or on anything you are not
being shown. Ratings, approvals, quality judgments, and
verdict-shaped language are out of scope per VL-008's
foundational rule that verdicts carry no verification weight.

Status implications: [STATUS_TRANSITIONS]

All listed outcomes are useful. None is a failure of the
verification; only a procedure violation under VL-008 (a) or
(b) is.

---

## What you do NOT need to address

[OUT_OF_SCOPE_BOUNDARIES - optional section. If the verification
question is narrower than the artifact under verification, list
the parts of the artifact that are out of scope for this
verification round. Skip this section if not applicable. Used
in VL-014 to exclude refusal reason codes, PEP boundary
behavior, rejected shapes, and open questions from the schema
derivation task.]

---

## Submission format

Respond in this structure, in this order:

```
[SUBMISSION_STRUCTURE - named sections, one paragraph each
describing what goes in that section. Always ends with:]

## Scope check

[For every concept, term, or claim in the sections above,
cite which attached file and which section/clause it comes
from. If any item cannot be cited, name it as out-of-scope and
remove it from the work above.]
```

Do not include sections beyond these. Do not rate, review, or
suggest. Do not reference any artifact you are not being
shown - speculating about it is out of scope.

---

## Attached files

Attached to this request:

[PRIMARY_SOURCES - re-listed here for clarity]

If any file is missing or appears truncated, stop and say so.
Do not work from a partial source.

---

## Ledger context (informational, not part of the task)

This verification, if successful under the procedure above,
becomes a new ledger entry (proposed [LEDGER_ENTRY_NUMBER] or
thereabouts in the project's numbering scheme; the exact number
depends on what else has happened in the repository when the
entry is appended). The entry will cite:

[LEDGER_ENTRY_FIELDS - always includes verifier identity, date,
procedure adherence, outcome category. Task-specific additions
go here.]

Your response is the artifact. The ledger entry is downstream.

---

[OPTIONAL_CLARIFICATIONS - optional final section for
clarifications that don't fit elsewhere. Used in VL-016
premises to explain why the corrections themselves were
withheld from the verifier. Skip if not needed.]
