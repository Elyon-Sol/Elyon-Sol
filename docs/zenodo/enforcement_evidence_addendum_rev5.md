# Elyon-Sol v0.9.8.4 — Enforcement Evidence Addendum (Revision 5)

## Abstract

Elyon-Sol is a deterministic, fail-closed HTTP admission gate derived from a formal
admissibility specification. The canonical model is unchanged from v0.9.8.4:

**G(I) = AC³ ∧ T²⁶ ∧ CCS**

No new invariants are introduced and no canonical definitions are modified. This revision
supersedes Revision 4 (DOI 10.5281/zenodo.20740388) and **corrects its distribution
statement**: Revision 4 described the core as "released as open source" and "public"; the
source repository is in fact **private, with access granted on request**. The enforcement
evidence and the implementation snapshot are otherwise unchanged from Revision 4.

**Snapshot:** commit `c6b4094d3df6881a5b802072f9268c22e8fdf056`, observed on 2026-06-18.
All three canonical invariants are implemented and exercised in code at this commit.
Authority (AC³, canon sections 11.3 and 11.5) and Coverage (T²⁶, canon sections 11.4 and
11.6) are evaluated at the request layer. Continuity (CCS, canon sections 12 and 13) is
realized at the admissibility envelope layer: on every ELIGIBLE decision the gate
constructs a content-hashed envelope recording canon, manifest, evaluator, request, and
condition-result state at decision time, and supports reassertion of that envelope against
the live system state. A change in canon, manifest, or evaluator hash invalidates the prior
ELIGIBLE per canon section 12.4; continuity does not persist across transitions without
revalidation (canon section 13).

**Licensing and access (corrected in this revision).** The canonical model remains published
for citation. The core implementation is **AGPL-3.0 licensed (open-core)** — the admission
gate, the admissibility envelope, the target-side verifier, and the ext-authz sidecar; a
commercial license is available for uses that cannot accept AGPL's network-copyleft terms;
and a separate administration / tooling SDK is proprietary and distributed separately. The
**source repository is private; access is granted on request** — email `admin@elyon-sol.io`
or `justin@elyon-sol.io`. This document is licensed CC BY 4.0. (Note: AGPL-3.0 grants every
recipient the right to redistribute; access-on-request controls initial, not eventual,
visibility.)

The full repository test suite is **419 of 419 passing, 0 xfailed**, up from 211 at
Revision 3 and 84 at Revision 2. The growth is real work, not re-counting: it adds an
OPA/Envoy ext-authz sidecar and its adversarial suite, a request-body-derived interaction
binding, a multi-instance fail-closed replay guard, signed published-record freshness
wiring, clock-skew tolerance tests, an envelope inspector, an executor SDK, an issuance log,
and an MCP server surface (inventory in Section 1).

This is an evidence publication, not a canonical update. It reports development-side
(referent-bound) evidence — the test suite and the runnable proofs. It does **not** report
external, third-party adversarial validation on a real multi-host surface; that remains the
open finish line (see "Honest scope and open items" below).

---

## What changed since Revision 4

Revision 5 makes one correction and no code change: it restates the distribution posture as
**AGPL-3.0 licensed with the source repository private and access granted on request**,
replacing Revision 4's "released as open source / public and inspectable" wording. The
implementation snapshot, the test count, and all enforcement evidence are carried forward
from Revision 4 unchanged.

## Capabilities (built since Revision 3, carried forward)

Revision 3 reported a signed, enforced, multi-process gate with target-side verification,
mandatory issuer signing, key/root records with revocation and planned rotation, cross-host
record transport (loopback model), and a reference enforcing target. Built and exercised in
code since that snapshot:

- **OPA / Envoy ext-authz "eligibility sidecar" — built.** `IMPLEMENTATION/authz_sidecar.py`
  exposes the gate's admissibility decision as an Envoy `ext_authz` ALLOW/DENY authorization
  filter, so the eligibility check can sit in a filter chain ahead of a policy engine such as
  OPA (eligibility first, policy second; each independently fail-closed; neither imports the
  other). The sidecar **reuses the production verifier** — it does not re-implement
  cryptography or admission logic. Covered by `test_authz_sidecar.py` (18) and
  `test_authz_sidecar_freshness.py` (8).
