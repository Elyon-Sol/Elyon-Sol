# 23 - Wiring the signed published-record freshness reader onto the default consult path

Repo path: docs/restructure/23_published_record_freshness_wiring_spec.md. Increment VL-091. The
WIRE half of B1 (VL-074 built the reader unwired; this is the seam-then-wire step, parity with the
VL-039 transport seam wired at VL-060). Closes the A3b sub-case (b) record-freshness gap for a
configured deployment: a stale-but-anchor-matching published record is now REFUSED, not honored.

## 1. Purpose and scope

The reference target's default consult (VL-061) fetches the byte-anchor published record
(`published_source.fetch_published_record`) and anchor-verifies the BYTES. That has no temporal
dimension: a stale record whose bytes still match the pinned anchor is honored arbitrarily later
(A3b sub-case (b)). VL-074 built the signed-record reader `published_record_source.py` (publisher
signature + `not_after` + monotonic serial -> `REF_VERIFY_PUBLISHED_RECORD_STALE`) but left it with
no caller. This increment gives it a caller on the reference target.

In scope (VL-091):
- `reference_target.py`: a SIGNED consult MODE. When the target is configured with a pinned
  publisher key (`ELYON_PUBLISHER_KEY_ID` + `ELYON_PUBLISHER_KEY_HEX`, optional
  `ELYON_SIGNED_RECORD_URL`), it fetches the SIGNED record via `fetch_signed_record`, which
  validates the publisher signature + freshness + serial, and uses the validated record (a drop-in
  `record_source` carrying the three currency pins) for `verify_envelope`. A STALE or INVALID
  record fails closed with the reader's reason code. When NO publisher key is configured (every
  existing runner and test), the byte-anchor path is UNCHANGED.
- `publisher.py`: a `/published_hashes_signed.json` endpoint that signs the LIVE currency pins with
  a configured publisher key (`ELYON_PUBLISHER_SIGNING_KEY_HEX` + `ELYON_PUBLISHER_KEY_ID`) and a
  `not_after` window (`ELYON_RECORD_MAX_AGE_SECONDS`, default 300), re-signed fresh per request.
  Absent the signing key it 503s (the byte-anchor endpoint is unchanged).
- Tests: the target in signed mode honors a fresh signed record, refuses a STALE one
  (`REF_VERIFY_PUBLISHED_RECORD_STALE`) and an INVALID one; the byte-anchor mode is unchanged; the
  publisher signs a record the reader validates.

Out of scope (named): making signed mode the BARE default (it stays opt-in via the publisher-key
config, so the existing green path - DEFAULT_SECURE / END_TO_END / ROOT_RECOVERY and the g4/g5
runners - is untouched); the shared-replay-cache wire (B3, separate); the real-publisher-key trust
distribution (the publisher key is the load-bearing floor, out-of-band, parity B-prime-2/VL-042).

## 2. The trust-model shift (honest)

Byte-anchor mode pins the record BYTES (sha256). Signed mode pins a publisher PUBLIC KEY, so the
record may be reissued (new serial / not_after) under a STABLE pin and a stale record fails closed.
This relocates trust from the record bytes to the publisher key (the same floor the key/root
records already introduced, VL-042/044). A deployment chooses byte-anchor (no freshness, simplest)
or signed (freshness, a publisher-key floor) by configuration.

## 3. Fail-closed / no new invariant

Signed mode fails closed on every reader fault (transport / bad signature / unknown key -> INVALID;
expired / serial-rollback -> STALE). The validated record feeds the unchanged `verify_envelope`
currency + binding checks; freshness is an ADDITIONAL gate before currency, not a replacement. No
canon / evaluator / MANIFEST / envelope change (canon section 14): freshness bounds how LONG a
record is usable; it adds no canonical invariant (the VL-074 basis).

## 4. Honest ceiling

This wires freshness for a CONFIGURED reference target; the bare default stays byte-anchor. It
does not make the publisher key trustless (root/publisher compromise is the named floor) and it is
single-host loopback until the real-transport deployment carries it (the REAL_TRANSPORT tier).
Closing A3b-b here means: a configured target REFUSES a stale published record; it does not change
the external-attacker (G5) line.

## 5. Acceptance (VL-091)

- `TESTS/adversarial/test_record_freshness_wiring.py`: the reference target in SIGNED mode honors a
  fresh signed record, refuses a STALE record (`REF_VERIFY_PUBLISHED_RECORD_STALE`) and an INVALID
  record (`REF_VERIFY_PUBLISHED_RECORD_INVALID`); the byte-anchor mode (no publisher key) is
  unchanged; the publisher's `/published_hashes_signed.json` serves a record the reader validates.
- The full suite stays green; the existing reference-target / g4 / g5 byte-anchor path is unchanged
  (no publisher key configured).
