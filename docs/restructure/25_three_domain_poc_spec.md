# 25 — Three-Domain Synthetic POC Spec

Increment: VL-096 (artifact 13, demonstration tier). Build-then-wire: a new
proof under `EVIDENCE/proofs/three_domain_poc/`. The gate, evaluator,
envelope, verifier, and reference target are byte-unchanged; this increment
adds synthetic *content* and a runner that drives the existing chain, nothing
more. Per GR-3 every in-loop run here is **characterization, not
certification**: it shows the production chain decides domain-shaped inputs the
way a domain reviewer would expect; it does not move G5.

---

## 1. Purpose

Demonstrate the same admission chain across three unrelated decision domains —
**medical**, **legal**, **finance** — using synthetic-but-realistic inputs, so
that a reviewer who knows that domain (a clinician, an attorney, a trader/
compliance officer) can read each envelope and each verdict and trace *why* it
was admitted or refused, in their own vocabulary.

The POC answers one question per case: *given this domain interaction, what did
the production gate decide, what did the production executor do with the
resulting envelope, and is that the outcome a domain reviewer would demand?*

What this is NOT: a new policy engine, a new invariant, or an external
validation. The three domains differ only in (a) the manifest's required sets
`AR`/`R` and `version`, and (b) the free-form `context` (canon 11.1 C) and the
`AP`/`OP` strings. The decision logic is the one production evaluator/verifier.

---

## 2. What a domain is, mechanically

A domain is fully specified by:

- **A manifest** — `{version, interaction_type, AR, R}` written to
  `MANIFEST/manifest.json` (the single on-disk source the evaluator reads;
  `evaluator.manifest_integrity_valid` fails closed on any other manifest).
  `AR` is the required **authority** set; `R` is the required **operation**
  set. To be admissible an interaction's `AP ⊇ AR` (AC³) and `OP ⊇ R` (T²⁶),
  and its pinned `expected_manifest_version` / `expected_manifest_sha256` must
  equal the live manifest's version and on-disk sha256 (manifest-integrity).
- **A set of synthetic interactions** — each a normalized interaction
  `{AP, OP, context, expected_manifest_version, expected_manifest_sha256}`
  where `AP`/`OP` carry domain authority/operation tokens and `context` carries
  the domain payload (a patient order, a court filing, a trade) as legible
  fields plus a content digest the envelope binds to.

Because the gate evaluates the **on-disk** manifest, a domain run pins its
manifest first (in-process: swap the file under try/finally + restore; live:
the operator copies the manifest, republishes, restarts the gate). The three
domains therefore run **sequentially**, each against its own pinned manifest —
not three manifests live at once.

---

## 3. The case taxonomy (per domain)

Each domain runs the same case shape so the three reports are comparable. Each
case names its intended cause, the layer that should catch it, and the exact
expected outcome (a production reason code or a gate REFUSE with the failing
condition). A case PASSES when the actual outcome equals the expected one.

### Admitted (positive controls) — gate ELIGIBLE, executor honors
1. `admit_primary` — a fully-authorized domain action. Gate → ELIGIBLE;
   executor → honored (`REASSERTED_AND_BOUND`).
2. `admit_secondary` — a second legitimate action (different context, still
   admissible). Honored.
3. `admit_minimal_authority` — `AP` exactly equals `AR` (no surplus authority).
   Admissible (superset is reflexive). Honored.

### Refused at the GATE (evaluator REFUSE; the runner reports which condition)
4. `insufficient_authority` — `AP ⊉ AR` (a real-world under-privileged actor).
   AC³ fails → REFUSE.
5. `wrong_operation` — `OP ⊉ R` (the wrong verb for this action). T²⁶ fails →
   REFUSE.
6. `stale_policy_pin` — `expected_manifest_version` names a superseded policy.
   manifest-integrity fails → REFUSE.

### Refused at the EXECUTOR (verify_envelope / replay; production reason codes)
7. `unattested` — the action reaches the target with no envelope (adversary
   A1). → `REF_VERIFY_ENVELOPE_ABSENT`.
8. `forged_envelope` — a signed field of a genuine envelope is altered (e.g.
   the authorized dose/amount in the envelope is edited). The signature is
   checked first → `REF_VERIFY_SIGNATURE_INVALID`.
9. `replay` — the same admitted envelope is presented twice (a duplicate
   dispense / double-filing / double-execution). Second → `REF_VERIFY_REPLAY`.
10. `rebind_operation` — a genuine envelope admitted for operation X is
    presented for operation Y. Binding fails → `REF_VERIFY_BINDING_MISMATCH`.
