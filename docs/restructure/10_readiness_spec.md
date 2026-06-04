# 10 - Readiness gate (T-readiness): the WIRING-track drift detector

Status: spec (Checkpoint B). Standalone artifact, parallel to 09. Defines the
machine-checked gate that makes prototype-drift fail closed. This artifact governs
a CI/pre-commit gate; it touches NO admission-path code, no `evaluate()`, no canon
invariant. It is a governance instrument (GR-rule candidate), not a capability.

## 1. Problem

The project runs two disciplined tracks: CAPABILITY (is the primitive built? -
proven by the adversarial tests) and CLAIM (is a stated property defensible? -
gated by the off-record cross-model evaluates). Both are healthy. The un-tracked
third axis is WIRING: is a built capability on the DEFAULT path, exercised END TO
END with no test-only shortcuts, and TRANSPORTED across hosts? Prototype-drift
lives here - it accumulates silently as built-but-unwired capability and as claims
that outrun what is wired. This gate converts that drift into a deterministic,
blocking, fail-closed signal.

## 2. The one principle

No readiness fact is ever human-attested. Every readiness flag is DERIVED from a
named test, or it is false. A true flag with no named proof test is a gate
failure, not a warning. The gate's only inputs are (a) which test proves a
property (declared in the manifest, reviewable) and (b) whether that test exists
and passes (machine fact). A readiness value a person can type without a test
behind it is exactly the bookkeeping this gate exists to detect.

## 3. The manifest (single source of truth)

`EVIDENCE/readiness.json` is the sole source of readiness truth. STATE.md and the
ledger REFERENCE it; they never restate readiness in prose (prose drifts; that is
the STATE-delivery-omission family). Schema (`schema_version: 1`):

- `capabilities`: a map name -> the four flags `built`, `wired_to_default`,
  `exercised_e2e`, `transported`. Each flag is an object
  `{value: bool, proof: <test id or null>, blocked_by: <reason or null>}`.
  - `value: true` REQUIRES a non-null `proof` (the named test that proves it).
  - `value: false` REQUIRES a non-null `blocked_by` (why it is not yet wired).
- `deployment_predicates`: the three named predicates (section 4), each
  `{green: bool, proof: <test id or null>, blocked_by: <reason or null>}` under
  the same true-needs-proof / false-needs-reason rule.

Rejected alternative (do not revisit): scanning STATE/ledger prose for readiness
claims. Rejected for fragility - prose-parsing is non-deterministic and would
itself become false confidence. Readiness lives ONLY in the structured manifest.

## 4. The three deployment predicates

1. DEFAULT_SECURE - `pep.py`'s DEFAULT forward (no opt-in flags) emits an envelope
   that carries a valid `issuer_signature` which `verify_envelope` accepts. The
   mandatory signing cutover lands at VL-047: `pep.py`'s default forward signs, a gate
   configured with no signing key fails closed (it does not downgrade to unsigned), and
   the canary `test_unsigned_path_unchanged_forge_still_accepted` is retired in favor of
   `test_default_path_is_signed_and_forge_refused`. DEFAULT_SECURE goes green at that
   cutover and its predicate test becomes a real regression gate (the xfail marker
   removed). Cross-host transport is explicitly NOT asserted by this predicate - that is
   END_TO_END_NO_SHORTCUT (G5).
