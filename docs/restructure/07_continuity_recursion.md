# Elyon-Sol - Continuity-Discipline Recursion

**Status:** Reading-aid artifact. Names a structural pattern that emerged
from VL-023's recursive-continuity hypothesis derivation (PARTIAL HOLDS,
2026-05-20), was strengthened by VL-023 follow-up's cross-model
convergence, refined by VL-024 to layer-bounded form (STRENGTHENS bounded
to layers B and C), implemented at the decision-layer anchor by VL-029
(G0 build half closes), and verified pre-draft by two-model convergence
under VL-022 + Lesson 6 procedural discipline at the T-07 trajectory.

**Purpose:** Make the pattern discoverable to future readers without
requiring them to re-derive it from scratch. This artifact introduces no
new invariant, claim, or vocabulary. Every observation it records is
already in the framework's primary sources; the artifact's value is in
naming what is structurally present so that readers can recognize the
pattern when they encounter its instances.

**Scope:** Reading-aid track only. This artifact does not change canon,
code, manifest, tests, or specifications. Canon section 1, section 6, and
section 14 remain the framework's declared purpose; this artifact
characterizes how the framework is *built*, not what it *is*.

---

## What this artifact names

Continuity discipline - the four-part structural shape canon section 12
specifies for `CCS(S_t, S_{t+1}, I)` - appears at **five layers** of the
framework, with structurally analogous instances at each layer. The shape
does **not** apply to one candidate layer (the request layer), and the
non-instance is itself load-bearing: it shows the recursion is bounded
rather than universal.

The five fitting layers:

1. **Decision layer** - canonical CCS itself, implemented at VL-029 in
   `IMPLEMENTATION/envelope.py`.
2. **Manifest layer** - `manifest_integrity_valid()` plus `reassert()`
   Row 4 manifest-mismatch behavior.
3. **Methodology layer** - the verification ledger plus the
   no-prose-promotion rule.
4. **Session layer** - the close/resume protocols.
5. **Evaluator-versioning layer** - `evaluator_sha256` plus `reassert()`
   Row 3 evaluator-mismatch behavior.

The non-fitting candidate:

- **Request layer** - schema validation. Fail-closed but no transition
  concept; a precondition layer rather than a continuity layer.

The strengthening claim is bounded per VL-024: the recursive pattern
applies to **layer B (epistemic discipline)** and **layer C
(reading-aid / structural-legibility)** of the framework's purposes, and
does **NOT** apply to **layer A (declared purpose / gate behavior)**.
Layer A remains exactly what canon section 1 and section 14 state: pre-
execution admissibility, deterministic refusal, governance-before-
intelligence. The recursion is structural, not foundational.

---

## The continuity shape (derived from canon section 12)

Canon `CCS(S_t, S_{t+1}, I)` decomposes into four components, derivable
from canon section 12 plus section 13:

