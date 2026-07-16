# STATE.md archive - manifest

Volumes of STATE.md's `PREVIOUS:` history, archived under GR-6
(`docs/MAINTENANCE_PROTOCOL.md`), which mirrors GR-5's ledger-archive design:
versioned, immutable, byte-preserving. Entries are MOVED, never rewritten.

| Volume | Range | Blocks | sha256 |
|---|---|---|---|
| `vol_001__VL-109_to_VL-145.md` | VL-145 .. VL-109 | 29 | `3f42d85bfd187bb00942704225780d411a604b6e75d87fb31512847c300d3345` |

## Reconstruction check (GR-6 clause 4)

Pre-split STATE.md sha256 (git blob, LF): `289fe5b2534da557bc0c7ee444d1cb2bf8ad7a2535f1afc77b12a233f9098252`

    python STATE_archive/reconstruct.py

Reassembles the pre-split file from this volume's entry region plus the active
STATE.md's sections in their original order, and compares the sha256. A split
whose check fails is rejected and nothing is moved.

Verified at the split commit: **PASS** (byte-for-byte).

## Note on representation

All hashes are over the **git blob (LF)**, not the working-tree file. This repo
declares `*.md text eol=lf` in `.gitattributes` while `core.autocrlf=true` gives
a CRLF working tree on Windows (`git ls-files --eol` -> `i/lf w/crlf`). Hashing
the working tree would not reproduce on a Linux checkout. Recompute with
`git show HEAD:STATE.md | sha256sum`.
