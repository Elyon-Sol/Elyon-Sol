# G5 signed cross-host transport evidence (VL-048)

**Status:** Current proof.
**Commit anchor:** `<BUILD_HASH>` (the VL-048 build commit; fill per the VL-012
self-referencing-hash discipline at commit time).
**Date of observation:** 2026-06-03.

## Claim

The full SIGNED admission chain runs across a process boundary over real
loopback transport, via the production fetch path, with NO test-only shortcut,
and enforces admissibility for routed-and-attested traffic:

- The GATE signs the envelope on its DEFAULT forward path, resolving its
  signing key through the PRODUCTION key path (the `ELYON_SIGNING_KEY_HEX` +
  `ELYON_SIGNING_KEY_ID` environment pair), not an in-process injection.
- A TARGET on a SEPARATE PROCESS, whose local `IMPLEMENTATION/evaluator.py` is
  byte-divergent from the gate's, FETCHES the published record over a real
  socket (the production `IMPLEMENTATION.published_source.fetch_published_record`,
  a real `requests.get`), anchor-verifies it against a single pinned root, and
  verifies the envelope's issuer signature against an OUT-OF-BAND-pinned public
  key plus currency-against-the-fetched-record plus interaction binding.
- The target HONORS a genuinely gate-signed, current, bound envelope EVEN
  THOUGH its own local disk is divergent (currency comes from the fetched
  record, Decision C). A VL-038-style local-disk verify would have FALSE-REFUSED
  the same envelope.
- The target REFUSES the VL-039-follow-up-2 keyless forge (a from-scratch
  envelope with a correctly recomputed unkeyed `decision_sha256` but NO issuer
  signature): on the signed path it is rejected with
  `REF_VERIFY_SIGNATURE_INVALID`. This is the forgery finding closed on the
  signed CROSS-HOST chain.
- The target REFUSES a tampered signed envelope, a fetched record that fails
  the pinned anchor, and an absent envelope.

This is the first state in which the project's SIGNED chain (issuer signing,
VL-040..047) and its CROSS-HOST transport (VL-039) run together end-to-end with
no shortcut. It does NOT make the system "deployed": true multi-machine
networking and TLS are the named G5 floor (Decision F), and the A3b freshness
sub-class (a stale-but-anchor-matching, validly signed record is still honored)
is unchanged and still named. "forgery-resistant" stays bounded
(signed-path-under-uncompromised-root) and out of any deposit.

## Method

A real two-context demonstration over loopback (`127.0.0.1`), driven by
`EVIDENCE/proofs/g5_signed_cross_host_001_runner.py`:

- **Gate (signing).** The runner generates a live ephemeral Ed25519 keypair,
  sets `ELYON_SIGNING_KEY_HEX` + `ELYON_SIGNING_KEY_ID`, and drives the real
  `IMPLEMENTATION/pep.py` `/governed-call` ELIGIBLE path so
  `pep._get_signing_key()` resolves the key from the environment (the deployed
  path), NOT via the autouse `gate_signing` conftest fixture. The pushed signed
  envelope is captured from the `X-Elyon-Sol-Envelope` header.
- **Publisher.** A stdlib `http.server` serves the authentic
  `EVIDENCE/published_hashes.json` bytes on an ephemeral loopback port; a second
  server serves a TAMPERED record (different bytes) for the anchor-failure case.
- **Target.** A SUBPROCESS whose working tree is a copy of the repository with
  `IMPLEMENTATION/evaluator.py` byte-mutated, so its local evaluator hash
  genuinely differs from the gate's. It fetches the published record over the
  real socket (`fetch_published_record`), anchor-verifies it against the pinned
  root, holds the gate PUBLIC key as out-of-band configuration, and runs
  `verifier.verify_envelope(..., record_source=<fetched>,
  pinned_public_keys={key_id: gate_pub})`. It imports the verifier, the
  transport reader, and the public-key reconstruction only; it never imports
  `pep.py`, and its environment has the signing key removed.

The pinned anchor is the sha256 of `EVIDENCE/published_hashes.json`, derived
live (constraint (i)) and held by the target as out-of-band configuration; it is
NOT fetched alongside the record.

Observed at this run:

| Value | Observed |
|---|---|
| Pinned anchor (sha256 of published_hashes.json) | `6abf9a1181121f963eb91e18df560499990396d540c00115ffcfd7bc8907daeb` |
| Gate evaluator sha256 | `cf311cb7fc99f170c4814eebeee63262946ac6b71099635986257887746e512b` |
| Target evaluator sha256 (mutated tree) | `480c73865f35db8f4737b9b51755f845dbc9eafd80d1a9946dab16d4e4c7fac5` |
| Gate public key (b64, pinned out-of-band) | `i1oRa2JU0nZlwwKvkYe99lCGLiBSXWpBQCSI1FpYPag=` |

