# 11 - Root succession and per-root status (B-prime-3): planned rotation, retired/revoked status, and the bootstrap floor

Status: SPEC (Checkpoint B; spec-defines-the-change). Drafted at VL-044 from a
source-first read of `IMPLEMENTATION/verifier.py`,
`IMPLEMENTATION/key_record_source.py`, `EVIDENCE/published_keys_gen.py`,
`docs/restructure/09_key_record_spec.md` (full), and `CANON/canon.md` sections
8.2 / 9 / 11.9 / 13 / 14. A spec commit PRECEDES the build commit.

This artifact is the third instance of the B-prime pattern, one trust layer up
from artifact 09:

- B-prime-1 (`published_source.py`, VL-038/039): pins the sha256 of a hash
  record's BYTES.
- B-prime-2 (`key_record_source.py`, VL-042): pins a root PUBLIC KEY and verifies
  a publisher signature over a record that vouches for ISSUER keys.
- B-prime-3 (`root_record_source.py`, this artifact): pins a root PUBLIC KEY and
  verifies a root signature over a record that vouches for ROOTS - their status
  (active / retired / revoked) and their successors.

Where artifact 09 made the ROOT a singular load-bearing trust floor, this artifact
gives that floor an in-band LIFECYCLE: a current root can designate a successor,
and roots carry status, so a deployment can rotate roots without a flag-day re-pin
at every target - WITHOUT solving root-key COMPROMISE recovery, which is
irreducibly out-of-band and is this increment's explicit non-goal (section 2).

---

## 1. Purpose and scope

VL-042 follow-up's three-lab evaluate found (3-0 convergent) that the pinned root
is a new, singular, load-bearing trust floor: root compromise is TOTAL, and the
record built no recovery (root custody is out-of-band; rotation was
schema-representable but process-unbuilt). This artifact builds the buildable half
of that recovery story: PLANNED rotation and PER-ROOT STATUS.

In scope:

- A signed root/succession record, distinct from the key record, that carries
  per-root status entries and successor designations.
- A reader (`root_record_source.py`) that validates it against pinned roots and
  yields a per-root STATUS VIEW.
- A cross-record check at the key-record reader: a key record whose SIGNING root
  is retired (for a new record) or revoked is refused, so a rotated-out or
  distrusted root cannot keep vouching for issuer keys.
- The reject vocabulary, the canon check, the build order, and the honest
  narrowing of the `ROOT_RECOVERY` deployment predicate.

Out of scope (named, not built): root-key COMPROMISE recovery (section 2),
cross-host record TRANSPORT (G5; section 11), and the mandatory signing cutover
(posture; an integrator knob).

No new canonical invariant. Admissibility (AC^3 AND T^26 AND CCS, via
`evaluate()`) is untouched. This is verifier-layer / reader-layer provenance
machinery, post-evaluation (section 10).

---

## 2. What "root recovery" can and cannot mean here (the honest ceiling)

Stated up front so the increment is never oversold and the `ROOT_RECOVERY`
predicate (section 16) is never overclaimed.

"Root recovery" does NOT mean recovering from root-key COMPROMISE. VL-042
follow-up's evaluate found root compromise is TOTAL: an adversary holding a root
private key can sign a record vouching for any issuer key, can sign a root record
asserting any status, and can sign a succession to an adversary-controlled root.
No in-band record signed BY a root can be trusted to revoke that same root once
its private key has leaked - the adversary produces the same signatures. Compromise
recovery is irreducibly OUT-OF-BAND: a human re-pins a new root at every target.
That is a non-goal of this increment and of the substrate; it is deployment and
custody, not code.

"Root recovery" in this artifact's buildable sense means two concrete things:

1. PLANNED ROTATION. While the current root is still trusted (uncompromised), it
   signs a designation of a successor root, so a deployment moves from root R1 to
   root R2 in-band, without a flag-day re-pin at every target. The interval in
   which both are trusted is the rotation OVERLAP.
2. PER-ROOT STATUS. A root carries one of three statuses:
   - `active`: signs new records and is fully trusted.
   - `retired`: trusted for its PAST-signed records to their freshness ceiling,
     but signs no NEW records - the graceful-rotation end state.
   - `revoked`: distrusted entirely - but see the bootstrap floor (section 6): a
     root cannot revoke ITSELF in-band; `revoked` is meaningful only when asserted
     by a DIFFERENT still-trusted root or out-of-band.

