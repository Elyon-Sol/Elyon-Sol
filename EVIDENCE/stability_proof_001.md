
---

# 📄 `EVIDENCE/stability_proof_001.md`

```md
# Elyon-Sol — Stability Proof #001 (Deterministic Enforcement)

## Objective

Demonstrate that Elyon-Sol maintains **deterministic enforcement behavior under repeated execution**.

Specifically:
- REFUSE → no leakage across repeated calls
- ELIGIBLE → exactly one execution per call
- No drift, duplication, or inconsistency

---

## Environment

- Evaluator: v0.9.8.4
- PEP: active
- External Target: https://webhook.site/4da50ca0-9824-4654-8394-848e3b355e38
- Test Count: 50 iterations per condition
- Date: 2026-05-04 (UTC)

---

## Test A — REFUSE Stability Loop

### Execution

50 repeated requests with invalid authority:

```json
{
  "AP": ["identity"],
  "OP": ["request"],
  "ccs_valid": true,
  "expected_manifest_version": "1.0",
  "target_url": "https://webhook.site/..."
}
