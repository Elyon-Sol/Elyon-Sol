import json

def load_manifest():
    with open("MANIFEST/manifest.json", "r") as f:
        return json.load(f)

def _valid_list_of_strings(x):
    return isinstance(x, list) and all(isinstance(i, str) for i in x)

def ac3_valid(ctx, AR):
    AP = ctx.get("AP")
    if not _valid_list_of_strings(AP):
        return False
    return set(AP) >= set(AR)

def t26_valid(ctx, R):
    OP = ctx.get("OP")
    if not _valid_list_of_strings(OP):
        return False
    return set(OP) >= set(R)

def ccs_valid(ctx, manifest):
    if not ctx.get("ccs_valid", False):
        return False

    expected_version = ctx.get("expected_manifest_version")
    actual_version = manifest.get("version")

    return expected_version == actual_version

def evaluate(ctx, manifest):
    AR = manifest["AR"]
    R = manifest["R"]

    if not ac3_valid(ctx, AR):
        return "REFUSE"

    if not t26_valid(ctx, R):
        return "REFUSE"

    if not ccs_valid(ctx, manifest):
        return "REFUSE"

    return "ELIGIBLE"

if __name__ == "__main__":
    manifest = load_manifest()

    with open("TESTS/test_cases.json") as f:
        tests = json.load(f)

    for t in tests:
        result = evaluate(t, manifest)
        print(f"{t['name']}: {result} (expected: {t['expected']})")
