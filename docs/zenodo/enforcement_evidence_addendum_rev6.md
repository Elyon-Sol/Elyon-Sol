# Elyon-Sol v0.9.8.4 — Enforcement Evidence Addendum (Revision 6)

## Abstract

Elyon-Sol is a deterministic, fail-closed HTTP admission gate derived from a formal
admissibility specification. The canonical model is unchanged from v0.9.8.4:

**G(I) = AC³ ∧ T²⁶ ∧ CCS**

No new invariants are introduced and no canonical definitions are modified. This revision
supersedes Revision 5 (DOI 10.5281/zenodo.20751592) and **advances the implementation
snapshot**: it adds a governance / human-oversight layer above the admissibility core, together
with its provenance, scaling, transport, and deployment-wiring hardening, and its independent
three-model white-box review. Revision 5's distribution correction — the core is AGPL-3.0
licensed with the source repository **private, access granted on request** — is carried forward
unchanged.

**Snapshot:** commit `9645fb82236131ce686d22c2dfed1416d54c252d`, observed on 2026-06-18. All
three canonical invariants are implemented and exercised in code at this commit. Authority
(AC³, canon sections 11.3 and 11.5) and Coverage (T²⁶, canon sections 11.4 and 11.6) are
evaluated at the request layer. Continuity (CCS, canon sections 12 and 13) is realized at the
admissibility envelope layer: on every ELIGIBLE decision the gate constructs a content-hashed
envelope recording canon, manifest, evaluator, request, and condition-result state at decision
time, and supports reassertion of that envelope against the live system state. A change in
canon, manifest, or evaluator hash invalidates the prior ELIGIBLE per canon section 12.4;
continuity does not persist across transitions without revalidation (canon section 13).

**Licensing and access (carried from Revision 5).** The canonical model remains published for
citation. The core implementation is **AGPL-3.0 licensed (open-core)** — the admission gate, the
admissibility envelope, the target-side verifier, and the ext-authz sidecar; a commercial
license is available for uses that cannot accept AGPL's network-copyleft terms; and a separate
administration / tooling SDK is proprietary and distributed separately. The **source repository
is private; access is granted on request** — email `admin@elyon-sol.io` or
`justin@elyon-sol.io`. This document is licensed CC BY 4.0. (AGPL-3.0 grants every recipient the
right to redistribute; access-on-request controls initial, not eventual, visibility.)

The full repository test suite is **512 of 512 passing, 0 xfailed**, up from 419 at Revision 5
and 211 at Revision 3. The growth is real work, not re-counting: it adds the governance /
human-oversight layer and its supporting machinery (inventory in Section 1).

