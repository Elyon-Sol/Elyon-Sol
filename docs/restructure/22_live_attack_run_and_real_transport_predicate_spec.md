# 22 - Live attack run + real-transport readiness predicate (C3-live + C4 staging)

Repo path: docs/restructure/22_live_attack_run_and_real_transport_predicate_spec.md. Increment
VL-083 (C3-live + C4, artifact 13 Phase C). Stages the last two Phase-C steps so the author's part
is "run it on real hosts," not "write it."

## 1. Purpose and scope, and the honest locus split

C3's LIVE run and C4 are both locus AUTHOR (they need a real deployed surface). This increment
authors the runnable scaffolding for both and is explicit that NEITHER is met in-sandbox:
- C3-live: the runner exists and its suite logic is validated in-process, but a real-transport
  result requires the stood-up C1/C2 surface (the author's). No in-process pass is a real-attack
  result.
- C4: the `REAL_TRANSPORT` deployment predicate exists in `EVIDENCE/readiness.json`, RED by design,
  naming its blocker and the runner that will produce its proof. It is GR-2-honest (a false flag
  with a named reason); it is NOT green and cannot be greened here (no real surface). The author
  flips it green naming the live run's log.

In scope (VL-083):
- `EVIDENCE/proofs/attack_suite_live_runner.py`: the AUTHOR-executed runner. Reads the live URLs +
  CA bundle from the environment, builds an `HttpSurface` over real `requests` (the
  `RequestsClient`, now with TLS `verify`), runs the VL-079 attack suite over real transport, and
  exits 0 iff every attack is defeated. Excluded from the CI runner loop (a documented skip,
  parallel to the multi-process-TLS / external-webhook skips), since no live surface exists in CI.
- `EVIDENCE/proofs/attack_harness.py`: two backward-compatible additions - `RequestsClient(verify=)`
  (a CA bundle for real TLS) and `run_suite(include_stale=)` (the live HTTP adapter cannot control
  the gate's decision window, so the live run sets it False).
- `EVIDENCE/readiness.json`: the `REAL_TRANSPORT` predicate (RED, named blocker).
- `TESTS/adversarial/test_attack_harness.py`: the live-suite subset (the 7 request-tampering
  attacks + positive control, `include_stale=False`, no drift) is defeated over an in-process
  `HttpSurface`; the live runner exits 2 (loud) when unconfigured.

Out of scope (named): the real two-host stand-up and the real-transport run (AUTHOR); a real
external attacker (the binding NOT-READY reason); the `stale` / `drifted_state` attacks over the
live adapter (surface-state attacks the generic HTTP adapter cannot drive - they stay covered by
the in-process suite; the author may script them separately).

## 2. Why the live run is the referent the in-process run is not

`external_verification_readiness.md` gate 2: the claim sheet "becomes a REAL attack surface only
once gate 1 [real cross-host transport] is met." The in-process attack suite (VL-079,
`attack_suite_001_runner.py`) defeats the attacks against a TestClient/ExecutorGate - a simulation.
The SAME suite, run by this runner against a real gate + reference target over real TLS, is a
real-attack result on a referent no framing can move. That is the only thing that turns the green
claim sheet from "necessary scaffolding" into evidence - and even then, a real EXTERNAL attacker
(not the author's own scripted run) is the final referent for G5 (GR-3).

## 3. The C4 predicate (GR-2-honest, red)

`REAL_TRANSPORT` is added to `deployment_predicates` as `green: false` with a `blocked_by` naming
the runner and the real-host requirement. `validate_manifest` honesty-checks it like any predicate
(a false flag must name a reason); it is NOT in the canonical 3-predicate summary count until the
author both greens it and (optionally) registers it in `PREDICATE_NAMES`. On a green live run the
author edits it to `green: true` naming the run log as `proof`.

## 4. Fail-closed / no new invariant

The runner only OBSERVES the gate over real transport; it adds no decision. The predicate asserts
a real-transport result that does not yet exist (red). No canon / evaluator / MANIFEST / envelope /
IMPLEMENTATION change (canon section 14). Build-then-wire: new runner + spec + a red predicate +
harness additions only; the default path is byte-unchanged.

## 5. Honest ceiling

Both deliverables are scaffolding for an AUTHOR step. The live runner produces no referent until
run on a real surface; the predicate is red until that run passes. A green live run is the author's
own scripted attack over real transport - strong, but still not a real EXTERNAL attacker, which
remains the G5 / GR-3 finish line. Nothing here moves the external-validation axis; it stages the
step that will.

## 6. Acceptance (VL-083)

- `TESTS/adversarial/test_attack_harness.py`: the live-suite subset (7 attacks + positive control,
  no stale/drift) is defeated over an in-process `HttpSurface`; the live runner exits 2 when
  unconfigured.
- `EVIDENCE/proofs/attack_suite_live_runner.py` committed and excluded from the CI runner loop;
  the harness additions are backward-compatible (the in-process runner + tests stay green).
- `EVIDENCE/readiness.json` carries `REAL_TRANSPORT` RED; the readiness gate stays honest (3/3
  canonical green, the new tier red and named).
- Full suite green; the default path byte-unchanged.
