# Elyon-Sol — Runtime Governance Regulatory Alignment Map

> **Not a compliance or conformity claim.** This document maps Elyon-Sol's *technical
> mechanisms* to the intent of the cited frameworks. It is not a statement of legal
> compliance, certification, or conformity assessment under ISO/IEC 42001, the EU AI Act,
> NSA/CISA/ASD guidance, or any other instrument. Compliance is a property of an
> organization's complete system and deployment, determined through formal conformity
> assessment — not a property of this software. "ATTAINED" here means only that a concrete
> mechanism exists in the code.

Maps the 14 rows of the "Regulatory & Standards Convergence Toward
Runtime Governance" table (ISO/IEC 42001, EU AI Act, NSA/CISA/ASD
guidance) to where and how Elyon-Sol's mechanisms align with each
requirement — or do not.

**Scope note.** Elyon-Sol is an *admissibility / authorization
substrate*: a deterministic, fail-closed, pre-execution HTTP admission
boundary (`pep.py`) backed by a centralized evaluator (`evaluator.py`)
and a content-hashed, signed decision record (`envelope.py`). It governs
**whether an action is admitted, bound, and recorded** at runtime. It is
not a model-internal safety layer and makes no claim about a model's
reasoning. Adherence below is for the *runtime governance* control
family — exactly what the image is about.

Two cross-cutting caveats apply to every "ATTAINED" below:

- **G4 — opt-in, not non-bypassable.** A caller can hit the target
  directly and skip the gate (`docs/restructure/04_current_vs_claimed.md`
  G4; README "Known limitations"). Enforcement holds only for traffic
  routed through the PEP / `authz_sidecar`. "Every request" / "non-
  bypassable" framing is aspirational until network-level mandatory
  routing is added.
- **No human-in-the-loop.** Every decision is automated
  (`ELIGIBLE`/`REFUSE`). There is no approval, escalation, or
  intervention surface anywhere in `IMPLEMENTATION/`. This is the single
  largest compliance gap (see EU AI Act Art 14, NSA "human approval").

Legend: **ATTAINED** (concrete mechanism in code) · **PARTIAL**
(mechanism present but narrower than the requirement) · **GAP** (no
implementation).

---

## ISO/IEC 42001

| § | Requirement | Status | Where / how |
|---|---|---|---|
| 8.1 | Operational planning & control — controls operate during execution | **ATTAINED** | `pep.py /governed-call` runs schema-validate → `evaluate()` → envelope → forward *before* the upstream is ever called; any exception is fail-closed `REFUSE`. Control is exercised at execution time, not at design time. |
| 8.2 | Ongoing AI risk assessment — per-action, per-context | **PARTIAL** | Evaluation re-runs on every request (`evaluator.evaluate`), and `context.args_sha256` binds the decision to the exact bytes executed (`authz_sidecar.build_request_body_extractor`). It is genuinely per-action/per-context, but the "assessment" is admissibility (authority/coverage/integrity), not a risk-scoring model. |
| 8.3 | AI risk treatment — enforcement, not just documentation | **ATTAINED** | Failure is *enforced*: `evaluate()` returns `REFUSE` → HTTP 403, upstream not called; "no fallback execution," "no retries" (README Guarantees). Treatment is a mechanism, not a policy document. |
| 9.1 | Monitoring, measurement, analysis & evaluation | **PARTIAL** | Issuance is logged one canonical JSONL line per signed `ELIGIBLE` (`issuance_log.py`); `reference_target.py /received` gives target-side observability; `envelope_inspector reconcile --issued/--executed` reconciles issued vs. executed. Continuous *behavioral* analytics / dashboards are not built. |
| Intro | AI systems change behavior during use → runtime drift detection & adaptive oversight | **PARTIAL** | `envelope.reassert()` invalidates a prior `ELIGIBLE` the moment canon, manifest, or evaluator hash changes (canon §12.4); decision freshness (`not_after`, default 300 s) bounds how long a decision is honored. This detects drift in the *governance state*, not drift in model behavior. |

## EU AI Act

