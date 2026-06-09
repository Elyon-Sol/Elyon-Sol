# Deposit-readiness audit (A6 / VL-059) - what may enter a public deposit, and what may not

Repo path: docs/methodology/deposit_readiness_audit.md

## What this is

This is the A6 item of `docs/restructure/13_road_to_external_readiness.md` (Phase A,
"clean the base"): the GR-3-bound audit of what is deposit-ready versus
bounded / named-open. Acceptance criterion (artifact 13, A6): "a recorded audit;
no overclaim enters any deposit." Locus: SANDBOX (analysis).

"Deposit" here means a public archival deposit (the Zenodo deposit line the project
already uses - see `docs/restructure/05_admissibility_envelope_spec.md` line 237 and
`docs/restructure/09_key_record_spec.md` line 405, where "forgery-resistant" is held
"out of any deposit"). A deposit is read by people the author did not brief, with no
ledger context and no chance to add a caveat after the fact. So the deposit is exactly
where an overclaim does the most damage: the bounded caveats that protect a claim
inside the repo do not travel with the words once they are published.

This file states, claim by claim, which assertions are carried by a referent the
framing cannot move (deposit-ready), which are admissible only WITH an explicit bound
(bounded), and which have no referent yet and must not appear in a deposit as settled
(named-open). It is the deposit-side companion to
`docs/methodology/external_verification_readiness.md` (the human-verification analog)
and is governed by the same rule.

## The governing rule (GR-3) and what counts as a referent

Per GR-3 (`docs/MAINTENANCE_PROTOCOL.md`; originating VL-057): a bounded claim about
the system or its worth moves only on a REFERENT-BOUND result - a passing or failing
test/runner (execution), or an adversarial-by-construction outcome (a demonstrated
bypass, or a demonstrated inability to produce one). No model-sourced evaluative
judgment - "sound", "novel", "convergent", "N-0", a rebuild-cost estimate - is evidence
or may move a claim. A deposit inherits this rule wholesale: a sentence is deposit-ready
only if a referent in this repository defends it, and it must be phrased no stronger
than that referent reaches.

Referent classes that COUNT for this audit:
- the pytest suite (298 passed, 0 xfailed) - confirmed live in-sandbox at HEAD; CI on
  GitHub Actions stays green per push (originally recorded green at `c519f34`, VL-073;
  the suite grew 218 -> 298 across Phase B/C, VL-074..VL-083);
- the hermetic `EVIDENCE/proofs/` runners gated in CI, each exiting 0 (the external-webhook,
  the multi-process-TLS, and the AUTHOR-executed live-attack runners are documented CI skips,
  not gated);
