# Gargoyle - external red-team briefing

You are invited to attack a live admission-control system. You win by producing a
working exploit against a defended claim below; you do not need to read any theory to
do it. This pack is deliberately minimal: a running surface, the claims, the limits,
and a tool to check decisions for yourself.

---

## 1. The surface

Real hosts, real TLS (public CA):
- GATE:      https://gate.elyon-sol.io:8443    (the admission point; POST /governed-call)
- TARGET:    https://target.elyon-sol.io:9443  (the enforcing target; POST /target, GET /received)
- SIDECAR:   https://authz.elyon-sol.io:9243   (the ext-authz eligibility filter; POST /authz)
- PUBLISHER: https://pub.elyon-sol.io:9143/published_hashes.json   (signed record)

Engagement window: <START> to <END>. Written authorization-to-test for these named
hosts is attached separately. Scope is these hosts only.

## 2. How to send a request / read a response

A caller POSTs a JSON interaction to the gate. On admission the gate signs a one-time
eligibility token and forwards the call to the target, which independently re-verifies
the token before acting. The same token can be presented to the sidecar, which answers
ALLOW/DENY only (it does not act). Minimal shape:

    POST https://gate.elyon-sol.io:8443/governed-call
    { "interaction": { "AP": [...authorities...], "OP": [...operations...],
                       "context": {...}, "expected_manifest_version": "...",
                       "expected_manifest_sha256": "..." },
      "target_url": "https://target.elyon-sol.io:9443/target" }

Refusals come back as an enumerated code (REF_SCHEMA_* at the gate, REF_VERIFY_* at the
target and sidecar). A 200 from the target means the operation actually executed; a 200
/ ALLOW from the sidecar means it judged the token admissible. Exact request/response
shapes, a working sample, and the inspector are in the "how to interact" appendix.

## 3. The claims to break (you win by breaking any DEFENDED row)

The target must ACT only on a valid, current, bound, single-use, signed token; the
sidecar must ALLOW only such a token. You break a claim by causing the TARGET to ACT,
the gate to ADMIT, or the SIDECAR to ALLOW on a call the row says must be refused, WITH
reproduction steps. Defended rows:

| # | What you try | The system must |
|---|--------------|-----------------|
| 1 | Send a valid, current, bound, signed call (positive control) | HONOR it (else the suite is vacuous) |
| 2 | Reach the target with NO token | refuse (token absent) |
| 3 | Tamper any signed field of a token | refuse (signature invalid) |
| 4 | Replay a verbatim previously-honored token | refuse (replay) |
| 5 | Reuse a token admitted for operation A to do operation B | refuse (binding mismatch) |
| 6 | Reuse a token with different/larger arguments | refuse (binding mismatch) |
| 7 | Present a token bound to target A against a different target | refuse (binding mismatch) |
| 8 | Mint acceptance against changed/republished server state (drift) | refuse (re-evaluate required) |
| 9 | Replay an admission past its freshness window | refuse (expired) |
| 10 | Get a revoked or out-of-window issuer key accepted | refuse (key revoked / out of window) |
| 11 | Get a key record under a revoked/retired root accepted | refuse (root revoked / retired) |
| 12 | Get a stale signed published record honored | refuse (published record stale) |
| 13 | Get the SIDECAR to ALLOW (200) a token that is absent/forged/replayed/mis-bound/expired | refuse (DENY) |

## 4. The limits (NOT findings - stated boundaries)

These are known, by-design boundaries. Reaching one is NOT a break of a defended claim:
- A1: a caller that simply DOESN'T route through the gate, calling the target directly,
  is closed by the target adopting the policy - not by the gate. A non-adopting target
  is out of scope of what the gate claims.
- ROOT: compromise of the root/publisher signing key is an out-of-band trust floor
  (true of any PKI-rooted system); recovery is not claimed here.
- Semantic legitimacy: the system guarantees an action is AUTHORIZED, not that it is
  WISE. "I described a harmful action in valid vocabulary and it passed" is by design,
  not a break.
- Availability / DoS: the gate trades availability for safety (fail-closed). Knocking
  it offline refuses everything - that is the design, not a finding.

## 5. Check decisions yourself (the inspector)

You do not have to trust the gate's say-so. The token inspector lets you decode,
verify, re-evaluate, and reconcile any token the surface emits:

    python -m IMPLEMENTATION.envelope_inspector inspect <env.json> [--keys keys.json] [--record record.json]
    python -m IMPLEMENTATION.envelope_inspector reevaluate <env.json>
    python -m IMPLEMENTATION.envelope_inspector reconcile --issued issued.jsonl --executed executed.jsonl

A disputed "break" is settled by running the inspector on the artifacts and reading the
verdict.

## 6. Reporting

Send findings to <CHANNEL YOU CONTROL THE TIMING OF>. Each finding: the claim-row