The honest-recovery test (definition of done): can a deployment rotate from R1 to
R2 in-band, with R1's existing records still honored to their freshness ceiling
during the overlap and R2's new records trusted, WITHOUT a simultaneous
out-of-band re-pin at every target? If yes for the PLANNED case, the increment
closed what it set out to. The COMPROMISE case stays out-of-band and named.

---

## 3. The trust-model shift

Artifact 09 relocated identity trust to a singular pinned root. This artifact makes
that trust TRANSITIVE under designation: a target that pins root R1 can come to
trust a root R2 it never pinned, because R1 (while trusted) signed a record
designating R2. This is the genuinely new trust relationship, and it is named here
explicitly so the section 12 evaluate (if run) finds it derivable rather than
having to surface it.

The provenance chain after this artifact:

```
pinned_root_keys (out-of-band, the bootstrap anchor)
  -> root/succession record (signed by a pinned-or-designated, trusted root)
       -> per-root STATUS VIEW {root_key_id: status + public key + window}
  -> key record (signed by some root R; artifact 09)
       -> the key reader checks R's status in the STATUS VIEW
          (active -> proceed; retired -> past records only; revoked -> refuse)
       -> issuer-key TRUST VIEW
  -> verify_envelope(..., key_record_view=...) (VL-042; logic unchanged)
```

Transitivity is bounded by status and freshness, not unlimited: a designated
successor is trusted only while `active` (or, for its past records, while
`retired` and within freshness), and only while the designating record is itself
fresh. The bound on "forgery-resistant" does not move because of rotation
(section 12); rotation is a lifecycle operation under the EXISTING root-trust
bound.

---

## 4. The root/succession record (`EVIDENCE/published_roots.json`)

The record is a deployment/runtime artifact, generated live and signed by a root
private key that is NEVER on disk and never in the repo (section 6, the artifact
09 custody rule carried up). It is NOT a committed repo file - the same status as
`published_keys.json` (VL-043 follow-up 2: a committed record would require a
persisted root private key to sign it, which the custody rule forbids; the path is
named here, not committed). The header above names a path, not a tracked file.

Mirrors the key-record shape (artifact 09 section 4; generator + reader sibling),
the third B-prime instance. Only `publisher_signature` is outside the signed
region, so every status entry, every successor public key, the serial, and the
record `not_after` are tamper-proof.

```
{
  "format": "elyon-sol-root-record",
  "version": 1,
  "signing_root_key_id": "<the root whose key signs THIS record>",
  "serial": <non-negative int, monotonic; opt-in rollback gate>,
  "issued_at": "<ISO-8601 tz-aware>",
  "not_after": "<ISO-8601 tz-aware; the record's own freshness ceiling>",
  "roots": [
    {
      "root_key_id": "<str>",
      "public_key": "<base64 raw Ed25519 public key>",
      "status": "active" | "retired" | "revoked",
      "not_before": "<ISO-8601 tz-aware>",
      "not_after": "<ISO-8601 tz-aware>",
      "retired_at": "<ISO-8601 tz-aware; present iff status == retired>",
      "revoked_at": "<ISO-8601 tz-aware; present iff status == revoked>",
      "successor_of": "<root_key_id; optional; this root was designated by that>"
    }
  ],
  "publisher_signature": "<hex; signature by the signing_root's private key>"
}
```

Field notes:

- `signing_root_key_id` names the root whose private key signed the record. The
  reader selects that root's pinned-or-designated public key to verify the
  signature. (Distinct from the key record's `root_key_id`, which names the same
  concept one layer down; the explicit name avoids conflation.)
- `roots[].public_key` carries the raw bytes of EACH root the record vouches for.
  This is what makes designation in-band: a target pinning only R1 obtains R2's
  public key FROM the record R1 signed.
- `retired_at` is load-bearing for the past-record honoring rule (section 6): the
  key reader compares a key record's `issued_at` against the signing root's
  `retired_at` to distinguish a retired root's honored past records from its
  forbidden new ones.
- The signing root SHOULD appear in its own `roots` array with its current status;
  it is not required to, and a signing root absent from the array is treated as
  `active` by virtue of being the trusted signer (the bootstrap default,
  section 6).

---

## 5. Freshness (the recursion, one more layer up)

Artifact 09 section 5 designed freshness into the key record (`not_after` strict,
plus opt-in `serial` rollback). The root record carries the same two mechanisms,
one layer up:

- `not_after` (always on): `now < record.not_after` strict. A stale root record
  fails closed to `REF_VERIFY_ROOT_RECORD_STALE`. This is the ceiling that keeps a
  cached or transported root record honest before G5 (section 11).
- `serial` (opt-in): monotonic; a verifier that persists `last_seen_root_serial`
  refuses a rollback to `REF_VERIFY_ROOT_RECORD_STALE`. Persistence is verifier-side
  state; the substrate offers the field and the
  equal-serial-implies-identical-record guarantee, and the integrator decides
  whether to persist.

The freshness guarantee is only as strong as the verifier's CLOCK (the open
carry-forward from VL-042 follow-up finding 2: a skewed-back clock could honor a
stale record within its skew). Stated here, as the artifact 09 section 5 note now
should be too; not closeable in code.

A tz-naive or unparseable `not_after` fails closed to STALE (the key reader's
existing convention, mirrored).

---

## 6. Root status model and the bootstrap floor (the design center)

This section is the difference between an orderly-rotation primitive (buildable,
honest) and an overclaimed compromise-recovery primitive (not buildable in-band).

### 6.1 The three statuses, reader-enforced

- `active`: the root signs new records and is fully trusted. A pinned root absent
  from any status assertion is `active` by virtue of being pinned (the bootstrap
  default).
