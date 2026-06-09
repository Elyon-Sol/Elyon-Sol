# 14 - Published record freshness (B-prime-1 signed): the temporal half of cross-host currency

Repo path: docs/restructure/14_published_record_freshness_spec.md. Increment VL-074 (B1,
artifact 13 Phase B). Sibling to `09_key_record_spec.md` (B-prime-2) and
`11_root_record_spec.md` (B-prime-3): it applies the same signed-record trust model to the
published HASH record that `IMPLEMENTATION/published_source.py` serves under the byte-anchor
model (B-prime-1 original).

## 1. Purpose and scope

A3b sub-case (b) - record freshness - is the open temporal gap recorded in
`docs/restructure/04_current_vs_claimed.md` (G5 / A3b): a stale-but-anchor-matching published
record can still be honored cross-host, because `envelope.reassert(record_source=...)` checks
the record's hashes, not its liveness, and the byte-anchor reader has no temporal dimension at
all. The decision-freshness half (sub-case a) closed at VL-065; the in-window exactly-once half
closed at VL-066. This increment closes the record-freshness half: it gives the published record
a signed `not_after` and a monotonic `serial`, and a reader that refuses a stale record.

In scope (VL-074): the signed published-record format; a signing generator; a reader that
verifies a publisher signature and enforces freshness; the two refusal codes; the acceptance
test that flips a stale record from honored to refused. Out of scope (named, not built): wiring
the signed reader onto the default `reassert()` / `verify_envelope()` / `reference_target`
consult path (a later increment); cross-host clock-skew tolerance (Phase-B item B2); true
multi-machine + TLS transport (the G5 floor).

## 2. The trust-model shift (byte-anchor -> signed record)

B-prime-1 original (`published_source.py`) pins the sha256 of the record BYTES
(`anchor_sha256`). That pin has two consequences this increment must respect and one it must
fix:

- It is BYTE-EXACT and load-bearing for the committed `EVIDENCE/published_hashes.json` and its
  consumers (the g4/g5 runners, the pinned-anchor tests). This increment leaves it byte-
  unchanged (build-then-wire; section 7).
- It has NO temporal dimension: a captured record verifies forever as long as its bytes are
  unchanged, so freshness cannot even be expressed, let alone checked. This is the gap.

B-prime-1 signed (this spec) pins a PUBLISHER PUBLIC KEY and verifies a publisher SIGNATURE over
a record that carries `serial` + `not_after`. Because the trust anchor is a stable key rather
than a byte hash, the record may be reissued (new serial, new window) under the SAME out-of-band
pin, and a stale record fails closed. This is exactly the B-prime-2 shift (`09` section 3),
applied to the hash record.

## 3. The signed published record

A single JSON object. Only `publisher_signature` is excluded from the signed region; every other
field (serial, not_after, and all three currency pins) is covered by the signature, so an
adversary cannot extend the window, roll the serial back, or swap a pin without breaking it.

    {
      "format": "elyon-sol-published-record",
      "version": 1,
      "publisher_key_id": "<stable id of the pinned publisher key>",
      "serial": <non-negative int, monotonic across reissues>,
      "issued_at": "<ISO-8601 tz-aware>",
      "not_after": "<ISO-8601 tz-aware>",
      "canon_version": "0.9.8.4",
      "canon_sha256": "<hex>",
      "evaluator_version": "0.9.8.4",
      "evaluator_sha256": "<hex>",
      "manifest_version": "1.0",
      "manifest_sha256": "<hex>",
      "publisher_signature": "<hex over canonical_json(record minus publisher_signature)>"
    }

The three currency pins (`canon_sha256`, `evaluator_sha256`, `manifest_sha256`) are derived LIVE
from `EVIDENCE/published_hashes_gen.build_record` (constraint (i): never hand-copied), so the
signed record wraps exactly the pins `build_envelope()` and the byte-anchor record carry. The
validated record is therefore a drop-in `record_source` for `reassert()` once a caller chooses
to use it.

Custody: like the key record (`09` section 6), the signed published record is a RUNTIME artifact
- re-signed on a schedule with a fresh serial and window - and is NOT committed. The publisher
PRIVATE key is never persisted to the repo; the generator takes a duck-typed signing object.

## 4. Freshness (designed in, not optional)

