# Elyon-Sol  -  Enforcement Design (G4): Non-Bypassable Enforcement

**Status:** Design analysis. Reading-aid / design track, paralleling
`07_continuity_recursion.md` (VL-031). Derived from locked canon
v0.9.8.4 (sections 2, 9, 10, 11.1, 13, 14), `05_admissibility_envelope_spec.md`
(open question 3, envelope structure, reassertion protocol),
`04_current_vs_claimed.md` (G4 and G5 rows), and the current
`IMPLEMENTATION/pep.py` and `IMPLEMENTATION/envelope.py`.

**What this artifact does and does not do.** It states a threat model for
gap G4 (bypassability), enumerates the G4 sub-questions, evaluates the
candidate enforcement mechanism named in artifact 05 open question 3 plus
alternatives, checks each against canon section 14, addresses the G4/G5
boundary, and recommends a first build increment for VL-037. It introduces
**no new canonical invariant** and **no new vocabulary**, and it changes no
implementation, canon, manifest, test, or spec file (this is a design
session). Where the analysis proposes rather than derives, the proposal is
marked `[INFERENCE]`.

**Derivation provenance.** The threat model and the mechanism-adequacy
premise were pre-draft cross-model verified (two recipients, framework-level
evaluate procedure under VL-008 + Lesson 8); the section-14 compatibility and
the G4/G5 boundary were derived source-first. See the closing "Derivation
provenance" section for the convergence/divergence record.

---

## 1. Why G4, and why design before code

With G0, G2, G3, and G7 resolved, the canon-honesty gaps are closed. What
remains for a *fully operational* gate is build-outward work, and G4 is the
load-bearing item. Artifact 05's build order makes G4 the canonical next
step: build-order step 6 reads "Only then: explore open question 3
(envelope-on-forwarded-call)", and the "only then" precondition (the CCS
build) closed at VL-029.

G4 is a genuine open *design* question, not a locked-procedure trajectory.
This artifact is therefore a design + spec deliverable: it produces the
analysis and a recommended first increment, and defers all code to VL-037.
This mirrors the CCS sequencing, in which artifact 05 preceded `envelope.py`.

---

## 2. Threat model

### 2.1 What "bypass" means

A **bypass** occurs when a caller causes the target to act on an interaction
without a valid, current Elyon-Sol decision covering that exact interaction.
The current architecture permits this in two structurally distinct ways, both
read from the current code:

