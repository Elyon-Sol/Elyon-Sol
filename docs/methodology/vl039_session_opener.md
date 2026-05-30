# VL-039 session opener - T-G5-transport: cross-host transport of the published record

Tag: T-G5-transport. Predecessor: VL-038 (T-G4-enforce) at commit `33d0f5c`.
Baseline suite: 126 passed + 0 xfailed.

This opener is written by the session that closed VL-038. Every file fact
below was read from disk during VL-038, but per Lesson 3 it is a precondition,
not a disposition: re-read each load-bearing file from disk at session start
before any claim or edit depends on it. Treat the pre-session checklist as a
hard gate. State "checklist complete; N files read" before substantive work.

ASCII note carried forward and made explicit (Lesson 7, recurring family): in
prose and in every file, spell out "section N"; never emit U+00A7, em-dashes,
curly quotes, or Greek letters. The section-sign chat-prose leak recurred
twice in VL-038; this is the standing corrective.

---

## Where VL-038 left it (source-grounded)

VL-038 made Elyon-Sol enforce, co-located:

- `IMPLEMENTATION/pep.py` PUSHES the envelope on the ELIGIBLE forward as the
  out-of-band header `X-Elyon-Sol-Envelope` (value = `canonical_json(envelope)`,
  ASCII). The forwarded body is unchanged (`normalized_interaction`), so a
  routed call and a direct call differ only by the header.
- `EVIDENCE/published_hashes.json` (committed) carries the canon, evaluator,
  and manifest versions plus sha256 hashes - the same three hashes
  `build_envelope()` pins. Generated live by `EVIDENCE/published_hashes_gen.py`
  (reads `_read_canon_lock()`, `_evaluator_sha256()`, `manifest_sha256()`).
- `TESTS/adversarial/test_enforcement.py` holds a test-scope published-source
  reader (`load_published_hashes`, `verify_against_published_record(envelope,
  published)`) and an enforcing target (`build_enforcing_target_app(published,
  expected_target_url)`) that honors a call iff the envelope's pins match the
  published record AND `verify_envelope()` accepts. The one new reason is
  `REF_TARGET_PUBLISHED_RECORD_MISMATCH`; a missing or unparseable header maps
  to `verify_envelope(None, ...)` reusing `REF_VERIFY_ENVELOPE_ABSENT`.
- `verify_envelope(envelope, interaction, target_url)` (VL-037, reused as-is
  per VL-038 Decision D) returns `{"accepted", "reason"}`: it calls
  `reassert()` for currency plus integrity, then a `request_context`/`target_url`
  binding check. `reassert()` reads LOCAL disk for all three hashes (canon.lock,
  evaluator.py via `_evaluator_sha256()`, manifest.json via `manifest_sha256()`).

The honest limit VL-038 named and did not close: co-located, the published
record and the target's local disk are the same repository, so the
published-record check proves reproducibility-against-a-committed-artifact, not
independence-from-the-host. `reassert()` reads local disk; the published-record
check reads a locally-committed file. Its independence from local disk is shown
only by the injected-divergence test (`test_envelope_not_matching_published_record_refused`),
never exercised on the real path. G5 is where that becomes real.

---

## Session goal

Build cross-host transport of the published record: a target on a separate
process, whose local working files may differ from the gate's, fetches the
published record from a publisher, verifies it against a single pinned trust
anchor, and reaches the correct verdict (honors valid, refuses absent / forged /
replayed / mismatched) trusting the FETCHED record over its own local disk.

The killer demonstration (the load-bearing evidence): a target whose local
`IMPLEMENTATION/evaluator.py` is byte-divergent from the publisher's. A valid
envelope built by the gate against the authentic evaluator is delivered to this
target. A VL-038-style target verifying against local disk would FALSE-REFUSE it
(its local evaluator hash does not match the envelope's pin, so `reassert()`
returns INVALIDATED). The G5 cross-host target instead fetches the authentic
published record, verifies the envelope's pins against it, and HONORS the valid
envelope despite its own divergent disk - and still REFUSES a forged one. That
is the proof G5 delivers something co-located verification cannot: a verdict
that does not depend on the target trusting its own files.

---

## The hard question (state it plainly; do not let it get lost)

G5 does NOT make verification trustless. Trust does not vanish; it bootstraps.
What G5 buys is reducing and explicitating the trust surface: from "the target
trusts its entire local working tree" down to "the target trusts one pinned
published-record anchor, distributed out-of-band, plus transport integrity."
Bootstrapping trust somewhere is unavoidable - the value is that the anchor is a
single value a third party can independently verify, not a whole repository the
target happens to hold.

