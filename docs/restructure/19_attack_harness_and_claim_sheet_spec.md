# 19 - Attack harness + falsifiable claim sheet

Repo path: docs/restructure/19_attack_harness_and_claim_sheet_spec.md. Increment VL-079 (C3,
artifact 13 Phase C). Turns the wedge claim and `external_verification_readiness.md` gate 2 into
runnable attacks - each emitting pass/fail against a surface - and a claim sheet pairing each
bounded claim to its attack and honest current status.

## 1. Purpose and scope

`external_verification_readiness.md` gate 2 names the deliverable: "every bounded claim restated
as a break-it challenge with an explicit pass/fail criterion, each mapped to the test or runner
that currently defends it." The deposit-readiness audit (VL-059) supplies the claim taxonomy
(Section A deposit-ready, B bounded, C named-open). C3 makes the gate-2 attacks executable and
writes the claim sheet.

The honest constraint, stated by gate 2 itself: the claim sheet "becomes a REAL attack surface
only once gate 1 [real cross-host transport] is met." So C3 is SCAFFOLDING: the harness runs the
attacks against an in-process surface now (proving the attacks are well-formed and the gate
defeats them locally), and is built against a pluggable `Surface` so the SAME attacks run against
a real deployed surface (C1/C2) when it exists. No attack result against the in-process surface
is presented as external validation - that remains gate 1's referent.

In scope (VL-079):
- `EVIDENCE/proofs/attack_harness.py`: a `Surface` adapter (admit a decision; attempt a tool call,
  returning honored/reason), an `InProcessSurface` (over the VL-078 `ExecutorGate`), an
  `HttpSurface` (over a real reference-target URL, the AUTHOR adapter), an `Attack` definition, and
  `run_suite` emitting per-attack pass/fail. An attack PASSES when it is DEFEATED (the surface
  refuses with the expected reason); the positive control passes when the valid call is honored.
- `EVIDENCE/proofs/attack_suite_001_runner.py`: runs the suite against the in-process surface,
  prints pass/fail per attack + an overall verdict, exits 0 iff every attack is defeated and the
  positive control honored.
- `docs/methodology/falsifiable_claim_sheet.md`: each Section-A/B claim restated as a break-it
  challenge, mapped to its attack id and defending test/runner, with the honest status
  (DEFENDED-in-process, referent-incomplete-until-gate-1) and the Section-C named-open boundaries
  listed as un-attackable limits, not defended claims.

Out of scope (named, not built):
- Running against a real cross-host surface (gate 1 / C1+C2). Locus AUTHOR: the `HttpSurface`
  adapter is built and shape-tested against a local TestClient reference target, but the
  real-transport run is the author's, on real hosts.
- The key-record / root-record attacks (revoked key, retired root). They are defended by
  `test_key_record` / `test_root_record` and the root-recovery runner, but require the key-record
  executor surface, not the pinned-key `ExecutorGate`; the claim sheet names them and points at
  their existing defenders rather than re-running them here.
- Rebuild-cost (gate 3) and the blind-reviewer process (gate 4): not attacks; named open in the
  claim sheet.

## 2. The Surface adapter

A `Surface` exposes two operations so the SAME attack runs anywhere:

    admit(tool, args, *, max_age=300) -> envelope        # drive the gate to mint a signed decision
    attempt(tool, args, envelope) -> (honored, reason)   # present a call to the executor

`InProcessSurface` admits via the production `pep` app and attempts via `ExecutorGate.check`.
`HttpSurface` admits via POST to the gate's `/governed-call` and attempts via POST to the
reference target's `/target` with the envelope header, reading honored/reason from the response.
The attack definitions never touch a surface's internals, so the suite is transport-agnostic.

## 3. The attack suite (gate-2 break-it challenges)

Each attack states the reviewer-form challenge, the tampering, and the expected refusal:
- `positive_control` - a valid admitted call IS honored (else "all refused" is vacuous).
- `unattested` (A1) - present no envelope -> `REF_VERIFY_ENVELOPE_ABSENT`. (Bound: A1 is closed
  only by a target-side policy, not by the gate - carried in the claim sheet.)
- `forged_signature` - mutate a signed field of a real envelope -> `REF_VERIFY_SIGNATURE_INVALID`.
- `replay` - present the same admitted envelope twice -> second `REF_VERIFY_REPLAY`.
- `rebind_tool` / `rebind_args` - an envelope admitted for one call presented for another ->
  `REF_VERIFY_BINDING_MISMATCH`.
- `target_url_swap` - an envelope bound to target A presented to target B ->
  `REF_VERIFY_BINDING_MISMATCH`.
- `drifted_state` - the executor's published/evaluator state moved -> `REF_VERIFY_REASSERT_RE_
  EVALUATE_REQUIRED` (run against a surface configured with a re-published record).
- `stale` - an admission past its freshness window -> `REF_VERIFY_SIGNATURE_EXPIRED`.

## 4. Fail-closed / no new invariant

The harness only OBSERVES; it adds no decision and no reason code (every expected reason is a
production `REF_*`). It changes nothing in the gate. No canon / evaluator / MANIFEST / envelope
change (canon section 14). Build-then-wire: new files only; the default path is byte-unchanged.

## 5. Honest ceiling

Defeating every attack against the IN-PROCESS surface proves the attacks are well-formed and the
gate refuses them locally; it is NOT external validation. Per gate 2, the claim sheet is
referent-incomplete until gate 1 (real cross-host transport) provides a genuine surface to attack.
The single binding NOT-READY reason is unchanged: the G5 real-transport floor and a real external
attacker, the author-arranged finish line. No in-process pass moves that axis.

## 6. Acceptance (VL-079)

- `EVIDENCE/proofs/attack_suite_001_runner.py` runs the suite against the in-process surface:
  the positive control honored, every adversarial attack defeated with the named reason, exit 0.
- `TESTS/adversarial/test_attack_harness.py`: each attack defeated against `InProcessSurface`; the
  positive control honored; the `HttpSurface` adapter drives a local TestClient reference target
  (proving the real-surface adapter shape, the seam C1/C2 plug into).
- `docs/methodology/falsifiable_claim_sheet.md` committed: every Section-A/B claim mapped to an
  attack id + defender + honest status; Section-C items listed as named-open boundaries.
- Full suite green; the default path byte-unchanged.
