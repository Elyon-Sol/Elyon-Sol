# 09 - Published signed key record (B-prime-2): revocation, rotation, and the new trust root

Status: SPEC (Checkpoint B). This artifact defines the VL-042 change before any
code commit (spec-defines-the-change). The build (VL-042) is derived from this
artifact; the framework-level cross-model evaluate on the new trust root is
drafted separately and run off-framework after the build commit, and only its
verdict-of-record is folded (VL-042 follow-up).

Canon basis: sections 8.2 (PoE), 9 (fail-closed), 11.9 (integrity-verifiability),
14 (identity-agnostic, under the narrowed reading recorded at VL-040 follow-up 2).
No new invariant. Verifier-layer; orthogonal to reassert() / CCS currency.

Cited inputs: VL-040 (issuer signing, opt-in), VL-040 follow-up 2 (key-governance
evaluate: forgery-resistance BOUNDED; key lifecycle the load-bearing floor),
VL-041 (issuer-key expiry, opt-in; undetected compromise time-bounded),
VL-038 / `IMPLEMENTATION/published_source.py` (the B-prime-1 record anchor this
artifact mirrors), VL-039 follow-up (freshness is load-bearing for a published
anchor - the finding that recurs one layer up here).

---

## 1. Purpose and scope

VL-041 time-bounded an UNDETECTED issuer-key compromise via a signed-region
`not_after`: a leaked key is useful only until its envelope-stamped expiry, and
that bound holds without detecting the leak. It does NOT reach a DETECTED
compromise: there is no way to INSTANTLY kill a key a deployment has decided is
bad, and there is no published statement of which issuer keys are currently
valid. Trust today is a static `{key_id: public_key}` map handed to the verifier
(VL-040/041): no revocation, no rotation, no published record.

This increment (B-prime-2) adds the complement: a published, integrity-anchored,
signed key record that a target consults to learn which issuer keys are currently
valid or REVOKED, with the record carrying its own freshness bound so a stale
record fails closed. It closes the detected-compromise instant-kill case that
expiry could not reach, and it relocates trust from N per-issuer pins to ONE
pinned publisher/root key.

In scope: the record format (a new published artifact), a reader that validates
it (publisher signature, freshness, per-key status), and a verifier consultation
path that sources issuer-key trust from the validated record. Out of scope and
named-not-built: cross-host durable TRANSPORT of the freshest record (that is
G5, the same boundary as B-prime-1 at VL-038), root rotation PROCESS, the
mandatory signing cutover (posture), and A1 target-side admission policy.

## 2. What "solve" can and cannot mean here (the honest ceiling)

"Solve" does NOT mean eliminating a trusted root; no PKI does. It means two
concrete things:

1. Revocation becomes POSSIBLE: a deployment consulting the current record can
   instantly refuse a key marked revoked.
2. Trust is REDUCED to one rarely-used, guarded root: the target pins ONE
   publisher/root key instead of N issuer keys; the publisher signs a record
   listing the currently-valid issuer keys.

The cost is explicit and load-bearing: the root is now SINGULAR. Root compromise
is TOTAL - an adversary holding the root private key can mint a record vouching
for any issuer key. That is the new trust floor, and it is exactly what the
new-trust-root cross-model evaluate (section 12) must bound before
"forgery-resistant" moves any further off its VL-040 follow-up 2 bound.

The honest-recovery test for this increment (definition of done, restated at
section 13): can a deployment now INSTANTLY refuse a key it has decided to
revoke, and refuse a stale key record? If the design cannot state that path
concretely, it has not closed the case it set out to.

## 3. The trust-model shift

VL-040 follow-up 2 established (3-0 convergent) that pinning a key buys issuer
PROVENANCE, and that the static map newly requires four obligations:
distribution, rotation, compromise-handling, revocation. VL-041 addressed the
undetected-compromise sub-case of compromise-handling (expiry). This increment
acts on revocation, rotation, and distribution, all via the record:

- Before: target holds `{key_id: public_key}` (N pins). To revoke, the operator
  must somehow re-distribute a new map to every target out-of-band. No standard
  mechanism; no freshness; a target with a stale map trusts a revoked key
  forever.
- After: target pins one `{root_key_id: root_public_key}`. The publisher signs a
  record listing the valid issuer keys with per-key windows and explicit revoked
  flags, plus the record's own freshness bound. Revocation is a publisher action
  (mark revoked, bump serial, reissue, publish); a target consulting the current
  record honors it immediately.

The static-map path is preserved unchanged (section 8): a deployment that
supplies no record gets exactly VL-040/041 byte-behavior.

## 4. The signed key record (`EVIDENCE/published_keys.json`)

Generated live by `EVIDENCE/published_keys_gen.py` (never hand-copied; the
constraint that governs `published_hashes_gen.py`). JSON, ASCII (`ensure_ascii=True`
per VL-009). Shape:

```
{
  "format": "elyon-sol-key-record",
  "version": 1,
  "root_key_id": "<string: which pinned root signed this record>",
  "serial": <non-negative integer, monotonic per root_key_id>,
  "issued_at": "<ISO-8601 tz-aware; informational>",
  "not_after": "<ISO-8601 tz-aware; the record's own staleness ceiling>",
  "keys": [
    {
      "key_id": "<string: matches an envelope's issuer_key_id>",
      "public_key": "<base64 of the raw 32-byte Ed25519 public key>",
      "not_before": "<ISO-8601 tz-aware: start of this key's validity>",
      "not_after": "<ISO-8601 tz-aware: end of this key's validity>",
      "revoked": <bool>,
      "revoked_at": "<ISO-8601 tz-aware; OPTIONAL; present iff revoked>",
      "reason": "<string; OPTIONAL; audit note>"
    }
  ],
  "publisher_signature": "<hex of Ed25519 signature over canonical_json(record minus publisher_signature)>"
}
```

Signature construction (mirror envelope/issuer signing exactly):
`publisher_signature = root_private.sign(canonical_json(record_without_publisher_signature).encode("utf-8"))`,
where `canonical_json` is the SAME function envelope.py uses, with
`ensure_ascii=True`. Only `publisher_signature` is excluded from the signed
region; everything else - `serial`, `not_after`, every key entry including its
`revoked` flag and window - is covered by the signature. This is the property
that makes the record tamper-proof: an adversary cannot extend the record's
window, un-revoke a key, bump the serial, or swap a key's public bytes without
breaking the publisher signature.

Notes:

- `revoked` is an EXPLICIT boolean rather than dropping the key from the list, so
  the verifier can emit `REF_VERIFY_KEY_REVOKED` distinctly from
  `REF_VERIFY_KEY_UNKNOWN` (decision 2: the richer trust view; decision 5: a
  distinct out-of-window code). A dropped key is UNKNOWN; a present-and-flagged
  key is REVOKED; these are different operator signals and the audit trail wants
  both.
- The key entry's `not_before` / `not_after` is the KEY's lifecycle window. It is
  DISTINCT from and orthogonal to the envelope's own `not_after` (VL-041): a key
  can be in-window while a specific envelope it signed is expired, and vice
  versa. Both are enforced (section 8 consultation order).
- `canonical_json` reuse MUST be the `ensure_ascii=True` variant. The
  `receipt.py` `ensure_ascii=False` divergence (VL-012 finding) is the known
  hazard to avoid; the gen-script and the reader must use the same
  `ensure_ascii=True` canonicalization or the signature will not verify
  cross-side.

## 5. Freshness (the recursion - designed in, not optional)

A stale-but-root-signed record predating a revocation would still list the
compromised key as valid. This is the VL-039 follow-up finding (freshness is
load-bearing for a published anchor) recurring one layer up, now for the KEY
record. Both mechanisms are specified; neither alone is honest:

- `not_after` (always-on absolute ceiling): the verifier requires
  `now < record.not_after` (strict, mirroring VL-041 envelope expiry: valid iff
  `now < not_after`). `now >= not_after` fails closed to
  `REF_VERIFY_KEY_RECORD_STALE`. A parseable but tz-naive `not_after` fails
  closed to `REF_VERIFY_KEY_RECORD_STALE` (it cannot satisfy the strict
  comparison safely); a non-parseable `not_after` is a structural fault and fails
  at the parse step to `REF_VERIFY_KEY_RECORD_INVALID`. This bound caps how long
  an adversary can hold a verifier on a frozen pre-revocation record, EVEN
  without any verifier-side state.

- `serial` (opt-in rollback gate, for state-persisting verifiers): a verifier MAY
  persist the highest `serial` it has seen per `root_key_id`. If persisted and
  `record.serial < last_seen`, fail closed to `REF_VERIFY_KEY_RECORD_STALE`
  (rollback / replay of a superseded record). `record.serial == last_seen` is
  accepted - because `serial` is inside the signed region, an equal serial
  guarantees an identical record (an adversary cannot produce a different record
  at the same serial without breaking the signature). The serial gate is
  state-dependent and therefore opt-in; `not_after` is the floor that needs no
  state.

The reader/verifier takes an injectable `now` (default
`datetime.now(timezone.utc)`), threaded through the record-freshness check, the
key-window check, and the envelope-expiry check (VL-041) so a single clock
governs all three - mirroring VL-041's `now` parameter for testability.

The freshness guarantee is only as strong as the verifier's CLOCK: a skewed-back
clock could honor a stale record within its skew (the VL-042 follow-up finding 2
carry-forward, the sibling of the artifact 11 section 5 note). This is a stated
assumption, not closeable in code without a trusted time source (out of scope).

## 6. Root key model and custody

- The root PRIVATE key is NEVER on disk and never in the repo. Live root keypairs
  exist only in the runner and the tests (the constraint that governs every key
  in this project).
- The root PUBLIC key is pinned out-of-band at the target as a duck-typed object,
  the exact analog of `pinned_public_keys` and of the B-prime-1 record-anchor
  pin: `pinned_root_keys = {root_key_id: root_public_key_object}`. The reader
  selects the pinned root by the record's `root_key_id`. A `root_key_id` not in
  `pinned_root_keys` means the record cannot be validated at all and fails closed
  to `REF_VERIFY_KEY_RECORD_INVALID` (folded into record-invalid rather than a
  separate unknown-root code; the closed set stays tight).
- Root ROTATION is schema-representable (the record names its `root_key_id`, and a
  target may pin more than one root), but the rotation PROCESS - how a new root is
  introduced and an old one retired - is named-not-built this increment, mirroring
  VL-040's "rotation: schema-representable, process-unbuilt." It is a later
  increment.

The root being singular and load-bearing is the deliberate trade of section 2.
It is the subject of the section 12 evaluate.

## 7. The record reader (the module that imports cryptography)

verifier.py and envelope.py do NOT import `cryptography` (duck-typed; the caller
supplies key objects). The record carries public-key BYTES on the wire, and
turning bytes into a verifying object calls `Ed25519PublicKey.from_public_bytes`,
which imports `cryptography`. So that reconstruction lives in the reader, not in
the verifier - keeping verifier.py import-clean (decision 2).

The reader MIRRORS `IMPLEMENTATION/published_source.py` (the B-prime-1 model) as a
sibling module `IMPLEMENTATION/key_record_source.py`; it does NOT extend it. The
source read at Checkpoint B settled this (section 14 open question 4, now resolved
in section 15): the two share a SHAPE but not a trust primitive. B-prime-1 pins
the sha256 of the record BYTES (`anchor_sha256`) - which would force re-pinning on
every revocation and so cannot serve a record that changes; B-prime-2 pins a root
PUBLIC KEY and verifies a publisher SIGNATURE, precisely so the record can change
(revoke, bump serial, reissue) under a stable pin. They also differ in import
profile (published_source.py is `cryptography`-free; this reader must import it)
and in return contract (published_source.py returns dict-or-None; this reader must
discriminate RECORD_INVALID from RECORD_STALE). What it reuses is the THREE-LAYER
SHAPE proven by published_source.py:

- a pin primitive (there `anchor_sha256` over bytes; here the pinned-root signature
  verification);
- a pure, network-free `load_key_record_from_bytes(record_bytes, pinned_root_keys,
  now=...)` that does the load-bearing trust check deterministically (verify
  publisher signature -> freshness -> build trust view), testable without a network
  exactly as `load_record_from_bytes` is;
- a thin `fetch_key_record(publisher_url, pinned_root_keys, now=..., timeout=...)`
  transport wrapper (the only network-touching layer; fail-closed to a reject on
  any connection / non-200 / timeout, mirroring `fetch_published_record`).

The freshness check (`now`) lives in the PURE loader so it is deterministically
testable, mirroring published_source.py's placement of the whole trust check in
`load_record_from_bytes`. The pinned root, like B-prime-1's pinned anchor, is held
out-of-band and is NEVER fetched alongside the record (that would be circular - the
published_source.py docstring's exact caution, carried up one layer).

Responsibilities of the pure loader, in order:

1. Load the record (from a path now; durable cross-host fetch is G5).
2. Parse JSON and structurally validate (required fields present, correct types,
   parseable timestamps). Any structural fault -> `REF_VERIFY_KEY_RECORD_INVALID`.
3. Select the pinned root by `root_key_id`. Unknown root ->
   `REF_VERIFY_KEY_RECORD_INVALID`.
4. Verify `publisher_signature` over `canonical_json(record minus
   publisher_signature)` against the selected pinned root. Failure ->
   `REF_VERIFY_KEY_RECORD_INVALID`.
5. Freshness (section 5): `now < not_after` (strict); serial monotonic if state
   persisted. Failure -> `REF_VERIFY_KEY_RECORD_STALE`.
6. Build the per-key TRUST VIEW. For each key entry, reconstruct the public-key
   object via `from_public_bytes` and carry status:
   `{key_id: {"public_key": <obj>, "revoked": <bool>, "not_before": <dt>,
   "not_after": <dt>}}`.
7. Hand the trust view to `verify_envelope`.

The reader fails closed on every record-state path. It returns either a validated
trust view or a single reject reason; it never returns a partially-trusted view.
This is a deliberate contract DIVERGENCE from `published_source.py`, whose pure
loader returns dict-or-None with no discrimination: B-prime-2 must distinguish
`REF_VERIFY_KEY_RECORD_INVALID` (bad publisher signature, unknown root, malformed)
from `REF_VERIFY_KEY_RECORD_STALE` (freshness / serial), so the loader returns the
reject reason rather than a bare None (decisions 2 and 5; the exact Python return
shape is a build detail, e.g. a `{trust_view, reason}` pair, parallel to
`verify_envelope`'s own `{accepted, reason}`).

## 8. Verifier consultation

`verify_envelope` gains a trust-view source:

```
verify_envelope(envelope, interaction, target_url,
                pinned_public_keys=None,   # VL-040/041 static map
                record_source=None,        # VL-039 hash record -> reassert() currency
                key_record_view=None,      # B-prime-2 validated issuer-key trust view
                now=None)
```

Note - two DISTINCT "record" inputs, do not conflate them. `record_source` already
exists (VL-039 / B-prime-1, confirmed in `published_source.py`'s docstring): it is
the published HASH record (canon / evaluator / manifest), fed to `reassert()` for
the CURRENCY check. `key_record_view` is the NEW B-prime-2 input: the validated
issuer-KEY trust view, for issuer-key trust selection. They are orthogonal and may
both be present (currency from the hash record; issuer trust from the key record).

Precedence (decision 3 - record-exclusive-when-present, NOT augment/union):

- `key_record_view` supplied -> it is the SOLE issuer-key trust source;
  `pinned_public_keys` is NOT consulted. Rationale: union undermines the one thing
  the record exists to do. If a key were revoked in the record but vouched for by
  the static map, a union verifier would still accept it - so the static map could
  silently defeat a revocation. Record-exclusive forecloses that. The
  local-pins-plus-CA hybrid is a real PKI pattern but reintroduces exactly this
  hazard, so it is a named future knob, not the default.
- `key_record_view` is None -> fall back to `pinned_public_keys` (VL-040/041
  byte-behavior, unchanged).
- Both supplied -> record-exclusive (the static map is ignored), documented.
- Neither supplied -> the unsigned path (VL-040 byte-behavior; no signature
  required).

Lookup of the envelope's `issuer_key_id` in the trust view, in this order (REVOKED
takes precedence over OUT_OF_WINDOW because it is the stronger operator signal):

1. absent from the view -> `REF_VERIFY_KEY_UNKNOWN`
2. present and `revoked` -> `REF_VERIFY_KEY_REVOKED`
3. present, not revoked, `now` outside `[not_before, not_after)` ->
   `REF_VERIFY_KEY_OUT_OF_WINDOW`
4. present, not revoked, in window -> proceed.

Full consultation order (record-sourced path), each step fail-closed:

1. Structural presence guard on the envelope (unchanged).
2. Validate the record via the reader (section 7): pinned-root signature ->
   freshness -> trust view. (When `key_record_view` is passed pre-validated, this
   is the reader's prior work; the reject codes are the reader's.)
3. Look up `issuer_key_id` in the trust view (the four-way result above).
4. Step 1.5 - issuer-signature check against the trust-view public-key object
   (mechanism unchanged from VL-040; only the key SOURCE changed).
5. Step 1.5b - envelope `not_after` expiry (VL-041, unchanged):
   `REF_VERIFY_SIGNATURE_EXPIRED`.
6. `reassert()` (currency + integrity) and the `request_context` / `target_url`
   binding check (unchanged; canon section 13 + 11.1).

The envelope-level expiry (`REF_VERIFY_SIGNATURE_EXPIRED`, VL-041) and the
key-level window (`REF_VERIFY_KEY_OUT_OF_WINDOW`, this artifact) are distinct and
both enforced: the first bounds a single attestation's lifetime, the second
bounds the signing key's lifetime.

## 9. Reject codes (closed set, parallel to REF_VERIFY_SIGNATURE_*)

- `REF_VERIFY_KEY_RECORD_INVALID` - bad publisher signature, unknown root,
  malformed/unparseable record (including non-parseable timestamps).
- `REF_VERIFY_KEY_RECORD_STALE` - `now >= record.not_after`, tz-naive record
  `not_after`, or serial rollback (when state persisted).
- `REF_VERIFY_KEY_UNKNOWN` - issuer `key_id` absent from the validated record.
- `REF_VERIFY_KEY_REVOKED` - issuer `key_id` present and flagged revoked.
- `REF_VERIFY_KEY_OUT_OF_WINDOW` - issuer `key_id` present, not revoked, `now`
  outside the key's `[not_before, not_after)`.

Pre-existing and unchanged: `REF_VERIFY_SIGNATURE_INVALID`,
`REF_VERIFY_SIGNATURE_UNKNOWN_KEY` (static-map path), `REF_VERIFY_SIGNATURE_EXPIRED`
(envelope expiry), and the binding/reassert reject set.

## 10. Canon basis and the section 14 check

- Section 8.2 (PoE): the key record is another optional, implementation-dependent
  integrity/provenance anchor that does not affect admissibility logic. No new
  invariant.
- Section 9: every record-state path and every key-status path fails closed.
- Section 11.9: extends integrity-verifiability from the envelope's own fields to
  the issuer key's validity statement.
- Admissibility (AC^3 AND T^26 AND CCS, via evaluate()) is untouched. Record
  consultation is post-evaluation, verifier-layer, orthogonal to reassert() /
  CCS currency. No new reassertion row.

Section 14 (identity-agnostic) - carry the VL-040 follow-up 2 finding forward
explicitly, because it applies again here, one layer up. VL-040 follow-up 2
recorded (two labs independently) that pinning an issuer key already places a
trusted identity in the verify path, so "identity-agnostic" holds only under the
NARROWED reading: identity is not an admissibility SUBSTITUTE, not "no identity
trust anywhere." Pinning a publisher/ROOT key is a further relocation of identity
trust - the root is now THE trusted identity, and the verifier refuses all but
issuer keys the root vouches for. Section 14 holds under the same narrowed
reading and only under it. This is a spec-clarification point the section 12
evaluate is expected to probe; it is stated here so the evaluate finds it
derivable from the artifact rather than asserted.

## 11. The G4 / G5 boundary

This increment builds the record format, the reader that validates it, and the
verifier consultation. The reader is HANDED a record loaded from a path, exactly
as `published_source.py` loads `published_hashes.json`. The durable, cross-host
TRANSPORT that reliably delivers the freshest record to a remote target is G5,
named-not-built, the same boundary B-prime-1 hit at VL-038. The record's
`not_after` ceiling is what makes a cached or transported record fail closed once
stale, so the primitive is honest without G5; G5 is the hardening that tightens
the fetch cadence toward "instant."

## 12. The new-trust-root cross-model evaluate (claim-track gate; drafted next, run after build)

Per VL-040 follow-up 2 logic - each new anchor owes its own framework-level
evaluate before "forgery-resistant" moves - the publisher/root key is a new trust
floor and owes one. The prompt is drafted this session from
`docs/methodology/cross_model_evaluate_template.md` plus the VL-040 follow-up 2
prompt as the model, and run off-framework AFTER the build commit (three labs,
blind, clean context, off-record). It asks:

- Q1: what pinning the publisher/root key BUYS versus the per-issuer-key pinning
  of VL-040/041 (fewer pinned things; explicit revocation; the provenance chain
  now runs root -> record -> issuer key -> envelope).
- Q2: what it newly REQUIRES (root distribution / custody / rotation; the record's
  own freshness) and which of those are named-not-built.
- Q3: the BOUND it places on "forgery-resistant."
- Q4: the canon check (still 8.2 / 9 / 11.9 / 14, no new invariant; the section 14
  narrowed reading of section 10).
- Q5: the decisive failure (root compromise is TOTAL; how is it bounded - custody,
  rarity of use, root rotation - and is any of that built or only named).

Build fast, claim slow: the build does not wait on the evaluate, but the CLAIM
does. Only after the verdict-of-record is folded (VL-042 follow-up) may
"forgery-resistant" move, and only as far as the bound permits. Until then it
stays in its VL-040 follow-up 2 bounded, signed-path form, and out of any Zenodo
deposit.

## 13. Build order (VL-042; build-then-wire)

1. `EVIDENCE/published_keys_gen.py` - generate the record live with a live root
   keypair (never on disk), sign it with `ensure_ascii=True` canonical_json.
2. `IMPLEMENTATION/key_record_source.py` - MIRRORS `published_source.py` (section
   7; sibling module, not an extension): the pure `load_key_record_from_bytes`
   (load, structural validate, pinned-root signature verify, freshness, build the
   trust view) plus a thin `fetch_key_record` transport. Imports `cryptography`
   (the only new import site; not a new mandatory dep - duck-typed at the verifier,
   as signing is).
3. `verify_envelope` consultation - add `key_record_view`, the record-exclusive
   precedence, the four-way key lookup, the new reject codes. verifier.py stays
   import-clean.
4. Tests (canon/spec-derived), `TESTS/adversarial/test_key_record.py`: revoked key
   refused (`REF_VERIFY_KEY_REVOKED`); rotated/new key honored; key absent
   (`REF_VERIFY_KEY_UNKNOWN`); out-of-window (`REF_VERIFY_KEY_OUT_OF_WINDOW`);
   stale record by `not_after` (`REF_VERIFY_KEY_RECORD_STALE`); serial rollback
   refused when state persisted; bad publisher signature
   (`REF_VERIFY_KEY_RECORD_INVALID`); unknown root (RECORD_INVALID); record-exclusive
   precedence (a key revoked in the record is refused even when the static map
   would accept it); the static-map path byte-unchanged; the unsigned path
   byte-unchanged.
5. Proof, `EVIDENCE/proofs/key_record_001_runner.py` (+ `.log`): live root keypair
   + issuer keypairs; a revoked key refused while a current key is honored, and a
   stale record refused; runner exits 0.

Build-then-wire: NO `pep.py` change; the gate's default forward is unchanged.
Consulting the record is target-side policy (posture). The mandatory cutover and
forcing record-consultation are integrator knobs, not this increment.

The honest-recovery test (definition of done): can a deployment INSTANTLY refuse a
revoked key? Yes - publisher marks revoked, bumps serial, reissues, publishes; any
target consulting the current record refuses via `REF_VERIFY_KEY_REVOKED`
immediately, and the serial gate stops replay of the prior record for
state-persisting verifiers. The residual: a target on a CACHED record is bounded
by that record's `not_after` - "instant" is realized at fetch-cadence granularity,
with `not_after` the absolute ceiling. That residual is the transport / G5
surface, not a hole in the primitive.

## 14. Open questions / decisions deferred

1. Root ROTATION process (named-not-built; schema-representable via `root_key_id`
   and multi-root pinning). A later increment.
2. Cross-host record TRANSPORT (G5; named-not-built). The `not_after` ceiling
   keeps a cached record honest in the interim.
3. Serial PERSISTENCE is verifier-side state; the substrate offers the `serial`
   field and the equal-serial-implies-identical-record guarantee, and the
   integrator decides whether to persist last-seen. Documented, not enforced.
4. RESOLVED at Checkpoint B (was: extend vs mirror `published_source.py`). The
   source read settled MIRROR - see section 7 and the decision in section 15.
   Different trust primitive (hash-pin vs signature-pin), import profile, and
   return contract make a sibling module the honest choice.

## 15. Checkpoint B decisions recorded

- Record vs static map: record-exclusive-when-present (section 8). Resolves the
  opener's "supersede vs augment" - supersede (exclusive), not augment (union).
- Root pin configuration: reader-supplied `pinned_root_keys = {root_key_id:
  root_public_key_object}`, out-of-band (section 6).
- Freshness on the wire: `not_after` (always-on) plus `serial` (opt-in rollback
  gate) (section 5).
- Out-of-window: its own reject code, `REF_VERIFY_KEY_OUT_OF_WINDOW`, distinct
  from REVOKED and UNKNOWN (sections 8, 9; decision 5).
- Reader module: MIRROR `published_source.py` as a sibling
  `IMPLEMENTATION/key_record_source.py`, not an extension (section 7; resolves
  section 14 open question 4). Load-bearing reason: B-prime-1 pins the sha256 of
  the record bytes (re-pinning on every revocation, fatal for a changing record),
  while B-prime-2 pins a root public key and verifies a signature (the record may
  change under a stable pin). Distinct import profile and return contract reinforce
  the split. Reuses published_source.py's three-layer shape (pin primitive / pure
  network-free loader / thin transport).
- Artifact placement: standalone `09_key_record_spec.md` (this file), parallel to
  `08_enforcement_design.md`, rather than a section in artifact 05 - this carries
  its own threat surface (root custody, the freshness recursion, revocation
  semantics) and artifact 05 stays the envelope spec.