This is the analog of how the project handled A1 (named as the gate-unreachable
floor) and the section-14 tension (named as pre-existing). The residual - how
the pinned anchor reaches the target securely, and record freshness/revocation -
is the G5 floor, named not closed. Do not overclaim "the target needs no trust";
claim "the target's trust is reduced to one pinned anchor."

This claim - "does pinned-anchor-plus-fetch reduce the trust surface, or merely
relocate it?" - is framework-level and is exactly the question deferred at the
end of VL-038. It is the natural Decision G election (see below).

---

## Pre-locked decisions

- **Decision A (scope).** In scope: a transport by which a target fetches the
  published record from a publisher; a single pinned trust anchor the target
  verifies the fetched record against; a cross-host verifier path whose currency
  dimension comes from the FETCHED record, not local disk; a genuinely-divergent-
  local-disk demonstration (the killer evidence above); and a cross-host evidence
  run. NOT in scope: signing / public-key infrastructure (named, not built);
  true multi-machine networking and TLS (modeled by two loopback processes);
  record freshness / revocation (named, not built); any change to the canon,
  manifest, or evaluator SEMANTICS. The co-located VL-038 path stays working.

- **Decision B (transport; PRE-LOCKED).** Transport: the target fetches the
  published record over loopback HTTP (`127.0.0.1`, a separate publisher process)
  - this models cross-host without external network (sandbox loopback is allowed;
  true multi-machine is deployment). Not contested. The trust ANCHOR is split out
  into Decision B-prime below, because it is no longer pre-locked.

- **Decision B-prime (trust anchor; GENUINELY OPEN - decide at Checkpoint A).**
  A prior draft of this opener pre-locked a single pinned `sha256` of
  `EVIDENCE/published_hashes.json` as the anchor and called the choice "open"
  while recommending it. A parallel cross-model adversarial audit (off-framework;
  see `docs/methodology/cross_model_adversarial_audit.md`) found, in both cold
  independent reads, that this was NOT actually open - the design had already
  accumulated momentum toward the committed-hash-record approach, and a stronger
  alternative family was omitted. So the anchor is now a real fork, undecided,
  and decided at Checkpoint A by someone OTHER than the author who wrote this
  opener (the single-author loop is exactly what the audit flagged):
  - **B-prime-1, pinned root hash.** A single pinned `sha256` of
    `published_hashes.json`, configured out-of-band; the target fetches, verifies
    the hash equals the pinned root, then trusts the record. Extends the hash
    chain (`canon.lock` -> `published_hashes.json` -> pinned root). Smallest
    bootstrap; one configured value.
  - **B-prime-2, signed record.** The publisher signs the record (or a detached
    signature over `decision_sha256`) with a release key; the target verifies the
    signature against a pinned public key. Removes per-record pinning; moves trust
    to key governance.
  - **B-prime-3, transparency log / TUF.** A signed, append-only log (TUF-style
    metadata, Sigstore/Rekor, or a Merkle inclusion proof) so freshness and
    revocation come for free and the anchor is auditable, not just pinned.
  Pick one at Checkpoint A on its merits, not by inheritance. Whatever is not
  chosen is named, not built (Decision F). The audit's point stands: do not let
  B-prime-1 win by default just because the co-located VL-038 work already speaks
  in committed hashes.

- **Decision C (load-bearing).** The cross-host verifier's CURRENCY check must
  come from the fetched-and-anchor-verified record, NOT from `reassert()`'s local
  disk reads. Decision C is proven by the divergent-local-disk demonstration: a
  target whose local disk differs from the publisher still honors a valid envelope
  (by trusting the fetched record) and still refuses a forged one. If the
  cross-host path still consulted local disk for currency, that demonstration
  would fail - which is the test that it is load-bearing.

