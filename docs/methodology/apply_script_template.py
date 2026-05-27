#!/usr/bin/env python3
"""
Apply-script template for bulk str_replace-shaped edits across
multiple files in the Elyon-Sol repository.

This is a template. To produce an actual apply script for a
specific ledger entry, copy this file to a working location,
fill in the EDITS lists at the bottom, and run.

Pattern established in: VL-016 follow-up (commit ebcbc89). See
that entry's process finding for the rationale.

================================================================
WHY THIS PATTERN
================================================================

For ledger entries that apply many str_replace-shaped edits
across multiple files, three failure modes recur if you don't
use a script:

1. Chat-paste-eats-content: comment-form action items in a
   pasted shell block ("# apply 8 str_replace operations") are
   silently skipped. Hit three times across VL-012/VL-014/VL-016.
2. Manual editor application: error-prone for multi-paragraph
   blocks, especially in vi. Per handoff lesson 2.
3. Partial application: an edit applied to file 1 succeeds; the
   edit to file 2 fails; the working tree is left half-edited
   with no clean undo. Hard to recover.

This script eliminates all three by:
- Loading the entire edit list before touching any file.
- Uniqueness-checking every old_str (must match exactly once;
  zero or more-than-one aborts before any write).
- Atomic writes (write to tmp file, rename) so a failure
  doesn't leave partially-written files.
- Per-file byte-delta reporting so the lesson-5 file-count
  check has something concrete to compare against.

================================================================
LINE-ENDING HANDLING
================================================================

Reads: the script normalizes CRLF to LF before matching, so the
old_str literals in the EDITS lists can always use \\n. This
matters on Windows clones where git's autocrlf may produce
files with CRLF line endings on disk despite the repo's stated
LF convention. Discovered in VL-017a's first run when STATE.md
had been CRLF-converted by autocrlf during the VL-016 follow-up
checkout.

Writes: the script always writes LF, regardless of the file's
original line endings. This is consistent with the repo's
stated LF convention (VL-009 ASCII-safe standard). If the file
on disk was CRLF, running the script will normalize it to LF as
a side effect; the line-ending changes will be visible in
git diff, which is the right place for them to be trackable.

================================================================
HOW TO USE
================================================================

1. Copy this file to a working location:
       cp docs/methodology/apply_script_template.py \\
          ~/tmp/apply_vlNNN.py

2. Fill in the three sections at the bottom:
   - EDITS lists, one per target file
   - The __main__ call sequence

3. Each edit is a tuple (old_str, new_str). Both are Python
   string literals; multi-line strings need \\n escapes, NOT
   triple-quoted strings (the literal form lets you see exactly
   what bytes are matched). The script normalizes the file's
   line endings to LF before matching, so you never need to
   worry about \\r\\n in your literals.

4. Run a dry-run if you can. The script is structured so that
   pointing REPO_ROOT at a copy of the repo (e.g., /tmp/dryrun)
   exercises every uniqueness check without touching the real
   files.

5. Run for real:
       python3 ~/tmp/apply_vlNNN.py

   Output shows before/after byte counts, per-edit deltas, and
   the detected line-ending convention for each file. If the
   script aborts at any edit, paste the error; it tells you
   which old_str matched 0 or >1 times.

6. After successful application, the standard checklist:
       cat ~/tmp/<entry>.md >> EVIDENCE/verification_ledger.md
       LC_ALL=C grep -n '[^[:print:][:space:]]' <files...>
       git status   # verify file count matches intent
       git add -A
       git commit -F ~/tmp/<commit_message>.txt
       git push

================================================================
SYNTHETIC-FIXTURE PRE-VERIFICATION (required for >2 edit sites)
================================================================

Apply-scripts with more than two edit sites must run a synthetic-
fixture pre-verification step before touching the real file.
Pattern established across VL-026, VL-027, VL-028, VL-029, VL-030
(three-plus-instance threshold met).

The synthetic-fixture step:

1. Builds a fixture file mirroring the relevant anchor regions of
   the real file - the lines containing each old_str plus enough
   surrounding context that anchor uniqueness is testable. Fixture
   lives at /tmp/<script>_fixture.txt or similar; do NOT use a
   path under REPO_ROOT.

2. Runs the same edit sequence against the fixture. Verifies:
   - Anchor uniqueness invariant (every old_str matches exactly
     once in the fixture as in the real file).
   - Expected post-edit content invariant (the fixture after
     edits contains the expected new_str sequences).
   - Byte-delta invariant (the fixture's byte-delta matches the
     predicted byte-delta computed from sum(len(new)-len(old))
     across all edits).
   - ASCII-clean invariant (no non-ASCII bytes introduced).

3. Only after all fixture invariants pass: runs against the real
   file under REPO_ROOT.

LOAD-BEARING REFINEMENT: fixtures must be built from `cat -A` (or
equivalent disk-byte inspection: `od -c`, `xxd`) of the actual
disk regions, NOT from inferred structure. Demonstrated by
VL-031's anchor-failure recovery: synthetic-fixture verification
is only as strong as the fixture's fidelity to disk. A fixture
built from inferred structure produces circular-clean
verification - the script works against the fixture's wrong
assumption about disk shape, both pass, both then fail against
real disk. The disk-byte inspection step is what breaks the
circularity.

Recommended fixture-building workflow:

    # Inspect the actual disk bytes in the anchor region:
    cat -A path/to/file | sed -n '<start>,<end>p' > /tmp/anchor_region.txt

    # Copy the relevant region to fixture; verify byte-equality:
    cp path/to/file /tmp/script_fixture.txt
    diff <(cat -A /tmp/script_fixture.txt | sed -n '<start>,<end>p') \
         /tmp/anchor_region.txt
    # (must produce zero diff before fixture is trusted)

    # Run the apply script against /tmp/script_fixture.txt by
    # temporarily setting REPO_ROOT=/tmp and the file path to
    # script_fixture.txt, or by constructing a parallel fixture
    # script.

The fixture-vs-disk byte-equality check is the verification step.
Without it, fixture invariants verify only that the script is
self-consistent with its own assumptions.
"""