1. **State.** A bundle of values whose internal consistency matters per
   canon section 12.1 ("interaction context, authority, coverage, or
   system state").
2. **Detectable transitions.** Enumerated changes per canon section 12.1
   plus the section 12.4 examples ("governing manifest version change,
   role or authority schema change, identity or mapping inconsistency").
3. **Invalidation / revalidation mechanism.** Per canon section 12.3:
   `CCS(S_t, S_{t+1}, I) = 1` iff authority/coverage transitions are
   justified by `AC^3` / `T^26` and `d_{t+1} = u_{t+1} AND c_{t+1}`. The
   mechanism is the check itself; what fails on violation is what
   constitutes invalidation.
4. **Fail-closed on unverified continuation.** Per canon section 12.4
   ("if any condition is violated: CCS = 0") plus canon section 13
   ("eligibility does not persist across state transitions without
   revalidation").

This four-part shape is the structural test. A layer that exhibits all
four components has a continuity-discipline instance; a layer that
fails any component is not a continuity layer. The shape was extracted
from canon section 12 independently at VL-023 (state + transitions +
invalidation/revalidation + fail-closed), confirmed by VL-023 follow-up's
cross-model run, and re-confirmed by both T-07 verifiers (Grok and OpenAI
independently extracted identical four-component decompositions from the
same canon passages).

---

## Per-layer instances

### Decision layer

The anchor layer. The continuity shape is *defined* at the decision
layer by canon section 12 itself.

- **State.** The interaction tuple per canon section 11.1 (`I = (A, S, C, t)`)
  plus the decision variables `u, c, d` per canon section 12.2.
  Implemented at `IMPLEMENTATION/envelope.py::build_envelope()`, which
  records `decision`, `condition_results.ac3` (`u`), `condition_results.t26`
  (`c`), plus the canon hash, manifest hash, and evaluator hash as the
  state-defining values.
- **Transitions.** Any change to context, authority, coverage, or
  system state per canon section 12.1. In code: a hash mismatch between
  the envelope's stored value and the live value, detected by
  `reassert()` Rows 1-4.
- **Invalidation / revalidation.** `reassert()` per
  `IMPLEMENTATION/envelope.py`, with the post-VL-026 ccs-derivation rule
  implemented at VL-029: returns `{"outcome": REASSERTED, "ccs": True}` on
  full consistency, `{"outcome": INVALIDATED, "ccs": False}` on canon
  change or tamper, `{"outcome": RE_EVALUATE_REQUIRED, "ccs": False}` on
  evaluator or manifest change.
- **Fail-closed.** Eligibility does not persist past a non-REASSERTED
  reassertion. Per `docs/restructure/06_spec_to_code_traceability.md`,
  canon sections 3 CCS, 12.1, 12.2, 12.3, 12.4, and 13 are all status
  FULL post-VL-029.

The decision layer's continuity instance is the *definition* of the
shape rather than an analogue of it; the other layers are tested for
structural analogy to this anchor.

### Manifest layer

- **State.** `(manifest.version, manifest_sha256)` per
  `SPEC/request_schema.md` manifest-pinning fields and canon section 11.9.
- **Transitions.** Manifest hash or version change, enumerated as an
  invalid transition in canon section 12.4 ("governing manifest version
  change").
- **Invalidation / revalidation.** Two mechanisms operate at this layer:
  (a) point-in-time check via
  `IMPLEMENTATION/evaluator.py::manifest_integrity_valid()`, run during
  `evaluate()` per canon section 8.1; (b) transition-shaped check via
  `IMPLEMENTATION/envelope.py::reassert()` Row 4, which returns
  `RE-EVALUATE-REQUIRED` on `manifest_sha256` mismatch per
  `docs/restructure/05_admissibility_envelope_spec.md` reassertion table
  row 4 ("section 7/section 12.4 - manifest version/schema transition").
- **Fail-closed.** `REF_SCHEMA_MANIFEST_PINNING_MISSING` at the schema
  boundary (`IMPLEMENTATION/request_validator.py`); refuse-on-mismatch
  inside `manifest_integrity_valid()`; `ccs: False` on `reassert()` Row 4.

**Refinement.** The manifest layer's continuity instance is not a
separate invariant. It is canonical CCS applied to the manifest
component of state. The point-in-time `manifest_integrity_valid()` check
is the per-instant precondition that establishes the state value a
future transition will be measured against. The transition-shape check
in `reassert()` Row 4 is canonical CCS narrowed to the manifest
sub-state. This refinement is explicit in
`docs/restructure/05_admissibility_envelope_spec.md`'s `condition_results`
field rationale and was independently surfaced by both T-07 verifiers.

### Methodology layer

- **State.** Epistemic status of project claims. Each row in
  `docs/restructure/04_current_vs_claimed.md` carries a status field
  (OPEN, PARTIALLY ADDRESSED, RESOLVED, etc.). Each ledger entry records
  a claim moving through statuses.
- **Transitions.** Explicit status changes recorded in the ledger. For
  example, VL-014 transitioned SINGLE-SOURCE -> DISPUTED at VL-015 ->
  CORRECTED at VL-016; G0 was DRIFTED pre-VL-012, PARTIALLY RESOLVED
  post-VL-012, RESOLVED at VL-029.
- **Invalidation / revalidation.** Ledger entries plus the no-prose-
  promotion rule at `docs/restructure/04_current_vs_claimed.md` line 10:
  "A row closes only when code, tests, or structure change such that the
  delta no longer exists - never by editing prose." The rule is the
  invalidation mechanism: a claim cannot move to RESOLVED without a
  primary-source change that justifies the move.
- **Fail-closed.** `docs/SESSION_PROTOCOL.md` line 64 (close protocol
  step 3): "Verification work that is not ledgered did not, for
  continuity purposes, happen." The protocol uses the framework's own
  continuity vocabulary at exactly this layer.

The methodology layer's detector is procedural rather than functional -
the mechanism is a discipline enforced at session and review boundaries
rather than a runtime check. The four-part shape is present nonetheless;
the framework treats procedural and functional detectors as equally
load-bearing, applying continuity discipline at layers where the
relevant transition rate is slow enough for human-driven checks to be
sufficient.

### Session layer

- **State.** The three at-rest invariants per `docs/SESSION_PROTOCOL.md`
  lines 80-83: working tree clean and HEAD == origin/main; STATE.md's
  "Next open action" first item is literally the next task; the
  verification ledger reflects all verification work to date.
- **Transitions.** Session close -> session start. The interval between
  sessions is the transition; the at-rest state is what must hold across
  that interval.
- **Invalidation / revalidation.** Close protocol per
  `docs/SESSION_PROTOCOL.md` lines 45-74 establishes the at-rest state;
  resume protocol per lines 10-41 checks it. A close that does not
  satisfy lines 71-74 ("Confirm the close is clean ... If git status is
  not clean and synced, the close protocol is not complete") is not a
  valid transition.
- **Fail-closed.** `docs/SESSION_PROTOCOL.md` lines 85-87: "If a resume
  protocol finds these untrue, the previous session's close protocol
  failed. Fixing that is the first task of the new session, before
  anything else." STATE.md's own session-close note uses identical
  vocabulary: "If they do not, the repository's continuity is broken -
  treat that as the first thing to fix."

Like the methodology layer, the session layer's detector is procedural.
The shape is the same; the enforcement medium differs.

### Evaluator-versioning layer

- **State.** `evaluator_sha256` field of the envelope's `evaluator`
  block per
  `docs/restructure/05_admissibility_envelope_spec.md` "Envelope
  structure" - the hash of `IMPLEMENTATION/evaluator.py` at envelope
  construction time. Computed by `IMPLEMENTATION/envelope.py::_evaluator_sha256()`.
- **Transitions.** Decision logic change. The artifact 05 `evaluator`
  block field rationale states: "A changed evaluator hash means the
  decision logic itself moved (section 12.4-class transition)."
- **Invalidation / revalidation.** `IMPLEMENTATION/envelope.py::reassert()`
  Row 3, with canon basis canon section 12.4. The implementation is
  five lines, post-VL-029:

      # ----- Row 3: evaluator_sha256 mismatch -> RE-EVALUATE-REQUIRED -----
      # Canon basis: whitepaper section 12.4 - "decision logic transition."
      live_evaluator_sha256 = _evaluator_sha256()
      if envelope["evaluator"]["evaluator_sha256"] != live_evaluator_sha256:
          return {"outcome": RE_EVALUATE_REQUIRED, "ccs": False}

- **Fail-closed.** `{"outcome": RE_EVALUATE_REQUIRED, "ccs": False}`
  per the implementation above. Eligibility does not persist past an
  evaluator change.

The evaluator-versioning layer was originally surfaced at VL-023 follow-
up as a sixth fitting layer that VL-023 had not examined. VL-024
Implication 1 instructed the future drafting of this artifact to "carry
the inference flag on evaluator-versioning's fail-closed component" -
because pre-VL-029, the fail-closed posture was implicit in artifact
05's mapping rather than explicit in code. VL-029 implemented Row 3
exactly as VL-024 anticipated; the T-07 verification confirmed two-model
convergence that the implementation explicitly fail-closes and the
inference flag dissolves. This artifact cites `envelope.py` directly
rather than carrying the inference caveat forward.

### Request layer (non-fit)

- **State.** Request shape, well-formed per `SPEC/request_schema.md`.
- **Transitions.** None. Requests are atomic. Per
  `SPEC/request_schema.md`: "Schema conformance is a precondition of
  evaluation, not part of evaluation." Each request is a fresh point-in-
  time admissibility query.
- **Invalidation / revalidation.** Schema validation in
  `IMPLEMENTATION/request_validator.py::validate_request()`.
- **Fail-closed.** Yes - the seven-code refusal vocabulary at the PEP
  boundary refuses any malformed request.

The request layer has fail-closed behavior but no transition concept,
which means it does **NOT** fit the four-part shape. It is a
precondition layer rather than a continuity layer. The session opener
for VL-023's derivation listed "Transition = ?" with a question mark at
this layer; the answer is that the question mark is the answer.

The non-fit is load-bearing: it shows the recursion is bounded. A
framework where every layer fit the shape would either be redundant
(applying continuity discipline where it isn't needed) or
incoherent (treating preconditions as transitions). The request layer's
exclusion is the framework's structural acknowledgment that not every
layer needs the same shape.

The request layer is also a carrier of state-pinning information for the
manifest layer's continuity check - the `expected_manifest_version` and
`expected_manifest_sha256` fields a request carries are the data the
manifest-layer mechanism consumes. The request layer is upstream of
manifest-layer continuity but is not itself a continuity layer.

---

## Layer A / B / C bounding (per VL-024)

VL-024 decomposes the framework's purposes into three layers and bounds
the recursive-continuity strengthening claim to two of them:

- **Layer A - declared purpose.** Governance-before-intelligence; pre-
  execution admissibility; deterministic refusal. Per canon section 1
  ("Introduction"), canon section 6 ("Lightweight Formal Model" scope
  framing), and canon section 14 ("Scope Clarification"). This is what
  the framework *is*.
- **Layer B - epistemic discipline.** VL-008 procedure (task-to-source
  binding); the no-prose-promotion rule at
  `docs/restructure/04_current_vs_claimed.md` line 10; the session
  protocol's continuity rule at `docs/SESSION_PROTOCOL.md` line 64. How
  the framework *knows what it knows*.
- **Layer C - reading-aid / structural-legibility track.** This artifact;
  the restructure package; STATE.md's role as entry point for fresh
  sessions per `docs/SESSION_PROTOCOL.md` lines 23-26. How the framework
  *makes itself legible*.

VL-024's verdict, refining VL-023 follow-up's unqualified "strengthened"
framing: the recursive-continuity claim **STRENGTHENS, bounded to layers
B and C; does NOT extend to layer A**. The cross-model run does not
make the gate more deterministic, more fail-closed, or more pre-
execution. The recursive-continuity hypothesis is "a structural property
of how the framework is built, not its declared purpose" (VL-023's own
framing).

This bound is honest scope, not hedging. A maximalist "strengthens at
all layers" claim would import claims the cross-model run did not test.
A minimalist "does not strengthen at all" claim would deny findings the
derivation actually produced.

---

## What this artifact does NOT claim

Following VL-023's "What this derivation explicitly does NOT claim"
section:

- The recursion is unusual, foundational, or commercially distinctive.
  No comparative evidence; canon section D.4 "Relation to Prior Work"
  addresses individual invariants against RBAC/ABAC/XACML/UCON, not
  recursive structure.
- The recursion is the framework's "true organizing principle" or "what
  it really is." Per canon section 1 and the abstract, the framework's
  organizing principle is governance-before-intelligence and pre-
  execution admissibility. The recursion of continuity discipline is a
  structural property of how the framework is built, not its declared
  purpose.
- The framework's authors intended the recursion. The artifacts support
  that each instance was built for its own reason. The recursion is
  observable; intentionality is not.
- The recursion is complete. The request layer does not exhibit it. The
  candidate space was not exhausted at VL-023 (POE anchoring per canon
  section 8.2 was named as another out-of-scope candidate, still
  unevaluated as of this artifact).

The bounded claim: continuity discipline (state + enumerated
transitions + invalidation/revalidation mechanism + fail-closed on
unverified continuation) is visible at five layers of the framework's
current artifacts, with structurally analogous shape at each, and the
strengthening of this observation across cross-model verification
applies to layers B and C of the framework's purposes.

---

## Provenance

- **VL-022** (2026-05-19, commit `dbd65aa`) - cross-model evaluate
  template promoted; presentation-indistinguishability lesson recorded.
- **VL-023** (2026-05-20, commit `83fa5a7`) - recursive-continuity
  hypothesis derivation; PARTIAL HOLDS verdict; four-part shape
  extracted from canon section 12.
- **VL-023 follow-up** (2026-05-20, commit `49b797a`) - cross-model
  convergence; evaluator-versioning layer added as fifth fitting layer.
- **VL-024** (2026-05-20, commit `c944a76`) - strengthening derivation;
  layer A/B/C bounding established.
- **VL-025** (2026-05-21, commit `096c933`) - `envelope.py` lands with
  `build_envelope()` and `reassert()` (build-only commit, no callers
  yet).
- **VL-025 follow-up** (2026-05-21, commit `f0c76cd`) - two-bundle
  cross-model verification of `envelope.py` against artifact 05 and
  canon section 12-13; substantive convergence across all four
  verifier-runs.
- **VL-026** (2026-05-21, commit `3c4c9b5`) - artifact 05 spec revision
  including the post-Edit-5 ccs-derivation rule.
- **VL-027** (2026-05-22, commit `05e27a0`) - `envelope.py` import fix
  surfaced by the planned VL-028 test session.
- **VL-028** (2026-05-22, commit `7efcefc`) - canon-derived tests for
  the envelope domain; G7 partial closure.
- **VL-029** (2026-05-25, commit `79012d7`) - G0 build half closes;
  `pep.py` wires envelope emission on ELIGIBLE; `reassert()` returns
  dict with `ccs` derived per the post-VL-026 rule; Row 3 implements
  the evaluator-versioning fail-closed posture VL-024 anticipated.
- **T-07 verification** (2026-05-26) - pre-draft cross-model verification
  of this artifact's claims by Grok and OpenAI, convergent on all four
  questions (four-part shape, per-layer recursion-fit, layer A/B/C
  bounding, evaluator-versioning fail-closed dissolution).
- **This artifact** (T-07) - reading-aid drafted post-verification per
  VL-023's scheduling recommendation (post-G0-build) and VL-024
  Implication 1's composition guidance, with the evaluator-versioning
  inference flag dissolved per T-07 Q4 convergence.

The verification ledger is the authoritative trace; this provenance list
is a navigational summary.
