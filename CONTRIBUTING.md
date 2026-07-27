# Contributing to Elyon-Sol

Contributions are welcome. Two things to know before you open a pull request.

## 1. Licensing of your contribution

Elyon-Sol is licensed under **AGPL-3.0** — there are no commercial or proprietary components.
By submitting a contribution (a pull request, patch, or any code/content), you agree to the
**Developer Certificate of Origin (DCO)** and license your contribution under **AGPL-3.0**.

Sign your commits to certify the DCO:

    git commit -s -m "your message"

The `-s` adds a `Signed-off-by:` line certifying you wrote the contribution or have the
right to submit it under AGPL-3.0. Contributions without sign-off cannot be merged.

## 2. How to contribute

- Open an issue first for anything non-trivial, so the approach can be agreed before you
  build it.
- Match the existing conventions (tests, ASCII/LF, type hints, the fail-closed discipline).
- Include tests. The project keeps a passing suite and an adversarial harness; new behavior
  needs coverage.
- Keep the core's verification logic reuse-only where possible — do not re-implement
  cryptography or admission logic.

Thanks for helping build inspectable, fail-closed governance infrastructure.
