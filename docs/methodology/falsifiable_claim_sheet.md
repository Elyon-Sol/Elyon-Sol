# Falsifiable claim sheet - break-it challenges and honest status

Repo path: docs/methodology/falsifiable_claim_sheet.md. Increment VL-079 (C3, artifact 13 Phase
C). This is the gate-2 deliverable of `docs/methodology/external_verification_readiness.md`:
every bounded claim restated as a break-it challenge with an explicit pass/fail criterion, mapped
to the attack that defends it and the honest current status. The claim taxonomy is the
deposit-readiness audit (`deposit_readiness_audit.md`, VL-059); the attacks are runnable in
`EVIDENCE/proofs/attack_harness.py` (run by `EVIDENCE/proofs/attack_suite_001_runner.py`).

## How to read this sheet

A reviewer succeeds by producing a working exploit and fails by not - a referent no framing can
move. Each row gives: the challenge (what the attacker tries), the expected gate behavior (the
pass/fail line), the attack id in the harness, and the STATUS.

STATUS values and their honest meaning:
- DEFENDED (in-process): the attack is defeated against the in-process surface
  (`attack_suite_001_runner.py`, exit 0). Per gate 2, this proves the attack is well-formed and
  the gate refuses it locally; it is NOT external validation. It becomes a REAL attack-surface
  result only when run against a real cross-host deployment (gate 1 / Phase C C1+C2) - the
  HttpSurface adapter exists and is shape-tested, but the real-transport run is the author's.
- NAMED-OPEN: there is no attack that closes this; it is a trust-model boundary or an unbuilt
  floor. It is stated to the reviewer as a limit, not presented as something the gate defends.

The single binding NOT-READY reason is unchanged and gates this whole sheet: the G5 real-transport
floor + a real external attacker (external_verification_readiness gate 1). Nothing below moves
that axis.

## Section 1 - Defended (attack defeated in-process; referent-incomplete until gate 1)

| # | Challenge (attacker attempts) | Gate must | Attack id | Defender | Status |
|---|-------------------------------|-----------|-----------|----------|--------|
| 1 | Have the executor honor a valid, current, bound, signed call | honor it (positive control - else "all refused" is vacuous) | `positive_control` | `test_attack_harness`, `test_enforcement` | DEFENDED (in-process) |
| 2 | Reach the target with NO admissibility envelope (A1 bypass) | refuse `REF_VERIFY_ENVELOPE_ABSENT` | `unattested` | `test_verifier`, wedge runner | DEFENDED (in-process) - BUT see NAMED-OPEN A1 below: the gate refuses an un-attested call only at a target that ADOPTS the policy; a declining caller hitting the target directly is closed by target-side policy, not by the gate |
| 3 | Pass off a FORGED envelope (tamper a signed field) on the signed path | refuse `REF_VERIFY_SIGNATURE_INVALID` | `forged_signature` | `test_signing`, `signing_forgery_defeated` runner | DEFENDED (in-process) - bound to the SIGNED path (Section B/1) |
| 4 | Get the target to act on a verbatim REPLAY | refuse `REF_VERIFY_REPLAY` | `replay` | `test_verifier`, `test_findings_001`, wedge runner | DEFENDED (in-process) - per-instance / in-window only (Section B/4) |
| 5 | Rebind: use an envelope admitted for tool A to authorize tool B | refuse `REF_VERIFY_BINDING_MISMATCH` | `rebind_tool` | `test_verifier`, MCP runner | DEFENDED (in-process) |
| 6 | Rebind: reuse the envelope with different (larger) args | refuse `REF_VERIFY_BINDING_MISMATCH` | `rebind_args` | `test_verifier`, MCP runner | DEFENDED (in-process) |
| 7 | Present an envelope bound to target A against target B (target_url swap) | refuse `REF_VERIFY_BINDING_MISMATCH` | `target_url_swap` | `test_verifier`, `test_findings_001` | DEFENDED (in-process) |
| 8 | Mint acceptance against a byte-divergent / re-published evaluator state (drift) | refuse `REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED` | `drifted_state` | `test_verifier`, wedge runner | DEFENDED (in-process) |
| 9 | Replay an admission PAST its decision-freshness window (stale) | refuse `REF_VERIFY_SIGNATURE_EXPIRED` | `stale` | `test_signing_expiry`, decision-freshness | DEFENDED (in-process) |

