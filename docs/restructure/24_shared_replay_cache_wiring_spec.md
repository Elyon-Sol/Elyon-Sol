# 24 - Wiring the shared-replay-cache seam onto the reference target

Repo path: docs/restructure/24_shared_replay_cache_wiring_spec.md. Increment VL-094. The WIRE half
of B3 (VL-076 built the seam; this wires it onto the reference target's default replay defense,
parity with the VL-039 -> VL-060 and VL-074 -> VL-091 seam-then-wire steps). Makes cross-instance
exactly-once REACHABLE for a horizontally-scaled executor.

## 1. Purpose and scope

The reference target's replay defense (VL-066) is an inline per-process `app.state.seen` dict: a
`decision_id` honored on instance A is unknown to instance B, so a horizontally-scaled executor can
honor the same decision once per instance (replay crosses instances). VL-076 built the `ReplayCache`
seam (`check_and_claim`) + an `InMemoryReplayCache` (behavior-identical to the inline dict) + an
`ExternalStoreReplayCache` over an injected store, but the reference target never consulted it. This
increment wires it.

In scope (VL-094):
- `reference_target.py`: the inline `app.state.seen` dict is REPLACED by an injectable
  `ReplayCache` (`app.state.replay_cache`). The default is `InMemoryReplayCache` (BYTE-BEHAVIOUR-
  IDENTICAL to the inline dict: prune-expired -> membership-refuse -> claim), so every existing
  runner/test is unchanged. The module-level app builds the cache from the environment.
- `replay_cache.py`: a concrete `RedisReplayStore` (a `ReplayStore` whose `claim` is Redis
  `SET key 1 NX EX <ttl>` - cross-process exactly-once when N instances share one Redis), with
  `redis` lazily imported (NOT a hard dependency); and `replay_cache_from_env()` - returns an
  `ExternalStoreReplayCache(RedisReplayStore.from_url(ELYON_REPLAY_REDIS_URL))` when that env is
  set, else an `InMemoryReplayCache`.
- Tests: the wired target still refuses a same-instance replay; a `RedisReplayStore` over a fake
  shared client catches a cross-instance replay (two `ExternalStoreReplayCache` over one store);
  `replay_cache_from_env` returns InMemory with no env set.
- A runbook procedure (deploy/host_setup_virtualbox.md appendix) for the live cross-instance demo:
  a Redis service + two target instances sharing it, where a decision_id honored on instance A is
  refused `REF_VERIFY_REPLAY` on instance B.

Out of scope (named): a true distributed-systems exactly-once proof under partition/failure (the
shared store's own consistency is its concern; Redis `SET NX EX` is the chosen primitive); the
external attacker (G5). Making a shared store the bare default stays a deployment choice (the bare
default is `InMemoryReplayCache`, per-instance, so the single-instance deployment is unchanged).

## 2. Fail-closed / no new invariant

The wire changes WHERE the seen-set lives (process dict -> shared store), not WHAT is decided.
`check_and_claim` returns True only on a positively-fresh, positively-claimed decision_id; a store
that cannot decide (a Redis error) raises through the target's per-request try/except to a refusal
(the call is NOT honored on an undecidable claim). No canon / evaluator / MANIFEST / envelope change
(canon section 14): replay defense is the acting party's stateful concern (VL-066).

## 3. Honest ceiling

Wiring makes cross-instance exactly-once REACHABLE for a CONFIGURED deployment (one Redis behind N
targets); the bare default stays per-instance in-memory. A shared cache is only as available as its
backend - a store outage fails closed (refuse), trading availability for the guarantee (the correct
trade for an admission gate, named so a deployment chooses it knowingly). Exactly-once remains
bounded by the freshness window. This does not move the external-attacker (G5) line.

## 4. Acceptance (VL-094)

- `TESTS/adversarial/test_reference_target.py` (replay) and the full suite stay green (the wired
  default InMemory cache is behavior-identical).
- `TESTS/adversarial/test_shared_replay_cache.py`: `RedisReplayStore` over a fake shared client -
  honor-once / refuse-replay; two `ExternalStoreReplayCache` over ONE store catch a cross-instance
  replay; `replay_cache_from_env()` returns InMemory with no env.
- The runbook carries the live cross-instance demo procedure.