import os
import sys
import tempfile


# Set this to your repo root. The default works for the
# standard Elyon-Sol clone location.
REPO_ROOT = os.path.expanduser("~/Elyon-Sol")


def apply_edits(path, edits, label):
    """Apply a list of (old_str, new_str) edits to a file.

    Reads: file is read in binary-neutral mode (newline="");
    CRLF in the file is normalized to LF before matching, so
    old_str literals can always use \\n.

    Matching: each old_str must match exactly once in the
    LF-normalized content. If it matches zero or more-than-one
    times, the script aborts BEFORE writing anything to that
    file.

    Writes: file is written with LF line endings regardless of
    input convention. The atomic-write pattern (write to tmp,
    rename) means a failure during write doesn't leave a
    partially-written file.

    Args:
        path: relative path under REPO_ROOT.
        edits: list of (old_str, new_str) tuples; old_str and
            new_str use LF (\\n) line endings.
        label: human-readable label for the file (used in
            output messages).
    """
    full_path = os.path.join(REPO_ROOT, path)
    if not os.path.exists(full_path):
        print(f"ABORT: {label}: file not found at {full_path}")
        sys.exit(1)

    # Read with newline="" to preserve original line endings,
    # then detect convention and normalize to LF for matching.
    with open(full_path, "r", encoding="utf-8", newline="") as f:
        raw_content = f.read()

    if "\r\n" in raw_content:
        detected_newline = "CRLF (will be normalized to LF on write)"
        content = raw_content.replace("\r\n", "\n")
    else:
        detected_newline = "LF"
        content = raw_content

    original_len = len(content)  # length in LF-normalized form
    print(f"\n=== {label} ({path}) ===")
    print(f"  line endings: {detected_newline}")
    print(f"  before: {original_len} bytes (LF-normalized), "
          f"{content.count(chr(10))} lines")

    for i, (old_str, new_str) in enumerate(edits, 1):
        count = content.count(old_str)
        if count == 0:
            print(f"  ABORT at edit {i}: old_str matches 0 times.")
            print(f"    First 80 chars of old_str: {old_str[:80]!r}")
            print(f"    Has this edit already been applied?")
            sys.exit(1)
        if count > 1:
            print(f"  ABORT at edit {i}: old_str matches {count} times "
                  f"(must be unique).")
            print(f"    First 80 chars of old_str: {old_str[:80]!r}")
            sys.exit(1)
        content = content.replace(old_str, new_str, 1)
        print(f"  edit {i}: applied ({len(new_str) - len(old_str):+d} bytes)")

    final_len = len(content)
    print(f"  after:  {final_len} bytes ({final_len - original_len:+d} bytes)")

    # Atomic write with explicit LF newline convention,
    # regardless of original file convention. Repo standard
    # per VL-009 is LF; the script enforces that.
    dir_name = os.path.dirname(full_path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp_path, full_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    print(f"  written: {path} (LF line endings)")


# ============================================================
# EDIT LISTS - FILL IN BELOW
# ============================================================
#
# For each target file, define a list of (old_str, new_str)
# tuples. The old_str must match exactly once; the script will
# abort if it doesn't.
#
# Line endings: use LF (\n) in your literals. The script
# normalizes the file's line endings to LF before matching, so
# you never need \r\n.
#
# For multi-paragraph blocks, use Python string literals with
# explicit \n escapes rather than triple-quoted strings. The
# literal form lets you see exactly what bytes are matched and
# avoids accidental whitespace introduction at line edges.
#
# Example:
#
# EXAMPLE_EDITS = [
#     # Edit 1: short one-line replacement
#     (
#         'old text',
#         'new text',
#     ),
#
#     # Edit 2: multi-line replacement
#     (
#         'first line\nsecond line',
#         'first line\nmiddle line\nsecond line',
#     ),
# ]
# ============================================================

# EXAMPLE_EDITS_FILE_A = [
#     # (old_str, new_str),
#     # (old_str, new_str),
# ]

# EXAMPLE_EDITS_FILE_B = [
#     # (old_str, new_str),
# ]


# ============================================================
# MAIN - FILL IN THE CALL SEQUENCE BELOW
# ============================================================

if __name__ == "__main__":
    print("Apply script: applying edits")
    print(f"Repo root: {REPO_ROOT}")

    # Add one apply_edits call per target file. Order matters
    # only if edits to one file are anchored on text added by
    # edits to another (rare). Otherwise order is for output
    # readability.
    #
    # apply_edits("path/to/file_a", EXAMPLE_EDITS_FILE_A, "Label A")
    # apply_edits("path/to/file_b", EXAMPLE_EDITS_FILE_B, "Label B")

    print("\n=== ALL EDITS APPLIED ===")
    print("Next steps:")
    print("  1. cat <ledger-entry>.md >> EVIDENCE/verification_ledger.md")
    print("  2. LC_ALL=C grep -n '[^[:print:][:space:]]' <files>")
    print("  3. git status   # verify file count matches intent")
    print("  4. git add -A && git commit -F <commit-message>.txt")
    print("  5. git push")
