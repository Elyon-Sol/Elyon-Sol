# POE - proof-of-existence snapshot (historical)

`POE_MANIFEST.md` and `POE_SHA256_HASHES.txt` are a snapshot taken on 2026-05-04
(commit `8d0dff5`, labelled "v0.9.8.5 post-enforcement"). They are kept unchanged as a
record of that date. They do **not** describe the current tree:

- The canon in force is v0.9.8.4 (`CANON/canon.lock`); no v0.9.8.5 canon increment was
  ever made. The "v0.9.8.5" label is the release-tag name
  (`v0.9.8.5-post-enforcement`), not a canon version.
- `EVIDENCE/interception_proof_002.md` and `EVIDENCE/stability_proof_001.md` were
  moved to `EVIDENCE/archive/` with a NON-CURRENT header (VL-011), so their current
  bytes differ from the pinned hashes.
- `MANIFEST/manifest.json` and `README.md` have changed since the snapshot. The pinned
  manifest hash is that of the version committed later in `c0867a6`. The pinned
  `README.md` hash matches no committed version, so the snapshot was generated from a
  working tree rather than from a commit.

So `sha256sum -c POE_SHA256_HASHES.txt` does **not** pass today, and that is expected.
`generate_poe_hashes.py` is method on record: it fails closed on the moved inputs and
is not meant to be re-run. The current hash pins of record are `CANON/canon.lock` and
`EVIDENCE/published_hashes.json`.

Honest scope: nothing here is external validation. G5 (a blind external party) is
not met.