11. `rebind_context` — a genuine, valid-signature envelope is presented against
    a *changed* live payload (dose/quantity/document altered after
    authorization). Signature verifies, reassert REASSERTED, binding fails →
    `REF_VERIFY_BINDING_MISMATCH`. (This is the case that distinguishes
    tamper-the-envelope (#8, signature) from change-the-call (#11, binding).)
12. `target_swap` — an envelope bound to target A is presented to target B. →
    `REF_VERIFY_BINDING_MISMATCH`.
13. `stale_decision` — an admitted envelope presented past its decision
    freshness window (`not_after`). → `REF_VERIFY_SIGNATURE_EXPIRED`.

Thirteen cases per domain, ≥10 as requested, spanning admit + every refusal
class the chain enforces. Forged (#8) vs rebind (#11) are kept distinct on
purpose: they are the two ways "the authorized thing changed" and they are
caught by two different defenses (signature vs binding).

---

## 4. The chain the runner drives (unchanged production code)

Admit (gate): POST `/governed-call` `{target_url, interaction}` to `pep.app`.
ELIGIBLE returns the signed envelope (`build_envelope` → `sign_envelope`, with
`not_after` and `decision_id`). REFUSE returns `{terminal_state: REFUSE}`.

For a gate REFUSE the runner additionally calls the three production condition
functions (`ac3_valid`, `t26_valid`, `manifest_integrity_valid`) on the
normalized interaction to report **which** admissibility condition failed — the
gate's HTTP body does not disclose this, but the functions are the same ones
`evaluate()` short-circuits on, so the diagnosis is faithful, not inferred.

Attempt (executor): the production `verify_envelope(envelope, interaction,
target_url, record_source=<record>, pinned_public_keys=<gate key>)` followed by
the `ReplayCache` exactly-once claim — i.e. the `ExecutorGate.check` sequence.
- In-process: `record_source=None` (local-disk currency; valid because the
  domain manifest is the live on-disk manifest during its run) and a per-run
  shared replay cache so #9 sees the first claim.
- Live: the deployed reference target over HTTP (signed-record currency via the
  publisher), exactly as the attack harness `HttpSurface` drives it.

No reason code is invented; every expected outcome is a production `REF_*` or a
gate REFUSE + a named failing condition.

---

## 5. Modes

The runner is surface-pluggable (mirroring `attack_harness.py`'s
InProcess/Http split):

- **`inproc`** (deterministic, hermetic, the self-verification + the artifact
  generator): drives `pep.app` via `TestClient` with an injected gate signing
  key and a mocked push-forward, and the executor via `verify_envelope` +
  replay cache. Swaps `MANIFEST/manifest.json` per domain under try/finally and
  restores it. Produces the three reviewer reports. This is what runs in the
  sandbox and what the committed reports are generated from.
- **`live`** (the author's referent-bound run): drives a real gate URL and a
  real reference-target URL over TLS. The operator pins each domain's manifest
  on the host, republishes, restarts the gate, runs the domain, collects the
  report. Honest ceiling per the project's live tier: two VMs, one host, a
  private network, a dev CA, the author's own calls — characterization over
  real transport, not external certification.

Both modes run the **same case set** and assert the **same expected outcomes**;
the only difference is the surface and the currency source. The runner exits
non-zero if any case's actual outcome ≠ expected (a self-check the author can
gate the live run on).

---

## 6. Deliverable

- `EVIDENCE/proofs/three_domain_poc/domains.py` — the three manifests + the
  case generators (the synthetic content; all data fictional, no real PHI/PII/
  account/bar numbers).
- `EVIDENCE/proofs/three_domain_poc/poc_runner.py` — the runner + report
  writer, both modes.
- `EVIDENCE/proofs/three_domain_poc/manifests/{medical,legal,finance}.json` —
  the manifest files (for the live host swap).
- `EVIDENCE/proofs/three_domain_poc/reports/{medical,legal,finance}_report.md`
  — the generated reviewer reports (from the in-process self-verify run).
- `EVIDENCE/proofs/three_domain_poc/RUNBOOK_live.md` — the per-domain
  live-drive procedure (manifest swap + republish + restart + run).

## 7. The reviewer report (per domain)

A human-readable Markdown report, one section per case, each showing: the case
name and plain-language intent; the **actor** (`AP`), the **operation**
(`OP`), the **payload** (`context`, the domain fields); the **gate decision**
(ELIGIBLE / REFUSE + failing condition); the **envelope** trace on admit
(decision_id, manifest version+sha, not_after, issuer key id, signature head,
decision_sha256); the **executor verdict** (honored / refused + reason); and a
one-line reviewer gloss in domain terms. A header block states the manifest
(version, sha, `AR`, `R`) and the synthetic-data disclaimer.

## 8. Honest ceiling (GR-3)

In-loop runs are characterization. Three domains do not add three validations —
they add breadth of *content* over one decision chain whose security properties
are exactly those already recorded (and unchanged). The only open road item
remains G5: a real external attacker on a real public surface. This increment
does not touch it.
