"""The readiness gate (T-readiness). Run as part of the normal pytest suite.

Fails the build if the manifest is malformed or DISHONEST (a true flag with no
proof, a false flag with no reason, a green predicate whose dependencies are not
wired, or a named proof file that does not exist). It does NOT fail merely because
predicates are red - red is the correct current state. See
docs/restructure/10_readiness_spec.md.
"""

import os

from IMPLEMENTATION import readiness


def _find_repo_root(start):
    d = start
    for _ in range(8):
        if os.path.isfile(os.path.join(d, "EVIDENCE", "readiness.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise AssertionError("could not locate EVIDENCE/readiness.json above %s" % start)


REPO_ROOT = _find_repo_root(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(REPO_ROOT, "EVIDENCE", "readiness.json")


def test_manifest_is_well_formed_and_honest():
    m = readiness.load_manifest(MANIFEST_PATH)
    errors = readiness.validate_manifest(m)
    assert not errors, "readiness manifest is dishonest/malformed:\n  - " + "\n  - ".join(errors)


def test_every_named_proof_file_exists():
    m = readiness.load_manifest(MANIFEST_PATH)
    missing = [f for (f, ok) in readiness.assert_proof_files_exist(m, REPO_ROOT) if not ok]
    assert not missing, "readiness manifest names proof files that do not exist: " + ", ".join(missing)


def test_print_readiness_summary(capsys):
    # Always passes; surfaces the one line you actually watch. Run pytest -s to see it.
    m = readiness.load_manifest(MANIFEST_PATH)
    line = readiness.summary_line(m)
    print("\n" + line)
    s = readiness.predicate_summary(m)
    assert s["n_green"] + len(s["red"]) == s["total"]