The reader enforces, in order, each fail-closed:

1. `now < not_after` (STRICT; `now == not_after` is stale). A tz-naive or unparseable
   `not_after` fails closed to STALE - it cannot be safely compared, and the freshness layer
   owns the field (parity with `09` section 5).
2. `serial` monotonicity: if the caller supplies `last_seen_serial`, a record whose `serial` is
   strictly less is a rollback and is STALE. (Persisting `last_seen_serial` is the caller's
   stateful concern, exactly as the key reader treats it; the default reader call is stateless
   and checks only `not_after`.)

`now` is injectable for deterministic tests; it defaults to `datetime.now(timezone.utc)`.

## 5. The record reader

`IMPLEMENTATION/published_record_source.py`, a SIBLING of `key_record_source.py`, three layers:

- `load_signed_record_from_bytes(record_bytes, pinned_publisher_keys, now=None,
  last_seen_serial=None)` - the pure, network-free trust check. Order: parse + structural
  validation -> select pinned publisher key by `publisher_key_id` -> verify `publisher_signature`
  -> freshness -> return the validated record. Returns `{"record": <dict>, "reason": None}` on
  success or `{"record": None, "reason": <REF_VERIFY_PUBLISHED_RECORD_*>}` on any fault.
- `fetch_signed_record(publisher_url, pinned_publisher_keys, ...)` - the transport: `requests.get`
  over loopback (the B-prime-1/2 transport model), then the pure check. Any connection / non-200
  / timeout fails closed to INVALID.

The reader imports `cryptography` (to reconstruct the publisher public key) and reuses
`canonical_json` from `envelope.py` so gen-side and reader-side canonicalization match exactly.
The pinned publisher key is held OUT-OF-BAND and is never fetched alongside the record.

## 6. Reject codes (closed set, parallel to the key-record codes)

Defined canonically in `verifier.py` (the `REF_VERIFY_*` home) and imported by the reader:

- `REF_VERIFY_PUBLISHED_RECORD_INVALID` - parse failure, structural fault, unknown
  `publisher_key_id`, or signature verification failure.
- `REF_VERIFY_PUBLISHED_RECORD_STALE` - `not_after` reached/passed (or unparseable), or a serial
  rollback against `last_seen_serial`.

INVALID vs STALE is the same discrimination the key reader draws (`09` section 9): a record that
never had standing vs a once-valid record that has aged out.

## 7. Build-then-wire boundary

This increment BUILDS the signed reader and signer; it does NOT WIRE them onto the default
consult path. `published_source.py` (the byte-anchor reader), `EVIDENCE/published_hashes.json`
(the committed byte-anchor record), `reassert()` / `verify_envelope()`, `reference_target.py`,
and `pep.py` are byte-unchanged, so the full suite and the named g4/g5 regression runners are
unaffected (no `evaluator_sha256` roll - no hashed-file edit). The wiring step - making the
target consult `fetch_signed_record` and fail on STALE on the live chain - is a later increment
with its own VL, mirroring how VL-039's transport seam was wired at VL-060.

## 8. Canon basis (no new invariant - canon section 14)

Validating a fetched record is verification I/O. The target still only verifies and acts /
refuses; it does not execute. This operationalizes canon section 11.9 (the manifest must be
deterministic, versioned, and integrity-verifiable, extended to the canon/evaluator pins), canon
section 13 (revalidation - a stale record forces re-fetch rather than honoring an aged decision),
and canon section 8.2 (the choice of anchoring system is implementation-dependent; a pinned
publisher key is such a choice). No new canonical invariant (parity with `09` section 10).

## 9. Honest ceiling

The freshness window bounds how LONG a captured record is usable; it does not, alone, make
cross-host currency trustless - the pinned publisher key is now the single load-bearing anchor
for the hash record (root-compromise-is-total, the same floor as B-prime-2). Clock-skew between
the publisher and the target is unmodeled here and is the adjacent named-open item (B2): with no
skew tolerance, `now < not_after` assumes synchronized clocks. And until the wiring step lands
(section 7), this reader defends nothing on the default path - it is build-then-wire, capability
present and unwired. The claim this increment earns is precisely: "a stale signed published
record is refused by the new reader," not "the gate refuses stale records end-to-end."
