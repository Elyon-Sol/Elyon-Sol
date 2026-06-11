# Cross-model verification request - VL-100 (audit-layer specs 26/27/28)

This is a verification request prepared under the procedure
established in `EVIDENCE/verification_ledger.md` entry VL-008.

Read this entire document before doing the task. Read the
"Procedure" section twice. The procedure is load-bearing: a
response that deviates from it carries no verification weight,
regardless of its conclusions.

---

## What you are being asked to do

Classify each of the 22 numbered claims below. Each claim is a
normative statement made by one of three specification documents
(specs 26, 27, 28) about the behavior of the attached
implementation files. For each claim, determine - from the
attached files only - whether the implementation supports it,
contradicts it, or leaves it under-specified. The output shape is
a per-claim classification table plus divergence notes.

Primary sources attached:

- `26_envelope_inspector_spec.md` - spec under verification
  (claims C26-1 .. C26-8).
- `27_envelope_reevaluation_spec.md` - spec under verification
  (claims C27-1 .. C27-7).
- `28_issuance_log_spec.md` - spec under verification
  (claims C28-1 .. C28-7).
- `envelope_inspector.py` - the implementation specs 26 and 27
  describe. Load-bearing for C26-* and C27-*.
- `issuance_log.py` - the implementation spec 28 section 2.1
  describes. Load-bearing for C28-1, C28-2.
- `pep.py` - the gate; spec 28 section 2.2 describes its VL-099
  wiring. Load-bearing for C28-3 .. C28-7.
- `envelope.py` - upstream: build_envelope / sign_envelope /
  reassert / canonical_json / _SIGNATURE_EXCLUDED_KEYS.
  Secondary (cited by claims, not under verification).
- `verifier.py` - upstream: verify_envelope, the REF_VERIFY_*
  vocabulary, the structural-guard tuples, the binding
  comparisons. Secondary.
- `evaluator.py` - upstream: evaluate and the three condition
  functions. Secondary.

The verification IS: does each spec claim hold of the attached
code? It is NOT an evaluation of whether the specs or the code
are well-designed.

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

## The claims

Spec 26 (`26_envelope_inspector_spec.md`):

- **C26-1** (spec 26 section 3.1): `inspect_envelope` is decode-only -
  no signature, currency, or binding judgment - and fails closed with
  `REF_VERIFY_ENVELOPE_ABSENT` on exactly the shapes the verifier's
  structural guard rejects.
- **C26-2** (spec 26 section 3.2): `verify_issuer` performs the
  signature + validity-window check with the same fail-closed
  semantics and reason codes as verifier.py steps 1.5/1.5b, over a
  signed region defined by importing `_SIGNATURE_EXCLUDED_KEYS` from
  envelope.py (one canonical definition; no independent re-derivation
  of the region).
- **C26-3** (spec 26 section 3.3): currency is not wrapped - the
  module adds no function around `reassert`; the CLI calls it
  directly.
- **C26-4** (spec 26 sections 2, 3.4): `reconcile`'s binding
  predicate applies the same five comparisons as `verify_envelope`
  step 3 (target_url string equality; AP/OP normalized-set equality;
  two manifest-pinning string equalities; context canonical_json
  equality).
- **C26-5** (spec 26 section 3.4): matching is single-use (a matched
  envelope is consumed and cannot match again), and an action
  carrying a `decision_id` matches only an envelope with that
  `decision_id`.
- **C26-6** (spec 26 section 3.4): when `pinned_public_keys` is
  supplied, an issued-log entry that fails the structural guard, or
  whose decision is not "ELIGIBLE", or that fails issuer
  verification, is reported `INVALID_ENVELOPE` and excluded from
  matching.
- **C26-7** (spec 26 section 3.4): `reassert` currency is NOT part of
  the matching predicate - no reconcile path calls `reassert`.
