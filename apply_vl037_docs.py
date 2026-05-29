#!/usr/bin/env python3
"""
VL-037 apply-script: structural-doc edits for the target-side verifier
commit. Per docs/methodology/apply_script_template.py.

Touches three files (the verifier.py + test files are added directly;
the ledger entry is appended separately - see the run order below):

  - docs/restructure/04_current_vs_claimed.md : G4 row gains a VL-037
    build bullet (G4 stays OPEN; verifier has no caller).
  - docs/restructure/06_spec_to_code_traceability.md : section-13 row
    gains a target-side-verifier note (no status change).
  - STATE.md : Last-updated line rewritten; VL-037 current-verified-state
    bullet added; Next-open-action item 31 added (3 edit sites ->
    synthetic-fixture pre-verification applies, exercised in the sandbox
    before this script was handed over).

Discipline: uniqueness-check every anchor (abort before any write on 0
or >1 matches); CRLF normalized to LF on read; always write LF; atomic
write (tmp + rename); per-edit byte delta; Stage-1 ASCII pre-write check
(Python byte scan, NOT grep -P, per VL-036 Finding 5).

RUN ORDER (the rest of the close):
  1. python3 apply_vl037_docs.py        # this script (3 doc files)
  2. cat vl037_ledger_entry.md >> EVIDENCE/verification_ledger.md
  3. python -m pytest TESTS/ --tb=no -q # expect 119 passed + 0 xfailed
  4. python -c "import IMPLEMENTATION.verifier"
  5. git add -A && git commit -F vl037_commit_msg.txt && git push
"""

import os
import sys
import tempfile

REPO_ROOT = os.path.expanduser("~/Elyon-Sol")


