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

## 4. The deployment predicates (three canonical + the REAL_TRANSPORT tier)

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
   every target, and refuse a retired/revoked root (the planned-rotation +
   per-root-status sub-case; compromise recovery's out-of-band re-pin is the
   named non-goal). The mechanism is BUILT at VL-044 (capability root_rotation,
   proof TESTS/adversarial/test_root_record.py; transitive-designation soundness
   evaluated SOUND 3-0 at VL-044 follow-up). GREEN at VL-049: a planned in-band
   R1->R2 rotation is consulted TARGET-side on the signed cross-host chain over
   real transport with no test-only shortcut. On the chain the gate's DEFAULT
   forward already drives (VL-047/048), the target additionally fetches the root
   record and the key record over real sockets (production fetch_root_record /
   fetch_key_record), builds the validated root-status + key-record views, and a
   target pinning ONLY R1 comes to honor a gate-signed envelope whose issuer key
   is vouched by a key record signed by the designated-active R2, with no re-pin;
   a revoked or retired signing root is refused (REF_VERIFY_ROOT_REVOKED /
   REF_VERIFY_ROOT_RETIRED) and any fetch failure or stale record fails closed.
   The gate's DEFAULT forward is UNCHANGED (it already signs; rotation is a
   target-trust-source concern, not a gate-signing one); "wired to the default
   path" here means consulted on the live no-shortcut chain the default forward
   drives, target-side, exactly as END_TO_END's target fetch+verify is part of
   that chain. The predicate's enumerated dependency set is exactly
   {root_rotation, issuer_key_revocation}: the rotation primitive plus the
   key-record path that lets R2 vouch the issuer key without a re-pin (the
   consistency check in IMPLEMENTATION/readiness.py quantifies over this set, the
   same narrowing as END_TO_END; validate_manifest still quantifies over every
   capability). The proof of record is the runner
   EVIDENCE/proofs/root_recovery_cross_host_001_runner.py (a real two-process,
   real-socket, divergent-disk run extending VL-048's transport; named in
   EVIDENCE/readiness.json as the exercised_e2e / transported proof and run in
   the author's real environment). Honest bound: green is PLANNED in-band
   rotation + per-root status ONLY; root-key COMPROMISE recovery is irreducibly
   out-of-band (artifact 11 section 2, the named non-goal), and green does NOT
   assert true multi-machine / TLS (the G5 floor; deployment).
4. REAL_TRANSPORT - the deployment tier added at VL-083 (artifact 13 C4; foreseen
   as option (b) in 12_g5_transport_design.md). GREEN only when the VL-079 attack
   suite is DEFEATED over real cross-host TLS by
   EVIDENCE/proofs/attack_suite_live_runner.py against a real C1/C2 stand-up (the
   gate-1 referent, external_verification_readiness.md) - NOT the loopback model
   the other three run on. RED by design today: no real surface exists in-sandbox,
   and its blocked_by names the runner + the real-host requirement. It is NOT in
   PREDICATE_NAMES and is therefore NOT counted in the canonical summary (which
   stays 3-of-3) until the author greens it naming the live run's log - this keeps
   the three canonical predicates' green count honest while the new tier is still
   tracked and honesty-checked by validate_manifest like any predicate (a false
   green requires a named blocked_by, which it carries). Honest bound: even a green
   REAL_TRANSPORT is the author's OWN scripted attack over real transport; a real
   EXTERNAL attacker remains the G5 / GR-3 finish line.

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
- ROOT_RECOVERY: green at VL-049 - a planned in-band R1->R2 rotation is consulted
  target-side on the signed cross-host chain over real transport with no shortcut
  (proof of record EVIDENCE/proofs/root_recovery_cross_host_001_runner.py);
  dependency set {root_rotation, issuer_key_revocation} per section 4. The
  VL-044-built mechanism wired onto the VL-048 transport; the gate's default
  forward is unchanged.
These three reds are the finite, ordered road from prototype to working system.

## 9. Canon basis

No new invariant; admissibility (AC^3 AND T^26 AND CCS, `evaluate()`) untouched;
not in the admission path. This is a repo-governance gate. Formalized at VL-048
as governance rule GR-2 (readiness is test-derived, never human-attested) in
`docs/MAINTENANCE_PROTOCOL.md`. No follow-up cross-model evaluate is
required - the gate makes no claim about the world, so the CLAIM track does not
apply.
