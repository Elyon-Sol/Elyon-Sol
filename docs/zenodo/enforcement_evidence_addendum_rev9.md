# Elyon-Sol v0.9.8.4 — Enforcement Evidence Addendum (Revision 9)

## Abstract

Elyon-Sol is a deterministic, fail-closed HTTP admission gate derived from a formal
admissibility specification. The canonical model is unchanged from v0.9.8.4:

**G(I) = AC³ ∧ T²⁶ ∧ CCS**

Here **AC³** and **T²⁶** are the two per-request admission checks — set-containment of the
caller's authority and operation sets against the SHA-256-pinned manifest (AP ⊇ AR and OP ⊇ R) —
and **CCS** is the continuity property. Per the canon (§3), the superscripts are nominal labels
from the original Elyon-Sol notation, not mathematical exponents. No new conditions are introduced
and no canonical definitions are modified. This revision supersedes Revision 8 (DOI
10.5281/zenodo.21364720) and **advances the implementation snapshot**. It is a
**correction-and-evidence revision**: it corrects four statements in Revision 8 that are no longer
true and re-measures the enforcement evidence at a new snapshot. It does not report an advance in
the admissibility model.

**Snapshot:** commit `2d5c6bf6c97edacc12748e6186b6ccf4eb853115`, observed 2026-10-08. Pinned
hashes at this snapshot: canon `d1c9d187` (unchanged), manifest `ac18ac78` (unchanged), evaluator
`ca7c922c` (**changed** from `e307fab2` — see "Consistency Statement"). The canon lock and the
manifest are byte-identical to Revision 8.

**What Revision 8 states that is no longer true, corrected here.** (1) *Licensing:* the core and
the companion operator console are AGPL-3.0 with no commercial, proprietary, or dual-licensed
components; Revision 8's "open-core / proprietary tooling SDK" description was withdrawn on
2026-07-26. (2) *The live surface:* the four public test nodes were retired on 2026-07-20, six days
after Revision 8; there is no live public surface, and nothing in this revision was measured on one.
(3) *The evaluator pin:* the SHA-pinned evaluator moved at VL-150 (refusal reason codes, see below);
a verifier comparing a current envelope against Revision 8's record sees an evaluator mismatch.
(4) *The test suite:* **689** tests (up from 616).

**Licensing and access.** The canonical model remains published for citation. The core
implementation, and the companion operator console GLESAC, are licensed under AGPL-3.0; there are
no commercial, proprietary, or dual-licensed components (see `LICENSING.md` in the repository).
Source public at https://github.com/Elyon-Sol/Elyon-Sol. This document is licensed CC BY 4.0.

This is an evidence publication, not a canonical update. It reports development-side
(referent-bound) evidence — the test suite, the runnable proofs, an enforcement census **re-run at
this revision's snapshot commit** with a now-committed hermetic harness (Section 2), and the live
attack suite and governance approval path executed against a real multi-container stack on one host
(Section 3). It does **not** report external, third-party adversarial validation on a real
multi-host surface, and it does **not** claim any guarantee as deployment-certified; both remain
open (see "Honest scope and open items").

---

## What changed since Revision 8

Ledger entries VL-147 … VL-155, 55 commits, range `61ad782..2d5c6bf`. Grouped:

**(1) Refusal reason codes (VL-150).** `evaluator.decide()` names which condition refused with a
disjoint `G_` vocabulary (`G_MANIFEST_MALFORMED`, `G_REQUIRED_SETS_UNRESOLVED`, `G_AC3`, `G_T26`,
`G_MANIFEST_INTEGRITY`, `G_INTERNAL`), surfaced in the gate's 403 as `refusal_reason_code`.
No admissibility decision changed; `evaluate()` is a byte-behavior-identical projection. **This is
the change that moved `evaluator_sha256`** (`e307fab2` → `ca7c922c`); `EVIDENCE/published_hashes.json`
was regenerated through its generator, and `canon_sha256`, `evaluator_version` (0.9.8.4) and
`manifest_sha256` are unchanged.

**(2) Governance substrate completed and proven under containers (VL-148, VL-152, VL-153).** The
gate resolves approver trust in-process from the pinned-root signed key-record chain, by explicit
`approver` role (SES-9b). A deployment manifest and compose overlay run the human-approval path
across two gate replicas with a shared Redis store and an mTLS target: a direct call that bypasses
the gate is refused at TLS; an unapproved high-impact call is held `202 PENDING_APPROVAL` with the
target never called; a grant minted by the separate approver container at the other replica
releases it exactly once; a replayed grant is refused on both replicas; the issuance and approval
logs reconcile clean. Repeated at the parent of this snapshot (VL-155).