- **Decision D (verifier reuse - the genuine fork).** VL-038 reused
  `verify_envelope()` as-is because `reassert()`'s local-disk reads were correct
  co-located. Cross-host they are not (the target's local disk is not the
  authority). So D must decide HOW the cross-host path gets currency-from-record
  plus integrity plus binding without `reassert()`'s local reads. Two shapes,
  both source-first calls at Checkpoint A/B:
  - **D-a (new module, wrap):** a new cross-host verifier composing
    (fetched-record currency) + (a `decision_sha256` integrity check) + (the
    `request_context`/`target_url` binding check). The co-located `verify_envelope`
    stays byte-unchanged. Risk: duplicating the integrity and binding logic, which
    can drift from `verifier.py`.
  - **D-b (parameterize, edit):** extend `reassert()` / `verify_envelope()` to
    accept an injected record source, so the three currency reads come from the
    provided record rather than local disk (the parameter VL-038 explicitly
    deferred). More unified; edits `verifier.py` and `envelope.py`. Note that
    `decision_sha256` integrity and the binding check are already pure functions
    over the envelope and interaction (no disk), so only the currency dimension
    is what changes.
  Flag honestly: VL-038's "no `verifier.py` edit" most likely does NOT survive G5
  - cross-host is the point at which the local-disk assumption finally has to
  give. Whichever shape is chosen, halt and treat as a real bug only if existing
  behavior is wrong (constraint l); a needed extension is not a bug.
  Dependency (cross-model audit F1): the cross-host verifier's integrity check
  inherits whatever the timestamp decision is - `timestamp_utc` is currently
  OUTSIDE `decision_sha256` (pinned by `TESTS/adversarial/test_findings_001.py::
  test_finding_timestamp_mutation_does_not_break_integrity`). Decide the timestamp
  question (fold it into the hash, or formally accept the exclusion) BEFORE wiring
  the cross-host integrity check, or the verifier will silently carry the same
  exclusion cross-host.

- **Decision E (evidence).** `EVIDENCE/proofs/g5_cross_host_001.{log,md}` in the
  g3/g4 format, driven by a runner that stands up a publisher process and a
  target process over loopback. It MUST include the divergent-local-disk case
  (honor-valid-despite-divergent-disk and refuse-forged-despite-divergent-disk),
  plus a fetched-record-fails-pinned-anchor refusal (the anchor doing its job).

- **Decision F (named, not built).** Signing / PKI (signed records, no per-target
  pinning); record freshness and revocation (a stale-but-anchor-matching record
  is a distinct threat - name it as the next hardening after transport); secure
  distribution of the pinned anchor itself (the G5 bootstrap floor, parallel to
  the A1 floor); TLS and true multi-machine networking (deployment).

