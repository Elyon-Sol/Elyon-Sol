> **ARCHIVED -- NON-CURRENT**
>
> This proof is preserved for historical record. It does not reflect
> the repository at HEAD.
>
> Reason(s): G2 (flat-key API rejected by pep.py), G5 (dead webhook.site URL)
> Archived: 2026-05-15
> Ledger entry: VL-011 (see EVIDENCE/verification_ledger.md)
>
> See docs/restructure/04_current_vs_claimed.md for the gap citations.

---

# Elyon-Sol Interception Proof #001

## Date
2026-05-03

## Repo
https://github.com/Elyon-Sol/Elyon-Sol

## Endpoint
POST /governed-call

---

## Request Sent

curl -X POST http://127.0.0.1:8000/governed-call \
-H "Content-Type: application/json" \
-d '{
  "AP": ["identity"],
  "OP": ["session", "request"],
  "ccs_valid": true,
  "expected_manifest_version": "1.0",
  "target_url": "http://127.0.0.1:9000/target"
}'

---

## Reason It Should Fail

AP is missing required authority role.

Manifest requires:
AR = ["identity", "role"]

Provided:
AP = ["identity"]

AC³ condition:
AP ≥ AR → FALSE

---

## Expected Result

REFUSE  
HTTP 403  
Target endpoint must not be called

---

## Observed Result

PEP returned HTTP 403 with REFUSE  
Target endpoint was NOT called

---

## Conclusion

Elyon-Sol prevented execution before the downstream action occurred.

This demonstrates deterministic pre-execution enforcement of invalid interaction.

---

## Classification

- Type: Authority Failure (AC³)
- Enforcement: Pre-execution (PEP)
- Outcome: REFUSE (fail-closed)

