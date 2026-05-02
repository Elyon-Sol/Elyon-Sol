import json

def load_manifest():
    with open("MANIFEST/manifest.json", "r") as f:
        return json.load(f)


def ac3_valid(ctx, AR):
    return set(ctx.get("AP", [])) >= set(AR)


def t26_valid(ctx, R):
    return set(ctx.get("OP", [])) >= set(R)


def ccs_valid(ctx):
    return ctx.get("ccs_valid", False)


def evaluate(ctx, manifest):
    AR = manifest["AR"]
    R = manifest["R"]

    if not ac3_valid(ctx, AR):
        return "REFUSE"

    if not t26_valid(ctx, R):
        return "REFUSE"

    if not ccs_valid(ctx):
        return "REFUSE"

    return "ELIGIBLE"


if __name__ == "__main__":
    manifest = load_manifest()

    with open("TESTS/test_cases.json") as f:
        tests = json.load(f)

    for t in tests:
        result = evaluate(t, manifest)
        print(f"{t['name']}: {result} (expected: {t['expected']})")
