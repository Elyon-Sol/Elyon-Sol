from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "EVIDENCE/interception_proof_002.md",
    "EVIDENCE/stability_proof_001.md",
    "POE/POE_MANIFEST.md",
]

OPTIONAL_FILES = [
    "README.md",
    "RELEASE_NOTES.md",
    "MANIFEST/manifest.json",
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    targets = []

    for rel in FILES:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f"Required PoE artifact missing: {rel}")
        targets.append(rel)

    for rel in OPTIONAL_FILES:
        path = ROOT / rel
        if path.exists():
            targets.append(rel)

    output = ROOT / "POE" / "POE_SHA256_HASHES.txt"

    lines = [
        "# Elyon-Sol PoE SHA-256 Hashes — v0.9.8.5 Post-Enforcement",
        "# Generated from repository root artifacts",
        "",
    ]

    for rel in sorted(targets):
        digest = sha256_file(ROOT / rel)
        lines.append(f"{digest}  {rel}")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Artifacts hashed: {len(targets)}")

if __name__ == "__main__":
    main()
