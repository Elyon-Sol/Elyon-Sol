# Elyon-Sol v0.9.8.4 — Enforcement Evidence Addendum (Revision 3)

## Abstract

Elyon-Sol is a deterministic, fail-closed HTTP admission gate derived from a formal
admissibility specification. The canonical model is unchanged from v0.9.8.4:

**G(I) = AC³ ∧ T²⁶ ∧ CCS**

No new invariants are introduced and no canonical definitions are modified. This
addendum publishes enforcement evidence at a specific commit of the implementation.

**Snapshot:** commit `c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920`, observed on 2026-06-08.
All three canonical invariants are implemented and exercised in code at this commit.
Authority (AC³, canon sections 11.3 and 11.5) and Coverage (T²⁶, canon sections 11.4 and
11.6) are evaluated at the request layer. Continuity (CCS, canon sections 12 and 13) is
realized at the admissibility envelope layer: on every ELIGIBLE decision the gate
constructs a content-hashed envelope recording canon, manifest, evaluator, request, and
condition-result state at decision time, and supports reassertion of that envelope against
the live system state. A change in canon, manifest, or evaluator hash invalidates the prior
ELIGIBLE per canon section 12.4; continuity does not persist across transitions without
revalidation (canon section 13).

Since Revision 2 (snapshot `89ff2f9`, 2026-05-25, VL-029, 84 tests) the implementation has
advanced substantially while the canon stayed locked. Target-side verification, envelope
delivery, an enforcing target, issuer signing (now the default forward), key/root records
with revocation and planned rotation, cross-host transport of the published record, a
readiness-drift instrument, and a standalone reference enforcing target are now built and
exercised in code. The full repository test suite is **211 of 211 passing, 0 xfailed**, up
from 84 at Revision 2.

**Observed enforcement behavior at the snapshot commit** (Section 2 below; re-run at this
commit against the webhook.site third-party receiver, inbox baseline 155 → 257): 204 HTTP
calls (102 REFUSE, 102 ELIGIBLE), 0 unexpected outcomes, exactly 102 external POSTs at the
receiver — one per ELIGIBLE call, zero from REFUSE calls. On the ELIGIBLE path the forwarded envelope is now cryptographically
**signed** by the gate before it is pushed (the VL-047 mandatory-signing cutover).