This is an evidence publication, not a canonical update. It reports development-side
(referent-bound) evidence — the test suite and the runnable proofs. It does **not** report
external, third-party adversarial validation on a real multi-host surface, and it does **not**
claim the human-oversight guarantee as deployment-certified; both remain open (see "Honest scope
and open items").

---

## What changed since Revision 5

Revision 5 corrected the distribution statement (private, access on request) at the 419-test
snapshot. Revision 6 carries that correction forward unchanged and advances the implementation
snapshot to add a **governance / human-oversight layer** above the admissibility core, plus its
provenance, scaling, transport, and wiring hardening. No canonical definition changes; the new
machinery layers **above** the SHA-pinned evaluator core (G(I)), leaving the pinned evaluator
byte-identical.

## Capabilities (built since Revision 5)

- **Human-in-the-loop approval (Feature 1) — built.** When the SHA-pinned manifest classifies an
  admitted interaction as **high-impact**, the gate **holds** it (a `202 PENDING_APPROVAL`
  terminal state) instead of forwarding, and emits an approval-request id. A human approver, in a
  separate process holding a **separate private key never resolvable by the gate**, signs an
  **approval grant**. The gate verifies the grant — bound to the exact decision (`decision_sha256`,
  which transitively binds target, authority/operation sets, context, and the manifest pins),
  separated in duty from the gate, fresh (its own expiry), and carrying a mandatory single-use id
  — then **consumes it exactly once before** forwarding. No code path forwards a high-impact call
  without a valid, fresh, single-use grant. Covered by `test_requires_approval.py` (10),
  `test_approval.py` (14), `test_pep_approval.py` (9), and `test_approval_audit.py` (9).
- **Approver provenance + role (R1) — built.** The public keys the gate trusts as approvers flow
  through the **signed key-record chain** with an explicit **`approver` role distinct from
  `issuer`**; separation of duties is enforced as **role-distinctness in the signed record**, not
  a key-identifier string comparison, so a gate-controlled key under a different identifier is
  structurally excluded. Covered by `test_approver_trust.py` (15).
- **Shared-store hardening for horizontal scale (R2) — built.** Grant single-use and the pending
  202 slot hold **across instances** with a shared store; a gate that declares itself
  horizontally scaled without one **fails closed at startup** rather than handing each replica a
  per-process cache. Covered by `test_pending_store.py` (18) and the prior
  `test_shared_replay_cache.py` (16).
- **Non-bypass transport proof (Feature 2, mutual-TLS) — built.** A mutual-TLS client-auth proof
  shows that a direct connection to the target **without the gate's client certificate is refused
  at the TLS handshake** (before any application logic), while a one-way-TLS contrast would accept
  it — so mutual-TLS is the layer that closes the off-gate-caller path within the operator's
  network boundary. Covered by `test_mtls_required.py` (4).
- **Integration proof + deployment-wiring guard — built.** An in-process proof composes the
  oversight and non-bypass mechanisms (`test_governance_integration.py`, 1), and a fail-closed
  **startup wiring guard** refuses a high-impact deployment that is not wired for safe oversight
  (`test_governance_wiring.py`, 13).

The Revision-5 capabilities (ext-authz sidecar, request-body binding, multi-instance replay
guard, signed published-record freshness, envelope inspector, executor SDK, issuance log, MCP
server, key/root records, mandatory signing, cross-host transport, reference enforcing target)
remain in place and under test.

---

## Enforcement Evidence

### Test environment

| Field | Value |
|---|---|
| Snapshot commit | `9645fb82236131ce686d22c2dfed1416d54c252d` |
| Canon version | v0.9.8.4 (locked; SHA256-pinned at `CANON/canon.lock`) |
| Canon SHA256 | `d1c9d187953eed8145c2d67a98e052415ca2a4c8b722a8011280e21502b4d7bd` |
| Date of observation | 2026-06-18 |
| Suite command | `python -m pytest -q` |
| Repository | private; AGPL-3.0 licensed; access on request (`admin@elyon-sol.io` / `justin@elyon-sol.io`) |

### Internal consistency (Section 1)

Full repository test suite at the snapshot commit:

```
$ python -m pytest -q
...
512 passed
```

The 512-test suite (0 xfailed) by file (governance-layer additions since Revision 5 in **bold**):

| Test file | Count |
|---|---|
| `TESTS/adversarial/test_envelope_inspector.py` | 52 |
| `TESTS/adversarial/test_request_schema.py` | 28 |
| `TESTS/test_adversarial_evaluator.py` | 23 |
| `TESTS/adversarial/test_evaluator_canonical.py` | 23 |
| `TESTS/adversarial/test_clock_skew_tolerance.py` | 21 |
| `TESTS/adversarial/test_root_record.py` | 18 |
| **`TESTS/adversarial/test_pending_store.py`** | **18** |
| `TESTS/adversarial/test_authz_sidecar.py` | 18 |
| `TESTS/adversarial/test_shared_replay_cache.py` | 16 |
| `TESTS/adversarial/test_key_record.py` | 15 |
| **`TESTS/adversarial/test_approver_trust.py`** | **15** |
| `TESTS/adversarial/test_mcp_server.py` | 14 |
| **`TESTS/adversarial/test_approval.py`** | **14** |
| `TESTS/adversarial/test_reference_target.py` | 13 |
| **`TESTS/adversarial/test_governance_wiring.py`** | **13** |
| `TESTS/adversarial/test_envelope.py` | 13 |
| `TESTS/adversarial/test_verifier.py` | 11 |
| `TESTS/adversarial/test_signing_expiry.py` | 11 |
| `TESTS/adversarial/test_signing.py` | 10 |
| **`TESTS/adversarial/test_requires_approval.py`** | **10** |
| `TESTS/adversarial/test_published_record_freshness.py` | 10 |
| `TESTS/adversarial/test_issuance_log.py` | 10 |
| `TESTS/adversarial/test_executor_sdk.py` | 10 |
| `TESTS/adversarial/test_authz_sidecar_body_binding.py` | 10 |
| **`TESTS/test_pep_approval.py`** | **9** |
| `TESTS/adversarial/test_ccs_canonical.py` | 9 |
| **`TESTS/adversarial/test_approval_audit.py`** | **9** |
| `TESTS/adversarial/test_cross_host.py` | 8 |
| `TESTS/adversarial/test_authz_sidecar_freshness.py` | 8 |
| `TESTS/test_pep.py` | 7 |
| `TESTS/adversarial/test_enforcement.py` | 7 |
| `TESTS/deploy/test_tls_certs.py` | 6 |
| `TESTS/adversarial/test_findings_002.py` | 6 |
| `TESTS/adversarial/test_record_freshness_wiring.py` | 5 |
| `TESTS/adversarial/test_findings_001.py` | 5 |
| `TESTS/adversarial/test_attack_harness.py` | 5 |
| `TESTS/test_concurrency.py` | 4 |
| **`TESTS/deploy/test_mtls_required.py`** | **4** |
| `TESTS/deploy/test_bootstrap_config.py` | 4 |
| `TESTS/deploy/test_authz_sidecar_tls.py` | 4 |
| `TESTS/test_replay_receipts.py` | 3 |
| `TESTS/readiness/test_readiness.py` | 3 |
| `TESTS/readiness/test_deployment_predicates.py` | 3 |
| `TESTS/adversarial/test_publisher.py` | 2 |
| `TESTS/adversarial/test_decision_freshness.py` | 2 |
| `TESTS/adversarial/test_bypass.py` | 2 |
| **`TESTS/test_governance_integration.py`** | **1** |
| **Total** | **512** |

The nine governance-layer files added since Revision 5 contribute 93 tests
(10+14+9+15+18+13+9+1+4); the remaining 419 are carried forward unchanged.

### External interception (Section 2) — carried forward from Revision 3

The measured interception run below was performed at the **Revision 3** snapshot commit
`c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920` (2026-06-08) against `webhook.site`, a third-party
HTTP intake outside the gate's process. It is **carried forward unchanged**; no new external
interception run was performed for Revisions 4–6. The enforcement code path it exercised
(admit → sign → forward) is unchanged at this snapshot; the governance layer adds a hold/approval
stage *above* it without altering the default forward.

| Metric | Value |
|---|---|
| Total HTTP calls | 204 |
| REFUSE calls (expected 403) | 102 |
| REFUSE returning 403 | 102 |
| ELIGIBLE calls (expected 200) | 102 |
| ELIGIBLE returning 200 | 102 |
| Unexpected HTTP outcomes | 0 |
| External POSTs observed | 102 |
| External POSTs from REFUSE calls | 0 |
| External POSTs from ELIGIBLE calls | 102 |
| Duplicate external executions | 0 |

---

## Honest scope and open items

This addendum reports **development-side, referent-bound** evidence: the test suite and the
runnable proofs. Per the repository's governance rule GR-3, a result is evidence only when it is
bound to a referent (execution, or an adversarial-by-construction artifact); model judgments of
soundness or value are not evidence. The following remain open and are **not** claimed closed:

- **The human-oversight guarantee is built and tested in-repo, NOT deployment-certified.** The
  approval mechanism, its provenance, single-use, and audit are exercised in code, and an
  in-process proof shows they compose with the mutual-TLS non-bypass layer. The end-to-end
  guarantee — that the only path to a high-impact execution is through the gate AND with a human
  grant — is claimable only inside a deployment that wires all of the operator-controlled
  non-bypass layers (inline body binding via Envoy `with_request_body`, mutual-TLS client auth,
  and network/egress isolation) together with a shared single-use store. That deployment is the
  operator's to stand up and is not certified here.
- **No external, third-party adversarial validation on a real multi-host public surface has been
  performed.** The interception run (Section 2) is author-driven third-party *observation* over
  local transport, not an external pen-test. Real cross-host external red-team validation is the
  named G5 floor and the finish line.
- **The governance layer's adversarial review is in-repo / white-box** (independent three-model
  runs over the full source). It found no exploitable defect on a correctly-wired single-process
  gate and converged on deployment-posture hardening items (since addressed or scheduled). This
  is internal convergence evidence, not an external attacker.