- **Request-body-derived interaction binding — built.** `build_request_body_extractor`
  derives the interaction from the ext-authz request body so a decision binds to the exact
  executed bytes (`context.args_sha256`) when the sidecar is placed inline in front of a
  body-carrying upstream (with Envoy `with_request_body`). Covered by
  `test_authz_sidecar_body_binding.py` (10). The default header-read extractor is documented
  as standalone-decision-only.
- **Multi-instance replay hardening — built.** The replay cache supports a shared store
  (`ELYON_REPLAY_REDIS_URL`); with `ELYON_REPLAY_MULTI_INSTANCE=1` a missing shared store
  **fails closed at startup** rather than silently giving each process its own cache. Covered
  by `test_shared_replay_cache.py` (16).
- **Signed published-record freshness mode — built.** An optional signed-record freshness
  mode in the sidecar and its wiring tests (`test_record_freshness_wiring.py`, 5;
  `test_published_record_freshness.py`, 10).
- **Tooling exercised under test:** an envelope inspector
  (`test_envelope_inspector.py`, 52), an executor SDK (`test_executor_sdk.py`, 10), an
  issuance log (`test_issuance_log.py`, 10), an MCP server surface (`test_mcp_server.py`,
  14), and clock-skew tolerance (`test_clock_skew_tolerance.py`, 21).

The earlier Revision-3 capabilities (target-side verification, mandatory signing, key/root
records, cross-host transport, reference enforcing target, readiness instrument) remain in
place and under test.

---

## Enforcement Evidence

### Test environment

