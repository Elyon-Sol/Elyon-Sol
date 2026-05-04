# Elyon-Sol PoE Manifest — v0.9.8.5 Post-Enforcement

## Purpose

This manifest defines the Proof-of-Existence set for the Elyon-Sol v0.9.8.5 post-enforcement state.

This PoE set anchors validated artifacts only.

It does not modify canon.
It does not introduce new invariants.
It does not expand the model.

Canonical function remains:

G(I) = AC³ ∧ T²⁶ ∧ CCS

## Included Artifact Classes

- Canon artifacts
- Enforcement evidence artifacts
- Stability evidence artifacts
- Release / promotion metadata where applicable

## Validation Basis

This PoE set corresponds to the post-enforcement promotion state in which:

- REFUSE produced zero external side effects
- ELIGIBLE produced exactly one external execution
- repeated execution showed no leakage, duplication, fallback, or drift
- adversarial validation remained passing

## Verification

Regenerate SHA-256 hashes from repository root and compare against:

POE/POE_SHA256_HASHES.txt

Any mismatch indicates artifact drift.
