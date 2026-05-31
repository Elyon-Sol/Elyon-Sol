# G5 cross-host transport evidence (VL-039)

**Status:** Current proof.
**Commit anchor:** `a4ec73639018e0185aa69673f6258cc067c00552` (the VL-039 commit; fill per the VL-012 self-referencing-hash discipline at commit time).
**Date of observation:** 2026-05-31.

## Claim

A target on a separate process, whose local working files differ from the
gate's, can fetch Elyon-Sol's published hash record from a publisher, verify
that record against a single pinned trust anchor, and reach the correct
admissibility verdict by trusting the FETCHED record over its own local disk:

* It HONORS a valid envelope built by the gate against the authentic
evaluator, EVEN THOUGH its own local `IMPLEMENTATION/evaluator.py` is
byte-divergent from the gate's. A VL-038-style target verifying against
local disk would have FALSE-REFUSED the same envelope.
* It REFUSES a forged envelope (tamper fails `decision\_sha256` integrity,
which is independent of both local disk and the fetched record).
* It REFUSES when the fetched record fails the pinned anchor (a substituted
or tampered record never becomes a trusted currency source).
* It REFUSES an un-attested call (A1; absent envelope).

This is the property co-located verification (VL-038) could not demonstrate
on the real path: the target's verdict does not depend on trusting its own
files. G5 reduces the target's trust surface from "its entire local working
tree" to "one pinned published-record anchor, distributed out-of-band, plus
transport integrity." Trust is not eliminated; it is bootstrapped at a single
value a third party can independently verify.

## Method

A real two-context demonstration over loopback (`127.0.0.1`), driven by
`EVIDENCE/proofs/g5\_cross\_host\_001\_runner.py`:

* **Publisher.** A stdlib HTTP server serves the authentic
`EVIDENCE/published\_hashes.json` bytes; a second server serves a TAMPERED
record (different bytes) for the anchor-failure case.
* **Target.** A SUBPROCESS whose working tree is a copy of the repository
with `IMPLEMENTATION/evaluator.py` byte-mutated, so its local evaluator
hash genuinely differs from the gate's. The target fetches the published
record from the publisher, anchor-verifies it against the pinned root
(`IMPLEMENTATION/published\_source.py::load\_record\_from\_bytes`,
Decision B-prime-1), and runs
`verifier.verify\_envelope(..., record\_source=<fetched record>)` so the
currency check consults the FETCHED record rather than local disk
(Decision C, via the Decision D-b parameterization of
`envelope.reassert()`).

The pinned anchor is the sha256 of `EVIDENCE/published\_hashes.json`, derived
live (constraint (i)) and held by the target as out-of-band configuration; it
is NOT fetched alongside the record.

Pinned anchor at observation:
`6abf9a1181121f963eb91e18df560499990396d540c00115ffcfd7bc8907daeb`

|Context|Evaluator sha256|
|-|-|
|Gate (authentic)|`cf311cb7fc99f170c4814eebeee63262946ac6b71099635986257887746e512b`|
|Target (mutated tree)|`592d6aec10334c86b4f3868ed5641851c4796381bc6c400e771c235dc02b0a25`|

## Observation

|Case|Adversary / role|Honored?|Reason|
|-|-|-|-|
|Valid envelope, authentic record, DIVERGENT target disk|none (the killer case)|yes|`REASSERTED\_AND\_BOUND`|
|Forged envelope, authentic record|A2|no|`REF\_VERIFY\_REASSERT\_INVALIDATED`|
|Valid envelope, tampered record (fails pinned anchor)|A5 (record-hop tamper)|no|`REF\_TARGET\_ANCHOR\_MISMATCH`|
|No envelope, authentic record|A1|no|`REF\_VERIFY\_ENVELOPE\_ABSENT`|

For the killer case, the target reported that a VL-038-style local-disk
verify on its divergent tree would have returned
`REF\_VERIFY\_REASSERT\_RE\_EVALUATE\_REQUIRED` (its local evaluator hash does not
match the envelope's pin). The G5 target honored anyway, because it verified
against the fetched authentic record. That contrast is the load-bearing proof
that Decision C is satisfied: currency comes from the record, not the disk.
The runner asserts every row plus the killer invariant and exits nonzero on
any failure (observed exit 0).

## Scope and honest limits (the G5 floor; Decision F, named not built)

* **Anchor distribution.** The pinned root reaches the target out-of-band;
securing that distribution is the G5 bootstrap floor, parallel to the A1
floor (artifact 08 section 4.4). G5 reduces and makes the trust surface
explicit; it does not eliminate trust.
* **Freshness / revocation.** A stale-but-anchor-matching record is a
distinct threat (an A3b-class freshness gap, kin to F2's verbatim-replay
pin). Not addressed here; the next hardening after transport.
* **Signing / PKI.** A signed record (B-prime-2) or a transparency log
(B-prime-3) would remove per-target pinning and add auditability; named,
not built.
* **TLS / true multi-machine.** Modeled here by loopback; deployment.
* **A1** remains closeable only by a target-side admission policy.

G5 therefore moves from "open with a committed local record" to "transport
built; trust bootstrapped at one pinned anchor." It does NOT become a blanket
RESOLVED.

## Reproducibility

1. Confirm the published record matches live state (the VL-038 checks).
2. Run `PYTHONPATH=. python3 EVIDENCE/proofs/g5\_cross\_host\_001\_runner.py`;
the output reproduces the Observation table and the runner exits 0 iff the
invariants hold.
3. The suite-level claim is reproducible by `python -m pytest TESTS/`; the
cross-host unit and end-to-end tests are
`TESTS/adversarial/test\_cross\_host.py`.

## Related artifacts

* Runner: `EVIDENCE/proofs/g5\_cross\_host\_001\_runner.py`.
* Log: `EVIDENCE/proofs/g5\_cross\_host\_001.log`.
* Transport module: `IMPLEMENTATION/published\_source.py`.
* Parameterization (Decision D-b): `IMPLEMENTATION/envelope.py::reassert`,
`IMPLEMENTATION/verifier.py::verify\_envelope` (new `record\_source` param,
local-disk default).
* Published record: `EVIDENCE/published\_hashes.json`.
* Tests: `TESTS/adversarial/test\_cross\_host.py`.
* Design: `docs/restructure/08\_enforcement\_design.md` (section 6, the G4/G5
boundary).
* Ledger entry: VL-039.

