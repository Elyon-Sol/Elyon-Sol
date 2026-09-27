# Elyon-Sol - session contract

Loaded automatically at the start of every session. It exists because
`STATE.md` is ~106k tokens and cannot be read in full inside a working
context; this file is the reachable half of the entry point. It carries
no claims of its own - every rule below cites its source, and the source
wins on any disagreement.

---

## Read order at resume (bounded)

Do NOT read `STATE.md` in full. Read, in order:

1. `git log --oneline -10`
2. `git status` - the at-rest invariant is: clean, `HEAD == origin/main`.
   If it is not, the previous session's close protocol failed and fixing
   that is this session's first task (`docs/SESSION_PROTOCOL.md`).
3. `STATE.md` section `## Next open action` - the FIRST item is the task.
4. `STATE.md` section `## Known open gaps`.
5. `EVIDENCE/verification_ledger.md` - the last 2-3 entries only
   (`grep -nE '^#{2,3} VL-' EVIDENCE/verification_ledger.md | tail -3`, then
   `sed -n` the ranges; never `cat` the whole ledger).
6. `python scripts/repo_health.py` - the continuity checks (STATE-archive
   reconstruction, ledger-index currency, STATE ordering). Exit 0 = green.

Read anything further on demand, by grep, for a specific question.
Full protocol: `docs/SESSION_PROTOCOL.md`. Governance: `docs/MAINTENANCE_PROTOCOL.md`.

## State the goal in one sentence before starting

It must map to an item in `## Next open action`. If it does not, either
STATE.md is stale or the goal is scope creep - resolve which, and say so,
before doing the work (`docs/SESSION_PROTOCOL.md` resume step 5).

## STATE.md is model-authored prose, not a primary source

GR-2: "prose drifts." This has already produced a recorded falsehood -
VL-125 asserted `site/index.html` carried the honest-scope note; VL-129
found it did not. Before building on any STATE.md claim, verify it against
the primary source: code, a test execution, canon, or the live surface.
Per VL-008, prior model output is not a source. `EVIDENCE/readiness.json`
is the single source of readiness truth; STATE.md only references it.

---

## Invariants - violating one of these is a stop-work event

- **GR-1** - canon is corrected only by version increment, never in-place.
  Do not edit `CANON/canon.md`, `canon.lock`, or the locked PDF.
- **GR-2** - no readiness fact is human-attested. Every true flag in
  `EVIDENCE/readiness.json` names a passing proof test. Claimed-but-unwired
  is forbidden; built-but-unwired is allowed (build-then-wire is the method).
- **GR-3** - no model evaluative judgment ("sound", "convergent", "N-0") is
  evidence. White-box review is internal hardening, NOT external validation.
- **GR-4** - a `VL-N` entry requires a verification event against a primary
  source. Authoring, refactors, packaging, bookkeeping -> commit + STATE
  only, never the ledger. The ledger is append-only and never renumbered.
- **GR-5** - ledger archiving is versioned, immutable, byte-preserving.
- **GR-6** - the same, for STATE.md history. See `docs/MAINTENANCE_PROTOCOL.md`.
- **G5 is NOT-MET** and is the finish line: a blind external attacker against
  a deployed surface. There has been no live surface since the public nodes
  were retired on 2026-07-20 (the project is paused, not ended), so G5 cannot
  advance until one exists again. Never write a claim that implies otherwise.
  Every artifact carries the honest-scope line.

## Hash-pinned files are generated, never hand-edited

`CANON/canon.lock`, `EVIDENCE/published_hashes.json`, and the
`evaluator_sha256` / `manifest_sha256` / `canon_sha256` pins are produced by
their generators (`EVIDENCE/published_hashes_gen.py` and siblings). Editing
`IMPLEMENTATION/evaluator.py` moves `evaluator_sha256` and REDs the
verify-against-pinned tests until the record is regenerated via its
generator - that is the VL-115 discipline, not a test failure to route around.

## Secrets

`*_SIGNING_KEY_HEX` and `*_PRIVATE*` values are never printed, echoed, or
pasted. Rotation is the only remedy once exposed, and this has already cost
the project twice - VL-108 and VL-146. Deploy `.env` files live only on the
hosts and are gitignored.

## Commits

- Do not commit mid-session unprompted. Commits land at close, per
  `docs/SESSION_PROTOCOL.md`, with the STATE.md update as its own commit.
- Never open a `VL-N` number for non-verification work (GR-4 clause 1).
- `git log --oneline` is the authoritative record of what was done;
  STATE.md is current state; the ledger is verification provenance only.

---

## Running the suite

    PYTHONPATH=. .venv/bin/python -m pytest TESTS/ -q

Run from the repository root with the repo root on `PYTHONPATH` (this is
what `.github/workflows/ci.yml` does). Hermetic proof runners:
`EVIDENCE/proofs/*_runner.py`, run the same way; CI's skip list names the
ones it excludes. Test counts are deliberately absent
from this file and from `docs/TOOLING.md` - per G1 discipline, STATE.md plus
the latest VL entry are the count of record.

Tool inventory: `docs/TOOLING.md`. The `scripts/` apply-scripts
(`update_state_vl011.sh`, `append_vl*.sh`) are method-on-record and are NOT
for re-running - their anchors are pinned to historical HEADs and they
fail closed.

## Environment

**Linux is the development environment** (from 2026-09-27; the former native
Windows checkout is deprecated and is not a source of truth). The working copy
is a plain clone of `origin/main` at `/home/elyon/Elyon-Sol`; git and push work
directly. `docs/SESSION_PROTOCOL.md`'s "Environment / sandbox recovery"
section is historical (the Windows-mounted container sandbox) and does not
apply.

- Python 3.14 in `.venv/` (git-ignored). Recreate with
  `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`.
  CI (`.github/workflows/ci.yml`) and the image (`deploy/Dockerfile`) use the
  same Python version and the same pinned `requirements*.txt`.
- Line endings: `.gitattributes` (`* text=auto eol=lf`) makes the working tree
  LF, identical to the index (`git ls-files --eol` -> `i/lf w/lf`). Byte-exact
  hashes of record are still defined over the **git blob**
  (`git show HEAD:<path>`, GR-6 clause 5); on this checkout the working-tree
  file hashes the same, but use the blob form in anything you record.
- Docker is installed, but the account is not in the `docker` group, so the
  compose stack cannot be run without `sudo usermod -aG docker $USER` (then
  re-login). Until that is done, `docker compose ... config` (no daemon)
  validates the compose files.
- `gh` is not authenticated; read CI status from the public API
  (`https://api.github.com/repos/Elyon-Sol/Elyon-Sol/actions/runs`), or run
  `gh auth login`.
- The public website (elyon-sol.io) is served by WordPress, not from this repo.
  `site/index.html` is its source: paste the WHOLE file and confirm the
  published page ends with the footer honest-scope line (a truncated paste has
  happened before - see STATE.md).
