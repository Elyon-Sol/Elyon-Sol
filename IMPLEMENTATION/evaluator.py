import hashlib
import json

MANIFEST_PATH = "MANIFEST/manifest.json"


def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def manifest_sha256(path=MANIFEST_PATH):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def safe_set(value):
    if not isinstance(value, list):
        return None
    if not all(isinstance(item, str) for item in value):
        return None
    return set(value)


def safe_manifest(manifest):
    if not isinstance(manifest, dict):
        return None

    AR = manifest.get("AR")
    R = manifest.get("R")
    version = manifest.get("version")

    if not isinstance(AR, list) or not all(isinstance(x, str) for x in AR):
        return None
    if not isinstance(R, list) or not all(isinstance(x, str) for x in R):
        return None
    if not isinstance(version, str):
        return None

    return manifest


def ac3_valid(ctx, AR):
    AP_set = safe_set(ctx.get("AP"))
    AR_set = safe_set(AR)

    if AP_set is None or AR_set is None:
        return False

    return AP_set >= AR_set


def t26_valid(ctx, R):
    OP_set = safe_set(ctx.get("OP"))
    R_set = safe_set(R)

    if OP_set is None or R_set is None:
        return False

    return OP_set >= R_set


def manifest_integrity_valid(ctx, manifest):
    """
    Point-in-time manifest integrity check.

    Verifies that the caller's pinned manifest version and SHA256 match the
    manifest currently loaded by the evaluator. Both expected_manifest_version
    and expected_manifest_sha256 are caller-asserted pinning tags - they
    express which manifest the caller expects to be evaluated against, not a
    property derived from any ground truth (canon, signed registry, etc.).
    The check is internal consistency between the caller's pins and the
    evaluator's loaded manifest; it is load-bearing because it gives the
    caller a mechanism to refuse evaluation against an unexpected manifest.

    This is NOT canonical CCS (whitepaper section 12). Canonical CCS is a
    temporal invariant over state transitions S_t -> S_{t+1}; this function
    is point-in-time. The name "CCS" is reserved for the canonical
    implementation (see docs/restructure/05_admissibility_envelope_spec.md;
    gap G0 in docs/restructure/04_current_vs_claimed.md; ledger VL-012).
    """
    # G11 fix (VL-053): the passed manifest is the source of truth for
    # the version and the AR/R sets ac3_valid/t26_valid read, but
    # manifest_sha256() below hashes the on-disk MANIFEST/manifest.json.
    # Before trusting that split-source check, require the passed manifest
    # to BE the on-disk source; a divergent manifest fails closed (canon
    # section 9) rather than yielding an integrity verdict whose version
    # came from the argument and whose sha came from a different file.
    # Closes the manifest-source asymmetry (G11, surfaced VL-012) WITHOUT
    # changing what manifest_sha256() hashes: the on-disk file remains the
    # single pinned source of truth (expected_manifest_sha256,
    # published_hashes.json, decision_sha256, reassert() Row 4).
    if manifest != load_manifest():
        return False

    expected_version = ctx.get("expected_manifest_version")
    actual_version = manifest.get("version")

    if not isinstance(expected_version, str) or not isinstance(actual_version, str):
        return False

    if expected_version != actual_version:
        return False

    expected_manifest_sha256 = ctx.get("expected_manifest_sha256")
    actual_manifest_sha256 = manifest_sha256()

    if (
        not isinstance(expected_manifest_sha256, str)
        or expected_manifest_sha256 != actual_manifest_sha256
    ):
        return False

    return True


def evaluate(ctx, manifest):
    try:
        manifest = safe_manifest(manifest)
        if manifest is None:
            return "REFUSE"

        if not ac3_valid(ctx, manifest["AR"]):
            return "REFUSE"

        if not t26_valid(ctx, manifest["R"]):
            return "REFUSE"

        if not manifest_integrity_valid(ctx, manifest):
            return "REFUSE"

        return "ELIGIBLE"

    except Exception:
        return "REFUSE"


if __name__ == "__main__":
    manifest = load_manifest()

    with open("TESTS/test_cases.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    for t in tests:
        result = evaluate(t, manifest)
        print(f"{t['name']}: {result} (expected: {t['expected']})")