The gate and target evaluator hashes differ, confirming the target tree is
genuinely divergent (the killer-case precondition).

## Observation

| Case | Adversary / role | Honored? | Reason |
|---|---|---|---|
| Signed valid, authentic record, DIVERGENT target disk | none (the killer case) | yes | `REASSERTED_AND_BOUND` |
| Keyless forge (no signature), authentic record | A2 (forgery) | no | `REF_VERIFY_SIGNATURE_INVALID` |
| Tampered signed envelope, authentic record | A2 (tamper) | no | `REF_VERIFY_SIGNATURE_INVALID` |
| Signed valid, tampered record (fails pinned anchor) | A5 (record-hop tamper) | no | `REF_TARGET_ANCHOR_MISMATCH` |
| No envelope, authentic record | A1 | no | `REF_VERIFY_ENVELOPE_ABSENT` |

For the killer case, the target reported that a VL-038-style local-disk verify
on its divergent tree would have returned
`REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED` (its local evaluator hash does not
match the envelope's pin). The signed cross-host target honored anyway, because
it verified the signature against the out-of-band pin and currency against the
fetched authentic record. That contrast is the load-bearing proof that the
currency check comes from the record, not local disk, AND that the signature
makes the chain forgery-resistant where VL-039's unsigned chain was only
tamper-evident. The runner asserts every row plus the killer invariant and exits
nonzero on any failure (observed exit 0).

## Scope and honest limits

- **The signed chain, end-to-end, no shortcut.** The gate signs on its default
  path via the production key path; the target verifies a signature it did not
  inject, over a record it fetched over a real socket, on a genuinely divergent
  tree. None of the four section-4.2 shortcuts (hand-built envelope, in-process
  key injection, loopback stub, target importing gate internals) is present.
- **The G5 floor (Decision F), named not built.** Secure distribution of the
  pinned anchor and the pinned public key; record/key freshness and revocation;
  true multi-machine networking and TLS (modeled here by loopback). Greening
  END_TO_END_NO_SHORTCUT does not claim these.
- **A3b freshness, unchanged and still named.** A stale-but-anchor-matching,
  validly signed record is still honored - `reassert()` checks repo-state
  currency, not request liveness. This is the same A3b bound the VL-039 proof
  named; VL-048 does not close it.
- **A1 (the declining caller)** remains closeable only by a target-side policy
  refusing un-attested calls; the absent-envelope row demonstrates the
  target-side defense.
- **"forgery-resistant" stays bounded** (signed-path-under-uncompromised-root,
  VL-040-follow-up-2 / VL-042-follow-up form) and out of any deposit. The
  decisive failure (root / issuer key compromise, recovery out-of-band) is
  unchanged.

## Reproducibility

1. Confirm the published record matches live state (the VL-038 checks).
2. Run `PYTHONPATH=. python3 EVIDENCE/proofs/g5_signed_cross_host_001_runner.py`;
   the output reproduces the Observation table and the runner exits 0 iff the
   invariants hold. (The observed evaluator hashes and the pinned anchor will
   match live state; the gate keypair is ephemeral per run, so the gate public
   key value will differ run to run - only the verdicts are invariant.)
3. The suite-level regression is `python -m pytest TESTS/`; the lighter
   in-process signed-chain gate is
   `TESTS/readiness/test_deployment_predicates.py::test_end_to_end_no_shortcut`.

## Related artifacts

- Runner: `EVIDENCE/proofs/g5_signed_cross_host_001_runner.py`.
- Log: `EVIDENCE/proofs/g5_signed_cross_host_001.log`.
- Transport module: `IMPLEMENTATION/published_source.py` (the production fetch).
- Signing: `IMPLEMENTATION/envelope.py::sign_envelope`,
  `IMPLEMENTATION/pep.py::_get_signing_key` (the production key path).
- Verification: `IMPLEMENTATION/verifier.py::verify_envelope`
  (`record_source` + `pinned_public_keys`, reused as-is; no logic change).
- Published record: `EVIDENCE/published_hashes.json`.
- Readiness: `EVIDENCE/readiness.json` (END_TO_END_NO_SHORTCUT green at VL-048;
  dependency set {issuer_signing, enforcement_push}).
- Predecessor (unsigned cross-host): `EVIDENCE/proofs/g5_cross_host_001.{log,md}`
  (VL-039).
- Design: `docs/restructure/08_enforcement_design.md` (section 6, the G4/G5
  boundary; the VL-048 update).
- Ledger entry: VL-048.
