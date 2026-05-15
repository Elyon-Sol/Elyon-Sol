# AC³ Mutation Sensitivity Validation

## Objective

Validate that intentional corruption of AC³ authority admissibility produces deterministic and observable operational failure surfaces rather than silent degradation.

The purpose of this test was not to preserve system correctness.

The purpose was to verify that legitimacy corruption becomes discriminable.

---

## Baseline State

Initial repository validation:

37 passed in 4.74s

Branch used:

test/ac3-mutation-sensitivity

Canonical AC³ logic before mutation:

return AP_set >= AR_set

---

## Intentional Corruption

The AC³ admissibility check was intentionally corrupted:

return True

Mutation rationale:

- force invalid authority admission
- intentionally violate authority legitimacy
- observe operational discrimination behavior

No canonical invariants were modified.

No corruption was committed to canonical branch state.

---

## Observed Failure Surface

Mutation result:

2 failed, 35 passed

Observed failures:

1. concurrent authority isolation
2. concurrent replay receipt terminal-state preservation

Representative failure:

assert eligible == 50
E assert 100 == 50

This demonstrated that unauthorized authority contexts were incorrectly admitted under the intentional mutation.

Replay continuity also preserved the corrupted admissibility outcome:

'ELIGIBLE' == 'REFUSE'

This is operationally important because replay continuity did not mask legitimacy corruption.

The system failed deterministically at the expected authority discrimination surfaces.

---

## Integrity Restoration

Canonical AC³ logic restored:

return AP_set >= AR_set

Post-restoration validation:

37 passed

No persistent contamination observed.

Replay integrity, concurrency isolation, and deterministic admissibility behavior returned to baseline state after restoration.

---

## Interpretation

This validation demonstrates bounded mutation sensitivity within the AC³ authority admissibility layer.

The implementation trajectory is no longer validating only passing behavior.

It is validating whether legitimacy corruption becomes operationally discriminable under bounded pressure conditions.

This test specifically demonstrated:

- deterministic authority corruption detection
- concurrent authority isolation sensitivity
- replay continuity discrimination preservation
- bounded integrity restoration

No claims are made regarding full-stack mutation completeness beyond the tested AC³ layer.
