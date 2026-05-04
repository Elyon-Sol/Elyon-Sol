import json


def load_manifest():
    with open("MANIFEST/manifest.json", "r", encoding="utf-8") as f:
        return json.load(f)


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


def ccs_valid(ctx, manifest):
    if ctx.get("ccs_valid") is not True:
        return False

    expected = ctx.get("expected_manifest_version")
    actual = manifest.get("version")

    if not isinstance(expected, str) or not isinstance(actual, str):
        return False

    return expected == actual


def evaluate(ctx, manifest):
    try:
        manifest = safe_manifest(manifest)
        if manifest is None:
            return "REFUSE"

        if not ac3_valid(ctx, manifest["AR"]):
            return "REFUSE"

        if not t26_valid(ctx, manifest["R"]):
            return "REFUSE"

        if not ccs_valid(ctx, manifest):
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
