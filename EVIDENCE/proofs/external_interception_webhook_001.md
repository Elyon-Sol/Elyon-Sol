# External-interception evidence (webhook.site third-party receiver)

Ledger: VL-062 (G4/G5 enforcement evidence; Enforcement Evidence Addendum Rev. 3 Section 2).
Snapshot under test: `c756f8fb773dcc9f64f1e99c0c7d8bc815ae2920`.
Runner: `EVIDENCE/proofs/external_interception_webhook_001_runner.py`.
Raw run: `EVIDENCE/proofs/external_interception_webhook_001.log`.

## What this proves

Fail-closed enforcement observed by a third party. A sequence of 204 HTTP calls to the gate
(`/governed-call`) — 102 REFUSE and 102 ELIGIBLE — was driven against a PEP whose ELIGIBLE
forward targets an out-of-process, third-party HTTP intake (`webhook.site`). Every REFUSE
returned 403 and produced no outbound forward; every ELIGIBLE returned 200, which the gate
returns only after its outbound `requests.post()` to the receiver completes. The receiver
inbox moved from a baseline of 155 to 257 — exactly +102, one external POST per ELIGIBLE
call and zero from REFUSE calls. On this commit each forwarded envelope is additionally
signed by the gate (the VL-047 mandatory-signing cutover).

| Metric | Value |
|---|---|
| Total HTTP calls | 204 |
| REFUSE -> 403 | 102 / 102 |
| ELIGIBLE -> 200 | 102 / 102 |
| Unexpected outcomes | 0 |
| Webhook inbox before / after | 155 / 257 |
| External POSTs (from ELIGIBLE / from REFUSE) | 102 / 0 |

## Honest scope (GR-3)

This is third-party *observation* of side effects, author-driven, over loopback transport
between the gate and the receiver — not an external adversarial pen-test on a real
multi-host surface. True multi-machine networking with TLS and an attacker external to the
build remain the named G5 floor and the finish line (`docs/methodology/external_verification_readiness.md`).
The webhook-count auto-verification in the runner is best-effort; the inbox delta 155 -> 257
was confirmed in the webhook.site control panel.
