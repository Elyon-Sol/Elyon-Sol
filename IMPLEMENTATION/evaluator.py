def ac3_valid(ctx):
    return set(ctx.get("AP", [])) >= set(ctx.get("AR", []))


def t26_valid(ctx):
    return set(ctx.get("OP", [])) >= set(ctx.get("R", []))


def ccs_valid(ctx):
    return ctx.get("ccs_valid", False)


def evaluate(ctx):
    if not ac3_valid(ctx):
        return "REFUSE"
    if not t26_valid(ctx):
        return "REFUSE"
    if not ccs_valid(ctx):
        return "REFUSE"
    return "ELIGIBLE"


if __name__ == "__main__":
    import json

    with open("TESTS/test_cases.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    for t in tests:
        result = evaluate(t)
        print(f"{t['name']}: {result} (expected: {t['expected']})")
