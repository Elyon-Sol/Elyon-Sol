# G3 enforcement evidence (VL-030)

**Status:** Current proof.
**Commit anchor:** `89ff2f9c02871d8641cebd3eb043d6c3c0d8471a` (HEAD at the time
of measurement, one commit ahead of VL-029's `79012d7` due to the README
rewrite at `5f833fb`).
**Date of observation:** 2026-05-25.

## Claim

The deterministic, fail-closed enforcement property of `IMPLEMENTATION/pep.py`
holds against a real external HTTP endpoint at the snapshot commit:

- REFUSE responses produce zero external side effects.
- ELIGIBLE responses produce exactly one external execution per call.

## Method

`POST /governed-call` issued repeatedly with two request bodies:

- **REFUSE pattern:** empty AP and OP arrays. Fails AC^3 and T^26 at the
  evaluator layer.
- **ELIGIBLE pattern:** AP = `["identity", "role"]`, OP = `["session",
  "request"]`. Both supersets of the manifest's required AR and R sets.

Both bodies carried `expected_manifest_version = "1.0"` and the live manifest
SHA256 `a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8`.

`target_url` for both bodies pointed at the public webhook intercept
`https://webhook.site/4da50ca0-9824-4654-8394-848e3b355e38`. The external
receiver is outside the gate's process, providing third-party observation
of side effects.

Three blocks issued:

- **Block 1 (sanity, manual):** 1 REFUSE + 1 ELIGIBLE, executed before the
  script.
- **Block 2 (temporal stability, scripted):** 50 REFUSE then 50 ELIGIBLE in
  sequence.
- **Block 3 (aggregate continuity, scripted):** 51 REFUSE and 51 ELIGIBLE
  alternating (102 calls).

Total: 2 manual sanity calls + 202 scripted calls = 204 HTTP calls.

The script that ran Blocks 2 and 3 captured its output in
`EVIDENCE/proofs/g3_enforcement_evidence_001.log` (start
`2026-05-25T22:45:42Z`, end `2026-05-25T22:48:58Z`).

## Observation

| Metric | Value |
|---|---|
| Total HTTP calls (manual + scripted) | 204 |
| Scripted calls (per log) | 202 |
| REFUSE calls (expected 403) | 102 |
| REFUSE returning 403 | 102 |
| ELIGIBLE calls (expected 200) | 102 |
| ELIGIBLE returning 200 | 102 |
| Unexpected HTTP outcomes | 0 |
| Webhook.site inbox before test | 53 |
| Webhook.site inbox after test | 155 |
| External POSTs observed (delta) | 102 |
| External POSTs from REFUSE calls | 0 |
| External POSTs from ELIGIBLE calls | 102 |
| Duplicate external executions | 0 |
| Retry artifacts | 0 |

The script log reports its own 101 REFUSE + 101 ELIGIBLE = 202 scripted
calls and expects the webhook.site inbox to reach 155 (53 baseline + 101
scripted ELIGIBLE-attributable POSTs + 1 manual-sanity ELIGIBLE-attributable
POST observed pre-script). The observed final inbox of 155 matches the
expectation. Total enforcement coverage including the manual sanity block
is 204 calls / 102 ELIGIBLE / 102 REFUSE / 0 unexpected.

The webhook.site baseline of 53 reflects unrelated prior testing on the
endpoint (dated 2026-05-04, three weeks before this run). The
delta-of-interest is the count of new POSTs during the test window, all
sourced from the user's NAT egress IP and all with timestamps inside the
script run window plus the manual-sanity pre-script window.

## Reproducibility

1. Clone the repository and check out commit
   `89ff2f9c02871d8641cebd3eb043d6c3c0d8471a`.
2. Compute the manifest hash: `sha256sum MANIFEST/manifest.json`. Confirm it
   matches the hash named in this proof. If it does not, the manifest at
   HEAD differs from the manifest at the time of this measurement; re-run
   with the live hash.
3. Start the PEP: `python -m uvicorn IMPLEMENTATION.pep:app`.
4. Provide a webhook.site URL or any HTTP intake endpoint outside the
   gate's process. If reusing an endpoint with prior state, name the
   baseline count explicitly and measure the delta (VL-030 SD-1
   baseline-arithmetic discipline).
5. Run the three blocks (manual sanity, then scripted Blocks 2 and 3 per
   the pattern documented in the log).

The internal-consistency claim (pytest 84/84 at HEAD) is reproducible by
`python -m pytest TESTS/` against the same commit.

## Related artifacts

- Public publication: Zenodo DOI `10.5281/zenodo.20387278` (Elyon-Sol
  v0.9.8.4 - Enforcement Evidence Addendum, Revision 2), published
  2026-05-25, attached PDF md5 `b750a803eb31a44248dd5fa89b4c273b`.
- Internal log: `EVIDENCE/proofs/g3_enforcement_evidence_001.log`.
- Ledger entry: VL-030.
