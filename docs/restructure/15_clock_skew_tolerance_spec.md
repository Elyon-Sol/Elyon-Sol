# 15 - Cross-host clock-skew tolerance: a configurable window on the freshness checks

Repo path: docs/restructure/15_clock_skew_tolerance_spec.md. Increment VL-075 (B2,
artifact 13 Phase B). Adjacent to `14_published_record_freshness_spec.md` (B1, record
freshness): B1 gave the published record a signed `not_after`; this increment makes every
consume-side `not_after` (and the symmetric `not_before`) comparison tolerate a bounded
clock divergence between the issuer/publisher and the consuming target.

## 1. Purpose and scope

The freshness checks added across VL-041 (decision `not_after`), VL-042 (issuer-key validity
window), and VL-048/049/074 (the signed key / root / published record `not_after`) all compare
the consumer's wall clock against a timestamp the ISSUER stamped. They assume the two clocks
agree. On a real cross-host deployment they do not: NTP keeps independent hosts within a bounded
error, not in lockstep. With a strict `now < not_after`, a target whose clock runs slightly ahead
of the issuer will refuse a decision or record the issuer still considers fresh - a false REFUSE
caused by skew, not by staleness. This is the gap the artifact-13 directive names B2.

In scope (VL-075): a single configurable `clock_skew` parameter (a `datetime.timedelta`, default
`timedelta(0)`) on each consume-side freshness check, widening the honored window symmetrically by
`clock_skew` on both ends; an explicit NTP / max-skew assumption; tests for in-window-by-skew
(accepted) and out-of-(window+skew) (refused), and that `clock_skew=0` is byte-behavior-identical
to the prior strict checks. Out of scope (named, not built): wiring a non-zero skew onto the
default `pep.py` / `reference_target.py` chain (that is a deployment-configuration choice, with its
own VL if it lands as a default); true multi-machine + TLS transport (the G5 floor); secure time
distribution (the skew window assumes NTP, it does not provide it).

## 2. The skew model (consume-side, symmetric, default-off)

A timestamp window `[not_before, not_after)` stamped by the issuer is interpreted by the consumer
as `[not_before - clock_skew, not_after + clock_skew)`. Equivalently:

- An expiry check `now < not_after` becomes `now < not_after + clock_skew`.
- A start check `not_before <= now` becomes `not_before - clock_skew <= now`.
- A two-sided window `not_before <= now < not_after` becomes
  `not_before - clock_skew <= now < not_after + clock_skew`.

The widening is on the CONSUME side only - no issuer stamps a wider window, and nothing on the
wire changes. `clock_skew` is the maximum absolute clock divergence the deployment is willing to
tolerate: set it to cover the realistic NTP error between the hosts (seconds, not hours), and no
larger. The default is `timedelta(0)`: with no skew configured, every check is byte-behavior-
identical to its strict pre-VL-075 form (`not_after + timedelta(0) == not_after`), so the default
path, the committed evidence runners, and the existing freshness tests are unaffected.

`clock_skew` must be non-negative. A negative value would NARROW the window (stricter than the
issuer intended) and is treated as a configuration error: each entry point raises `ValueError`
rather than silently applying it. This is a setup-time guard (the operator chooses the skew), not
an adversary-facing path; it fails loud, consistent with `sign_envelope`'s refusal to stamp a
tz-naive `not_after`.

## 3. The checks made skew-tolerant

All four consume-side loci, each gaining a `clock_skew: timedelta = timedelta(0)` parameter
appended last (positional-call compatibility, the VL-042 `key_record_view` convention):

1. `verifier.verify_envelope` - DECISION freshness (step 1.5b, the signed-envelope `not_after`,
   VL-041): `current >= not_after` becomes `current >= not_after + clock_skew` ->
   `REF_VERIFY_SIGNATURE_EXPIRED`. This is the "decision freshness" half the directive names.
2. `verifier.verify_envelope` - ISSUER-KEY validity window (step 1.5, the `key_record_view` path,
   VL-042): `not (not_before <= current < not_after)` becomes
   `not (not_before - clock_skew <= current < not_after + clock_skew)` ->
   `REF_VERIFY_KEY_OUT_OF_WINDOW`. This is the symmetric `not_before` case ("where relevant").
3. `published_record_source.load_signed_record_from_bytes` / `fetch_signed_record` - the signed
   PUBLISHED record `not_after` (VL-074): `now < record_not_after` becomes
   `now < record_not_after + clock_skew` -> `REF_VERIFY_PUBLISHED_RECORD_STALE`.
4. `key_record_source` and `root_record_source` `load_*` / `fetch_*` - the signed KEY and ROOT
   record `not_after` (VL-042 / VL-048): same record-level widening, ->
   `REF_VERIFY_KEY_RECORD_STALE` / `REF_VERIFY_ROOT_RECORD_STALE`.

The per-entry KEY/ROOT windows (the `not_before`/`not_after` each key or root entry carries) are
parsed by the readers into the trust/status view and TIME-CHECKED at the verifier consume side
(locus 2), so the skew is applied once, there - the readers store the raw windows unchanged. Only
the record-level `not_after` (the record's own liveness) is widened inside the readers.

The serial-monotonicity rollback check is untouched: a serial is an integer counter, not a clock
reading, so skew does not apply to it.

## 4. Fail-closed ordering preserved

Skew widens the time window; it changes no other gate. Structural validation, key selection,
signature verification, revocation, and serial-rollback all run before and independent of the
skew-adjusted time comparison, in the same order. A forged or unknown-key record is still rejected
on provenance before any freshness arithmetic; a tz-naive or unparseable `not_after` still fails
closed (it cannot be compared, with or without skew). Skew only moves the boundary at which a
structurally-valid, correctly-signed, in-serial record/decision is judged fresh-vs-stale.

## 5. Canon basis (no new invariant - canon section 14)

A skew window is a tolerance on the existing revalidation check (canon section 13), not a new
admissibility invariant. The target still only verifies and acts / refuses; AC^3, T^26, and
manifest-integrity are unchanged. Canon section 8.2's "the choice of anchoring system is
implementation-dependent" extends to the choice of time source and its assumed error bound; this
spec records that the bound is a deployment parameter and that its default is zero (perfectly
synchronized clocks, the prior assumption). No new canonical invariant (parity with `14`
section 8).

## 6. Honest ceiling

A skew window trades a bounded amount of staleness for resilience to clock divergence: a record or
decision remains honored for up to `clock_skew` beyond its true `not_after`. Therefore `clock_skew`
is a security-relevant knob, not free latitude - it should be the smallest value that covers the
deployment's real NTP error, and it is the operator's to justify. The window assumes the clocks ARE
within `clock_skew` of true time; it does not enforce that (it cannot - that is what NTP, or a
secure time source, is for). And, exactly as in `14` section 9, this increment is capability-
present-and-default-off: with `clock_skew=0` (the default, and the only value any committed caller
passes today) nothing on the live chain changes. The claim this increment earns is precisely: "the
freshness checks accept a configurable, symmetric, non-negative clock-skew window, default zero,"
not "the gate tolerates clock skew end-to-end on the default path."