## Section 2 - Defended elsewhere (require the key-record / root-record executor surface)

These bounded claims are defended by existing runners/tests but use the key-record executor
surface, not the pinned-key ExecutorGate the harness drives; the harness names them and points at
their defenders rather than re-running them.

| # | Challenge | Gate must | Defender | Status |
|---|-----------|-----------|----------|--------|
| 10 | Get a REVOKED or out-of-window issuer key accepted | refuse `REF_VERIFY_KEY_REVOKED` / `REF_VERIFY_KEY_OUT_OF_WINDOW` | `test_key_record`, `key_record_001` runner | DEFENDED (in-process), via the key-record surface |
| 11 | Get a key record signed by a REVOKED/RETIRED root accepted | refuse `REF_VERIFY_ROOT_REVOKED` / `REF_VERIFY_ROOT_RETIRED` | `test_root_record`, `root_recovery_cross_host` runner | DEFENDED (single-host real-TLS), via the root surface |
| 12 | Honor a STALE signed published record (record freshness) | refuse `REF_VERIFY_PUBLISHED_RECORD_STALE` | `test_published_record_freshness` (B1) | DEFENDED in the reader, NOT WIRED on the default consult path (NAMED-OPEN A3b below) |

## Section 3 - Named-open (no attack closes these; stated as boundaries, not defended)

| # | Boundary | Why it is not attack-closeable | Reference |
|---|----------|-------------------------------|-----------|
| A1 | A declining caller / non-adopting target can bypass the gate by calling the target directly | Closeable only by a target-side admission policy, not by the gate; G4 is not blanket-resolved | deposit audit C/1; ext-readiness gate 5 |
| G5 | Real multi-machine transport + TLS, and a real EXTERNAL attacker on a real surface | NOT MET - the load-bearing floor; the in-process / single-host-TLS surface is partly a simulation; this is engineering + an external party, not framing | deposit audit C/2; ext-readiness gate 1 |
| A3b | A stale-but-anchor-matching published record honored on the DEFAULT consult path | The signed-record reader (B1) refuses stale, but is not wired onto the default path yet | deposit audit C/3 |
| ROOT | Root / publisher key COMPROMISE recovery | Irreducibly out-of-band; a single load-bearing trust floor stated as a limit, not defended | deposit audit B/2, C; ext-readiness gate 5 |
| COST | "Cheaper than assembling OPA + SPIFFE + PKI" | No referent: needs a stake-free human rebuild attempt; model estimates are non-evidential (GR-3) | deposit audit C/6; ext-readiness gate 3 |

## Forbidden in any reviewer briefing (carry-over hazards)

Per the deposit audit Section D and ext-readiness gate 4: no cross-model convergence verdict
("SOUND 3-0", "convergent", "N-0") is shown to a blind reviewer (demoted at VL-057, non-evidential
by GR-3); no "whole canon realized" framing (use the FULL/PARTIAL/UNIMPLEMENTED picture); no
"non-bypassable" without the routed-and-attested qualifier.

## Honest verdict of this sheet

Sections 1-2 are GREEN against the in-process surface. That is necessary scaffolding and nothing
more: per gate 2 it is referent-incomplete until gate 1 provides a real surface to attack. The
sheet's value is that it forces every bounded claim to be a falsifiable challenge BEFORE an
external party arrives, and pairs each to a runnable attack and a defender - so when the real
surface exists (C1/C2), the same suite runs over real transport and the STATUS column moves from
"in-process" to a real-attack result, or it does not, on a referent no framing can move.