def _read_lf(full_path):
    with open(full_path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    if "\r\n" in raw:
        return raw.replace("\r\n", "\n"), "CRLF (normalized to LF on write)"
    return raw, "LF"


def _ascii_guard(content, label):
    bad = [(i, b) for i, b in enumerate(content.encode("utf-8")) if b > 0x7F]
    if bad:
        i, b = bad[0]
        print(f"  ABORT: {label}: non-ASCII byte 0x{b:02x} at offset {i} "
              f"({len(bad)} total). Fix before writing (VL-009).")
        sys.exit(2)


def _atomic_write_lf(full_path, content):
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


def apply_to_file(path, literal_edits, line_prefix_edits, label):
    """
    Apply edits to one file.

    literal_edits: list of (old_str, new_str); each old_str must match
        exactly once.
    line_prefix_edits: list of (prefix, new_line); exactly one line must
        start with prefix; the whole line is replaced with new_line.
    """
    full_path = os.path.join(REPO_ROOT, path)
    if not os.path.exists(full_path):
        print(f"ABORT: {label}: file not found at {full_path}")
        sys.exit(1)

    content, detected = _read_lf(full_path)
    before = len(content)
    print(f"\n=== {label} ({path}) ===")
    print(f"  line endings: {detected}")
    print(f"  before: {before} bytes, {content.count(chr(10))} lines")

    # Line-prefix replacements first (they target whole lines).
    for j, (prefix, new_line) in enumerate(line_prefix_edits, 1):
        lines = content.split("\n")
        idx = [k for k, ln in enumerate(lines) if ln.startswith(prefix)]
        if len(idx) != 1:
            print(f"  ABORT at line-prefix edit {j}: prefix matched "
                  f"{len(idx)} lines (must be exactly 1).")
            print(f"    prefix: {prefix[:80]!r}")
            sys.exit(1)
        old_line = lines[idx[0]]
        lines[idx[0]] = new_line
        content = "\n".join(lines)
        print(f"  line-prefix edit {j}: applied "
              f"({len(new_line) - len(old_line):+d} bytes)")

    # Literal str-replace edits.
    for i, (old_str, new_str) in enumerate(literal_edits, 1):
        count = content.count(old_str)
        if count != 1:
            print(f"  ABORT at literal edit {i}: old_str matched {count} "
                  f"times (must be 1).")
            print(f"    first 80 chars: {old_str[:80]!r}")
            sys.exit(1)
        content = content.replace(old_str, new_str, 1)
        print(f"  literal edit {i}: applied "
              f"({len(new_str) - len(old_str):+d} bytes)")

    _ascii_guard(content, label)
    after = len(content)
    print(f"  after:  {after} bytes ({after - before:+d} bytes)")
    _atomic_write_lf(full_path, content)
    print(f"  written: {path} (LF)")


# ===========================================================================
# EDIT CONTENT
# ===========================================================================

# --- artifact 04: G4 row VL-037 build bullet (inserted before ### G5) ---
ART04_LITERAL = [
    (
        'closeable only by target-side policy, not by the gate.\n\n### G5  -  "External" verification is not durable',
        'closeable only by target-side policy, not by the gate.\n'
        '- **VL-037 (build, increment 1):** `IMPLEMENTATION/verifier.py` '
        '`verify_envelope()` landed. It is a delivery-agnostic target-side '
        'verifier reusing `reassert()` (currency plus integrity; closes forgery '
        'A2) plus a symmetric `request_context`/`target_url` binding check '
        '(closes same-state replay A3 per artifact 08 section 7). Canon-derived '
        'tests at `TESTS/adversarial/test_verifier.py`; honest A1-bypass '
        'demonstration at `TESTS/adversarial/test_bypass.py` (the Action item, '
        'done). Delivery wiring pending VL-038. **G4 enforcement status '
        'unchanged**: the verifier has no caller yet, so the opt-in delta above '
        'still holds, and G4 does NOT transition to RESOLVED. G5 remains the '
        'named deployment precondition; A1 remains closeable only by a '
        'target-side policy, not by the gate.\n'
        '\n### G5  -  "External" verification is not durable',
    ),
]

# --- artifact 06: section-13 row target-side-verifier note (no status change) ---
ART06_LITERAL = [
    (
        'honored without re-evaluation. |',
        'honored without re-evaluation. Target-side reuse: '
        '`IMPLEMENTATION/verifier.py::verify_envelope()` (VL-037) consumes '
        '`reassert()` as the revalidation step for a target verifying a '
        'delivered envelope, and adds a `request_context`/`target_url` binding '
        'check operationalizing section 13 per-interaction coverage plus the '
        'section 11.1 interaction identity; it implements no new canon section '
        '(a note here, not a new row) and is exercised by '
        '`TESTS/adversarial/test_verifier.py` (VL-037). Delivery wiring (a '
        'caller for the verifier) is VL-038 (G4). |',
    ),
]

# --- STATE.md: last-updated (line-prefix), current-verified-state bullet,
#     Next-open-action item 31 (two literal inserts) ---
STATE_NEW_LASTUPDATED = (
    'Last updated: 2026-05-29 (commit: see `git log` for STATE.md; VL-037 '
    'T-G4-build: `IMPLEMENTATION/verifier.py` target-side verifier landed '
    '(`verify_envelope()` reuses `reassert()` plus a symmetric '
    '`request_context`/`target_url` binding check; closes forgery A2 and '
    'same-state replay A3 for routed traffic per artifact 08 sections 4.2/7); '
    'canon-derived tests `TESTS/adversarial/test_verifier.py` (11) plus honest '
    'A1-bypass `TESTS/adversarial/test_bypass.py` (2); first G4 build increment '
    'per artifact 08 section 8 step 1; build-then-wire (verifier now, delivery '
    'VL-038); Decision A scope held (no pep.py/canon/manifest/spec change); G5 '
    'named as deployment precondition, A1 named as gate-unreachable floor; G4 '
    'enforcement status unchanged (verifier has no caller yet), G4 NOT '
    'resolved; Checkpoint-C finding: asymmetric AP/OP normalization caught by '
    'the sandbox smoke, fixed to symmetric canon-11.5/11.6 set comparison; '
    'context-equality canonical_json choice flagged [INFERENCE] per artifact '
    '08 gap candidate 1; pytest 106 -> 119 passed + 0 xfailed; prior ledger '
    'entry VL-036 at commit `e138cbf`; parent commit `e138cbf`; next '
    'trajectory action: VL-038 G4-delivery)'
)

STATE_LINE_PREFIX = [
    ("Last updated:", STATE_NEW_LASTUPDATED),
]

STATE_LITERAL = [
    # current-verified-state VL-037 bullet (one physical line) after the
    # VL-036 bullet, before "## What is locked vs. open".
    (
        'unchanged from HEAD `cdeeb25`.\n\n## What is locked vs. open',
        'unchanged from HEAD `cdeeb25`.\n'
        '- **VL-037 T-G4-build: target-side envelope verifier landed; first G4 '
        'build increment; G4 enforcement status unchanged (this commit).** '
        '`IMPLEMENTATION/verifier.py` lands per '
        '`docs/restructure/08_enforcement_design.md` section 8 step 1: '
        '`verify_envelope(envelope, interaction, target_url)` returns '
        '`{"accepted", "reason"}` after a structural presence guard, then '
        '`envelope.reassert()` for currency plus integrity (any outcome other '
        'than REASSERTED rejects, closing forgery A2 and detecting '
        'canon/evaluator/manifest transitions), then a symmetric '
        '`request_context`-vs-live-interaction binding check (AP/OP as canon '
        'section 11.5/11.6 sets normalized on both sides, `context` by '
        '`canonical_json` equality, manifest-pinning and `target_url` by string '
        'equality; closes same-state replay A3, which `reassert()` alone does '
        'not per artifact 08 sections 4.2/7). Closed REF_VERIFY_ reject set '
        '(parallel to REF_SCHEMA_): REF_VERIFY_ENVELOPE_ABSENT, '
        'REF_VERIFY_REASSERT_INVALIDATED, '
        'REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED, REF_VERIFY_BINDING_MISMATCH; '
        'accept reason REASSERTED_AND_BOUND. Canon basis: section 13 '
        'revalidation (the verifier is the target-side revalidation step) plus '
        'section 11.1 interaction identity; no new invariant (artifact 08 '
        'section 5); non-executing (canon section 14 holds). '
        '`TESTS/adversarial/test_verifier.py` adds 11 canon-derived tests '
        '(accept; the four reassert() rows; absent; malformed; '
        'replay-binding-mismatch A3; target_url-mismatch; AP/OP normalization '
        'parity; context binding) and `TESTS/adversarial/test_bypass.py` adds 2 '
        'honest A1-bypass tests (direct-to-target reaches the target with no '
        'envelope; a target running the verifier would reject the un-attested '
        'call) per Decision E. Build-then-wire per VL-025 to VL-029: the '
        'verifier has NO caller; `pep.py` is untouched (Decision A) and '
        'delivery (push vs caller-carry vs target-pull) is VL-038. G5 named as '
        'the deployment precondition in the module docstring, NOT built '
        '(Decision F; artifact 08 section 6); A1 named as closeable only by a '
        'target-side policy, not by the gate (artifact 08 section 4.4); the '
        'verifier is necessary-but-not-sufficient. Checkpoint-C finding: the '
        'sandbox smoke caught an asymmetric AP/OP normalization in the first '
        'draft (live side normalized, envelope side raw, so a valid envelope '
        'false-rejected), fixed to symmetric set normalization per canon '
        '11.5/11.6 and Decision C; an implementation bug, not a spec gap, so no '
        'Checkpoint B halt. The `context` canonical_json equality is flagged '
        '[INFERENCE] (artifact 08 gap candidate 1). '
        '`docs/restructure/04_current_vs_claimed.md` G4 row gains a '
        'verifier-built-VL-037/delivery-pending-VL-038 bullet; '
        '`docs/restructure/06_spec_to_code_traceability.md` section-13 row '
        'gains a target-side-verifier note (the verifier consumes `reassert()`, '
        'implements no new canon section, so a note, not a new row). G4 does '
        'NOT transition to RESOLVED (the verifier has no caller; enforcement is '
        'unchanged). Classification: trajectory move per VL-017a distinction (a '
        'new `IMPLEMENTATION/` module plus two new `TESTS/` files; '
        'structural-doc updates only). Pytest 106 -> 119 passed + 0 xfailed '
        '(real environment).\n'
        '\n## What is locked vs. open',
    ),
    # Next-open-action item 31 (one physical line) after item 30, before the
    # trailing "4 (SPEC/request_schema.md ...)" block.
    (
        'G5 is the named G4 dependency and may merge with or precede the G4 build.\n'
        '4 (SPEC/request_schema.md drafted + verified + corrected)',
        'G5 is the named G4 dependency and may merge with or precede the G4 build.\n'
        '31. **T-G4-build: target-side envelope verifier built; delivery wiring '
        'deferred to VL-038.** Done (VL-037, this commit). '
        '`IMPLEMENTATION/verifier.py` `verify_envelope()` reuses `reassert()` '
        '(canon section 13 revalidation) and adds a symmetric '
        '`request_context`/`target_url` binding check (canon section 11.1; '
        'closes replay A3 per artifact 08 section 7). Canon-derived tests at '
        '`TESTS/adversarial/test_verifier.py` (11) plus honest A1-bypass at '
        '`TESTS/adversarial/test_bypass.py` (2) per Decision E. First G4 build '
        'increment per artifact 08 section 8 step 1; build-then-wire per VL-025 '
        'to VL-029. No pep.py/canon/manifest/spec change (Decision A). G5 named '
        'as the deployment precondition, A1 named as the gate-unreachable floor '
        '(artifact 08 sections 6/4.4). G4 NOT resolved (verifier has no caller; '
        'enforcement unchanged). Pytest 106 -> 119 passed + 0 xfailed. Next: '
        'VL-038 G4-delivery (decide push vs caller-carry vs target-pull per '
        'artifact 08 sections 4.3/9, wire into `pep.py`, migrate '
        '`TESTS/test_pep.py` to the delivered wire shape, connect the verifier '
        'as the target-side check); G5 (durable verification) is the named '
        'cross-host precondition and may merge with or precede VL-038; '
        'T-bookkeeping (G1/G8/G9/G11/G14) and T-prose-drift remain open with no '
        'priority blocker.\n'
        '4 (SPEC/request_schema.md drafted + verified + corrected)',
    ),
]


if __name__ == "__main__":
    print("VL-037 doc apply-script")
    print(f"Repo root: {REPO_ROOT}")
    apply_to_file("docs/restructure/04_current_vs_claimed.md",
                  ART04_LITERAL, [], "artifact 04 (G4 row)")
    apply_to_file("docs/restructure/06_spec_to_code_traceability.md",
                  ART06_LITERAL, [], "artifact 06 (section-13 note)")
    apply_to_file("STATE.md", STATE_LITERAL, STATE_LINE_PREFIX, "STATE.md")
    print("\n=== ALL DOC EDITS APPLIED ===")
    print("Next: cat vl037_ledger_entry.md >> EVIDENCE/verification_ledger.md")
    print("Then: pytest, import check, git add -A, commit -F, push.")
