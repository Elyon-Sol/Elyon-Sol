#!/usr/bin/env python3
"""GR-6 reconstruction check for the STATE.md archive.

Proves that the archive split MOVED content without altering it: every byte of
the pre-split STATE.md is either still in the active file (possibly reordered)
or verbatim inside an archive volume. Nothing was rewritten; nothing was lost.

    python STATE_archive/reconstruct.py

Exit 0 = PASS. Exit 1 = FAIL (the split is rejected; see GR-6 clause 4).

Hashes are over the GIT BLOB (LF), never the working-tree file: this repo
declares `*.md text eol=lf` while core.autocrlf gives a CRLF working tree on
Windows, so a working-tree hash would not reproduce on a Linux checkout.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# Recorded at the split. The pre-split file remains reachable in git history --
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


def sections(data):
    """Split a STATE.md byte-blob into {heading: body_bytes}, byte-exact."""
    lines = data.split(b"\n")
    offs, cur = [], 0
    for ln in lines:
        offs.append(cur)
        cur += len(ln) + 1
    heads = [i for i, l in enumerate(lines) if l.startswith(b"## ")]
    out = {}
    for n, h in enumerate(heads):
        end = offs[heads[n + 1]] if n + 1 < len(heads) else len(data)
        out[lines[h].decode("utf-8")] = data[offs[h]:end]
    return out


print("GR-6 reconstruction check\n")

pre = blob(PRE_SPLIT_COMMIT, "STATE.md")
check("pre-split blob sha256 matches the recorded anchor",
      hashlib.sha256(pre).hexdigest() == PRE_SPLIT_SHA256,
      hashlib.sha256(pre).hexdigest())

# --- the archived history region ---
vols = sorted(REPO.glob("STATE_archive/vol_*.md"))
check("at least one archive volume present", bool(vols))

archived = b""
for v in vols:
    data = v.read_bytes()
    if MARK_BEGIN not in data or MARK_END not in data:
        check(f"{v.name} has an entry region", False)
        continue
    region = data[data.index(MARK_BEGIN) + len(MARK_BEGIN):data.index(MARK_END)]
    archived += region

    sidecar = v.with_suffix(v.suffix + ".sha256")
    if sidecar.exists():
        recorded = sidecar.read_text().split()[0]
        check(f"{v.name} matches its .sha256 sidecar",
              recorded == hashlib.sha256(data).hexdigest())
    else:
        check(f"{v.name} has a .sha256 sidecar", False)

# The pre-split history region: first PREVIOUS: line through the last, inclusive.
pl = pre.split(b"\n")
offs, cur = [], 0
for ln in pl:
    offs.append(cur)
    cur += len(ln) + 1
pidx = [i for i, l in enumerate(pl) if l.startswith(b"PREVIOUS:")]
pre_history = pre[offs[pidx[0]]:offs[pidx[-1] + 1]]

# GR-6 clause 4: volumes + the active file's history region == the historical region.
active = (REPO / "STATE.md").read_bytes().replace(b"\r\n", b"\n")
active_history = b"".join(
    l + b"\n" for l in active.split(b"\n") if l.startswith(b"PREVIOUS:"))

check("volumes + active history region == pre-split history region, byte-for-byte",
      archived + active_history == pre_history,
      f"{len(archived) + len(active_history)} vs {len(pre_history)} bytes")

check(f"all {len(pidx)} PREVIOUS blocks accounted for",
      archived.count(b"\nPREVIOUS:") + archived.startswith(b"PREVIOUS:") + len(
          [l for l in active.split(b"\n") if l.startswith(b"PREVIOUS:")]) == len(pidx))

# --- the sections: reordered is allowed, altered is not ---
pre_secs, act_secs = sections(pre), sections(active)

check("no section lost", set(pre_secs) <= set(act_secs),
      f"missing: {sorted(set(pre_secs) - set(act_secs))}")

for h, body in pre_secs.items():
    if h in act_secs:
        check(f"section body byte-identical: {h}", act_secs[h] == body,
              f"{len(act_secs[h])} vs {len(body)} bytes")

# --- headings are load-bearing anchors (scripts/update_state_vl011.sh) ---
for h in pre_secs:
    check(f"heading verbatim: {h}", (h.encode() + b"\n") in active)

# --- the active file must carry no un-archived history ---
check("active STATE.md carries no PREVIOUS: chain", not active_history)

# --- full byte reconstruction of the pre-split file ---
# Built from the ARCHIVE's history region + the ACTIVE file's section bodies,
# restored to the pre-split section order. Only the head block and the
# inter-region gap (scaffolding, never archived) come from the pre-split file.
# Reassembling from `pre`'s own sections would be circular and could not fail.
head_block = pre[:offs[pidx[0]]]
first_head_off = min(offs[i] for i, l in enumerate(pl) if l.startswith(b"## "))
gap = pre[offs[pidx[-1] + 1]:first_head_off]
recon = head_block + archived + active_history + gap + b"".join(
    act_secs[h] for h in pre_secs if h in act_secs)
check("full pre-split file reconstructs from archive + active, byte-for-byte",
      hashlib.sha256(recon).hexdigest() == PRE_SPLIT_SHA256,
      hashlib.sha256(recon).hexdigest())

print()
if failures:
    print(f"FAIL: {len(failures)} check(s) failed. The split is rejected (GR-6 clause 4).")
    sys.exit(1)
print("PASS: the archive is byte-preserving and provably complete.")
sys.exit(0)