- **C26-8** (spec 26 section 3.4): the per-action verdict set is
  closed at {MATCHED, OUT_OF_SCOPE, DUPLICATE_CONSUMPTION} and the
  per-envelope status set at {CONSUMED, UNUSED, INVALID_ENVELOPE};
  `summary.clean` is true iff out_of_scope and duplicate_consumption
  are both zero.

Spec 27 (`27_envelope_reevaluation_spec.md`):

- **C27-1** (spec 27 section 2.1): the consistency check mirrors
  `evaluate()`'s short-circuit logic - decision "ELIGIBLE" is
  consistent iff all of the recorded ac3/t26/manifest_integrity are
  True; "REFUSE" iff at least one is False; any other decision value
  or a missing/non-boolean condition is classified inconsistent.
- **C27-2** (spec 27 section 2.1): `condition_results.ccs` is not
  consulted by the consistency check.
- **C27-3** (spec 27 section 2.2): the live re-run rebuilds the
  evaluator ctx from exactly four recorded fields (AP, OP,
  expected_manifest_version, expected_manifest_sha256) - the recorded
  `context` does not enter - and runs the production `evaluate` plus
  the three condition functions individually.
- **C27-4** (spec 27 section 2.2): live-state semantics are inherent
  rather than chosen: `manifest_integrity_valid` (evaluator.py)
  fails closed unless its passed manifest equals the on-disk
  manifest, so re-evaluation against any other manifest dict cannot
  return a true integrity condition.
- **C27-5** (spec 27 section 2.3): a structurally unsound envelope
  returns the same fail-closed shape as `inspect_envelope`
  (`{"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}`).
- **C27-6** (spec 27 section 2.3): `reevaluate_envelope` judges and
  does not raise on content (undecidable content yields the
  conservative classification, not an exception).
- **C27-7** (spec 27 section 3): the CLI `reevaluate` subcommand
  exits 0 iff ok AND consistent AND reproduced.

Spec 28 (`28_issuance_log_spec.md`):

- **C28-1** (spec 28 section 2.1): `JsonlIssuanceLog.append` writes
  exactly one line per call - `canonical_json(envelope)` plus a
  newline - in append mode with flush and fsync per line.
- **C28-2** (spec 28 section 2.1): `issuance_log_from_env` returns a
  `JsonlIssuanceLog` over `ELYON_ISSUANCE_LOG_PATH` when set and
  non-empty, else None.
- **C28-3** (spec 28 section 2.2): pep.py resolves the log
  injected-then-env (`_INJECTED_ISSUANCE_LOG` first, then
  `issuance_log_from_env`), the same resolution order as
  `_get_signing_key`.
- **C28-4** (spec 28 section 2.2): the append happens after
  `sign_envelope` and before the upstream push, inside the same
  try/except that protects envelope construction.
- **C28-5** (spec 28 section 2.2): an append exception on a
  configured log results in a 403 with refusal_reason_code
  `REF_PEP_FAIL_CLOSED`, and the upstream target is never called.
- **C28-6** (spec 28 section 2.2): with no injected log and no env
  var, the ELIGIBLE path's behavior is identical to a gate without
  the VL-099 change (the only added operations are the resolution
  check itself).
- **C28-7** (spec 28 sections 1, 3): the logged line is an envelope
  JSON object of the same shape `reconcile` accepts as an
  issued-envelopes entry (one `json.loads` of a log line yields a
  dict that `reconcile`'s issued-side screening and matching operate
  on without transformation).

---

## What "classify" means (and what it does not mean)

Classify MEANS: for each numbered claim, read the cited spec
section and the relevant implementation code, and assign exactly
one of the outcome categories below, citing the specific
functions, lines, or clauses (file + location) that ground the
assignment.

Classify DOES NOT MEAN:

- "Tell me whether the specs or the code are good." That's code
  review, not classification. Verdicts carry no verification
  weight under VL-008.
- "Suggest improvements." Out of scope; the task is classify,
  not co-design.