- **A1 (the declining caller)** — a caller that does not route through the gate is closeable only
  by a target-side admission policy plus network isolation, not by the gate alone.
- **Sidecar inline placement, record freshness, root-key compromise recovery** — carried forward
  from Revision 5 unchanged.

---

## Reproducibility

The full sequence is reproducible from the repository (AGPL-3.0 licensed; private — request
access at `admin@elyon-sol.io` or `justin@elyon-sol.io`) at the snapshot commit:

1. Obtain repository access, then check out commit
   `9645fb82236131ce686d22c2dfed1416d54c252d`.
2. Verify the canon lock: `sha256sum -c CANON/canon.lock` against `CANON/canon.md`.
3. Run the suite: `python -m pytest -q` → `512 passed`.

The internal-consistency claim (Section 1) is reproducible by `python -m pytest` against the
same commit. The external-interception claim (Section 2) is the Revision-3 run, reproducible via
the procedure documented in Revision 3.

---

## Consistency Statement

The Elyon-Sol repository preserves the canon (v0.9.8.4) unchanged. No change to the canonical
model (G(I) = AC³ ∧ T²⁶ ∧ CCS). This revision advances the implementation snapshot to add a
governance / human-oversight layer **above** the SHA-pinned evaluator core, leaving the pinned
evaluator byte-identical; it carries Revision 5's distribution correction forward. The
implementation snapshot and the enforcement evidence are as stated for commit
`9645fb82236131ce686d22c2dfed1416d54c252d`.

---

## Provenance

| Field | Value |
|---|---|
| Canonical model | v0.9.8.4 (locked) |
| Implementation snapshot commit | `9645fb82236131ce686d22c2dfed1416d54c252d` |
| Core license | AGPL-3.0 (open-core); commercial license available; admin SDK proprietary |
| Source repository | private; access on request (`admin@elyon-sol.io` / `justin@elyon-sol.io`) |
| Document license | CC BY 4.0 |
| Supersedes | Revision 5 (DOI `10.5281/zenodo.20751592`, record https://zenodo.org/records/20751592) — advances the snapshot to add the governance / human-oversight layer; carries the distribution correction forward |
| Author | Justin Laporte (ORCID 0009-0008-3785-3089) |
