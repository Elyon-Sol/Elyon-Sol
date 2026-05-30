"""
Generate EVIDENCE/published_hashes.json from live repository state (VL-038).

The published record extends CANON/canon.lock's discipline to the
evaluator and manifest hashes: it carries the same three hashes
build_envelope() pins, so a target can verify an envelope's pins against
this committed record rather than against its own local disk (Decision C).

Derived LIVE here (VL-038 constraint (i): never hand-copied). Regenerate
whenever IMPLEMENTATION/evaluator.py, MANIFEST/manifest.json, or
CANON/canon.lock change. Run from repo root:

    PYTHONPATH=. python3 EVIDENCE/published_hashes_gen.py

Output is sorted-keys, two-space-indented, LF, ASCII (VL-009).
"""

import json

from IMPLEMENTATION.envelope import _read_canon_lock, _evaluator_sha256
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256

OUT_PATH = "EVIDENCE/published_hashes.json"


def build_record():
    mfst = load_manifest()
    return {
        "canon_version": "0.9.8.4",
        "canon_sha256": _read_canon_lock(),
        "evaluator_version": "0.9.8.4",
        "evaluator_sha256": _evaluator_sha256(),
        "manifest_version": mfst["version"],
        "manifest_sha256": manifest_sha256(),
    }


def main():
    record = build_record()
    text = json.dumps(record, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if any(ord(c) >= 128 for c in text):
        raise SystemExit("ABORT: non-ASCII byte in published record")
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote " + OUT_PATH)
    print(text, end="")


if __name__ == "__main__":
    main()