2. END_TO_END_NO_SHORTCUT - the whole chain runs with NO test-only shortcut:
   caller -> gate -> signed envelope -> TRANSPORT -> target verifies the
   transported artifact against the published record -> admit/refuse. A shortcut
   is any step present ONLY in tests and absent in deployment: hand-built
   envelopes, in-process key injection bypassing the real key path, a loopback
   stub standing in for cross-host transport, or a target importing the gate's
   internals instead of verifying a transported artifact. GREEN at VL-048: the
   signed cross-host chain runs over real loopback transport via the production
   fetch path with no shortcut (the gate signs on its DEFAULT path via the
   production env-var key path; a target on a separate process with a genuinely
   divergent local disk fetches the published record over a real socket and
   verifies the issuer signature against an out-of-band-pinned key AND currency
   against the fetched record AND interaction binding). The proof of record is
   the runner EVIDENCE/proofs/g5_signed_cross_host_001_runner.py (a real
   two-process, real-socket, divergent-disk run; named in EVIDENCE/readiness.json
   as the exercised_e2e / transported proof and run in the author's real
   environment). The predicate's enumerated dependency set is exactly
   {issuer_signing, enforcement_push}: those are the capabilities the signed
   chain exercises end-to-end over transport. issuer_key_expiry,
   issuer_key_revocation, and root_rotation are deliberately NOT in the set -
   they are not on the default signed chain (expiry: the default forward stamps
   no not_after; revocation / rotation: target-side record posture, the
   ROOT_RECOVERY predicate's territory). Quantifying the green-consistency check
   over ALL capabilities would make green require ROOT_RECOVERY's work and is
   incoherent with it being a separate red; the consistency check in
   IMPLEMENTATION/readiness.py therefore quantifies over this enumerated set
   (the validate_manifest honesty check still quantifies over every capability -
   only the predicate-green consistency narrows). Honest bound: green does NOT
   assert true multi-machine / TLS (the named G5 floor; deployment), and does
   NOT close the A3b freshness sub-class (a stale-but-anchor-matching, validly
   signed record is still honored; reassert checks repo-state currency, not
   request liveness).
3. ROOT_RECOVERY - a deployment can rotate a root on schedule without redeploying
   every target, and refuse a retired/revoked root (the VL-043 buildable sub-case;
   compromise recovery's out-of-band re-pin is the named non-goal). RED today:
   VL-043 not built.

## 5. Allowed vs forbidden states

- ALLOWED: `built: true` with the wiring flags false. That is build-then-wire
  working as intended - building ahead of wiring is the method, not debt.
- FORBIDDEN (gate fails): any flag or predicate `true`/`green` whose named proof
  test does not exist (and, in-repo, does not pass). Claiming a property ahead of
  the test that proves it is the drift this gate blocks.

## 6. Fail-closed semantics

Any predicate red is reported, not silently passed. The two predicate tests that
are RED by design ship as DECLARED xfail (an xfail whose reason names the blocker),
so the suite is green-with-declared-xfail rather than silently broken - the red is
visible and named, never hidden by a skip. A true flag without its proof test is a
hard suite failure. Same posture as canon section 9 elsewhere.

## 7. The honest ceiling (stated so the gate is never oversold)

This gate catches claim-vs-wiring divergence and makes the build go RED the moment
the documentation and the system diverge. It does NOT make the wiring happen - the
signing cutover, real transport (G5), and root recovery are real engineering it
cannot perform. Its only guarantee: you can never MISCOUNT how close the system is,
and you can never commit a readiness claim ahead of its test. If this gate ever
ships all-green in the current state, it is broken - the correct initial state is
mostly red.

## 8. What goes green, when

- DEFAULT_SECURE: the day the mandatory signing cutover lands (the canary flips).
- END_TO_END_NO_SHORTCUT: green at VL-048 - the signed cross-host chain runs over
  real loopback transport via the production fetch path with no shortcut (proof
  of record EVIDENCE/proofs/g5_signed_cross_host_001_runner.py); dependency set
  {issuer_signing, enforcement_push} per section 4.
- ROOT_RECOVERY: the day VL-043's planned-rotation + per-root-status build lands
  and is wired.
These three reds are the finite, ordered road from prototype to working system.

## 9. Canon basis

No new invariant; admissibility (AC^3 AND T^26 AND CCS, `evaluate()`) untouched;
not in the admission path. This is a repo-governance gate. Formalized at VL-048
as governance rule GR-2 (readiness is test-derived, never human-attested) in
`docs/MAINTENANCE_PROTOCOL.md`. No follow-up cross-model evaluate is
required - the gate makes no claim about the world, so the CLAIM track does not
apply.