| Article | Requirement | Status | Where / how |
|---|---|---|---|
| 14 | Effective human oversight — approval workflows, escalation, intervention | **GAP** | No human-in-the-loop anywhere in `IMPLEMENTATION/`. Decisions are fully automated. The fail-closed `REFUSE` is an automated stop, not human oversight. Closing this needs an approval/escalation surface (e.g. a "pending human decision" terminal state in `pep.py`). |
| 12 | Logging & traceability — action-level evidence | **ATTAINED** | Each `ELIGIBLE` yields a content-hashed, Ed25519-signed envelope with `decision_sha256` + unique `decision_id`, appended to an append-only issuance log (`envelope.py`, `issuance_log.py`). Records are reproducible and externally verifiable (`verifier.verify_envelope`, `envelope_inspector`). |
| 15 | Accuracy, robustness & cybersecurity during operation — enforcement outside the model | **ATTAINED** (security/robustness) | Enforcement lives entirely outside the model: Ed25519 signing with key-expiry and revocation (`key_record_source.py`, `root_record_source.py`), TLS transport (`transport.py`), exactly-once replay defense (`replay_cache.py`), fail-closed at every layer, and a passing adversarial attack suite — forge/replay/rebind/swap/stale/unattested (`EVIDENCE/proofs/attack_suite_001_runner.py`). "Accuracy" of the model itself is out of scope. |
| 72–73 | Post-market monitoring & incident reporting — continuous monitoring + event reconstruction | **PARTIAL** | Event reconstruction is strong: signed envelopes + issuance log + `envelope_inspector reconcile` let any decision be replayed and audited after the fact. Continuous automated monitoring and a structured *incident-reporting* pipeline are not implemented. |

## NSA / CISA / ASD Guidance

| Requirement | Status | Where / how |
|---|---|---|
| Continuous runtime authorization — per-action policy evaluation & enforcement | **ATTAINED** | `pep.py` + `evaluator.py` evaluate and enforce on every routed request; `authz_sidecar.py` exposes the same gate as an Envoy/OPA `ext_authz` ALLOW/DENY surface. |
| Human approval for high-impact actions — execution gating & approval controls | **PARTIAL → GAP** | Execution *gating* is real (`REFUSE` blocks the call). The *human-approval* half is absent — no high-impact classification, no approval step. Same gap as EU AI Act Art 14. |
| Runtime monitoring & anomaly detection — continuous behavioral oversight | **PARTIAL** | Monitoring/observability exist (`issuance_log`, `/received`, reconcile) and the gate detects defined attack classes (replay, forgery, stale, rebind) via `replay_cache.py` + `verifier.py`. There is no general behavioral *anomaly-detection* engine. |
| Fresh authentication before privileged actions — dynamic authorization & trust verification | **ATTAINED** | Decision freshness via signed `not_after` (`pep.py`, default 300 s); signed published-record freshness with monotonic serial (`published_record_source.py`); issuer-key and root validity/revocation windows (`key_record_source.py`, `root_record_source.py`); exactly-once `decision_id` (`replay_cache.py`). A captured, validly-signed decision is not honored arbitrarily later. |
| Centralized policy decision point for every request — runtime governance architecture | **ATTAINED** (modulo G4) | `evaluator.py` is the single decision point; `MANIFEST/manifest.json` (SHA256-pinned) is the single policy source; required authority/coverage are derived from the manifest, never caller-supplied, so a caller cannot weaken policy. `authz_sidecar.py` centralizes the decision in front of any target. "Every request" holds only for routed traffic (G4). |

---

## Summary

| Bucket | Count | Rows |
|---|---|---|
| **ATTAINED** | 6 | ISO 8.1, 8.3; EU Art 12, Art 15; NSA continuous-authz, NSA fresh-auth, NSA centralized-PDP |
| **PARTIAL** | 6 | ISO 8.2, 9.1, Intro; EU Art 72–73; NSA monitoring/anomaly, NSA human-approval (gating only) |
| **GAP** | 1 | EU Art 14 / NSA human-approval (no human-in-the-loop at all) |

**Where Elyon-Sol is strongest:** the technical/architectural spine of
runtime governance — per-action enforcement, a centralized fail-closed
decision point, cryptographic action-level evidence, dynamic/fresh
authorization, and replay/forgery defense. These are attained with named
modules, tests, and ledger entries.

**The two things to build for full adherence:**

1. **Human oversight (Art 14 / NSA high-impact approval).** Add a
   `PENDING_APPROVAL` terminal state and an out-of-band approval surface
   so high-impact actions gate on a human, not only on the automated
   evaluator. This is the only outright GAP and it blocks two rows.
2. **Non-bypassable enforcement (G4).** Make routing through the PEP
   mandatory at the network layer (sidecar inline + deny-direct egress)
   so "every request" and "non-bypassable" become literally true rather
   than true-for-routed-traffic. This upgrades every "ATTAINED (modulo
   G4)" to unconditional.

Lesser PARTIAL upgrades (continuous behavioral monitoring/anomaly
detection for ISO 9.1 / EU 72–73 / NSA monitoring; a structured incident-
reporting pipeline) build naturally on the issuance log and
`envelope_inspector` that already exist.

---

*Source files referenced: `IMPLEMENTATION/{pep,evaluator,envelope,verifier,authz_sidecar,issuance_log,replay_cache,reference_target,key_record_source,root_record_source,published_record_source,transport}.py`, `MANIFEST/manifest.json`, `EVIDENCE/proofs/attack_suite_001_runner.py`, `docs/restructure/04_current_vs_claimed.md`, `README.md`. Compiled 2026-06-17.*
