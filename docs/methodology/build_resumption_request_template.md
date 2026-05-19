# Build-resumption request template

A parameterized prompt artifact for handing a build-order step to a
fresh model session (Grok, OpenAI, or any other model) under the
VL-008 procedural posture adapted for build.

## When to use this template

When a build-order step (named in a SPEC artifact's "Build order"
section) is the next trajectory move, and the build will be performed
by a fresh model session whose only context for the task will be the
prompt produced from this template plus the primary-source files
listed in the prompt.

This template does NOT replace the live build session. The model
session produces the artifact (typically a single file); the human
collaborator commits it, runs the relevant test suite, records the
findings in a ledger entry. The template's purpose is to position
the model in the procedural posture the project requires - scope
adherence, primary-source derivation, gap-candidate enumeration -
not to substitute for the build session's evaluation work.

## Relationship to the verification-request template

The verification-request template at
`docs/methodology/verification_request_template.md` (VL-017a) handles
the verification shape: derive X from primary sources, classify against
the artifact under verification. This template handles the build shape:
produce new artifact Y satisfying spec Z, with primary sources scoped
to those needed for the build.

Shared structure (the seven-section shape, the VL-008 procedure block,
the primary-source list, the submission-format requirements) is
identical. What differs is the task verb (BUILD vs VERIFY), the
submission format (the artifact itself plus citation/mapping/gaps,
not a classification table), and the outcome categories.

## Template

The following block is a fill-in-the-blanks template. Placeholders in
ANGLE BRACKETS are task-specific parameters. Everything outside the
placeholders is fixed content forming the procedural posture.

---

```
# Build-resumption request: <LEDGER_ENTRY_ID> (<BUILD_ARTIFACT_BRIEF>)

## What you are being asked to do

Produce <BUILD_ARTIFACT_PATH> per <SPEC_PATH> build-order step
<BUILD_ORDER_STEP_NUMBER>. The artifact implements the boundary
behavior in the order specified in the spec (<SPEC_BUILD_ORDER_BRIEF>),
emitting one of the schema-named refusal codes on rejection. The
artifact is a new file; it does not modify any existing file.

## Procedure (VL-008-bound, adapted for build)

a. Read only the primary sources listed under "Attached files" below.
The verification ledger, the restructure artifacts in `docs/`, and
any prior knowledge you may have of this project from earlier
exposure are out of scope for this task.

b. Do not infer or fill from external sources. If the attached files
are insufficient to answer a structural question, name the gap
explicitly in a "Gap candidates" section rather than fill it from
inference.

c. Confirm explicitly in your response that you stayed within (a)
and (b). Procedure compliance is a required output, not optional.

Prior exposure to this project does not disqualify your response,
provided (a), (b), and (c) hold.

## What BUILD means / does not mean

BUILD means: produce a new file at <BUILD_ARTIFACT_PATH> whose
behavior, when invoked from a future <DOWNSTREAM_FILE> revision (not
authored in this task), would cause <DOWNSTREAM_EFFECT>.

BUILD does NOT mean:

- Modifying <OUT_OF_SCOPE_FILE_1>, <OUT_OF_SCOPE_FILE_2>, ... (each
out-of-scope file enumerated with the build-order step that owns it).
- Changing <OUT_OF_SCOPE_BEHAVIOR_1>.
- Inferring <FORBIDDEN_INFERENCE_CATEGORY>.
- Adding <FORBIDDEN_ADDITION_CATEGORY>.
- Producing tests, evidence files, ledger entries, or documentation
changes.
- Editing `.gitignore`, dependencies, or any project structure file.

## Bounded deliverable

One file: <BUILD_ARTIFACT_PATH>.

- <DELIVERABLE_CONSTRAINT_1>
- <DELIVERABLE_CONSTRAINT_2>
- ...

## What outcome means what

- Procedurally clean, complete: You produce the file, confirm scope
adherence under (c), and the spec-citation map and <TASK_SPECIFIC_MAPPING>
are present and complete.

- Procedurally clean, gap-finding: You produce the file AND surface
one or more gap candidates where the spec under-determines the
artifact's behavior. Gap candidates go in a separate section; they
do not become silent assumptions in the code.

- Procedurally unclean: You cannot produce the file without
consulting non-attached sources. State this and stop; do not produce
a partial file. This is an informative outcome, not a failure.

## Submission format

Your response must contain, in this order:

1. Procedure confirmation. One sentence stating you stayed within
the attached primary sources, or a specific named exception.

2. The artifact file. The full content of <BUILD_ARTIFACT_PATH> in
a single fenced code block.

3. Spec-citation map. For each <SCHEMA_NAMED_ELEMENT> your artifact
emits, the section or line range of <SPEC_PATH> that defines its
trigger condition. Format: one row per element, columns
`element | spec_citation`. Citations should quote spec text where
possible, not just name the section.

4. <TASK_SPECIFIC_MAPPING_NAME>. <TASK_SPECIFIC_MAPPING_DESCRIPTION>.
Format: one row per <UNIT_OF_MAPPING>.

5. Gap candidates. Each gap: a one-line description plus the spec
section that under-determines it. If no gap candidates, state "None"
explicitly rather than omit the section.

## Attached files (primary sources)

<NUMBERED_LIST_OF_PRIMARY_SOURCE_FILES_WITH_PURPOSE_NOTES>

## Hard constraints (reiterating, since these are the most common
procedural failures)

- Do not modify any existing file.
- Do not change any specified-as-out-of-scope behavior.
- Do not invent schema-named elements; use only those named in the
spec.
- Do not consult the verification ledger, restructure artifacts, or
prior knowledge of this project's history.
- Do not produce tests, evidence files, or ledger entries.

## Why this prompt looks the way it does

This invocation follows a procedural pattern documented in the
project as the VL-008 cross-model procedure, originally established
for verification and adapted here for build resumption. The
structure (procedure block, scope definition, bounded deliverable,
submission format, primary-source list) exists to make your response
evaluable on procedural grounds independently of artifact quality.
A response that produces an excellent artifact but skips the procedure
confirmation or the spec-citation map cannot be evaluated against
this procedure, so the procedural outputs are not optional.
```