**(3) Twelve admission fixes, each pinned by a revert-proven test (VL-154, VL-155).** A white-box
review of every path that honors a token found four breaks (an approver-role key could sign
envelopes in key-record mode; the sidecar decided Envoy-forwarded requests from a client header;
the SDK's single-use claim expired inside the clock-skew window; the gate's forward followed
redirects past the SSRF guard) and named eight more, all now closed: the forward connects to the
address the guard vetted (DNS pinning, with SNI and certificate verification still on the name);
the SDK refuses an envelope without a `decision_id` and can never reach the verifier's unsigned
path; root-record validity windows are enforced at the cross-record gate (new code
`REF_VERIFY_ROOT_OUT_OF_WINDOW`); approval holds carry a TTL; the guard blocks everything not
globally routable and the allowlist matches origins rather than hostnames; the generated secrets
file is owner-only; the sidecar's decision port is loopback-only and OPA's port unpublished; every
container image is pinned by digest. Each test was run against the pre-fix blob of the file it
guards and failed there. New verifier code: `REF_VERIFY_KEY_ROLE_NOT_ISSUER`.

**(4) Reproducibility.** A self-host compose stack replaces the retired live surface
(`deploy/SPIN_UP_YOUR_OWN.md`); the development environment, CI and the image share Python 3.14
and pinned requirements; the local-receiver census harness is committed (Section 2).

**(5) Direction.** A domain-semantic validity layer above G(I) was built and withdrawn within one
day in July 2026; no residue remains in code. The two design documents record the attempt and the
bypass it produced. The forward direction is depth on the existing surfaces.

**Suite.** 616 → 689 (+73): two new test files and additions across 21 existing ones.

---

## Enforcement Evidence

### Test environment

Full repository test suite at commit `2d5c6bf`, Python 3.14.4 / pytest 9.1.1 on Linux.
**689 passed.** The suite is network-free by construction. The runnable proofs are 22 exit-coded
runners under `EVIDENCE/proofs/`; 19 run in CI on every push (the third-party webhook runner, the
author-live runner and the loopback-TLS sidecar runner are excluded there), and all 20 hermetic
runners pass locally at the parent commit `918f6f5`, which differs from this snapshot only by the
addition of the census harness in Section 2.

### Internal consistency (Section 1)

Canon `d1c9d187` and manifest `ac18ac78` are byte-identical to Revision 8; `CANON/canon.lock` is
byte-identical. The evaluator pin is `ca7c922c`. The verify-against-pinned tests pass at this
snapshot against the regenerated record, so the published record, the evaluator on disk and the
canon lock agree.

### Enforcement census (Section 2) — RE-RUN at this snapshot, hermetic harness

The census exercises the gate's fail-closed enforcement property: REFUSE produces zero external
side effects; ELIGIBLE produces exactly one external execution. Revision 8 measured it with a
loopback receiver but named no committed harness for that variant. This revision commits one,
`EVIDENCE/proofs/enforcement_census_local_001_runner.py`: the gate runs as a subprocess with an
ephemeral Ed25519 signing key; the receiver is an HTTP server in the runner's own process on a free
loopback port, counting every POST and checking that each carries a signed envelope with a distinct
`decision_id`; the call pattern is the webhook runner's, verbatim.

| Metric | Value |
|---|---|
| Snapshot commit | `2d5c6bf` |
| Manifest SHA-256 | `ac18ac78` |
| Total HTTP calls | 204 |
| REFUSE calls (expected 403) | 102 |
| REFUSE returning 403 | 102 |
| ELIGIBLE calls (expected 200) | 102 |
| ELIGIBLE returning 200 | 102 |
| Unexpected HTTP outcomes | 0 |
| External POSTs observed (loopback receiver) | 102 |
| External POSTs carrying a signed envelope | 102 |
| Distinct `decision_id` values among them | 102 |
| External POSTs from REFUSE calls | 0 |
| Duplicate external executions | 0 |

