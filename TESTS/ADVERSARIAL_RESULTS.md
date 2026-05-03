

Source:
- Claude-generated adversarial test suite

Scope:
- Type coercion (string, int, dict, nested)
- Missing / malformed fields (AP, OP, CCS, version)
- Structural anomalies (null, empty, partial)
- String integrity (case, whitespace, unicode)
- CCS behavior (missing, false, truthy)
- Manifest continuity (version drift, mismatch)

Total cases: 26

Initial result:
- 25 passed
- 1 failed (ap_wrong_type_dict)

Finding:
- Dict input for AP was coerced via `set(dict)` → keys accepted
- Result: unintended ELIGIBLE

Resolution:
- Enforced strict input typing:
  - AP ∈ list[str]
  - OP ∈ list[str]
  - ccs_valid must be True (not truthy)

Final result:
- 26/26 passed
- All malformed inputs fail-closed

Notes:
- Manifest integrity (hash) not enforced
- Empty AR/R remains fail-open by design constraint
