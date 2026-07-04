# Verification ledger - archive manifest (INDEX)

Immutable, versioned archive of `verification_ledger.md` (GR-5). Each volume is
append-CLOSED and hash-anchored; nothing is ever deleted or renumbered.

## The reconstruction invariant (GR-5 clause 3)

Concatenating, in volume order, each volume's entry region (the bytes after its
`## Entries` header) then the active ledger's entry region (after its `## Entries
(current era ...)` header) reproduces the historical entry region byte-for-byte;
prepending the active ledger's preamble yields the pre-split ledger exactly.

- Pre-split full-ledger sha256 (2026-07-03, 163 entries): `a9fd3197a0e04d3710562bbc9517dff1a05ef608ef29234c88a22510ec3f2c8d`
- Verified at split time: reassembled preamble + vol_001 + active == this sha (PASS).

## Volumes

| Volume | File | VL range | Entries | sha256 |
|--------|------|----------|---------|--------|
| 001 | `vol_001__VL-001_to_VL-107.md` | VL-001 .. VL-107 | 133 | `381008b5fedb48555cd1c642529680c04e8ed438ed06b292e2915a08b0bab66a` |

Active ledger holds VL-108 onward (30 entries).

## Adding the next volume (GR-5)

When the active ledger exceeds 100 entries, move its oldest contiguous block (cut at a
primary `### VL-N` header, never mid-entry) into `vol_002__VL-<a>_to_VL-<b>.md`, append a
row here with its sha256, update the active ledger's `Archived volumes` table, and record
the reconstruction check in the archiving commit. Volumes, once written, are immutable.