- `retired`: the root's PAST-signed records stay honored to THEIR `not_after`
  ceiling, but the root signs no NEW records. Reader-enforced, not honor-system:
  when a key record is signed by a retired root R, the key reader accepts it ONLY
  if the key record's `issued_at` precedes R's `retired_at` AND the key record is
  still fresh. A key record from a retired root with `issued_at >= retired_at`
  (a new record from a rotated-out root) is refused to `REF_VERIFY_ROOT_RETIRED`.
  This is what makes "signs no new records" machine-checkable: both timestamps
  exist (the key record's `issued_at` is a required field per artifact 09; the
  root's `retired_at` is required when status is retired, section 4).
- `revoked`: the root is distrusted entirely and immediately. A key record signed
  by a revoked root is refused to `REF_VERIFY_ROOT_REVOKED` regardless of freshness
  or `issued_at`.

### 6.2 The bootstrap floor (self-revocation is meaningless in-band)

A root CANNOT revoke ITSELF in-band. A compromised root would sign a fake "I am
active"; a healthy root that signs "I am revoked" is performing retirement, not
revealing compromise. Therefore `revoked` status for root Rx is meaningful ONLY
when asserted by a DIFFERENT still-trusted root (R2 revokes R1 during overlap) or
out-of-band (a human re-pins). The reader enforces this: a status entry marking the
record's OWN `signing_root_key_id` as `revoked` is treated as at-most `retired`
(it cannot be a trusted compromise signal), and a self-`revoked` assertion never
distrusts the signer mid-validation of its own record.

The FIRST root, and any root whose successor is not yet established, can be revoked
ONLY out-of-band. This is the bootstrap floor: the trust graph has to start
somewhere, and that starting pin is trusted by being pinned, not by any in-band
statement. Stated derivably so the section 12 evaluate finds it.

### 6.3 The overlap-conflict hazard (cross-signer; named, not loader-resolved)

During the rotation overlap, two roots (R1 and R2) are both trusted. If one is
COMPROMISED in the overlap, it can sign a root record contradicting the honest
root's: R1 signs "R2 revoked, R1 active" while R2 signs "R1 revoked, R2 active."
A target presented with both records - each validly signed by a then-trusted root -
faces an UNRESOLVABLE in-band conflict: serial and freshness order honest issuance
WITHIN one signer but cannot adjudicate a contradiction ACROSS two signers (a
compromised root issues high serials too).

This conflict is CROSS-SIGNER, and a single root record carries exactly one
`signing_root_key_id` and one signature. The pure single-record loader (section 7)
therefore CANNOT detect it - it sees one signer's assertions, not two records'. The
conservative build (the single-hop lock, section 14 item 3) does not merge records:
a target consults one validated root record at a time. Cross-signer overlap conflict
is thus a NAMED DEPLOYMENT-LAYER hazard, resolved by out-of-band re-pin, NOT a
loader function - and soundly so, because no in-band rule can adjudicate adversarial
multi-root contradiction. Planned rotation never produces conflict, because an
honest operator issues a single coherent succession; conflict IS the compromise
signal, and the response is the same out-of-band re-pin that all root compromise
requires (section 2).

What the loader DOES enforce is the WITHIN-record analog: the same `root_key_id`
appearing more than once in a single record's `roots` array, or appearing with
contradictory status, is malformed and fails closed to
`REF_VERIFY_ROOT_RECORD_INVALID`. That is deterministic on one record and is the
buildable piece; the cross-signer case above is the named-not-built piece.

---

## 7. The succession-record reader (`IMPLEMENTATION/root_record_source.py`)

A sibling module mirroring `key_record_source.py` (Decision A/B: standalone
artifact, sibling reader). It shares the SAME trust primitive as B-prime-2
(pinned-root signature, not B-prime-1's byte-hash), the same import profile (it
reconstructs root public keys, so it imports `cryptography`, keeping verifier.py /
envelope.py import-clean), and the same INVALID/STALE discriminating return
contract. It is a sibling rather than an extension because what it vouches for
(ROOTS) and its threat surface (succession authority, retired-vs-revoked, the
bootstrap floor) are distinct from the issuer-key reader's - the same
distinct-threat-surface test that made artifact 09 standalone from artifact 05.

Three layers, mirroring `key_record_source.py`:

- `load_root_record_from_bytes(record_bytes, pinned_root_keys, now=None,
  last_seen_root_serial=None)` - the pure, network-free trust check. Returns
  `{"status_view": <dict>, "reason": None}` on success, or
  `{"status_view": None, "reason": <REF_VERIFY_ROOT_RECORD_*>}` on any fault.
- `fetch_root_record(publisher_url, pinned_root_keys, now=None,
  last_seen_root_serial=None, timeout=...)` - the thin transport (loopback now;
  true cross-host is G5). Fail-closed to `REF_VERIFY_ROOT_RECORD_INVALID` on any
  connection / non-200 / timeout.

Pure-loader responsibilities, in order (each step fail-closed):

1. Parse JSON and structurally validate (required fields present, correct types,
   parseable tz-aware timestamps; `status in {active, retired, revoked}`; a
   `retired` entry has `retired_at`, a `revoked` entry has `revoked_at`). Any
   structural fault -> `REF_VERIFY_ROOT_RECORD_INVALID`.
2. Select the signing root by `signing_root_key_id` from `pinned_root_keys`. A
   signing root not pinned -> `REF_VERIFY_ROOT_RECORD_INVALID` (unknown signing
   root folded into record-invalid, the artifact 09 section 6 closed-set-stays-tight
   precedent).
3. Verify `publisher_signature` over `canonical_json(record minus
   publisher_signature)` against the selected pinned root. Failure ->
   `REF_VERIFY_ROOT_RECORD_INVALID`.
4. Freshness (section 5): `now < not_after` strict; serial monotonic if state
   persisted. Failure -> `REF_VERIFY_ROOT_RECORD_STALE`.
5. Apply the bootstrap rule (section 6.2): a self-`revoked` assertion on the
   signing root is downgraded to at-most `retired`.
6. Apply the WITHIN-record consistency check (section 6.3): a `root_key_id` that
   appears more than once in `roots`, or with contradictory status, is malformed ->
   `REF_VERIFY_ROOT_RECORD_INVALID`. (The CROSS-signer overlap conflict of section
   6.3 is a named deployment-layer hazard the single-record loader cannot and does
   not resolve; out-of-band re-pin, not a loader code.)
7. Build the per-root STATUS VIEW, reconstructing each root public key via
   `Ed25519PublicKey.from_public_bytes`:
   `{root_key_id: {"public_key": <obj>, "status": <str>, "not_before": <dt>,
   "not_after": <dt>, "retired_at": <dt|None>, "revoked_at": <dt|None>}}`.
   Bad key material / naive / unparseable window -> `REF_VERIFY_ROOT_RECORD_INVALID`.

`canonical_json` is REUSED from `envelope.py` (prefix-ful import per VL-027) so
gen-side and reader-side canonicalization match exactly. The pinned root, like
B-prime-1's pinned anchor and B-prime-2's, is held out-of-band and NEVER fetched
alongside the record (that would be circular).

The reader fails closed on every path; it returns a validated status view or a
single reject reason, never a partially-trusted view.

---

## 8. Cross-record composition (where status is checked; the verifier is untouched)

The section-1 source correction (VL-044 opener), confirmed against disk:
`verify_envelope` CONSUMES an already-validated `key_record_view` and never sees a
root. Per-root status therefore belongs where the root is verified - at the reader
layer - not at `verify_envelope`. `verify_envelope`'s LOGIC is unchanged; only the
`REF_VERIFY_ROOT_*` constants are added to verifier.py (its canonical
`REF_VERIFY_*` home).

`key_record_source.load_key_record_from_bytes` gains one optional parameter,
`root_status_view=None`, and one cross-check after pinned-root signature
verification (step 4 of its existing order) and BEFORE building the issuer trust
view:

Root resolution and status gate (fail-closed), when `root_status_view` is supplied:

1. If the key record's `root_key_id` is in `root_status_view`: that entry is the
   authoritative source for the signing root's public key AND status (the
   record-exclusive precedence of artifact 09 decision 3, mirrored one layer up -
   a status view, when present, supersedes a bare pin so a pin cannot silently
   defeat a revocation). Then:
   - `revoked` -> `REF_VERIFY_ROOT_REVOKED`.
   - `retired` -> accept only if `key_record.issued_at < root.retired_at` AND the
     key record is fresh; otherwise `REF_VERIFY_ROOT_RETIRED`.
   - `active` -> proceed with the status-view public key.
