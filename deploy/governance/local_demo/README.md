# Local governance demo

Drive the REAL 202 -> approve -> consume governance flow on ONE machine and write the
issuance + approval decision logs - no Redis, no mTLS, no extra hosts. Use it to get real
decision logs to read, trace, and reconcile while developing operator tooling, without
standing up the full `docker-compose.governance.yml` deployment.

## Run

```
python deploy/governance/local_demo/run_local_governance.py
```

It prints a summary and writes two JSONL logs under `runtime/` (gitignored):

- `runtime/issuance.log` - one signed envelope per ELIGIBLE decision (`JsonlIssuanceLog`).
- `runtime/approval.log` - `approval_request` at each 202 hold and `grant_consumed` on each
  approved release (`JsonlApprovalLog`).

It runs two scenarios so the logs have variety: one high-impact action taken all the way
through 202 -> human grant -> single forward, and one left pending (a 202 with no grant).

## What is real vs simplified

REAL: `pep.governed_call` (the 202 state machine), the Ed25519 approval grant
(`approver_cli.make_grant` -> `verify_grant`, SoD/binding/freshness/single-use), and the JSONL
logs. The records are exactly what a deployed governance gate writes.

SIMPLIFIED for a single-box demo:
- **Custody is collapsed.** The approver private key is generated in this one process. In a real
  deployment ([FIX H5]) it lives ONLY in a separate approver-CLI process/host
  (`deploy/governance.env.example: ELYON_APPROVER_KEY_HEX`), never on the gate. The demo signs the
  grant in a marked "APPROVER (separate in prod)" block to keep the shape honest.
- **High-impact is forced** via the `requires_approval` seam instead of declaring `HIGH_IMPACT`
  actions in the manifest (so the demo does not change the pinned manifest hash). In production you
  declare the high-impact selector set in `MANIFEST/manifest.json`.
- **The forward is stubbed** (no real target). Replace with a real `target_url` to forward for real.
- **In-memory pending/replay stores** (single instance). Multi-instance needs the shared Redis store
  (R2) per `docker-compose.governance.yml`.

For the full, non-simplified stand-up (Redis + mTLS + separate approver custody), see
`deploy/GOVERNANCE_DEPLOYMENT.md`.

## Read the logs

Point any read-only operator tooling at the two files, or inspect directly:

```
cat runtime/approval.log
python -m IMPLEMENTATION.envelope_inspector reconcile --issued runtime/issuance.log --executed runtime/approval.log
```
