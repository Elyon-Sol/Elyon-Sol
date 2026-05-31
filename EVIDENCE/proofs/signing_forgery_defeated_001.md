# Issuer-signing: the three-model forgery, defeated (VL-040)

**Status:** Current proof.
**Commit anchor:** `<fill the VL-040 build commit hash at commit time per the VL-012 self-referencing-hash discipline>`.
**Spec commit:** `b9ca90a` (artifact 05 "Issuer signature (opt-in)").
**Date of observation:** 2026-05-31.

## Claim

On the SIGNED path, a target holding the gate's pinned public key HONORS a
genuinely gate-signed, current, bound envelope and REFUSES the VL-039 follow-up 2
three-model forgery construction. This closes the forgery finding on the signed
path. It is NOT a blanket "forgery-resistant" claim: forgery is closed only
where signing is required (opt-in); the unsigned path is unchanged and still
forgeable; trust moves to the pinned issuer public key, distributed out-of-band
(see Scope).

* It HONORS a genuinely gate-signed valid envelope (`REASSERTED_AND_BOUND`).
* It REFUSES the verbatim three-model forge - a from-scratch envelope built from
  PUBLIC knowledge only (the published record's hashes + the envelope shape),
  with a correctly recomputed unkeyed `decision_sha256` and NO issuer signature -
  with `REF_VERIFY_SIGNATURE_INVALID`. This directly falsifies the prior
  finding's attack: the forge that three independent models built is now refused.
* It REFUSES a forge that fabricates an `issuer_key_id` the target has not pinned
  (`REF_VERIFY_SIGNATURE_UNKNOWN_KEY`).
* It REFUSES a tampered signed envelope (request_context mutated, not re-signed):
  the signature breaks; refused on `REF_VERIFY_SIGNATURE_INVALID` (the signature
  is checked before `reassert()`).
* On the UNSIGNED path (no pinned key) the SAME forge is still ACCEPTED - the
  honest opt-in boundary.

## Method

A single-process demonstration, `EVIDENCE/proofs/signing_forgery_defeated_001_runner.py`:

* A live Ed25519 keypair is generated in-process (the `cryptography` library);
  the private key is NEVER written to disk (constraint i: no key material
  persisted, nothing hand-copied).
* The gate signs an envelope via `IMPLEMENTATION/envelope.py::sign_envelope`
  (signature over `canonical_json(envelope minus issuer_signature and
  timestamp_utc)`, covering `decision_sha256` and `issuer_key_id`).
* The forge is constructed verbatim from VL-039 follow-up 2: the public
  canon/evaluator/manifest hashes copied into a fresh envelope, decision and
  request_context set to an adversary-chosen interaction, `decision_sha256`
  recomputed over the canonical envelope - no key, no signature.
* The target's admission policy is `IMPLEMENTATION/verifier.py::verify_envelope(
  ..., pinned_public_keys={key_id: public_key})`: the issuer signature is
  verified against the pinned public key BEFORE `reassert()`, fail-closed.

Unlike the G5 cross-host runner, this is single-process: issuer signing is a
PROVENANCE property (did the gate mint this?), verifiable wholly in-process via
`verify_envelope`. No divergent disk, subprocess, or loopback is required (those
were the G5 cross-host TRANSPORT property).

## Observation

|Case|Path|Honored?|Reason|
|-|-|-|-|
|genuine gate-signed envelope|signed (pinned key)|yes|`REASSERTED_AND_BOUND`|
|three-model forge, no signature|signed (pinned key)|no|`REF_VERIFY_SIGNATURE_INVALID`|
|forge with unknown key_id|signed (pinned key)|no|`REF_VERIFY_SIGNATURE_UNKNOWN_KEY`|
|tampered signed envelope|signed (pinned key)|no|`REF_VERIFY_SIGNATURE_INVALID`|
|three-model forge (honest contrast)|unsigned (no pinned key)|yes|`REASSERTED_AND_BOUND`|

The runner asserts every row plus the killer invariant - the signed path refuses
the forge the unsigned path accepts - and exits nonzero on any failure (observed
exit 0). The full suite is 139 -> 149 passed + 0 xfailed (`TESTS/adversarial/test_signing.py`, 10).

## Scope and honest limits (the claim-track gate)

* **Opt-in.** Forgery is closed only on the SIGNED path (`pinned_public_keys`
  supplied). `pep.py`'s default forward stays UNSIGNED; the unsigned path is
  byte-behavior-unchanged and STILL forgeable. The mandatory cutover (signature
  required on the gate's default path) is named, not built.
* **Trust is bootstrapped, not eliminated.** Trust moves from "anyone can
  recompute `decision_sha256`" to "the target trusts the pinned issuer public
  key, distributed out-of-band" - the analog of the B-prime-1 record anchor.
* **Key governance, named not built.** Key distribution, rotation, compromise,
  and revocation are the floor. The word "forgery-resistant" is NOT asserted as
  a settled claim and enters no citable claim / no Zenodo deposit until the
  key-governance cross-model evaluate has run and is folded.
* **Record signing is a different thing.** Signing the published record
  (publisher-signed `published_hashes.json`) is the freshness/revocation anchor
  upgrade, not this increment.

## Reproducibility

1. `pip install "cryptography==44.0.0"`.
2. `PYTHONPATH=. python3 EVIDENCE/proofs/signing_forgery_defeated_001_runner.py`;
   the output reproduces the Observation table and the runner exits 0 iff the
   invariants hold.
3. The suite-level claim is reproducible by `python -m pytest TESTS/`; the
   signing tests are `TESTS/adversarial/test_signing.py`.

## Related artifacts

* Runner: `EVIDENCE/proofs/signing_forgery_defeated_001_runner.py`.
* Log: `EVIDENCE/proofs/signing_forgery_defeated_001.log`.
* Signing: `IMPLEMENTATION/envelope.py::sign_envelope`.
* Verification: `IMPLEMENTATION/verifier.py::verify_envelope` (`pinned_public_keys`).
* Tests: `TESTS/adversarial/test_signing.py`.
* Spec: `docs/restructure/05_admissibility_envelope_spec.md` "Issuer signature (opt-in)".
* The finding this closes: ledger VL-039 follow-up 2; `EVIDENCE/proofs/g5_cross_host_001.md` "Forgery finding".
* Ledger entry: VL-040.
