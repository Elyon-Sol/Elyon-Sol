# Elyon-Sol  -  Honest Core Description

**Derived strictly from `IMPLEMENTATION/evaluator.py` and `IMPLEMENTATION/pep.py`.**
No term appears here that the code does not execute.

---

## One-paragraph description (proposed README opening)

Elyon-Sol is a deterministic, fail-closed HTTP admission gate. Given a request and a
SHA256-pinned manifest, it returns `ELIGIBLE` only if **all three** of the following hold:
the caller's authority set (`AP`) is a superset of the manifest's required authority set
(`AR`); the caller's operation set (`OP`) is a superset of the manifest's required
operation set (`R`); and the continuity check passes  -  meaning `ccs_valid` is exactly
`True`, the caller's expected manifest version matches the manifest, and the caller's
expected manifest SHA256 matches the active manifest's hash. If any condition fails, the
manifest is malformed, or any exception is raised, the gate returns `REFUSE`. On
`ELIGIBLE`, the HTTP layer forwards the request to the target URL; on `REFUSE` it returns
HTTP 403 and the target is not called.

---

## What the code does  -  precise statement

| Canon term | Code construct | What it actually checks |
|---|---|---|
| Authority (AC^3) | `ac3_valid(ctx, AR)` | `set(ctx["AP"]) >= set(manifest["AR"])` after string-list type validation |
| Coverage (T^26) | `t26_valid(ctx, R)` | `set(ctx["OP"]) >= set(manifest["R"])` after string-list type validation |
| Continuity (CCS) | `ccs_valid(ctx, manifest)` | `ctx["ccs_valid"] is True` AND version string match AND SHA256 match |
| G(I) | `evaluate(ctx, manifest)` | manifest validity, then AC^3, then T^26, then CCS  -  all must pass; else `REFUSE` |
| Enforcement | `pep.py /governed-call` | `ELIGIBLE` -> forward to `target_url`; else -> HTTP 403 |

## Properties the code genuinely has

- **Deterministic.** Same context + same manifest -> same result. No randomness, no hidden state, no time dependence in the gate logic.
- **Fail-closed.** Every `None` guard, every malformed input, and a bare `except Exception` all route to `REFUSE`. The HTTP layer's `except` paths all return 403.
- **Strict typing.** `safe_set` rejects non-lists and non-string elements. `ccs_valid is True` rejects truthy non-booleans (`1`, `"true"`, objects). These are real, tested boundaries.
- **Manifest-bound.** Continuity is tied to the active manifest's SHA256, not just a version label.
- **Pre-execution.** The gate runs before the target is contacted; `REFUSE` means the target is never called *via this path*.

## Properties the code does NOT currently have  -  stated plainly

- **It is not non-bypassable.** `pep.py` forwards via plain `requests.post`. The target has no way to verify a call arrived through the gate. A caller can POST the target directly and bypass Elyon-Sol entirely. Elyon-Sol gates calls *routed through it*; it does not make the target unreachable by other paths.
- **The forwarded call is unsigned.** Nothing cryptographically marks a call as gate-approved.
- **`ccs_valid` (the input field) is caller-asserted.** The function checks that the caller claimed `True`; the real continuity enforcement is the SHA256 match. The boolean is not independent evidence.
- **No audit trail.** No persistent, third-party-verifiable record of decisions is produced.
- **Single-node, no concurrency guarantees beyond what's tested.** No distributed coordination.

## What Elyon-Sol is, in one honest sentence

A deterministic, fail-closed admission gate that forwards an HTTP call only if the caller
presents authority and operation sets satisfying a SHA256-pinned manifest  -  currently an
opt-in control, not an unbypassable one.

## What it is not (and should not be described as, today)

It is not, as currently implemented, a general "governance substrate," a runtime policy
engine, or an enforcement layer that constrains anything the caller does not voluntarily
route through it. Those are reachable goals  -  see the gap document and the build-outward
scope  -  but they are not current properties, and describing them as current is the
specific thing that produced poor assessments.
