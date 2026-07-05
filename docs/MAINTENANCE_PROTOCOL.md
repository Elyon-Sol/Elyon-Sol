# Elyon-Sol - Maintenance Protocol

Governance rules for how this repository is maintained over time.

This file is the home for governance rules (GR-N) that constrain how the
repository, the canon, and the ledger may be changed. It is the
counterpart to `EVIDENCE/verification_ledger.md`: the ledger records how
claims became trusted; this file records the rules under which the
repository is allowed to change.

## Rules
- A governance rule enters as a numbered entry GR-N when established.
- A rule is established only by a ledger entry (VL-N) that derives or
  decides it. The originating ledger entry is cited in the rule entry.
- Entries are append-only. Amendments are new entries, not edits;
  superseding entries cite the rule they supersede.
- Each entry cites the originating ledger entry and the date established.

## Status values
ACTIVE | SUPERSEDED | RETIRED

---

## Entries

### GR-1 - Canon is corrected only by version increment
- Date established: 2026-05-14
- Originating ledger entry: VL-007
- Status: ACTIVE
- Rule: The locked canon version (currently v0.9.8.4) is corrected only
  by version increment, never by in-place edit. Any correction is a new
  canon-version event - a new version, a new hash, a new lock, and a new
  ledger entry recording the change.
- Scope: applies to `CANON/canon_v0.9.8.4.pdf` (the immutable source of
  record), `CANON/canon.md` (the ASCII-safe transcription locked against
  it), and `CANON/canon.lock` (the sha256 of canon.md at lock time).
- Rationale: the canon is the highest-order primary source in this
  repository. Every verification entry in the ledger that cites a canon
  section depends on the canon at that section being stable. In-place
  edits would silently invalidate prior verifications without a record
  of the change. Version increment makes any change explicit, hashable,
  and auditable.
- Known canonical properties of v0.9.8.4 (recorded under this rule):
    - Section 8 has subsections 8.1, 8.2, 8.4 - no 8.3.
    - Appendix D begins at D.2 - no D.1.
  These are present in the source PDF and are not transcription errors.
  They are properties of the locked version, not defects under repair.
  See VL-007.

### GR-2 - Readiness is test-derived, never human-attested
- Date established: 2026-06-03
- Originating ledger entry: VL-048
- Status: ACTIVE
- Rule: No readiness fact in `EVIDENCE/readiness.json` is human-attested.
  Every readiness flag (`built`, `wired_to_default`, `exercised_e2e`,
  `transported`) and every deployment predicate (`green`) that is true MUST
  name a proof test that exists and passes; a true flag or green predicate with
  no named, existing, passing proof is a hard build failure (not a warning).
  A false flag MUST name a `blocked_by` reason. built-but-unwired is ALLOWED
  (build-then-wire is the method); claimed-but-unwired is FORBIDDEN. The gate
  is enforced by `IMPLEMENTATION/readiness.py` and `TESTS/readiness/`.
- Scope: `EVIDENCE/readiness.json` (the single source of readiness truth),
  `IMPLEMENTATION/readiness.py` (the validator), and `TESTS/readiness/` (the
  enforcing suite). STATE.md and the ledger REFERENCE the manifest; they do not
  restate readiness in prose (prose drifts).
