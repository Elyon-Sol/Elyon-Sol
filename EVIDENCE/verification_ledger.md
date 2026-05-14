# Elyon-Sol - Verification Ledger

Append-only record of how claims about Elyon-Sol became trusted.

## Rules
- A claim enters as SINGLE-SOURCE when first derived.
- A claim becomes CONFIRMED only when independently re-derived FROM PRIMARY
  SOURCES (canon, code) - never from an artifact that merely asserts it.
- A verdict or rating ("approved", "8.7/10") is NEVER a confirmation event
  and is never recorded here as one. Only derivations against primary sources are.
- Entries are append-only. Corrections are new entries, not edits.
- Each entry cites the sources and, where one exists, the commit hash.

## Status values
SINGLE-SOURCE | CONFIRMED | DISPUTED | RETRACTED | CORRECTED

---

## Entries

### VL-001 - Ledger established
- Date: 2026-05-14
- Event: Verification ledger created.
- Note: Entries VL-002..VL-005 record verification work performed during the
  Rev. 2 restructure session, which PREDATES this ledger. Those verifications
  reference primary sources by version, not by commit hash, because they were
  performed before the ledger and commit-anchoring existed. All future entries
  cite a commit hash.

### VL-002 - G0 (CCS specification/implementation drift)
- Date: 2026-05-14
- Claim: Canonical CCS (whitepaper v0.9.8.4 sections 12-13) is a temporal
  invariant over state transitions; implemented ccs_valid() is a point-in-time
  manifest-integrity check. They are not the same invariant.
- Status: CONFIRMED
- Derived by: Claude, from whitepaper section 12 + IMPLEMENTATION/evaluator.py
- Independently re-derived by: Grok, from the same primary sources (whitepaper
  sections 12-13 + evaluator.py), reaching the same localization including the
  section 8.1 comparison.
- Basis for CONFIRMED: two independent derivations from primary sources, not
  from each other's artifacts.

### VL-003 - G1 (README test count) corrected
- Date: 2026-05-14
- Claim (Rev. 1): Test counts 3/30/34/37 constitute a four-way contradiction.
- Status: CORRECTED
- Correction: Verified against test_pep.py (contains 4 tests) and manifest.json.
  The 30/34/37 figures are plausibly one growing suite at different commits.
  Real issue downgraded to: no commit-pinned source of truth; stale README.
- Derived by: Claude, against test_pep.py + manifest.json + repo README.

### VL-004 - "Validator wrapped in oversized language" read retracted
- Date: 2026-05-14
- Claim (earlier): Elyon-Sol is a ~100-line validator with oversized framing.
- Status: RETRACTED
- Reason: Retracted after reading whitepaper v0.9.8.4. The canon is a
  legitimate formal specification (formal interaction model, set-theoretic
  invariant definitions, prior-work positioning). Accurate finding: faithful
  partial implementation of a real specification, one drifted invariant (G0).
- Derived by: Claude, against whitepaper v0.9.8.4.

### VL-005 - Grok first review (rating) - NOT a confirmation event
- Date: 2026-05-14
- Event: Grok produced a rated review ("8.7/10", "Approved") of the Rev. 2
  package, working from the package artifacts only - not primary sources.
- Status: recorded for history; carries NO verification weight.
- Reason: Per ledger rules, a verdict/rating is not a confirmation event. The
  review did not derive claims from canon or code. Grok's LATER clean-room
  pass against primary sources is the entry that counts - see VL-002.

### VL-006 - canon.md transcribed and locked
- Date: 2026-05-14
- Event: v0.9.8.4 canon transcribed from CANON/canon_v0.9.8.4.pdf to
  CANON/canon.md and locked via CANON/canon.lock.
- Status: CONFIRMED
- Sources: CANON/canon_v0.9.8.4.pdf (immutable source of record).
- Transcription by: Claude. Verified by: Justin Laporte, against the PDF.
- Verified points:
    F4 - Section 3 Notation Clarification: confirmed faithful.
    F5 - Sections 12.1-12.4 and 13 (the G0 sections), checked section by
         section: confirmed faithful. G0 therefore rests on a verified
         transcription.
    F6 - Abstract "ElyonSol" -> "Elyon-Sol": a line-wrap artifact in the PDF,
         normalized in canon.md by decision (kept, not reverted).
- Representation decision (F3): canon.md uses ASCII-safe notation (AC^3, T^26,
  S_{t+1}, <=>, AND, superset-or-equal, etc.) as a representation choice, NOT a
  content change. Per Section 3 the notation is nominal; ASCII forms denote the
  identical constructs. A Transcription Note in canon.md records this and is
  marked non-canonical. Pure-ASCII confirmed by automated byte check.
- Lock: see CANON/canon.lock (sha256 of canon.md at commit time).
- Effect: canon.md is now the working canonical reference, anchored to the PDF.

### VL-007 - v0.9.8.4 known canonical properties (numbering gaps)
- Date: 2026-05-14
- Event: Two structural gaps identified in canon v0.9.8.4 during transcription:
    1. Section 8 has subsections 8.1, 8.2, 8.4 - no 8.3.
    2. Appendix D begins at D.2 - no D.1.
  Both are present in the source PDF; they are not transcription errors.
- Status: CONFIRMED (properties of the locked version, not defects under repair)
- Decision: v0.9.8.4 is locked AS-IS, including these gaps. They are recorded
  known properties of this canonical version. Any correction is a future
  canon-version event - a new version, new hash, new lock, new ledger entry -
  never an in-place edit of v0.9.8.4.
- Decided by: Justin Laporte
- Establishes governance rule GR-1: canon is corrected only by version
  increment, never by in-place edit. (To be recorded in the maintenance
  protocol artifact.)