**Receiver note.** As at Revision 8, the receiver is a separate local process, not an off-host
third party, and the gate runs with the documented dev/test opt-out `ELYON_ALLOW_PRIVATE_TARGETS=1`
so the loopback target passes the SSRF guard (the guard's blocking is covered by its own tests).
**The third-party receiver leg was not re-run at this snapshot.** Revision 8's run at `61ad782`
(2026-07-14, inbox delta +102, 0 errors) stands as the last third-party confirmation of the forward
count. The committed webhook runner is unchanged since Revision 8, including the stale baseline
offset Revision 8 noted.

### Live attack suite and governance path against a real stack (Section 3)

At the parent commit `918f6f5` (same code as this snapshot apart from the census harness), the
compose stack was rebuilt from the tree and driven in three configurations on one host. The
results are recorded in ledger entry VL-155; the figures are:

| Referent | Result |
|---|---|
| `attack_suite_live_runner.py`, base stack over HTTP | positive control honored; 6/6 adversarial attacks defeated; exit 0 |
| `attack_suite_live_runner.py`, TLS overlay over HTTPS (dev CA) | positive control honored; 6/6 defeated; exit 0 |
| Walkthrough (`deploy/BREAK_IT_IN_60_SECONDS.md`), verbatim | control executed once; four target attacks refused with the documented codes; sidecar ALLOW on the control, DENY on forged, replayed and rebound tokens |
| Governance legs A–D (two replicas, Redis, mTLS target) | A refused at TLS; B held 202, target not called; C released once at the other replica; D replay refused on both; `reconcile_approvals` clean |
| Separation of duties | gate-key self-approval refused under its own id, another id, and the approver's id |
| Target side-effect counter | moved only on genuine mints |

These are author-side executions on one machine; they are not external validation.

---

## Honest scope and open items

Development-side, referent-bound evidence only. The following remain open and are **not** claimed
closed:

- **No external, third-party adversarial validation on a real multi-host public surface has been
  performed.** There has been no live public surface since 2026-07-20, so this cannot advance until
  one exists again. It remains the named G5 floor and the finish line.
- **All Section 3 evidence is single-host.** Custody separation (gate, approver, publisher) was by
  container and process, not by host.
- **The third-party census leg was not re-run** (see Section 2).
- **No guarantee is claimed as deployment-certified.**
- **Deployment-visible change:** an allowlist entry that is a bare hostname now admits that host on
  the scheme's default port only; a target on a non-default port must be written as `host:port` or
  a full origin.
- Named open in the repository, non-blocking: the TLS certificate generator writes private-key
  files under the process umask; the Envoy example uses a deprecated `ext_authz` field that the
  image pin keeps valid until the pin is next refreshed; the approval-hold TTL expiry is proven by
  test, not observed live.

---

## Reproducibility

From repository root at commit `2d5c6bf`, with the pinned dependencies (`requirements-dev.txt`,
Python 3.14):

```
# Full suite (689 tests)
PYTHONPATH=. python -m pytest TESTS/ -q

# Enforcement census, local-receiver variant (Section 2); exit 0 iff all expected
PYTHONPATH=. python EVIDENCE/proofs/enforcement_census_local_001_runner.py

# Every hermetic proof runner, as CI runs them
for r in EVIDENCE/proofs/*_runner.py; do PYTHONPATH=. ELYON_ALLOW_PRIVATE_TARGETS=1 python "$r"; done

# Section 3 against a stack you run yourself (see deploy/SPIN_UP_YOUR_OWN.md)
cd deploy && python bootstrap_config.py && docker compose up --build -d && cd ..
ELYON_LIVE_GATE_URL=http://localhost:8000 ELYON_LIVE_TARGET_URL=http://localhost:9000 \
ELYON_LIVE_TARGET_ID=http://target:9000/target \
PYTHONPATH=. python EVIDENCE/proofs/attack_suite_live_runner.py
```

The third-party (`webhook.site`) variant, `EVIDENCE/proofs/external_interception_webhook_001_runner.py`,
is unchanged from Revision 8 and was not run for this revision.

---

## Consistency Statement

The canonical model (v0.9.8.4) is unchanged; `CANON/canon.lock` and `MANIFEST/manifest.json` are
byte-identical to Revision 8 (canon `d1c9d187` / manifest `ac18ac78`). The SHA-pinned evaluator is
**not** byte-identical to Revision 8: it moved once, at VL-150, to carry refusal reason codes, with
no change to any admissibility decision, and the published record was regenerated through its
generator so the pin, the record and the verify-against-pinned tests agree. Every other change in
this revision layers above the pin. The enforcement census in Section 2 was measured at this
revision's snapshot commit with a committed, hermetic harness.

## Provenance

Snapshot commit `2d5c6bf6c97edacc12748e6186b6ccf4eb853115`, observed 2026-10-08. Supersedes
Revision 8 (DOI 10.5281/zenodo.21364720); concept DOI 10.5281/zenodo.19367848. Source public
(AGPL-3.0) at https://github.com/Elyon-Sol/Elyon-Sol. Ledger entries VL-147 … VL-155; the
Section 3 executions are VL-155's referents.

Enforcement census (Section 2) executed at this commit on 2026-10-08 with
`enforcement_census_local_001_runner.py`: 204 / 102→403 / 102→200 / 0 unexpected / 102 forwards,
each a signed envelope with a distinct `decision_id`, 0 from REFUSE. No third-party receiver run.

---

### Additional notes (for the Zenodo record)
Revision 9 — correction-and-evidence revision. Corrects Revision 8 on licensing (AGPL-3.0 only; no
commercial, proprietary or dual-licensed components), on the live surface (retired 2026-07-20; no
live public surface exists), on the evaluator pin (`ca7c922c` since VL-150, refusal reason codes;
canon and manifest unchanged) and on the test count (689). Twelve admission fixes since Revision 8,
each pinned by a revert-proven test; the governance approval path proven across two replicas under
containers; the enforcement census re-run at the snapshot commit with a committed hermetic harness
(204 / 102 / 102 / 0 unexpected / 102 forwards, 0 from REFUSE); the live attack suite 6/6 over HTTP
and over TLS against a self-hosted stack. Supersedes Revision 8 (DOI 10.5281/zenodo.21364720).
Canonical model (v0.9.8.4) unchanged. Honest scope retained: author-side / white-box / single
host; the third-party census leg not re-run; no external multi-host adversarial validation.