- **Non-coverage.** A target action can occur with no Elyon-Sol decision at
  all. The gate is a separate HTTP service the caller chooses to route
  through; nothing forces routing. (`04_current_vs_claimed.md` G4 row: "The
  gate is opt-in. A caller can hit the target directly and bypass it.")
- **Non-attestation.** Even when a caller routes, the target cannot tell.
  `pep.py` forwards with `requests.post(body["target_url"],
  json=normalized_interaction, timeout=10)`  -  the interaction only. The
  envelope is returned to the *caller* in `{"decision": "ELIGIBLE",
  "envelope": envelope}`, never to the target. A routed call and a direct
  call are therefore byte-identical at the target, which has no decision
  artifact to check. (`04_current_vs_claimed.md` G4 row: "The target cannot
  verify a call came through the gate.")

**Framing bound (load-bearing for honesty).** The canon never states
non-bypassability. Section 2 calls the gate a "non-executing governance
substrate"; section 14 says it "operates pre-execution" and "governs
legitimacy"; neither promises enforcement against a caller who declines to
route. (`04_current_vs_claimed.md` G4 row, Canon note: "The canon does not
explicitly claim non-bypassability  -  but a reader reasonably infers
enforcement.") So this artifact treats non-bypassability as a design goal
that the canon *permits* and a reader *expects*, not as a canon-mandated
invariant. Every claim below is framed accordingly.

### 2.2 Trust roots (assumptions, not adversaries)

Three parties are assumed honest; they are the roots against which everything
else is verified. A compromise of any of them is out of scope by assumption,
because it removes the ground the design stands on:

- **The gate is honest.** It is the decision oracle; its envelope is the
  thing being verified. A compromised gate makes every decision meaningless;
  out of scope. `[INFERENCE]`
- **Transport integrity holds (TLS).** An adversary who can rewrite bytes on
  the wire is out of scope (this is adversary class A5 below, named only to
  be excluded). `[INFERENCE]`
- **The published reference for the gate's hashes is authentic.** Target-side
  verification needs an authentic, current source for the canon (and
  evaluator and manifest) hashes; that durable source is gap G5 (see section
  6). Its authenticity is assumed; its *durability* is the G5 build problem.

### 2.3 Adversary classes, by construction

The adversary set is derived as a partition over the parties that can cause
the target to act, rather than asserted. Over the scope "who can make the
target act without a valid current decision", the non-trusted parties are the
**caller**, the **target**, and the **transport**. Partitioning by what each
can do exhausts the space:

- The **caller** has exactly four behaviors relative to the gate: route with
  a valid current envelope (not adversarial); decline to route (**A1**);
  route with a forged or fabricated decision artifact (**A2**); route with a
  genuine but stale or mismatched envelope (**A3**). A1/A2/A3 are the three
  adversarial caller behaviors and they are jointly exhaustive of "caller does
  something other than present a valid current decision."
- The **target** can ignore or fake verification, or collude with a caller
  (**A4**). No caller-side mechanism reaches this; it is a trust boundary.
- The **transport** can strip or swap the envelope on a hop (**A5**); excluded
  per section 2.2.

This is exhaustiveness *by construction over the participant set*, which is
checkable, rather than by assertion. (The participant partition follows the
interaction model of canon section 11.1, `I = (A, S, C, t)`: actors and
context are the parties to an interaction.)

Mapping to the two bypass routes: A1 is the sole **non-coverage** adversary;
A2 and A3 are the **non-attestation** adversaries (forge and replay
respectively).

### 2.4 In scope / out of scope

In scope: closing A2 and A3 for routed traffic, and stating plainly what can
and cannot be done about A1. Out of scope: A4 (a target that does not want to
verify), A5 (transport), caller-to-gate identity/authentication (canon section
14 is identity-agnostic and the gate "does NOT replace identity systems"), any
canon-version question (flagged, not performed), and the durable-source
*build* for G5 (named as a precondition per Decision E1; see section 6).

---

## 3. G4 sub-questions

- **Q1 Coverage.** Can the declining caller (A1) be closed by the gate at
  all? (See section 4.4: no  -  only a target-side policy closes A1.)
- **Q2 Attestation.** How does a routed call carry proof of a decision?
  (Artifact 05 open question 3: attach the envelope to the call.)
- **Q3 Verification.** What does the target check, and against what?
  (`decision_sha256` for integrity; canon/evaluator/manifest hashes via
  `reassert()` for currency  -  against a durable published source, G5.)
- **Q4 Freshness / anti-replay.** How is a stale or reused envelope rejected?
  (Canon section 13; but see section 7  -  `reassert()` alone does not close
  same-state replay.)
- **Q5 Binding.** Is the envelope bound to the specific interaction it
  admitted? (Splits into authenticity vs interaction-binding; see section 4.2.)
- **Q6 Section-14 compatibility.** Does the mechanism keep the gate
  non-executing? (See section 5.)
- **Q7 G4/G5 boundary.** Where does the published reference for the gate's
  hashes durably live? (See section 6; G5 dependency.)
- **Q8 Trust boundary.** What is assumed and therefore not closeable by the
  gate? (Section 2.2: gate, transport, published-source authenticity; plus
  A4.)

---

## 4. Mechanism evaluation

### 4.1 The artifact-05 candidate

Artifact 05 open question 3 names the candidate: "If `pep.py` attaches the
envelope to the forwarded request and the target verifies `decision_sha256`
against Elyon-Sol's published canon hash, the target can refuse calls lacking
a valid envelope. That is a concrete first step toward non-bypassable
enforcement." Artifact 05 flags it as build-outward, not part of the CCS
implementation itself.

The mechanism has two separable parts: **delivery** (how the envelope reaches
the target) and **verification** (what the target does with it). Treating them
separately is what makes the section-14 analysis tractable.

### 4.2 What verification proves, and what it does not (Q5 split)

The verification side reuses the existing `reassert()` (canon section 13;
artifact 05 reassertion protocol). What it establishes, and its limit:

- **Envelope authenticity and integrity: closed by the mechanism.** A target
  that re-canonicalizes the envelope (minus `decision_sha256` and
  `timestamp_utc`) and recomputes the hash detects any tampering. Because
  `build_envelope()` computes `decision_sha256` over the envelope minus only
  `timestamp_utc` (`envelope.py`: `hashable = {k: v for ... if k !=
  "timestamp_utc"}`), the envelope's `target_url` and `request_context` (AP,
  OP, context, expected_manifest fields) are *inside* the signed region. An
  authentic envelope's recorded interaction is therefore tamper-evident. This
  closes the TAMPER sub-case of **A2** for routed traffic: an envelope mutated
  without re-hashing fails `decision_sha256`, and `reassert()` Row 2 returns
  INVALIDATED. **It does NOT close the FORGERY sub-case** (VL-039 follow-up 2):
  `decision_sha256` is an unkeyed hash over the envelope's own public fields, so a
  party who knows the published record can build a from-scratch envelope with a
  correctly recomputed `decision_sha256` and no issuer signature, which Row 2
  accepts. The envelope is tamper-evident, not forgery-resistant. Forgery is closed
  by issuer signing (VL-040): on the signed path the gate signs the envelope
  (Ed25519) and the target verifies `issuer_signature` against a pinned public key
  before `reassert()` (REF_VERIFY_SIGNATURE_INVALID / REF_VERIFY_SIGNATURE_UNKNOWN_KEY,
  fail-closed). The signed path closes forgery; as of the VL-047 mandatory cutover
  `pep.py`'s default forward signs, so the gate's default path IS the signed path and
  forgery is closed there  -  the named follow-on is discharged. The verifier's unsigned
  mode is preserved for the A1 / enforcement demonstrations that use it. See artifact 05
  "Issuer signature (opt-in)".
- **Interaction binding: NOT closed by the mechanism alone.** Verifying
  `decision_sha256` proves the envelope is an authentic decision about the
  `target_url` *it records*. It does not prove that the envelope's
  `request_context` matches the interaction the target is *actually* being
  asked to perform now. `reassert()` compares live repository-state hashes
  (canon, evaluator, manifest); it never compares the envelope's
  `request_context` against a live request. So a genuine envelope for
  interaction X presented alongside a forwarded body Y will REASSERT.

This is the precision the premise testing surfaced: Q5 must be split into
**envelope authenticity** (closed) and **interaction binding** (a *separate*
target-side obligation: compare the envelope's `request_context` and
`target_url` against the live interaction before honoring the decision). The
binding check is what actually closes **A3** (replay across interactions under
unchanged repo state). See section 7.

### 4.3 Delivery architectures

Three ways the envelope can reach the target, evaluated against section 14
(section 5) and the adversary classes:

- **Push (gate attaches the envelope to its forward).** Smallest diff from
  current code: change the forward from `json=normalized_interaction` to also
  carry the envelope. But the gate does *more* on the execution hop, and if
  the target relies on the gate-attached attestation, the gate edges toward
  being the enforcement actor. **Deepens** the section-14 tension (section 5).
- **Caller-carry (gate returns the envelope; the caller delivers it to the
  target).** The gate need not forward at all  -  it returns the envelope as
  it already does. The (potentially adversarial) caller carrying the
  attestation is acceptable *because the envelope is tamper-evident*: forge
  is caught by `decision_sha256`, replay by the binding check. Removes the
  gate from the execution hop entirely. **Relieves** the section-14 tension;
  the section-14-cleanest option. `[INFERENCE]`
- **Target-pull (target queries the gate or a published store for the
  decision).** Keeps the gate an oracle; requires a queryable durable source
  (G5) and a target-side policy. Section-14-neutral to mildly relieving:
  answering a decision query is publication, not execution. `[INFERENCE]`

Verification is delivery-agnostic: the same `reassert()`-plus-binding-check
runs regardless of how the envelope arrived. This is why the *verifier* is the
reusable, architecture-neutral piece to build first (section 8).

### 4.4 The A1 floor

No delivery or verification mechanism closes **A1** (the caller who never
routes), because the gate never sees that call. A1 is closeable only by a
**target-side policy that refuses any call lacking a verifiable decision**.
That policy is a property of the target's deployment, not of the gate
(`04_current_vs_claimed.md` G4 Action: enforcement is build-outward; this
artifact states the floor plainly). Consequently every enforcement mechanism
here is **necessary-but-not-sufficient** for full non-bypassability: it makes
routed calls verifiable and forge/replay-resistant, while A1 remains a
separate, harder sub-problem that the gate alone cannot solve.

---

## 5. Canon compatibility (section 14)

Canon section 14: the gate "governs legitimacy", "operates pre-execution", is
"identity-agnostic", and does **NOT** "execute actions", "replace identity
systems", or "function as a policy engine". Section 2 ("non-executing
governance substrate") and section 10 ("does not execute actions or enforce
policies directly") reinforce this.

**The tension is pre-existing, not introduced by G4.** `pep.py` already
performs `requests.post(...)` to the target on ELIGIBLE, so the gate already
acts as a forwarding proxy on the execution hop  -  in mild tension with
"does NOT execute actions" *before any enforcement work*. Artifact 06 already
records this: the section 14 row is PARTIAL, "non-bypassable only for routed
calls (G4)". The design must open by admitting this, not by treating section
14 as pristine.

Against that baseline:

- **Push deepens** the tension (more gate action on the execution hop; gate
  drifts toward enforcement actor).
- **Caller-carry and target-pull relieve** it (gate returns to being a
  decision oracle; the *target* enforces its own admission by its own policy;
  refusal is the target's policy, not the gate's execution). Caller-carry can
  even remove the gate from the execution hop entirely, which *reduces* the
  pre-existing tension below today's level.

**No new invariant.** The envelope is already the implementation of canonical
CCS (artifact 05; canon section 12); target verification reuses `reassert()`
(canon section 13, "Eligibility does not persist across state transitions
without revalidation"). The interaction-binding check (section 4.2)
operationalizes canon section 13's "covering that exact interaction" and the
interaction identity of canon section 11.1; it is an *application* of existing
constructs, not a new invariant. Enforcement-by-target-verification is an
architecture choice over existing pieces.

---

## 6. The G4/G5 boundary (Decision E1)

`reassert()` reads its comparison hashes from **local disk**:
`_read_canon_lock()` reads `CANON/canon.lock`, `_evaluator_sha256()` reads
`IMPLEMENTATION/evaluator.py`, and `manifest_sha256()` reads the on-disk
manifest. A **target** is a different process and host from the gate; it does
not necessarily hold those files, and any copy it holds may differ from the
gate's. So a target-side reuse of `reassert()` requires an authentic, current,
**published** reference for the canon (and evaluator and manifest) hashes from
a durable source.

That durable source is exactly **G5** (`04_current_vs_claimed.md` G5 row: the
prior "external verification" rested on "an ephemeral, now-dead `webhook.site`
URL" and is "neither a persistent, reproducible, [nor] third-party artifact";
Action: "Build a target-side logging receiver; commit its log to
`EVIDENCE/proofs/`"). The dependency is concrete: **G4 verification depends on
a G5 artifact.**

This does **not** force a joint G4+G5 package. The G4 design is fully
*stateable* with G5 named as the durable-source precondition for the
verification step; resolving G5's build is not required to *write* the design.
**Decision E1 holds.** `[INFERENCE]` A VL-037 increment can stand up a minimal
published-hash source (for example, a committed hashes file under
`EVIDENCE/`) as a stub pending the real G5 build, or pair with G5 directly;
that ordering is a VL-037 decision, not a blocker for this artifact.

**VL-039 update (G5 boundary partially closed).** The durable-source precondition is now met for cross-host over loopback: `IMPLEMENTATION/published_source.py` fetches the published record and anchor-verifies it against a single pinned root (Decision B-prime-1), and `reassert()`/`verify_envelope()` accept an optional `record_source` (Decision D-b) so currency is checked against the fetched record, not local disk (Decision C). Evidence: `EVIDENCE/proofs/g5_cross_host_001.{log,md}`. The G5 floor remains, named not built (Decision F): secure distribution of the pinned anchor, record freshness/revocation, signing/PKI, and true multi-machine/TLS. G5 is transport-built, not blanket RESOLVED.

**VL-048 update (signed chain on the default path over the section-6 transport).**
The mandatory signing cutover (VL-047) put issuer signing on `pep.py`'s default
forward; VL-048 runs the full SIGNED chain over the section-6 cross-host
transport with no test-only shortcut: the gate signs on the default path via the
production env-var key path, pushes the envelope, and a target on a separate
process with a genuinely divergent local disk fetches the published record over a
real socket (the production `fetch_published_record`) and verifies the issuer
signature against an out-of-band-pinned key plus currency against the fetched
record plus binding. The proof of record is
`EVIDENCE/proofs/g5_signed_cross_host_001_runner.py`; the readiness predicate
END_TO_END_NO_SHORTCUT goes green at VL-048 (dependency set {issuer_signing,
enforcement_push}). This does NOT move the G5 floor: secure pinned-anchor and
pinned-key distribution, record/key freshness and revocation, and true
multi-machine / TLS remain named, not built (Decision F). The A3b freshness
sub-class (a stale-but-anchor-matching, validly signed record is still honored)
is unchanged and still named. No new invariant; `verify_envelope` logic
unchanged (the fetch is real, the verify is as-is); section 14 holds.

---

## 7. The reassert() replay / binding gap

Restating section 4.2 as a standalone finding because it is load-bearing for
the recommended increment:

`reassert()` checks repository-state currency (canon/evaluator/manifest hash
matches) plus tamper-integrity (`decision_sha256` verifies). It does **not**
compare the envelope's `request_context` against the live interaction. A
genuine, current envelope therefore REASSERTS even when presented alongside a
*different* forwarded body  -  so **same-repo-state replay across interactions
(A3) is not closed by `reassert()` alone**.

This is not a defect in `reassert()`: it does exactly what artifact 05's
reassertion protocol specifies (detect transitions via hash change). The point
is that canon section 13's per-interaction non-persistence is *broader* than
`reassert()`'s hash-based transition detection: a new interaction under
unchanged repo state is not a "transition" in `reassert()`'s sense, yet it is
plainly not covered by the prior ELIGIBLE. The missing piece is a target-side
**binding check**: before honoring an envelope, the target compares the
envelope's `request_context` (and `target_url`) against the interaction it is
about to act on, and refuses on mismatch.

`[INFERENCE]` This is an artifact-05-layer / verifier-obligation matter, not a
canon-version (GR-1) trigger: the binding check operationalizes existing canon
section 13 scope; it does not modify canon. If a later reviewer judges that the
canon should *name* per-interaction binding explicitly, that would be a
separate canon-layer question, flagged here and not performed.

---

## 8. Recommended VL-037 increment

Ordered, smallest-defensible-first. The verifier is built before any delivery
wiring because it is the reusable, delivery-agnostic, section-14-neutral piece;
the delivery choice (which deepens or relieves the section-14 tension) is then
made without having locked it in prematurely.

1. **Build the delivery-agnostic target-side verifier.** A function that takes
   an envelope plus the live interaction and returns accept/reject by:
   (a) running `reassert()` against a durable published hash source (the G5
   precondition; stubbed if G5 is not yet built); and (b) running the
   **binding check**  -  comparing the envelope's `request_context` and
   `target_url` against the live interaction. Reject on any `reassert()`
   outcome other than REASSERTED, and on any binding mismatch. This closes A2
   and A3 for routed traffic. `[INFERENCE]`
2. **Wire delivery minimally.** Smallest diff is **push** (attach the envelope
   to the existing forward). Recommend implementing push as the first
   measurable delivery step **with an explicit recorded note that push deepens
   the pre-existing section-14 tension**, and naming **caller-carry /
   proxy-removal** as the section-14-faithful target architecture for a later
   step. `[INFERENCE]` A reviewer who weights section-14 purity over diff-size
   may prefer to start with caller-carry; the artifact records both and leaves
   the weighting to the VL-037 author.
3. **Name A1 as out of the gate's reach.** Document that the declining caller
   is closeable only by a target-side policy refusing un-attested calls  -  a
   deployment decision, not a gate increment. Pair with the honest
   `TESTS/adversarial/test_bypass.py` that `04_current_vs_claimed.md` G4
   Action already calls for, demonstrating the A1 bypass plainly.

**Tests VL-037 will need (named, not written here, per design-session scope):**

- target verifier rejects a **forged** envelope (mutated field -> `reassert()`
  Row 2 INVALIDATED).
- target verifier rejects an **absent** envelope (no decision artifact ->
  reject).
- target verifier rejects a **replayed / binding-mismatched** envelope
  (genuine envelope for interaction X against live interaction Y -> binding
  check rejects, even though `reassert()` would REASSERT).
- target verifier **accepts** a valid, current, correctly-bound envelope.
- the A1 bypass is demonstrated honestly (direct-to-target call with no
  envelope still reaches the target; the gate cannot prevent it).

---

## 9. Open questions

1. **Delivery architecture for the eventual target state.** Push (smallest
   diff, deepens section 14) vs caller-carry (section-14-cleanest, removes the
   gate from the execution hop) vs target-pull. VL-037 picks the first
   increment; the eventual architecture is open. `[INFERENCE]`
2. **G5 durable-source form.** Committed hashes file under `EVIDENCE/`,
   a target-side logging receiver per the G5 Action, or a third-party anchor
   (canon section 8.2 PoE is the canon's optional hook). E1 names it a
   precondition; its form is a G5 decision.
3. **Binding-check canon status.** Whether per-interaction binding warrants
   explicit canon naming (a GR-1 question) or stays a verifier obligation
   operationalizing canon section 13. Flagged; not performed here.
4. **Whether A1 should be reflected in public framing.** G3 closed by stating
   properties honestly; if non-bypassable enforcement is built for routed
   traffic only, the public materials must keep saying so (A1 remains).

---

## 10. Derivation provenance

- **Threat model (section 2) and mechanism adequacy (section 4):** pre-draft
  cross-model verified, two recipients, framework-level evaluate procedure
  (VL-008 + Lesson 8). Both classified the mechanism-adequacy premise
  (closes A2 and routed-call binding; not A1) as holding under the strict
  authorization-by-direct-naming criterion  -  convergent. On the threat-model
  premise the recipients diverged: one held it under direct-naming; the other
  classified the **adversary-set exhaustiveness** sub-claim as
  under-determined because the source asserted exhaustiveness rather than
  deriving it. This artifact resolves that divergence by deriving
  exhaustiveness by construction over the participant set (section 2.3),
  upgrading the sub-claim from asserted to derived. The criterion-divergence
  is recorded as a finding, not a disagreement.
- **Q5 authenticity-vs-binding split (section 4.2, 7):** source-first from
  `envelope.py` (`decision_sha256` covers `request_context`; `reassert()`
  does not compare `request_context` to a live interaction). The cross-model
  run validated the premise as phrased ("closes Q5"); the source-first read
  adds that "Q5" must split, since the mechanism closes authenticity but not
  interaction-binding. No contradiction; the artifact is precise where the
  premise was loose.
- **Section-14 compatibility (section 5) and the G4/G5 boundary (section 6):**
  source-first from canon section 14 / section 2 / section 10, `pep.py` (the
  gate already POSTs), and `envelope.py` (`reassert()` reads local disk).
