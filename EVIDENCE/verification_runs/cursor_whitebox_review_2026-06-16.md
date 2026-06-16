# Cursor white-box adversarial review (Mode A) - 2026-06-16

WHITE-BOX, in-house hardening. The reviewer (Cursor, over the full local repo) is
NOT blind - this is internal evidence, FORBIDDEN to show a blind external reviewer
as validation (VL-057 / ext-readiness gate 4). NOT a G5 referent. Adjudicated
against HEAD by Claude; every Cursor line-citation verified accurate (no fabrication).

## Findings (adjudicated)

| ID | class | verdict | invariant | fix / status |
|----|-------|---------|-----------|--------------|
| R-01 | replay | REAL, FIXED | single-use | InMemoryReplayCache.check_and_claim was lock-free check-then-set; sidecar runs check() in a threadpool -> two concurrent POST /authz could both claim one decision_id (live single-use bypass). Fixed: threading.Lock over prune+check+set (replay_cache.py). |
| P-01 | parsing | REAL, FIXED | signature/integrity | duplicate X-Elyon-Sol-Envelope / -Interaction header was first-wins; now treated as absent -> fail closed (authz_sidecar.py + reference_target.py). |
| B-01 | binding | REAL, NAMED-OPEN | bound-to-executed-action | sidecar binds the interaction HEADER, not the upstream's executed body/path (Envoy ext_authz). Not a narrow-claim break (token is valid) and not live-exploitable on the standalone sidecar, but defeats gating when fronting a body-carrying upstream. = build-order step 4 (CUSTOM body->interaction mapping), unbuilt. |
| F-01 | freshness | REAL, NAMED-OPEN | published-record currency | sidecar is byte-anchor only (no signed-record freshness); stale-but-anchor-matching record passes, bounded by decision not_after (300s). Target has signed mode (VL-108); sidecar should too. |
| R-02 | replay | KNOWN boundary | single-use (multi-instance) | per-process InMemoryReplayCache default; workers>1 / replicas without ELYON_REPLAY_REDIS_URL -> cross-process replay. Documented in readiness.json; NOT live-exploitable (nodes are single-worker). Want a fail-closed guard. |

## Probed-and-held (cryptographic core held)
signed region vs sign_envelope; single canonical_json for hash+sign+binding; verifier-core
target_url/AP/OP/context binding; manifest_integrity == on-disk + anchor-before-parse;
fail-closed error mapping; verify->claim->act ordering; Redis SET NX atomicity.

## Outcome
Two real bugs fixed (R-01, P-01), tested (suite 391 -> 394 green, native run), committed
3343e32, redeployed to all four live nodes, live sidecar ALLOW/DENY re-passed. Three
named-open items (B-01, F-01, R-02) carried to the build backlog. G5 unchanged.