- the deployment predicates in `EVIDENCE/readiness.json`
  (`IMPLEMENTATION/readiness.py` engine; `TESTS/readiness/` gate): DEFAULT_SECURE /
  END_TO_END_NO_SHORTCUT / ROOT_RECOVERY green, each TRUE flag naming a passing proof;
  REAL_TRANSPORT red (the C4 tier, VL-083, awaiting the author's real-transport run);
- the gap-tracker rows in `docs/restructure/04_current_vs_claimed.md`, which close only
  on a code/test/structure change, never on prose.

Referent classes that DO NOT count (and must never carry a deposit claim):
- any cross-model "evaluate" verdict ("SOUND 3-0", "convergent", "N-0"); these were
  demoted at VL-057 and are non-evidential by GR-3;
- any model-sourced cost or value estimate (e.g. "a small team could rebuild this in
  1-2 months");
- internal consistency or polish of the documents themselves.

## Section A - Deposit-ready (a referent in this repo defends the exact wording)

Each of these may enter a deposit AS STATED, because a named referent carries it.

1. "Elyon-Sol is a deterministic, fail-closed HTTP admission gate derived from the
   v0.9.8.4 canonical whitepaper; given a request and a SHA256-pinned manifest it
   returns ELIGIBLE only if the authority set and operation set each satisfy the
   manifest's required sets and the manifest hash and version match, else REFUSE; on
   REFUSE or any exception the target is not called."
   Referent: the pytest suite (218/0), specifically `TESTS/test_pep.py` and the
   canon-derived `TESTS/adversarial/test_evaluator_canonical.py` (AC^3, T^26,
   manifest-integrity).

2. "AC^3 (authority) and T^26 (coverage) and the manifest-integrity layer are faithfully
   implemented and canon-derived-tested."
   Referent: G3 RESOLVED (VL-030), G7 RESOLVED (VL-028 + VL-034); the canon-derived
   test files cited in artifact 04 G7.

3. "Canonical CCS (continuity) is implemented at the envelope layer."
   Referent: G0 RESOLVED (VL-012 rename half + VL-029 build half);
   `TESTS/adversarial/test_ccs_canonical.py`. Phrase it at the envelope layer - do not
   say "CCS is fully realized end-to-end on the default transport" (see Section C).

4. "A signed admissibility envelope is emitted on every ELIGIBLE forward; an enforcing
   target can verify decision integrity, currency, issuer signature, expiry, and
   request/target binding, fail-closed."
   Referent: the deployment predicate DEFAULT_SECURE is GREEN
   (`EVIDENCE/readiness.json`, VL-047); `TESTS/adversarial/test_enforcement.py`,
   `test_signing.py`, `test_verifier.py`.

5. "The gate is defensibly non-bypassable for routed-and-attested traffic: a direct,
   forged, replayed, target_url-swapped, or published-record-mismatched call is refused
   and the target is not acted on."
   Referent: `EVIDENCE/proofs/g4_refused_bypass_001.{log,md}` (1 honored+acted, 5 refused,
   0 target actions). Note the exact scope qualifier "for routed-and-attested traffic" -
   it is load-bearing (see Section C, item 1).

6. "Issuer-key expiry, published-key revocation, and planned in-band root rotation are
   built and exercised over the cross-host chain."
   Referent: `EVIDENCE/readiness.json` capabilities (issuer_key_expiry built;
   issuer_key_revocation / root_rotation exercised_e2e + transported);
   `TESTS/adversarial/test_signing_expiry.py`, `test_key_record.py`, `test_root_record.py`;
   `EVIDENCE/proofs/root_recovery_cross_host_001_runner.py`.

7. "Decision freshness and in-window exactly-once replay defence hold in-process
   end-to-end, demonstrated on an MCP-shaped tool-call surface."
   Referent: A3b sub-case (a) CLOSED (VL-065) and replay/exactly-once CLOSED (VL-066);
   `EVIDENCE/proofs/wedge_agent_toolcall_001_runner.py` (7/7, tool fired exactly once).
   Carry the "in-process / per-instance" qualifier (Section B, item 4).

8. "The full suite plus the hermetic evidence runners are enforced in CI; the run is
   green."
   Referent: G8 CI half closed (VL-073); GitHub Actions green at `c519f34`, author-
   confirmed (VL-073 follow-up 4). State it as "CI green" - not "fully reproducible on
   any machine" (the two documented skips and the STATE.md auto-regen residual are real;
   Section C, item 5).

9. "Every published claim is hash-anchored: a third party can clone the repo and
   re-derive the verdicts against a committed published record."
   Referent: `EVIDENCE/published_hashes.json` (derived live by
   `EVIDENCE/published_hashes_gen.py`), `CANON/canon.lock`; the g4/g5 runners anchor every
   verdict to the committed record.

## Section B - Bounded (admissible ONLY with the stated bound attached)

These claims are true within a boundary and become overclaims the instant the boundary
is dropped. In a deposit they must appear WITH the bound in the same sentence, never as
a bare adjective.

1. "Forgery-resistant." ADMISSIBLE ONLY AS: forgery is closed on the SIGNED path, where
   issuer signing is REQUIRED; the default unsigned forward is tamper-evident, not
   forgery-resistant (an `decision_sha256` is unkeyed). The repo has repeatedly held the
   bare phrase "forgery-resistant" OUT OF ANY DEPOSIT pending a referent
   (artifact 04 VL-040/042; artifact 05 line 209; artifact 09 line 405). HOLD THAT LINE:
   the bare adjective does not enter a deposit. If used, it is bound to the signed path
   and to the named trust floor below.

2. "Trust floor: root/publisher key compromise is total." The relocation of trust from
   N issuer pins to ONE pinned publisher/root key (VL-042) is a SINGLE load-bearing floor;
   root-key COMPROMISE recovery is irreducibly out-of-band (artifact 11 section 2). A
   deposit must state this floor as a boundary, not imply the gate defends it. (Mirrors
   external_verification_readiness gate 5: named, not defended.)

3. "Cross-host transport works." ADMISSIBLE ONLY AS: real TLS between distinct OS
   PROCESSES ON ONE HOST (VL-063, single-host fidelity). It is NOT true multi-machine
   transport and NOT an external-network surface (Section C, item 2).

4. "Exactly-once / no replay." ADMISSIBLE ONLY AS: per-instance, in-process. Multi-
   instance exactly-once needs a SHARED replay cache, which is named-not-built
   (artifact 04 A3b; Phase-B item B3). A deposit may not imply distributed exactly-once.

5. "Externally verified interception." This older framing (G5) is bounded to
   "observable at the PEP" / "re-derivable from the committed published record." The
   original `webhook.site` / loopback evidence is non-durable; the durable form is the
   committed hash record. Do not deposit "externally verified" unqualified.

## Section C - Named-open (NO referent yet; must NOT enter a deposit as settled)

These are the gate's honest open edges. They may be DESCRIBED in a deposit as open /
future / out-of-scope, but must never be asserted as done.

1. A1 - the declining caller. A caller can still hit the target directly and bypass the
   gate; A1 is closeable only by a target-side admission policy, not by the gate itself.
   The reference target (VL-061) closes it for any target that ADOPTS that policy; a
   non-adopting target or a declining caller can still bypass. G4 is therefore NOT
   blanket RESOLVED.

2. G5 - real-transport floor / external attacker. True multi-machine + TLS, and an
   EXTERNAL attacker on a real surface, are NOT MET (external_verification_readiness
   gate 1, the load-bearing gate; artifact 04 G5; VL-063). This is the single binding
   reason the project is NOT READY for external verification. A deposit must not claim
   "externally attack-tested" or "production-deployed."

3. A3b sub-case (b) - record freshness. A stale-but-anchor-matching published record can
   still be honored cross-host; `reassert(record_source=...)` checks the record's hashes,
   not its liveness. OPEN (Phase-B item B1). Do not claim "freshness-complete."

4. G12 / G13 - canon-layer halves. The schema-layer halves are closed (VL-016); the
   canon-layer under-specification of `C`/`t` wire-origin (G12) and the manifest-pinning
   provenance (G13) remain OPEN pending a canon-version event under GR-1. A deposit must
   not claim the canon itself fully specifies these.

5. G8 residual - STATE.md auto-regenerability. CI is green, but STATE.md is not
   auto-regenerable; G8 stays NEAR-CLOSED. Two runners are documented CI skips (external
   webhook, non-hermetic; multi-process-TLS, hosted-runner networking - verified locally,
   cross-host coverage retained in CI by three other runners). Do not claim "fully
   reproducible CI on any runner."

6. Rebuild-cost ratio ("cheaper than assembling OPA + SPIFFE + PKI"). No referent exists:
   no stake-free rebuild attempt has been made; the only estimate on record is model-
   sourced and is non-evidential per GR-3 (external_verification_readiness gate 3). This
   claim does not enter a deposit in any form until a person, not a model, attempts the
   assembly.

## Section D - Forbidden framings (carry-over hazards a deposit must not inherit)

1. Cross-model convergence verdicts. Any "SOUND 3-0", "convergent", "N-0" language was
   demoted at VL-057 and is non-evidential (GR-3). It must not appear in a deposit as
   validation, and a blind reviewer must not be shown it (external_verification_readiness
   gate 4).

2. "The whole canon is realized." The implementation faithfully realizes AC^3, T^26, the
   manifest layer, and envelope-layer CCS; it does not implement the section 4/15 failure
   constructs (CDD/SAP/PAD/ILT) - consistent with canon (they "do not participate in
   admissibility determination"), not a gap, but a deposit must not imply 1:1 whole-canon
   realization. Use the FULL/PARTIAL/UNIMPLEMENTED picture from artifact 06.

3. "Non-bypassable" without the routed-and-attested qualifier (see Section A item 5 and
   Section C item 1).

## Phase B/C additions (VL-074..VL-083) - where the new work falls

The Phase-B/C build (the artifact-13 road) added capability and packaging WITHOUT moving the
external-validation axis; each new item is classified by the same rule:
- DEPOSIT-READY (with the in-process / local bound): the wedge property holds on a real MCP
  `tools/call` server over real stdio (VL-077, `mcp_server_001_runner.py`); the executor
  sequence is packaged as a thin SDK (VL-078); the gate-2 attacks are runnable and defeated
  in-process (VL-079, `attack_suite_001_runner.py`) with the falsifiable claim sheet committed.
  Carry the "in-process / single-host / local-stdio" bound; none is a real-transport result.
- BOUNDED (built, not wired to the default path): the signed published-record freshness reader
  (VL-074) and the configurable clock-skew window (VL-075, default 0) and the shared-replay-cache
  seam (VL-076) are CAPABILITIES present and default-off (readiness.json shows them built /
  unwired with named blockers). A deposit may say "built," not "enforced on the default path."
- NAMED-OPEN (no referent yet): the deploy packaging (VL-081) and real-TLS tooling (VL-082) are
  authored but the container/TLS STAND-UP is UNVALIDATED (no docker / real CA in-sandbox); the
  live attack run + the REAL_TRANSPORT predicate (VL-083) are RED, awaiting the author's real-host
  run. The latency figure (VL-078) is INDICATIVE (sandbox hardware), not a budget of record.
The single binding NOT-READY reason is unchanged: the G5 real-transport floor + a real external
attacker (external_verification_readiness gate 1).

## Deposit gate (the operational test)

A sentence is admissible in a deposit iff:
(1) it names, or is directly backed by, a Section-A referent AND is phrased no stronger
    than that referent reaches; OR
(2) it is a Section-B claim carrying its bound in the same breath; OR
(3) it is a Section-C item described explicitly as open / future / out-of-scope.

Anything else - any Section-D framing, any bare bounded adjective, any model-sourced
judgment - is an overclaim and is held out of the deposit.

## Honest ceiling of this audit

This audit constrains what may COUNT as deposit-ready; it does not itself produce a
referent. The single fact that most limits the project's deposit surface is unchanged by
this document: the G5 real-transport floor and the absence of an external attacker
(external_verification_readiness, NOT READY). A deposit made today can honestly publish
the in-process / single-host-TLS gate, its canon derivation, its hash-anchored evidence,
and its named-open edges - but not a real-transport, externally-attacked, production
claim. That claim awaits the referent, not better wording.