| Field | Value |
|---|---|
| Snapshot commit | `c6b4094d3df6881a5b802072f9268c22e8fdf056` |
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
419 passed
```

The 419-test suite (0 xfailed) by file:

| Test file | Count |
|---|---|
| `TESTS/adversarial/test_envelope_inspector.py` | 52 |
| `TESTS/adversarial/test_request_schema.py` | 28 |
| `TESTS/test_adversarial_evaluator.py` | 23 |
| `TESTS/adversarial/test_evaluator_canonical.py` | 23 |
| `TESTS/adversarial/test_clock_skew_tolerance.py` | 21 |
| `TESTS/adversarial/test_root_record.py` | 18 |
| `TESTS/adversarial/test_authz_sidecar.py` | 18 |
| `TESTS/adversarial/test_shared_replay_cache.py` | 16 |
| `TESTS/adversarial/test_key_record.py` | 15 |
| `TESTS/adversarial/test_mcp_server.py` | 14 |
| `TESTS/adversarial/test_reference_target.py` | 13 |
| `TESTS/adversarial/test_envelope.py` | 13 |
| `TESTS/adversarial/test_verifier.py` | 11 |
| `TESTS/adversarial/test_signing_expiry.py` | 11 |
| `TESTS/adversarial/test_signing.py` | 10 |
| `TESTS/adversarial/test_published_record_freshness.py` | 10 |
| `TESTS/adversarial/test_issuance_log.py` | 10 |
| `TESTS/adversarial/test_executor_sdk.py` | 10 |
| `TESTS/adversarial/test_authz_sidecar_body_binding.py` | 10 |
| `TESTS/adversarial/test_ccs_canonical.py` | 9 |
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
| `TESTS/deploy/test_bootstrap_config.py` | 4 |
| `TESTS/deploy/test_authz_sidecar_tls.py` | 4 |
| `TESTS/test_replay_receipts.py` | 3 |
| `TESTS/readiness/test_readiness.py` | 3 |
| `TESTS/readiness/test_deployment_predicates.py` | 3 |
| `TESTS/adversarial/test_publisher.py` | 2 |
| `TESTS/adversarial/test_decision_freshness.py` | 2 |
| `TESTS/adversarial/test_bypass.py` | 2 |
| **Total** | **419** |

### External interception (Section 2) — carried forward from Revision 3

The measured interception run below was performed at the **Revision 3** snapshot commit
`c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920` (2026-06-08) against `webhook.site`, a
third-party HTTP intake outside the gate's process. It is **carried forward unchanged**; no
new external interception run was performed for Revision 4 or Revision 5. The enforcement
code path it exercised is unchanged at this snapshot.

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

The observed pattern — 102 ELIGIBLE responses paired with exactly 102 external POSTs, and
102 REFUSE responses paired with exactly 0 external POSTs — exhibits the deterministic,
fail-closed enforcement property the canon specifies. Each ELIGIBLE forward carries a
gate-signed envelope.

---

## Honest scope and open items

This addendum reports **development-side, referent-bound** evidence: the test suite and the
runnable proofs. Per the repository's governance rule GR-3, a result is evidence only when
it is bound to a referent (execution, or an adversarial-by-construction artifact); model
judgments of soundness or value are not evidence. The following remain open and are **not**
claimed closed:

- **No external, third-party adversarial validation on a real multi-host public surface has
  been performed.** The interception run (Section 2) is author-driven third-party
  *observation* over local transport, not an external pen-test. The ext-authz sidecar's
  real-TLS evidence is a loopback handshake plus a scripted two-VM procedure, not an attacker
  external to the build. Real cross-host external red-team validation is the named G5 floor
  and the finish line.
- **A1 (the declining caller)** — a caller that does not route through the gate is closeable
  only by a target-side admission policy (built as the reference enforcing target), not by
  the gate itself.
- **Sidecar inline placement** — the default body extractor reads a client-controllable
  header and is for standalone-decision use only; inline placement requires the
  request-body-derived extractor plus Envoy `with_request_body`.
- **Record freshness** — a stale-but-anchor-matching, validly signed record is still honored
  unless the signed-record freshness mode is enabled.
- **Root-key compromise recovery** is irreducibly out-of-band; only planned rotation is
  built.

---

## Reproducibility

The full sequence is reproducible from the repository (AGPL-3.0 licensed; the repository is
private — request access at `admin@elyon-sol.io` or `justin@elyon-sol.io`) at the snapshot
commit:

1. Obtain repository access, then check out commit
   `c6b4094d3df6881a5b802072f9268c22e8fdf056`.
2. Verify the canon lock: `sha256sum -c CANON/canon.lock` against `CANON/canon.md`.
3. Run the suite: `python -m pytest -q` → `419 passed`.

The internal-consistency claim (Section 1) is reproducible by `python -m pytest` against the
same commit. The external-interception claim (Section 2) is the Revision-3 run, reproducible
via the procedure documented in Revision 3.

---

## Consistency Statement

The Elyon-Sol repository preserves the canon (v0.9.8.4) unchanged. No change to the
canonical model (G(I) = AC³ ∧ T²⁶ ∧ CCS). The change in this revision is a **distribution
correction**: the core is AGPL-3.0 licensed with the source repository private and access
granted on request, restating Revision 4's "open source / public" wording accurately. The
implementation snapshot and enforcement evidence are unchanged from Revision 4.

---

## Provenance

| Field | Value |
|---|---|
| Canonical model | v0.9.8.4 (locked) |
| Implementation snapshot commit | `c6b4094d3df6881a5b802072f9268c22e8fdf056` |
| Core license | AGPL-3.0 (open-core); commercial license available; admin SDK proprietary |
| Source repository | private; access on request (`admin@elyon-sol.io` / `justin@elyon-sol.io`) |
| Document license | CC BY 4.0 |
| Supersedes | Revision 4 (DOI `10.5281/zenodo.20740388`, published 2026-06-18) — corrects the distribution statement from "open source / public" to "AGPL-3.0 licensed; access on request" |
| Author | Justin Laporte (ORCID 0009-0008-3785-3089) |