---

## Caller-side evaluation criteria

After receiving a response generated from this template, evaluate
against four criteria:

1. **Procedure confirmation present.** The response opens with explicit
scope-adherence confirmation. Absent = procedurally unclean, regardless
of artifact quality.

2. **Spec-citation map present and citing actual spec content.** Each
schema-named element is mapped to a spec section, ideally with quoted
text. Hand-waving citations ("as defined in the spec") are a procedural
warning sign; treat as a calibration issue and revise the template's
submission-format wording if it recurs.

3. **Out-of-scope items not produced.** No edits to forbidden files,
no inventions outside the spec, no extra-deliverable artifacts. If
extras appear, the out-of-scope boundaries are not binding; revise
the template's hard-constraints section before next use.

4. **Internal consistency between the artifact and the mapping
tables.** The mapping tables should accurately describe what the
artifact's code would actually do. A mapping claiming a route the
code would not take is a calibration finding (the model is filling
in an idealized response rather than describing its actual output)
and should be noted in the receiving ledger entry. Two-model
corroboration on this point is more reliable than single-model.

## When to use two-model corroboration

For build-order steps where the spec has been cross-model-verified
(per VL-008) but the build behavior has additional implementation
freedom (error-handling style, internal organization, etc.), running
the template against two model sessions surfaces:

- Convergence on schema-named elements (corroborates the spec is
build-ready on those elements)
- Divergence on schema-named elements (surfaces under-specified
loci as candidate gaps, analogous to VL-015's G12/G13 emergence)
- Divergence on implementation freedom (informs which implementation
choice the project's downstream wiring prefers)
- Asymmetric internal consistency (informs which model is more
reliable for which task type)

Two-model corroboration on a build is more expensive than single-model
(twice the prompt cost, twice the response evaluation cost). The cost
is justified for high-stakes build steps where divergence would be
informative, less so for routine build steps where the spec leaves
little room for divergence.

The two-model corroboration on a build is NOT a substitute for
running the live build's test suite. A two-model dry-run can prove
the spec is build-ready and the invocation positions the models
correctly; it cannot prove the resulting code passes the tests, which
requires actual execution.

## First-instance and template-evolution notes

This template was first used in VL-017b's dry-run test (two-model
corroboration on `IMPLEMENTATION/request_validator.py` per
`SPEC/request_schema.md` build-order step 3). The first use surfaced
one revision worth folding into the template before its next use:

- The submission format's gap-candidates section should require
explicit enumeration even when zero, not allow the section to be
skipped. In the first use, one model reported "None" and the other
reported two gap candidates; the asymmetry is procedurally
informative only if the zero-case is also asserted rather than
silent.

This revision is incorporated above (item 5 of Submission format
specifies "If no gap candidates, state 'None' explicitly rather
than omit the section").

Future first-uses of this template should record similar revisions
in this section, following VL-017a's pattern of hardening templates
against real-use failure modes before the next use rather than after.
