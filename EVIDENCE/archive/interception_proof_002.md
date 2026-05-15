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

# Elyon-Sol Interception Proof #002

## Title
Malformed Input and Strict CCS Enforcement

## Date
2026-05-04

## Repo
https://github.com/Elyon-Sol/Elyon-Sol

## Endpoint
POST /governed-call

---

## Purpose

Validate that the PEP refuses malformed or structurally invalid requests before downstream execution.

---

## Cases Tested

### 1. T²⁶ Coverage Failure

Input:
- AP = ["identity", "role"]
- OP = ["session"]

Expected:
- REFUSE
- HTTP 403
- Target not called

Observed:
- REFUSE
- HTTP 403
- Target not called

---

### 2. CCS Version Drift

Input:
- expected_manifest_version = "2.0"
- manifest.version = "1.0"

Expected:
- REFUSE
- HTTP 403
- Target not called

Observed:
- REFUSE
- HTTP 403
- Target not called

---

### 3. Type Confusion Attempt

Input:
- AP = {"identity": true, "role": true}

Expected:
- REFUSE
- HTTP 403
- Target not called

Observed:
- REFUSE
- HTTP 403
- Target not called

---

### 4. Truthy CCS Bypass Attempt

Input:
- ccs_valid = 1

Expected:
- REFUSE
- HTTP 403
- Target not called

Observed:
- REFUSE
- HTTP 403
- Target not called

---

## Conclusion

Elyon-Sol refused malformed input, coverage failure, CCS drift, and truthy CCS bypass attempts before downstream execution.

This confirms strict input boundary enforcement and fail-closed behavior at the PEP layer.

---

## Classification

- Type: Boundary Hardening Proof
- Enforcement: Pre-execution PEP
- Outcome: REFUSE
- Target Execution: Blocked