2. Else if `root_key_id` is in `pinned_root_keys`: bootstrap/active-by-pinning;
   proceed with the pinned key (a pinned root with no status assertion is trusted
   active).
3. Else: unknown signing root -> `REF_VERIFY_KEY_RECORD_INVALID` (folded; the key
   reader's existing behavior).

When `root_status_view` is None: VL-042 byte-behavior exactly (select from
`pinned_root_keys` only; no status gate). Backward-compatible; the static-map and
unsigned paths are byte-unchanged.

A deployment that wants rotation passes BOTH: it validates the root record first
(`root_record_source` -> status view), then passes that view to the key reader
(`key_record_source(..., root_status_view=...)`), then passes the resulting issuer
trust view to `verify_envelope(..., key_record_view=...)`. Three readers compose;
the verifier is the unchanged terminal consumer.

---

## 9. Reject codes (closed set, parallel to REF_VERIFY_KEY_*)

New, defined in verifier.py (the REF_VERIFY_* home), emitted by the readers:

- `REF_VERIFY_ROOT_RECORD_INVALID` - bad publisher signature, unknown signing
  root, malformed/unparseable root record, or a within-record duplicate or
  contradictory `root_key_id` (section 6.3; the cross-signer overlap conflict is a
  named deployment-layer hazard, not this code).
- `REF_VERIFY_ROOT_RECORD_STALE` - `now >= record.not_after`, tz-naive record
  `not_after`, or serial rollback when state persisted.
- `REF_VERIFY_ROOT_RETIRED` - a key record signed by a retired root with
  `issued_at >= retired_at` (a forbidden new record; past records age via freshness,
  not this code).
- `REF_VERIFY_ROOT_REVOKED` - a key record signed by a revoked root.

Folded, NOT a new code (artifact 09 section 6 precedent, the closed set stays
tight): an unknown signing root folds into `REF_VERIFY_ROOT_RECORD_INVALID`; an
unknown key-record signing root with no status view folds into the key reader's
existing `REF_VERIFY_KEY_RECORD_INVALID`.

Pre-existing and unchanged: the entire `REF_VERIFY_KEY_*`, `REF_VERIFY_SIGNATURE_*`,
and binding/reassert reject sets.

---

## 10. Canon basis and the section 14 check

- Section 8.2 (PoE): the root record is another optional, implementation-dependent
  provenance anchor that does not affect admissibility logic. No new invariant.
- Section 9: every record-state path and every root-status path fails closed.
- Section 11.9: extends integrity-verifiability one layer up - from the issuer
  key's validity statement (artifact 09) to the ROOT's validity and succession
  statement.
- Section 13 (revalidation): unchanged; `reassert()` is not touched. Root status is
  consulted at the reader, post-evaluation, orthogonal to `reassert()` / CCS
  currency. No new reassertion row.
- Admissibility (AC^3 AND T^26 AND CCS, via `evaluate()`) is untouched.

Section 14 (identity-agnostic) - carry the VL-040 follow-up 2 and artifact 09
section 10 finding forward, one more layer up. Pinning a root already placed a
trusted identity in the verify path; "identity-agnostic" holds only under the
NARROWED reading (identity is not an admissibility SUBSTITUTE). This artifact adds
TRANSITIVE root identity (a pinned root vouches for a successor's identity), which
is a further relocation of identity trust, not an admissibility input. Section 14
holds under the same narrowed reading and only under it. Rotation MOVES the trusted
identity; it does not ADD identity to the admission path. Stated derivably so the
section 12 evaluate finds it rather than surfacing it.

---

## 11. The G4 / G5 boundary

This increment builds the record format, the reader that validates it, the status
view, and the cross-record gate at the key reader. The reader is HANDED a record
loaded from a path, exactly as `key_record_source.py` and `published_source.py`
are. Durable, cross-host TRANSPORT that reliably delivers the freshest root record
to a remote target is G5, named-not-built, the same boundary B-prime-1 and
B-prime-2 hit. The record's `not_after` ceiling is what makes a cached or
transported root record fail closed once stale, so the primitive is honest without
G5; G5 is the hardening that tightens fetch cadence toward "instant."

---

## 12. The claim-track evaluate (Decision H; flagged open)

Per VL-040 follow-up 2 logic - each new trust relationship owes a framework-level
evaluate before "forgery-resistant" moves. The question for VL-044 is whether
planned rotation is such a relationship.

- Reading (i), build-only (like the readiness gate VL-043): rotation introduces no
  new anchor ABOVE the root (the root is the top; rotation is lateral, R1 to R2);
  it operationalizes a process under the EXISTING root-trust bound and makes no new
  claim about the world, so no evaluate.
- Reading (ii), owes-an-evaluate: succession designation makes root trust
  TRANSITIVE (section 3) - a target comes to trust a root it never pinned. That is
  a genuine new trust ASSERTION ("R1 says trust R2"), and the overlap-conflict
  hazard (section 6.3) is exactly the kind of property a fresh adversarial read
  should probe.

This spec records the analysis and LOCKS (ii) (Decision H, session start): the
evaluate is not gating the word "forgery-resistant" (constraint l holds it fixed
regardless - rotation is a lifecycle op under the same bound); it is validating the
SOUNDNESS of transitive designation itself (overlap double-authority, a retired
root's past designation still binding, the bootstrap floor's derivability). A
mechanism that can MOVE the load-bearing trust floor merits that scrutiny, and the
framework's bias is "if in doubt, run it." The prompt is drafted this session (from
`cross_model_evaluate_template.md` plus the VL-042 follow-up prompt as the model)
and run off-framework AFTER the build commit, three labs, blind, off-record; only
the verdict-of-record folds (VL-044 follow-up). Build fast, claim slow.

The questions a (ii) evaluate would ask:

- Q1: what transitive designation BUYS (in-band rotation without flag-day re-pin)
  versus per-root out-of-band re-pinning.
- Q2: what it newly REQUIRES (designation authority, overlap management, the
  retirement timestamp discipline) and which are built vs named.
- Q3: the BOUND - does transitive trust expand the adversary's reach BEYOND what
  root compromise (already total) grants?
- Q4: the canon check (section 10; section 14 narrowed reading one layer up).
- Q5: the decisive failure (root compromise during overlap; the conflict case of
  section 6.3; recovery still out-of-band).

---

## 13. Build order (VL-044; build-then-wire)

Mirrors the artifact 09 section 13 order, one layer up:

1. SPEC (this artifact; spec-defines-the-change). A spec commit PRECEDES the build.
2. `EVIDENCE/published_roots_gen.py` - live generator/signer for the root record,
   mirroring `published_keys_gen.py`: build the record dict, sign with a duck-typed
   root private key, write ASCII JSON (`ensure_ascii=True`, sort_keys, VL-009). The
   root private key is ephemeral, generated in `_demo()` / tests, NEVER persisted.
   Derived live, never hand-copied (constraint i).
3. `IMPLEMENTATION/root_record_source.py` - the sibling reader (section 7): pure
   `load_root_record_from_bytes` + thin `fetch_root_record`. Imports `cryptography`
   (the reader, not the verifier).
4. `IMPLEMENTATION/key_record_source.py` - add the `root_status_view` parameter and
   the cross-record status gate (section 8). VL-042 byte-behavior preserved when the
   parameter is None.
5. `IMPLEMENTATION/verifier.py` - add the four `REF_VERIFY_ROOT_*` constants
   (section 9). NO `verify_envelope` logic change (constants only; confirmed by the
   reader return-contract read). Fix the stale Step 1.5 "signed-path only" comment
   while here (the VL-042 carry-forward T-prose-drift micro-edit) only if it lands
   cleanly in the same edit; otherwise leave to T-prose-drift.
6. Tests, `TESTS/adversarial/test_root_record.py` (canon/spec-derived): active root
   honored; retired root's PAST record honored to freshness ceiling; retired root's
   NEW record refused (`REF_VERIFY_ROOT_RETIRED`); revoked root refused
   (`REF_VERIFY_ROOT_REVOKED`); successor designation honored (R2's key record
   trusted after R1 designates R2); unknown signing root refused (RECORD_INVALID);
   stale root record refused (RECORD_STALE); self-revocation downgraded to retired
   (bootstrap, section 6.2); within-record duplicate/contradictory root entry refused
   (RECORD_INVALID, section 6.3); the cross-signer overlap conflict documented as an
   out-of-band hazard the loader does not resolve (a boundary the test states, not a
   loader code it exercises);
   the bootstrap-floor boundary documented (a sole pinned root can be revoked only
   out-of-band - the test asserts the boundary, does not pretend to close it); the
   static-map and unsigned paths byte-unchanged; `root_status_view=None` is VL-042
   byte-behavior.
7. Proof, `EVIDENCE/proofs/root_record_001_runner.py` (+ `.log`): live R1/R2 root
   keypairs; in-band rotation R1 -> R2 demonstrated (R1 signs R2's designation, a
   key record signed by R2 is honored, a NEW key record signed by retired R1 is
   refused while R1's prior record ages out via freshness), exit 0. Invoke via
   `python -m EVIDENCE.proofs.root_record_001_runner` (the VL-042 runner `-m`
   convention).
8. The `ROOT_RECOVERY` predicate wired to a real proof test with the honest
   narrowing note (section 16; Decision F); `readiness.json` `blocked_by`
   VL-number corrected (Decision G).
9. Docs: artifact 04 (root-recovery / G-area bullet; ROOT_RECOVERY predicate note),
   artifact 06 only if a canon row is touched (likely not - no new invariant),
   00_README (now owes artifacts 08 / 09 / 10 / 11).

Build-then-wire: NO `pep.py` change (consuming the root record is target-side
posture, the same as the key record). If Decision H goes (ii), the evaluate runs
off-framework AFTER the build commit; only its verdict-of-record folds.

---

## 14. Open questions / decisions deferred

1. Root-key COMPROMISE recovery (out-of-band re-pin). Irreducible; non-goal
   (section 2). Named, never built in-band.
2. Cross-host record TRANSPORT (G5; section 11). Named-not-built; `not_after`
   keeps a cached record honest in the interim.
3. Multi-generation succession chains (R1 -> R2 -> R3 where a target pins only R1).
   DECIDED conservative at Checkpoint B (recorded in section 15, locked at session
   start): the build honors a SINGLE designation hop from a pinned root and treats
   deeper chains as requiring an intermediate pin. Chain-FOLLOWING across multiple
   records (resolving R3's trust through R1 -> R2 -> R3 without pinning R2) is the
   deferred later increment, with its own threat analysis - a long designation chain
   widens the compromise blast radius (any one compromised generation vouches for
   everything downstream). The record shape carries `successor_of` for one hop; it
   does not encode a followable chain, and the reader does not traverse one.
4. Serial PERSISTENCE for the root record is verifier-side state, as for the key
   record (artifact 09 section 14 item 3). Documented, not enforced.

---

## 15. Checkpoint B decisions recorded

- Artifact placement: standalone `11_root_record_spec.md`, parallel to artifact 09,
  rather than a section of artifact 09 - the succession record carries its own
  distinct threat surface (succession authority, retired-vs-revoked, the bootstrap
  floor), the same distinct-threat-surface test that made 09 standalone from 05
  (Decision A; confirmed by the two-record architecture lock).
- Two records, not one: a root/succession record distinct from the issuer-key
  record, composed at the reader layer (section 8), rather than folding per-root
  status into the key record. Keeps the two trust layers (root provenance vs issuer
  provenance) separable (Decision B / the records-count hinge, locked at session
  start).
- Reader module: a sibling `IMPLEMENTATION/root_record_source.py` mirroring
  `key_record_source.py` (same trust primitive as B-prime-2; distinct vouched-for
  object and threat surface), PLUS a `root_status_view` parameter added to
  `key_record_source.py` for the cross-record gate. "Sibling" does not mean the key
  reader is untouched (Decision B).
- Status checked at the reader, not the verifier (Decision E; the section-1 source
  correction). `verify_envelope` logic unchanged; verifier.py gains constants only.
- Reject codes: add `REF_VERIFY_ROOT_RECORD_INVALID`, `REF_VERIFY_ROOT_RECORD_STALE`,
  `REF_VERIFY_ROOT_RETIRED`, `REF_VERIFY_ROOT_REVOKED`; fold unknown signing root
  into RECORD_INVALID (Decision D; the artifact 09 section 6 closed-set precedent).
- Retirement is reader-enforced via `issued_at < retired_at`, not honor-system
  (section 6.1; the timestamp-comparison precision point surfaced by the two-record
  read).
- Self-revocation is downgraded to at-most retired; real root revocation requires a
  different trusted root or out-of-band; the first/successor-less root is
  out-of-band-only (section 6.2, the bootstrap floor).
- Overlap conflict is CROSS-signer and a named deployment-layer hazard (out-of-band
  re-pin), NOT a single-record loader function - the loader sees one signer
  (section 6.3, conservative-frame clarification). The loader enforces only the
  WITHIN-record analog (duplicate or contradictory `root_key_id` in one record ->
  RECORD_INVALID). Planned rotation never conflicts; conflict is the compromise
  signal.
- Multi-generation chains: conservative SINGLE hop from a pinned root (decision on
  section 14 item 3, locked at session start). A target pinning R1 trusts R1's
  directly-designated successor R2, but not a further-designated R3 unless R2 is
  itself pinned; chain-following is deferred (a long chain widens the compromise
  blast radius). Surfaced as an open question by the two-record read; decided here.
- Claim-track: Decision H locked to (ii) run-the-evaluate (section 12). The prompt
  is drafted this session and run off-framework AFTER the build commit; only the
  verdict-of-record folds (VL-044 follow-up). Does not block the build.

---

## 16. The `ROOT_RECOVERY` deployment predicate (Decision F)

`EVIDENCE/readiness.json`'s `ROOT_RECOVERY` predicate has `proof: null` and a
`blocked_by` that currently cites the wrong VL number (Decision G; a one-line
prose fix, `cat -A` the line before editing). VL-044 gives it a path toward green:

- Option (i), taken: keep the single predicate, NARROW its semantics explicitly in
  `readiness.json`'s note/`blocked_by` to "planned in-band rotation + per-root
  status; root-key COMPROMISE recovery is out-of-band and out of scope." Add a
  proof test (the rotation runner of section 13 step 7, or its pytest analog) and
  name it, so the VL-043 gate's rule (a green flag MUST name a passing proof) is
  satisfied. Avoids predicate proliferation (option ii, a second predicate).

CRITICAL HONESTY CONSTRAINT: the predicate going green must mean
PLANNED-ROTATION-BUILT, not COMPROMISE-RECOVERABLE. The gate is the framework's own
honesty instrument; overclaiming the predicate it watches is exactly the failure it
exists to catch. The narrowing note is not optional polish - it is the honesty
hinge, and it is the gate watching its own author.

---

## Appendix - source reads grounding this spec (VL-044, re-verified against disk)

- `verifier.py`: `verify_envelope` (lines 185-394) consumes a pre-validated
  `key_record_view`; the issuer-key lookup is lines 277-291; the REF_VERIFY_* home
  is lines 120-141; the stale "signed-path only" comment is line 256 against the
  line 268 guard.
- `key_record_source.py`: the pure loader, the `{trust_view, reason}` contract, the
  `_REQUIRED_RECORD_KEYS` (including `issued_at`), the pinned-root selection by
  `root_key_id`, the `canonical_json` reuse from `envelope.py`.
- `published_keys_gen.py`: `build_key_record` field order and the signed-region
  rule (only `publisher_signature` excluded), `write_key_record` ASCII discipline,
  the ephemeral-root `_demo` pattern. The root record generator mirrors this.
- `09_key_record_spec.md`: sections 6 (custody, multi-root pin), 7 + 15
  (mirror-vs-extend test, keyed on trust primitive), 8 (record-exclusive
  precedence, decision 3), 10 (canon basis, section 14 narrowed reading), 13 (build
  order), 14 (rotation named-not-built, the question this artifact answers).
- `CANON/canon.md`: sections 8.2 / 9 / 11.9 / 13 / 14 (no new invariant; fail-closed;
  integrity-verifiability; revalidation; identity-agnostic narrowed reading).
