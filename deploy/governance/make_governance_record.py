"""
Published record for the governance deployment's own manifest.

docker-compose.governance.yml runs every service against
deploy/governance/manifest.governance.json (mounted over MANIFEST/manifest.json),
a DEPLOYMENT policy that declares HIGH_IMPACT actions - the committed reference
manifest declares none (`HIGH_IMPACT: []`, the conscious opt-out) and stays the
default for every other stack. The target checks each envelope's pins against
the published record, so this deployment needs a record whose manifest pins are
the governance manifest's. Same fields and byte format as
EVIDENCE/published_hashes_gen.py; canon + evaluator pins are derived live, never
hand-copied, and the committed EVIDENCE/published_hashes.json is not touched.

Writes deploy/governance/published_hashes.governance.json (git-ignored: it is
per-deployment and moves whenever evaluator.py changes) and prints the
ELYON_GOV_PINNED_ROOT_SHA256 anchor line for deploy/.env (public material).

Run from the repo root:  PYTHONPATH=. python deploy/governance/make_governance_record.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from IMPLEMENTATION.envelope import _evaluator_sha256, _read_canon_lock  # noqa: E402
from IMPLEMENTATION.evaluator import manifest_sha256, safe_manifest  # noqa: E402
from IMPLEMENTATION.impact import safe_high_impact  # noqa: E402
from IMPLEMENTATION.published_source import anchor_sha256  # noqa: E402

MANIFEST_PATH = "deploy/governance/manifest.governance.json"
OUT_PATH = "deploy/governance/published_hashes.governance.json"


def build_record(manifest_path=MANIFEST_PATH):
    with open(manifest_path, "r", encoding="utf-8") as f:
        mfst = json.load(f)
    if safe_manifest(mfst) is None:
        raise SystemExit("ABORT: governance manifest is malformed (safe_manifest)")
    if not safe_high_impact(mfst):
        raise SystemExit("ABORT: governance manifest declares no valid HIGH_IMPACT set")
    return {
        "canon_version": "0.9.8.4",
        "canon_sha256": _read_canon_lock(),
        "evaluator_version": "0.9.8.4",
        "evaluator_sha256": _evaluator_sha256(),
        "manifest_version": mfst["version"],
        "manifest_sha256": manifest_sha256(manifest_path),
    }


def main():
    text = json.dumps(build_record(), sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote " + OUT_PATH)
    print(text, end="")
    print("deploy/.env addition (public):")
    print("  ELYON_GOV_PINNED_ROOT_SHA256=" + anchor_sha256(text.encode("ascii")))


if __name__ == "__main__":
    main()