- **Decision G (cross-model - recommended this time).** The trust-reduction
  claim ("pinned-anchor-plus-fetch reduces the trust surface to one bootstrapped
  value rather than eliminating trust") is framework-level and genuinely
  contested - it is the question VL-038 left open. Electing the framework-level
  `cross_model_evaluate_template.md` on THIS claim at Checkpoint A is recommended
  (it is in scope for that template, unlike code questions, per VL-036 Finding 1).
  Pose it narrowly: "Does a target verifying a fetched record against a single
  pinned hash, on a host whose own files may differ, gain defensible independence
  from its local disk, or does it only relocate trust to the pinned anchor and
  the channel?" Build/wire forks (D-a vs D-b) route to
  `build_resumption_request_template.md`, not the evaluate template.

---

## Checkpoints

- **Checkpoint A (design; pause for review).** State: the transport mechanism
  and the publisher/target process shapes; the pinned-anchor artifact and how the
  target is configured with it; the Decision-D resolution (D-a new module vs D-b
  parameterize) with the source-first reasoning; the cross-host verifier's exact
  check order (anchor-verify the fetched record, then currency-against-record,
  then integrity, then binding); the divergent-local-disk demonstration; and the
  evidence plan. Confirm Decision C is satisfied (currency from the record, not
  disk). Elect Decision G on the trust-reduction claim. Pause.

- **Checkpoint B (spec-gap; mandatory).** Decide: does the transport / fetched-
  record shape need a `SPEC/` home, or is it a deployment-wire concern like the
  forward (VL-038 Checkpoint B precedent)? Where does the pinned anchor live -
  `CANON/` (lock-class, but then GR-1's version-increment-only scope applies and
  is wrong for a derived anchor), `EVIDENCE/`, or target configuration outside the
  repo? Read `MAINTENANCE_PROTOCOL.md` GR-1 source-first before placing it. If a
  `verifier.py`/`envelope.py` edit is chosen (D-b), confirm whether candidate GR-2
  (spec-edit-first) is triggered. Decide test-vs-code timing.

- **Checkpoint C (implementation review).** Confirm: the cross-host path reads
  NO local disk for currency (grep/inspect); the co-located VL-038 path is
  unchanged or correctly subsumed; if `verifier.py`/`envelope.py` were edited,
  the diff is exactly the intended change and the 126 baseline plus new tests are
  green; section 14 re-read (does fetching make the gate or target execute or do
  more? - it should not: the target still only verifies and acts/refuses, now
  against a fetched authority). All new/changed files ASCII-clean.

- **Checkpoint D (pre-commit).** Structural-doc edits (artifact 04 G5 row moves
  from open-with-committed-record to transport-built; artifact 06 section 14 row;
  artifact 08 section 6 the G5 boundary now partially closed), STATE.md, the
  VL-039 ledger entry anchored after the `### VL-038 -` header, and the commit.
  Stage intended paths only; never `git add -A`.

---

## Constraints

- **(i)** Any pinned trust anchor is derived live (sha256 of the actual
  `published_hashes.json` on disk), never hand-copied.
- **(j)** ASCII discipline: byte-sweep drafted text and files with a Python
  byte check or `LC_ALL=C grep -n '[^[:print:][:space:]]'` (basic regex); never
  `grep -P` on MINGW64 (it rejects `-P` under `LC_ALL=C`). Spell out "section N"
  in all prose and files. Run the sweep on chat prose too, not only files
  (the recurring section-sign family is a chat-prose leak).
- **(k)** Network: the demonstration uses loopback `127.0.0.1` two-process only;
  no external domains. A real second process (not in-process `TestClient`
  sharing the tree) is what makes the cross-host claim honest - prefer it over
  an in-process mock where feasible, or a target whose local disk is genuinely
  mutated to differ.
- **(l)** A real bug in existing code halts the build (do not work around it).
  A needed extension to enable cross-host (D-b) is NOT a bug.
- **(m)** MINGW64 discipline: work OUTSIDE the repo working tree; stage intended
  paths explicitly and never `git add -A` (the VL-037 and VL-038 root-scratch
  family - now two instances; the `.gitignore` guard for `vl*` scratch is a
  standing candidate, see carried debts). Use the `IMPLEMENTATION.` import prefix;
  import-test any new module; pytest runs from repo root with `PYTHONPATH=.`.
- **(n)** Work order: read checklist -> Checkpoint A design (pause) -> Checkpoint
  B spec-gap -> build the publisher/transport -> build the pinned-anchor verify
  and the cross-host verifier (D-a or D-b) -> the divergent-disk demonstration
  and tests -> evidence run -> real-environment pytest (expect 126 + new) ->
  artifact 04/06/08 -> STATE.md -> ledger (anchor `### VL-038 -`) -> commit.

---

## Pre-session checklist (hard gate)

**Tier 1 (load-bearing for G5):**
1. `IMPLEMENTATION/verifier.py` - `verify_envelope()`, the REF_VERIFY_ set, the
   binding check (the thing D-a wraps or D-b edits).
2. `IMPLEMENTATION/envelope.py` - `reassert()` (the local-disk currency reads),
   `_read_canon_lock()`, `_evaluator_sha256()`, `manifest_sha256` usage,
   `canonical_json()`, `build_envelope()`.
3. `TESTS/adversarial/test_enforcement.py` - the VL-038 reader + enforcing target
   that G5 extends cross-host.
4. `EVIDENCE/published_hashes.json` and `EVIDENCE/published_hashes_gen.py` - the
   record and its live derivation (the anchor is the sha256 of this file).
5. `IMPLEMENTATION/pep.py` - the push delivery (context; unchanged by G5).
6. `IMPLEMENTATION/evaluator.py` - `manifest_sha256()`, `load_manifest()`.
7. `docs/restructure/08_enforcement_design.md` - sections 4.4 (A1 floor) and 6
   (the G4/G5 boundary; G5 named as the deployment precondition).
8. `docs/restructure/04_current_vs_claimed.md` - the G5 section (gap definition +
   the VL-038 partial bullet).
9. `docs/restructure/06_spec_to_code_traceability.md` - section 13 and section 14
   rows.
10. `CANON/canon.md` - sections 11.7 / 11.8 / 11.9, 12, 13, 14 (the invariants and
    the scope clause; confirm G5 introduces no new invariant).
11. `CANON/canon.lock`, `MANIFEST/manifest.json` - the pinned originals.
12. `docs/MAINTENANCE_PROTOCOL.md` - GR-1 scope (decides where the anchor lives)
    and the GR-2 candidate status.

**Tier 2 (tests / regression, for the 126 baseline and the migration surface):**
13. `TESTS/test_pep.py`, `TESTS/adversarial/test_verifier.py`,
    `TESTS/adversarial/test_bypass.py`, `TESTS/adversarial/test_request_schema.py`,
    `TESTS/adversarial/test_envelope.py`, `TESTS/adversarial/test_ccs_canonical.py`,
    `TESTS/adversarial/test_evaluator_canonical.py`,
    `TESTS/test_adversarial_evaluator.py`, `TESTS/test_concurrency.py`,
    `TESTS/test_replay_receipts.py`.

**Tier 3 (methodology / state):**
14. `STATE.md` (the VL-038 current-verified-state bullet and Next-open-action 33).
15. `EVIDENCE/verification_ledger.md` (the `### VL-038 -` entry; the append anchor).
16. `docs/session_mechanics_lessons.md` - Lessons 2, 3, 5, 7 (anchor discipline,
    source-first precondition, set-exhaustiveness, two-stage ASCII).
17. `docs/methodology/apply_script_template.py` (if an apply-script is used).
18. `EVIDENCE/proofs/g4_refused_bypass_001.md` (the evidence format G5 extends).
19. `README.md`.

State "checklist complete; N files read" before any design or edit.

---

## What done means

A publisher process serves the published record; a target process, with a local
working tree that differs from the publisher's, fetches the record, verifies it
against a single pinned anchor, and verifies a delivered envelope's currency
against the FETCHED record (not local disk), plus integrity and binding. The
target honors a valid envelope and refuses absent / forged / replayed /
mismatched ones, and - the load-bearing case - honors a valid envelope and
refuses a forged one EVEN THOUGH its own local disk differs from the publisher's.
A fetched record that fails the pinned anchor is refused. Captured as
`EVIDENCE/proofs/g5_cross_host_001.{log,md}`, reproducible. G5 moves from
open-with-committed-record to "transport built; trust bootstrapped at one pinned
anchor; signing, freshness/revocation, anchor distribution, and multi-machine
named not built." G5 does NOT become blanket RESOLVED.

---

## What this opener does NOT predict (honest scope shape)

- Whether Decision D resolves to D-a (new module) or D-b (edit `verifier.py` /
  `envelope.py`) - a source-first call at Checkpoint A/B.
- Where the pinned anchor lives (`CANON/` vs `EVIDENCE/` vs out-of-repo target
  config) - decided at Checkpoint B after reading GR-1 source-first.
- Whether any `SPEC/` edit is needed (lean: no, transport is a wire/deployment
  concern like the forward) - Checkpoint B.
- The test-count delta and which existing tests (if any) shift - enumerated
  against `TESTS/` at build time, never predicted (Lesson 5).
- Whether the co-located VL-038 path needs any change to coexist with the
  cross-host path - likely not, but source-first.
- The exact pinned-anchor and transport encodings.

---

## Carried VL-038 follow-up debts (optional first; a small follow-up commit)

- Post-commit hash fill: `STATE.md`'s last-updated `HEAD <this commit>` and the
  `EVIDENCE/proofs/g4_refused_bypass_001.md` commit anchor take the real `33d0f5c`
  (the VL-012 self-referencing-hash pattern).
- Ledger correction: the VL-038 entry's process finding 1 says "two chat-prose
  section-sign instances ... user-caught both times" as established fact; the
  second instance is user-reported but not self-verifiable (the file sweep does
  not cover prose; the two flags were identical messages). It should read "one
  self-verified plus one user-reported." Recording user-reported-but-unverified
  as confirmed is the soft overclaim the ledger exists to prevent.
- `.gitignore` guard for `apply_vl*.py` / `vl*_commit_msg.txt` /
  `vl*_ledger_entry.md` / root-level `published_hashes*.json` duplicates - the
  root-scratch family now has two data points (VL-037 sweep; VL-038 root
  duplicates caught pre-stage). Deferred pending a source-first read of the
  current `.gitignore`.

These are not blocking; handle as a VL-038 follow-up commit before or alongside
VL-039 at the session's discretion.

---

## After VL-039 (the remaining map)

Record freshness / revocation (the next hardening after transport); signing /
PKI (removing per-target pinning); A1 target-side admission policy (the declining
caller); caller-carry / proxy-removal (the section-14-faithful architecture);
the T-bookkeeping backlog (G1 / G8 / G9 / G11 / G14) and T-prose-drift. None
blocking.
