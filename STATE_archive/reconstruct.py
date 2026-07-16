#!/usr/bin/env python3
"""GR-6 reconstruction check for the STATE.md archive.

Proves the archive MOVED content without altering it: the pre-split STATE.md
reassembles byte-for-byte from the archive volumes plus the file's own
pre-split sections, and every archived block is verbatim what was cut.

    python STATE_archive/reconstruct.py

Exit 0 = PASS. Exit 1 = FAIL (the split is rejected; see GR-6 clause 4).

WHAT THIS DOES *NOT* CHECK, BY DESIGN
-------------------------------------
The ACTIVE STATE.md is current state and is REWRITTEN every session close
(SESSION_PROTOCOL close step 2: update "Last updated", "Current verified
state", "Next open action"; the displaced entry becomes a new "PREVIOUS:"
block). So this check must never assert that the active file's sections are
byte-frozen, nor that it carries no PREVIOUS: chain -- a fresh chain is
expected to accumulate until GR-6 clause 2 archives it into the next volume.
An earlier version of this script asserted both and would have failed
spuriously at the next close.

The archive's integrity does not depend on the active file holding still.
Both sides of the real invariant are immutable: a closed volume (GR-6 clause 3)
and the pre-split commit, which git retains forever. That is what is checked.

Hashes are over the GIT BLOB (LF), never the working-tree file: this repo
declares `*.md text eol=lf` while core.autocrlf gives a CRLF working tree on
Windows, so a working-tree hash would not reproduce on a Linux checkout.
"""
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# Recorded at the split. The pre-split file stays reachable in git history --
# that is why archiving costs nothing in integrity.
PRE_SPLIT_COMMIT = "61ad782843f0dfdfa19f94a7b2445278e42067e3"
PRE_SPLIT_SHA256 = "289fe5b2534da557bc0c7ee444d1cb2bf8ad7a2535f1afc77b12a233f9098252"

MARK_BEGIN = b"<!-- entry-region-begin -->\n"
MARK_END = b"<!-- entry-region-end -->\n"

failures = []


def check(label, ok, detail=""):
    print(f"  [{'OK  ' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(label)


def blob(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"ABORT: cannot read {ref}:{path} - {r.stderr.decode().strip()}")
    return r.stdout


def line_offsets(data):
    lines = data.split(b"\n")
    offs, cur = [], 0
    for ln in lines:
        offs.append(cur)
        cur += len(ln) + 1
    return lines, offs


print("GR-6 reconstruction check\n")

pre = blob(PRE_SPLIT_COMMIT, "STATE.md")
check("pre-split blob sha256 matches the recorded anchor",
      hashlib.sha256(pre).hexdigest() == PRE_SPLIT_SHA256,
      hashlib.sha256(pre).hexdigest())

pl, offs = line_offsets(pre)
pidx = [i for i, l in enumerate(pl) if l.startswith(b"PREVIOUS:")]
pre_history = pre[offs[pidx[0]]:offs[pidx[-1] + 1]]
head_block = pre[:offs[pidx[0]]]
first_head = min(offs[i] for i, l in enumerate(pl) if l.startswith(b"## "))
gap = pre[offs[pidx[-1] + 1]:first_head]
pre_sections = pre[first_head:]

# --- volumes ---
vols = sorted(REPO.glob("STATE_archive/vol_*.md"))
check("at least one archive volume present", bool(vols))

archived = b""
for v in vols:
    data = v.read_bytes()
    if MARK_BEGIN not in data or MARK_END not in data:
        check(f"{v.name} has an entry region", False)
        continue
    archived += data[data.index(MARK_BEGIN) + len(MARK_BEGIN):data.index(MARK_END)]

    sidecar = v.with_suffix(v.suffix + ".sha256")
    if sidecar.exists():
        check(f"{v.name} matches its .sha256 sidecar (immutability, clause 3)",
              sidecar.read_text().split()[0] == hashlib.sha256(data).hexdigest())
    else:
        check(f"{v.name} has a .sha256 sidecar", False)

# --- THE invariant (GR-6 clause 4): the archive is byte-faithful to the cut ---
check("volumes' entry regions == the pre-split history region, byte-for-byte",
      archived == pre_history,
      f"{len(archived)} vs {len(pre_history)} bytes")

# Count BLOCKS (lines that start a block), not substring occurrences -- at least
# one archived block discusses "PREVIOUS:" in its own prose.
archived_prev = [l for l in archived.split(b"\n") if l.startswith(b"PREVIOUS:")]
check(f"all {len(pidx)} PREVIOUS blocks preserved in the archive",
      len(archived_prev) == len(pidx),
      f"{len(archived_prev)} vs {len(pidx)}")

# --- the cut was lossless: the pre-split file reassembles byte-for-byte ---
recon = head_block + archived + gap + pre_sections
check("pre-split STATE.md reassembles byte-for-byte from the archive",
      hashlib.sha256(recon).hexdigest() == PRE_SPLIT_SHA256,
      hashlib.sha256(recon).hexdigest())

# --- no duplication: archived blocks must not ALSO still sit in the active file ---
active = (REPO / "STATE.md").read_bytes().replace(b"\r\n", b"\n")
al, _ = line_offsets(active)
active_prev = [l for l in al if l.startswith(b"PREVIOUS:")]
dupes = [l for l in active_prev if l in archived_prev]
check("no archived block is duplicated in the active file", not dupes,
      f"{len(dupes)} duplicated")

# A fresh post-split chain is EXPECTED (GR-6 clause 2 archives it at ~25 blocks).
print(f"\n  note: active file carries {len(active_prev)} post-split PREVIOUS block(s); "
      f"GR-6 clause 2 archives the chain at roughly 25.")

# --- headings are load-bearing anchors (scripts/update_state_vl011.sh) ---
pre_heads = [l.decode() for l in pl if l.startswith(b"## ")]
for h in pre_heads:
    check(f"heading still present verbatim: {h}", (h.encode() + b"\n") in active)

print()
if failures:
    print(f"FAIL: {len(failures)} check(s) failed. The split is rejected (GR-6 clause 4).")
    sys.exit(1)
print("PASS: the archive is byte-preserving and provably complete.")
sys.exit(0)