This is an evidence publication, not a canonical update. It reports development-side
(referent-bound) evidence — the test suite, the runnable proofs, and a measured
interception run. It does **not** report external, third-party adversarial validation on a
real multi-host surface; that remains the open finish line (see "Honest scope and open
items" below).

---

## What changed since Revision 2

Revision 2 listed four build-outward gaps as open: non-bypassable enforcement, durable
external verification, evaluator-domain canon-derived tests, and a structural-position
question on the in-evaluate CCS failure case. The status at this commit:

- **Non-bypassable enforcement — built for routed-and-attested traffic.** The gate now
  PUSHES the admissibility envelope on every ELIGIBLE forward as the out-of-band header
  `X-Elyon-Sol-Envelope`, and a target-side verifier (`IMPLEMENTATION/verifier.py`,
  `verify_envelope()`) decides honor/refuse by re-asserting the envelope's pinned state and
  binding it to the live interaction. This closes forgery (A2) and same-state replay (A3)
  for routed, attested calls. It does **not** blanket-resolve bypassability: a caller that
  declines to route through the gate (A1) is closeable only by a target-side admission
  policy — which is itself now built as the reference enforcing target (below).
- **Issuer signing, now the default.** ELIGIBLE envelopes are signed (Ed25519) before they
  are forwarded; an enforcing target verifies the signature against a pinned issuer key
  before reassertion. A gate with no signing key configured fails closed rather than
  forwarding unsigned (the VL-047 mandatory-signing cutover). Issuer-key expiry, a published
  signed key record with revocation, and planned in-band root rotation with per-root status
  are also built.
- **Cross-host transport of the published record — built (loopback model).** A target on a
  separate process can fetch the published hash record over HTTP and verify it against a
  single out-of-band-pinned root anchor, so its currency check consults the fetched record
  rather than its own local disk. True multi-machine networking and TLS remain the named
  floor (not closed; see below).
- **Reference enforcing target — built.** `IMPLEMENTATION/reference_target.py` is a
  standalone, deployable target that resolves its trust configuration out-of-band, reads the
  attestation header, fetches and anchor-verifies the published record, and honors a call
  only if `verify_envelope()` accepts against the fetched record and the pinned gate
  signature verifies. It is a reference policy, not tuned to author test vectors.
- **Evaluator-domain canon-derived tests — built.** In addition to the envelope-domain
  canon-derived suite, the evaluator domain now has canon-derived tests
  (`TESTS/adversarial/test_evaluator_canonical.py`) citing canon sections 11.7, 11.8, and
  11.9. Gap G7 (tests are code-derived, not canon-derived) is recorded RESOLVED across both
  domains in the repository gap tracker.
- **Readiness-drift instrument.** A machine-checked readiness manifest
  (`EVIDENCE/readiness.json`) records, per capability, whether it is built, wired to the
  default path, exercised end-to-end, and transported — each field test-backed or false with
  a stated reason. Its three deployment predicates (DEFAULT_SECURE, END_TO_END_NO_SHORTCUT,
  ROOT_RECOVERY) are green at the loopback model and each explicitly excludes "true
  multi-machine / TLS" from its scope.

---

## Enforcement Evidence

### Test environment

| Field | Value |
|---|---|
| Snapshot commit | `c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920` |
| Canon version | v0.9.8.4 (locked; SHA256-pinned at `CANON/canon.lock`) |
| Canon SHA256 | `d1c9d187953eed8145c2d67a98e052415ca2a4c8b722a8011280e21502b4d7bd` |
| PEP runtime | `python -m uvicorn IMPLEMENTATION.pep:app` on `http://127.0.0.1:8000` |
| External receiver | webhook.site (third-party HTTP intake) — `https://webhook.site/4da50ca0-9824-4654-8394-848e3b355e38` |
| Date of observation | 2026-06-08 |
| Manifest version asserted | `1.0` |
| Manifest SHA256 asserted | `a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8` |
| Gate signing | Ed25519, key resolved via `ELYON_SIGNING_KEY_HEX` + `ELYON_SIGNING_KEY_ID` (VL-047) |

Two request bodies were used. REFUSE pattern: empty AP and OP arrays, schema-valid but
failing AC³ and T²⁶ at the evaluator layer. ELIGIBLE pattern: `AP = ["identity", "role"]`,
`OP = ["session", "request"]`, both supersets of the manifest's required sets. Each body
carries the manifest-pinning fields (`expected_manifest_version`,
`expected_manifest_sha256`) per the wire schema.

### Internal consistency (Section 1)

Full repository test suite at the snapshot commit:

```
$ python -m pytest TESTS/ -q
...
211 passed in 1.62s
```

The 211-test suite (0 xfailed) includes, by file:

| Test file | Count | Domain |
|---|---|---|
| `TESTS/adversarial/test_ccs_canonical.py` | 9 | Canon-derived CCS (sections 11.9, 12.1, 12.3, 12.4, 13) |
| `TESTS/adversarial/test_evaluator_canonical.py` | 23 | Canon-derived AC³/T²⁶/manifest (11.7, 11.8, 11.9) |
| `TESTS/adversarial/test_envelope.py` | 13 | Admissibility envelope spec |
| `TESTS/adversarial/test_request_schema.py` | 28 | Wire-schema refusal classes + accepting case |
| `TESTS/adversarial/test_verifier.py` | 11 | Target-side verifier (integrity + binding) |
| `TESTS/adversarial/test_enforcement.py` | 7 | Enforcing target; A1/A2/A3 + published-record anchor |
| `TESTS/adversarial/test_cross_host.py` | 8 | Cross-host record transport + pinned anchor |
| `TESTS/adversarial/test_signing.py` | 10 | Issuer signing / forgery defeat |
| `TESTS/adversarial/test_signing_expiry.py` | 11 | Issuer-key expiry |
| `TESTS/adversarial/test_key_record.py` | 15 | Published key record / revocation |
| `TESTS/adversarial/test_root_record.py` | 18 | Root record / planned rotation / per-root status |
| `TESTS/adversarial/test_reference_target.py` | 8 | Reference enforcing target |
| `TESTS/adversarial/test_bypass.py` | 2 | Honest A1-bypass demonstration |
| `TESTS/adversarial/test_findings_001.py` | 5 | Regression of specific findings |
| `TESTS/test_adversarial_evaluator.py` | 23 | Evaluator-layer regression |
| `TESTS/test_pep.py` | 7 | PEP boundary, envelope emission, signed default forward |
| `TESTS/test_concurrency.py` | 4 | Concurrency |
| `TESTS/test_replay_receipts.py` | 3 | Replay receipts |
| `TESTS/readiness/test_readiness.py` | 3 | Readiness-manifest honesty gate |
| `TESTS/readiness/test_deployment_predicates.py` | 3 | Deployment predicates |
| **Total** | **211** | |

The full test inventory is pinned to the snapshot commit in the repository's verification
ledger (`EVIDENCE/verification_ledger.md`, current trajectory entry VL-061).

### External interception (Section 2)

> **Note on this run.** The figures below were measured at the snapshot commit `c756f8f`
> against `webhook.site` — a third-party HTTP intake outside the gate's process, providing
> independent observation of side effects. The receiver inbox held 155 requests before the
> run (the baseline offset); a clean run leaves it at 257. Each ELIGIBLE call returned HTTP
> 200, which the gate returns only after its outbound `requests.post()` to the receiver
> completes, so the 102 external POSTs are confirmed gate-side and corroborated by the
> receiver inbox delta. The gate's outbound client identifies as `python-requests`.

Sanity check (two single calls):

| Call | Body | HTTP | Receiver delta |
|---|---|---|---|
| 1 | REFUSE (empty AP/OP) | 403 | +0 |
| 2 | ELIGIBLE | 200 | +1 |

Block 2 — Temporal stability (sequential):

| Phase | Calls | Expected HTTP | Observed HTTP | Receiver delta |
|---|---|---|---|---|
| 50 REFUSE | 50 | 403 | 403 × 50 | +0 |
| 50 ELIGIBLE | 50 | 200 | 200 × 50 | +50 |
| Block 2 total | 100 | — | 0 unexpected | +50 |

Block 2 wall-clock: 2026-06-08T18:10:19Z to 2026-06-08T18:11:04Z (≈ 45 seconds).

Block 3 — Aggregate continuity (alternating REFUSE/ELIGIBLE):

| Phase | Calls | Expected HTTP | Observed HTTP | Receiver delta |
|---|---|---|---|---|
| 51 REFUSE | 51 | 403 | 403 × 51 | +0 |
| 51 ELIGIBLE | 51 | 200 | 200 × 51 | +51 |
| Block 3 total | 102 | — | 0 unexpected | +51 |

Block 3 wall-clock: 2026-06-08T18:11:04Z to 2026-06-08T18:11:47Z (≈ 44 seconds).

Aggregate observation:

| Metric | Value |
|---|---|
| Total HTTP calls (sanity + Blocks 2 and 3) | 204 |
| REFUSE calls (expected 403) | 102 |
| REFUSE returning 403 | 102 |
| ELIGIBLE calls (expected 200) | 102 |
| ELIGIBLE returning 200 | 102 |
| Unexpected HTTP outcomes | 0 |
| Webhook.site inbox before test | 155 |
| Webhook.site inbox after test | 257 |
| External POSTs observed | 102 |
| External POSTs from REFUSE calls | 0 |
| External POSTs from ELIGIBLE calls | 102 |
| Duplicate external executions | 0 |
| Retry artifacts | 0 |

The webhook.site receiver is an HTTP intake running outside the gate's process, providing
third-party observation of side effects independent of the gate. The observed pattern — 102
ELIGIBLE responses paired with exactly 102 external POSTs (inbox 155 → 257), and 102 REFUSE
responses paired with exactly 0 external POSTs — exhibits the deterministic, fail-closed
enforcement property the canon specifies.
At this commit each ELIGIBLE forward additionally carries a gate-signed envelope (VL-047),
so the side-effecting POST is not only gated but attested.

### Adversarial validation surface (Section 3)

The canon-derived surface for canonical CCS remains at
`TESTS/adversarial/test_ccs_canonical.py`, each test docstring citing the canon clause it
verifies:

| Test | Canon clause cited |
|---|---|
| `test_canon_12_1_state_transition_detected_via_hash_change` | §12.1 state-transition definition with §12.4 invalid-transition examples |
| `test_canon_12_3_d_consistency_first_issuance_null` | §12.3 continuity constraint; inapplicable on first issuance |
| `test_canon_12_3_ccs_derived_true_on_REASSERTED` | §12.3 continuity constraint; derived CCS on reassertion |
| `test_canon_12_4_ccs_derived_false_on_INVALIDATED` | §12.4 failure condition; CCS = 0 on invalidation |
| `test_canon_12_4_ccs_derived_false_on_RE_EVALUATE_REQUIRED` | §12.4 failure condition; CCS = 0 on re-evaluation required |
| `test_canon_12_4_evaluator_change_invalidates_continuity` | §12.4 evaluator hash change as decision-logic transition |
| `test_canon_11_9_manifest_change_invalidates_continuity` | §11.9 manifest integrity with §12.4 governing manifest version change |
| `test_canon_13_eligibility_does_not_persist` | §13 eligibility does not persist without revalidation |
| `test_row_2_tamper_detection_via_artifact_05_mechanism` | §§12.3/12.4 fail-closed semantics via envelope-layer tamper detection |

At this commit the canon-derived and adversarial surface extends well beyond the envelope
domain. The evaluator domain is covered by `test_evaluator_canonical.py` (canon §§11.7,
11.8, 11.9). The enforcement surface is exercised adversarially by: `test_verifier.py` and
`test_enforcement.py` (forgery A2, same-state replay and target_url binding A3, the
un-attested A1 caller, and the published-record-mismatch defensibility case);
`test_cross_host.py` (currency from a fetched, anchor-verified record despite a divergent
local disk; a record failing the pinned anchor is refused); `test_signing.py` /
`test_signing_expiry.py` (keyless forge on the signed path, expired issuer key);
`test_key_record.py` / `test_root_record.py` (unknown/revoked/out-of-window issuer keys,
retired/revoked roots, planned rotation); and `test_reference_target.py` (the deployable
target honoring a valid signed routed call and refusing forge, replay, target_url-swap,
absent-envelope, record-mismatch, and unconfigured cases). Runnable, exit-coded proofs for
the cross-host and signed chains live under `EVIDENCE/proofs/`.

Build-outward and open items are documented openly in the repository gap tracker at
`docs/restructure/04_current_vs_claimed.md`.

---

## Honest scope and open items

This addendum reports **development-side, referent-bound** evidence: the test suite, the
runnable proofs, and a measured interception run. Per the repository's governance rule GR-3
(`docs/MAINTENANCE_PROTOCOL.md`), a result is evidence only when it is bound to a referent
(execution, or an adversarial-by-construction artifact); model judgments of soundness or
value are not evidence. The following remain open and are not claimed closed:

- **External, third-party adversarial validation on a real surface has not been performed.**
  The interception run above uses a third-party receiver (webhook.site) for side-effect
  observation, but the gate and receiver were driven by the author and the cross-host chains
  are proven over loopback transport — this is observation, not an adversarial pen-test.
  True multi-machine networking with TLS, and an attacker external to the build, are the
  named G5 floor and the finish line; see
  `docs/methodology/external_verification_readiness.md`, which records the current verdict as
  NOT READY for external verification, the binding reason being referent quality (loopback
  transport), not documentation.
- **A1 (the declining caller)** is closeable only by a target-side admission policy (now
  built as the reference enforcing target), not by the gate itself.
- **Record freshness (A3b):** a stale-but-anchor-matching, validly signed record is still
  honored (reassertion checks repository-state currency, not request liveness).
- **Root-key compromise recovery** is irreducibly out-of-band; only planned rotation is
  built.
- **G12/G13** (canon-layer wire-origin and manifest-pinning provenance questions) have their
  schema-layer halves addressed and their canon-layer halves open pending a canon-version
  event.

---

## Reproducibility

The full sequence is reproducible from the public repository at the snapshot commit:

1. Clone the repository and check out commit `c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920`.
2. Verify the canon lock: `sha256sum -c CANON/canon.lock` against `CANON/canon.md`.
3. Compute the manifest SHA256: `sha256sum MANIFEST/manifest.json`.
4. Configure a gate signing key out-of-band: set `ELYON_SIGNING_KEY_HEX` (hex of a raw
   Ed25519 private key) and `ELYON_SIGNING_KEY_ID` (the VL-047 mandatory-signing cutover; a
   gate with no key fails closed rather than forwarding unsigned).
5. Start the PEP: `python -m uvicorn IMPLEMENTATION.pep:app`.
6. Provide an HTTP intake endpoint outside the gate's process (a local receiver, or a
   third-party external receiver for the stronger observation).