- "Compare with how other systems do this." Out of scope; only
  the attached files are in scope.
- "Rate the quality." Out of scope; verdict-shaped responses
  carry no weight.
- "Evaluate the test suite." The tests are not attached and are
  not part of this verification round.
- "Re-derive the claims list." The 22 claims above are the
  fixed object of this round; if a claim misquotes its spec,
  classify it Reframing required and say what the spec actually
  says.

If you find yourself wanting to write a sentence that doesn't
trace to a specific clause in one of the attached files, that
sentence is out of scope. Either find the clause that supports
it or remove it.

---

## What outcome means what

Each claim receives exactly one of:

- **Supported.** The attached implementation does what the claim
  says, and you can cite the function/lines that do it.
- **Contradicted.** The attached implementation demonstrably does
  something the claim excludes, or fails to do something the
  claim requires; cite the contradicting code.
- **Under-specified.** The implementation neither clearly
  supports nor contradicts the claim from the attached files
  alone (e.g., the claim depends on behavior the attached files
  do not determine); name exactly what is missing.
- **Reframing required.** The claim as stated is ambiguous,
  ill-formed, or misquotes its spec section; name the
  reformulation and classify the reformulated claim. Do not
  silently substitute a different question.

These outcomes are classification outcomes. They are NOT
verdicts on the artifacts, the project, or anything you are not
being shown.

Status implications: each spec is currently SINGLE-SOURCE in the
project's ledger. A spec transitions SINGLE-SOURCE -> CONFIRMED
if every one of its claims is Supported by two independent
verifier runs; any Contradicted claim transitions the spec to
DISPUTED pending correction; Under-specified claims become named
gap candidates without blocking CONFIRMED status for the rest.

All listed outcomes are useful. None is a failure of the
verification; only a procedure violation under VL-008 (a) or
(b) is.

---

## What you do NOT need to address

- The test files (not attached; a separate concern).
- The specs' "Tests" sections (they describe the unattached
  test files).
- Spec 26 section 5 and spec 28 section 3 deployment narratives
  (what the tools enable operationally), except where a numbered
  claim cites them.
- The project's gap tracker, ledger, canon, or any document not
  attached.
- request_validator.py (not attached; verifier.py contains the
  normalization logic the claims reference).

---

## Submission format

Respond in this structure, in this order:

```
## Classification table

[One row per claim, C26-1 through C28-7: claim ID, outcome
category, one-sentence ground citing file + function/section.]

## Divergence notes

[One short paragraph per claim NOT classified Supported,
explaining the contradiction, the missing determinant, or the
reformulation. "None" if all 22 are Supported.]

## Scope check

[For every concept, term, or claim in the sections above, cite
which attached file and which section/clause it comes from. If
any item cannot be cited, name it as out-of-scope and remove it
from the work above.]
```

Do not include sections beyond these. Do not rate, review, or
suggest. Do not reference any artifact you are not being
shown - speculating about it is out of scope.

---

## Attached files

Attached to this request:

- `26_envelope_inspector_spec.md`
- `27_envelope_reevaluation_spec.md`
- `28_issuance_log_spec.md`
- `envelope_inspector.py`
- `issuance_log.py`
- `pep.py`
- `envelope.py`
- `verifier.py`
- `evaluator.py`

If any file is missing or appears truncated, stop and say so.
Do not work from a partial source.

---

## Ledger context (informational, not part of the task)

This verification, if successful under the procedure above,
becomes a new ledger entry (proposed VL-102 or thereabouts in
the project's numbering scheme; the exact number depends on what
else has happened in the repository when the entry is appended).
The entry will cite:

- verifier identity (model and operator) and date
- procedure adherence (rules a and b, checked against the Scope
  check section)
- the per-claim classification table verbatim
- the resulting status transition for each of specs 26, 27, 28
- any Under-specified claims promoted to named gap candidates

Your response is the artifact. The ledger entry is downstream.