- Rationale: prototype-drift accumulates silently as built-but-unwired
  capability and as claims that outrun what is wired. A readiness value a person
  can type without a test behind it is exactly that drift. Deriving every
  readiness fact from a named test makes the count un-fakeable and makes a
  claim-ahead-of-its-test a blocking, fail-closed signal. See
  `docs/restructure/10_readiness_spec.md` (the spec) and VL-043 (the build) /
  VL-047 (DEFAULT_SECURE green) / VL-048 (END_TO_END_NO_SHORTCUT green +
  this rule's formalization).
- Honest ceiling (recorded under this rule): the gate catches claim-vs-wiring
  divergence; it does NOT perform the wiring. The remaining red
  (ROOT_RECOVERY) is real engineering the gate cannot do for the project.

### GR-3 - Evidence is referent-bound; model evaluative judgment is not evidence
- Date established: 2026-06-06
- Originating ledger entry: VL-057
- Status: ACTIVE
- Rule: A bounded claim about the system or its worth moves only on a
  referent-bound result: a passing or failing test/runner (execution), or an
  adversarial-by-construction outcome (a demonstrated bypass, or a demonstrated
  inability to produce one). No model-sourced evaluative judgment - soundness,
  novelty, value, "convergent", "N-0" - is evidence or may move a claim, because
  when the artifact under review and the evaluate prompt share an author the
  judgment measures framing, not the world. A cross-model run is permitted ONLY
  as (a) an adversarial break-it task with a pass/fail referent, or (b) an
  explicitly-labeled framing stress-test whose output reaches neither the
  evidence record (the ledger) nor any claim.
- Scope: every cross-model "evaluate" the project commissions; every ledger use
  of "convergent" / "N-0" / "SOUND" as confirmation; the
  `cross_model_evaluate_template`. Referent-bound results (tests, runners, pytest
  counts, the readiness predicates under GR-2) are unaffected - they ARE the
  evidence this rule routes belief toward.
- Rationale: when one iterative build surface produces the artifact, its framing,
  AND the evaluate prompt, agreeable judges fed that shared framed input produce
  correlated error, not independent confirmation; adding judges launders the bias
  rather than cancelling it. The contamination is upstream of procedure, so a
  procedurally clean evaluate is still non-evidential on value/soundness. This is
  the evaluate-side analog of GR-2: GR-2 forbids a human-attested readiness value
  standing in for a test; GR-3 forbids a model-persuaded value judgment standing
  in for a referent-bound result. See the VL-057 demotion entry
  (which demoted the VL-023 / VL-040 / VL-042 / VL-044 follow-up convergence
  verdicts), and `docs/methodology/external_verification_readiness.md` (the
  human-verification analog).
- Honest ceiling (recorded under this rule): this rule constrains what may COUNT
  as evidence; it does not itself produce evidence. The referent-bound results it
  routes belief toward (real-transport adversarial attack; a stake-free rebuild
  attempt) largely do not yet exist - `external_verification_readiness.md` records
  the project as NOT READY, the binding gate being the G5 real-transport floor.

### GR-4 - The verification ledger is append-only and scoped to verification events
- Date established: 2026-07-03
- Originating record: commit-only. Per clause 1 below, adopting this rule is not a
  verification event, so it takes NO VL entry - it is recorded in STATE.md and this
  commit. The rule obeys itself on the way in.
- Status: ACTIVE
- Rule:
  1. SCOPE. An action earns a `VL-N` entry ONLY if it verified, corrected, retracted,
     or disputed a claim about the system against a PRIMARY SOURCE (canon, code, a
     test/runner execution, a live-surface result, or an external referent).
     Authoring (docs, recruiting, site copy), refactors, packaging, bookkeeping, and
     environment/recovery notes are recorded in the git commit message and, if they
     change current state, in STATE.md - NOT in the ledger. `git log` is the
     authoritative record of what was done; STATE.md is current state; the ledger is
     verification provenance only.
  2. APPEND-ONLY. The ledger is never pruned, curated, renumbered, or edited for
     length or aesthetics. Existing `VL-N` entries and their numbers are immutable:
     they are cross-referenced by later entries, by GR rules, by STATE.md, and by
     published Zenodo records, and are reconstructable from git history regardless. A
     correction to a past entry is a NEW entry that cites it, never an in-place edit.
  3. READABILITY IS ADDITIVE. Signal-to-noise is managed only by ADDING navigation:
     a curated index/summary (`EVIDENCE/verification_ledger_index.md`) and/or a
     byte-preserving archive split that keeps every entry and every cross-reference
     intact. Reorganizing for the read is permitted; removing content is not.
  4. SIZE. A new entry states the verification event, its referent, and the outcome.
     Process/environment diaries and ritual boilerplate are minimized; such notes
     belong in the commit message, not the entry.
- Scope: every session close; every candidate ledger entry; the SESSION_PROTOCOL
  close step "if any claim was verified, corrected, retracted, or disputed this
  session: append a ledger entry" - GR-4 is the operative definition of that "if".
- Rationale: the ledger's value is that it is append-only, cross-referenced, and
  externally cited - credible precisely because it has never been edited for
  convenience. Two failure modes threaten it. Dilution (logging non-verification work
  until the load-bearing entries are buried) is cured going forward by clause 1.
  Curation (pruning/renumbering for cleanliness) is forbidden by clause 2 because it
  (a) breaks the internal cross-reference graph and external DOI citations, (b)
  demonstrates the record CAN be author-edited for convenience - self-refuting for a
  project whose thesis is immutable, fail-closed record-keeping - and (c) is pointless
  regardless, since git history retains every byte, so it incurs the credibility cost
  without any storage benefit. The legitimate impulse behind pruning (poor
  signal-to-noise) is real and is satisfied by clause 3's additive index/archive.
- Honest ceiling: this rule governs the RECORD, not the work. A leaner, higher-signal
  ledger is more credible to an external auditor but does not itself advance G5; the
  binding gate remains a blind external attacker on the live surface.

### GR-5 - Ledger archiving is versioned, immutable, and byte-preserving
- Date established: 2026-07-03
- Originating record: commit-only (per GR-4 clause 1; archiving is reorganization, not a
  verification event - no VL entry).
- Status: ACTIVE
- Rule:
  1. VOLUMES. When the active `EVIDENCE/verification_ledger.md` exceeds 100 entries, its
     oldest contiguous block is MOVED verbatim - cut at a primary `### VL-N` header, never
     mid-entry - into the next numbered volume under `EVIDENCE/ledger_archive/`, named
     `vol_NNN__VL-<first>_to_VL-<last>.md`. Entries are moved, never rewritten; numbers
     never change. (The initial consolidation volume may cover all pre-existing history;
     subsequent volumes are ~100 entries.)
  2. IMMUTABILITY + VERSIONING. Each volume, once written, is append-CLOSED and immutable.
     Its sha256, VL range, and entry count are recorded in the manifest
     `EVIDENCE/ledger_archive/INDEX.md` and in a sidecar `vol_NNN__*.sha256` (mirroring
     `canon.lock`). A closed volume is never edited; a correction to an archived entry is a
     NEW entry in the ACTIVE ledger that cites it (GR-4 clause 2).
  3. BYTE-PRESERVING RECONSTRUCTION (the invariant). Concatenating, in volume order, every
     volume's entry region and then the active ledger's entry region MUST reproduce the
     historical entry region byte-for-byte; with the preamble prepended, the pre-split
     ledger exactly. Every archiving commit records this reconstruction check (the
     reassembled sha256 == the pre-split sha256) in INDEX.md; a split whose check fails is
     rejected and nothing is moved.
  4. THE ACTIVE FILE. `verification_ledger.md` always keeps its preamble, an "Archived
     volumes" pointer table (volume, range, sha256), and all un-archived entries. The
     curated index (`verification_ledger_index.md`) spans all volumes + active.
- Scope: every archiving event; the archive manifest; any reader reconstructing history.
- Rationale: archiving keeps the active ledger lean (GR-4 clause 3) WITHOUT deletion.
  Per-volume hashes plus the reconstruction invariant make the archive tamper-evident AND
  provably complete, so leanness costs nothing in integrity - the same chunk-and-hash
  discipline as `canon.lock` and the published record. This is the sanctioned form of the
  GR-4 clause-3 archive split; it is NOT pruning, which GR-4 clause 2 forbids.
- Honest ceiling: governs the record's storage, not the work; does not advance G5.