7. Substitute the manifest SHA256 and the receiver URL into the request bodies in the "Test
   environment" section and re-issue the sequence.

The internal-consistency claim (Section 1) is reproducible by `python -m pytest TESTS/`
against the same commit. The external-interception claim (Section 2) requires an
out-of-process HTTP intake to verify the side-effect property; the architectural property
being demonstrated is that `requests.post()` in the PEP is reached only on the ELIGIBLE
branch of the decision logic. The signed-cross-host and root-recovery chains are
reproducible via the exit-coded runners under `EVIDENCE/proofs/`.

---

## Consistency Statement

The Elyon-Sol repository preserves the canon (v0.9.8.4) unchanged and documents
spec-to-code traceability at `docs/restructure/06_spec_to_code_traceability.md`. The current
canonical implementation, the verification ledger (`EVIDENCE/verification_ledger.md`), and
this addendum's measurement evidence reside in the current Elyon-Sol repository.

This publication reflects continuous system evolution. No change to the canonical model
(G(I) = AC³ ∧ T²⁶ ∧ CCS); the addition is updated, referent-bound enforcement evidence at
the named commit, superseding Revision 2's snapshot (`89ff2f9`, 2026-05-25).

---

## Provenance

| Field | Value |
|---|---|
| Canonical model | v0.9.8.4 (locked) |
| Implementation snapshot commit | `c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920` |
| Supersedes | Revision 2 (DOI `10.5281/zenodo.20387278`, snapshot `89ff2f9`, published 2026-05-25) |
