# G2 Schema-Layer Failing Tests Proof #001

## Date
2026-05-18

## Ledger entry
VL-017 (`EVIDENCE/verification_ledger.md`)

## Source
`TESTS/adversarial/test_request_schema.py`, derived from
`SPEC/request_schema.md` (post-VL-016, CORRECTED).

## Raw output
`EVIDENCE/proofs/g2_schema_failing_tests_001.log`

---

## What this proof shows

27 tests, derived one per refusal class named in
`SPEC/request_schema.md` "Rejected shapes" and "PEP boundary
behavior," plus a positive accepting-shape case. Against
`IMPLEMENTATION/pep.py` at HEAD (commit `572828e`, VL-017a), all
27 tests fail. This is the honest G2 signal that the schema's
build-order step 2 specifies.

## How they fail (the uniform-422 finding)

All 27 tests fail at the same wire-shape gate with HTTP 422 from
Pydantic, message `Field required` with `loc=["body","context"]`.
None of the tests reach `evaluate()`. None of the tests reach
`requests.post()` (upstream_guard records zero calls across all
27 cases). The failure is at the FastAPI/Pydantic boundary
because `GovernedCallRequest` declares `context: Dict[str, Any]`
at the top level, but every test request uses the new schema's
`interaction` envelope.

This is a stronger statement than "the tests fail." The tests
collectively prove that the current `pep.py` wire shape is
incompatible with the corrected schema: ANY request conforming
to the new wire shape is rejected at the Pydantic layer before
validator-level discrimination is possible.

## What this proof does NOT show

The uniform-422 failure mode means the tests do not, today,
discriminate between the seven refusal classes
(`REF_SCHEMA_TOP_LEVEL`, `REF_SCHEMA_BAD_URL`,
`REF_SCHEMA_FLAT_KEYS`, `REF_SCHEMA_MANIFEST_PINNING_MISSING`,
`REF_SCHEMA_TYPE_MISMATCH`, `REF_SCHEMA_RESERVED_CCS`,
`REF_SCHEMA_PARSE_ERROR`). They all fail at the same gate. The
discrimination tests become genuinely independent once VL-019
lands the new wire shape; before VL-019 they are effectively
one test with 27 names, all asserting "current `pep.py` is
incompatible with the corrected schema's wire."

This is a property of the current code, not a defect in the
tests. There is no way to write a test that exercises the new
wire shape against the current code without that test failing
at the Pydantic gate. The tests' diagnostic value is
post-VL-019; their G2-signal value is now.

## Reproducibility

Run:

    python -m pytest TESTS/adversarial/test_request_schema.py -v

Expected outcome (current HEAD): 27/27 fail, all with HTTP 422
on the wire-shape gate. Expected outcome (post-VL-019, with
validator landed): 27/27 pass, with each negative case
producing HTTP 403 and the schema-named refusal code.

## Regression footprint

Running `python -m pytest TESTS/test_adversarial_evaluator.py -v`
continues to produce 23/23 passing. The new test file is purely
additive at the wire/PEP boundary; it does not touch the
evaluator-boundary tests.