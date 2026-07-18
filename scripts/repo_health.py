#!/usr/bin/env python3
"""Repo continuity health-check — automates the close-protocol bookkeeping that
has historically been skipped by hand and drifted (the STATE-index / ledger-index
lag recorded at VL-147/149). Run at session close, or in CI.

    python scripts/repo_health.py

Exit 0 = all green; exit 1 = at least one check failed. Read-only: changes nothing.

Rationale: the recurring failure mode is "a protocol step too expensive to run by
hand silently stops being run." This turns those steps into one command:
  1. GR-6 STATE-archive reconstruction (byte-preserving proof).
  2. Ledger-index currency — every active-ledger VL entry has an index line.
  3. STATE.md ordering — Next open action leads (GR-6 clause 1).
  4. Ledger heading-format census (informational; GR-5 Amendment A1 tolerates both).
"""
import re
import subprocess
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
fails = []


def check(label, ok, detail=""):
    print(f"  [{'OK  ' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


# 1. GR-6 STATE-archive reconstruction
print("1. GR-6 STATE-archive reconstruction")
r = subprocess.run([sys.executable, "STATE_archive/reconstruct.py"], cwd=REPO, capture_output=True)
tail = r.stdout.decode("utf-8", "replace").strip().splitlines()[-1:] if r.stdout else [""]
check("STATE_archive/reconstruct.py passes", r.returncode == 0, tail[0] if tail else "")

# 2. Ledger-index currency
print("2. Ledger-index currency (every active-ledger VL entry has an index line)")
ledger = (REPO / "EVIDENCE/verification_ledger.md").read_text(encoding="utf-8")
index = (REPO / "EVIDENCE/verification_ledger_index.md").read_text(encoding="utf-8")
entry_nums = sorted(set(int(n) for n in re.findall(r"^#{2,3} VL-(\d+)\b", ledger, re.M)))
index_nums = set(int(n) for n in re.findall(r"^- VL-(\d+)\b", index, re.M))
missing = [n for n in entry_nums if n not in index_nums]
check(f"all {len(entry_nums)} active-ledger VL entries are indexed", not missing,
      f"missing from index: {missing}")

# 3. STATE.md ordering (GR-6 clause 1)
print("3. STATE.md ordering (GR-6: Next open action leads)")
state = (REPO / "STATE.md").read_text(encoding="utf-8")
noa, cvs = state.find("## Next open action"), state.find("## Current verified state")
check("'## Next open action' precedes '## Current verified state'",
      noa != -1 and (cvs == -1 or noa < cvs), f"noa@{noa} cvs@{cvs}")

# 4. Ledger heading-format census (informational)
h2 = len(re.findall(r"^## VL-\d+", ledger, re.M))
h3 = len(re.findall(r"^### VL-\d+", ledger, re.M))
print(f"4. Ledger heading formats (GR-5 Amendment A1 accepts both): '## VL-N'={h2}, '### VL-N'={h3}")

print()
if fails:
    print(f"FAIL: {len(fails)} check(s) failed.")
    sys.exit(1)
print("PASS: repo continuity checks green.")
sys.exit(0)
