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
