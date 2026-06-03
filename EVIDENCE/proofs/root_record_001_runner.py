"""
VL-044 proof runner: in-band planned root rotation R1 -> R2, demonstrated live.

Repo path: EVIDENCE/proofs/root_record_001_runner.py. Invoke from the repo root:

    python -m EVIDENCE.proofs.root_record_001_runner

(the VL-027 runner convention: -m puts the repo root on sys.path so the
IMPLEMENTATION. / EVIDENCE. imports and build_*'s relative reads resolve; direct
script invocation does not).

The honest-recovery test (spec section 2): a deployment pins ONLY root R1 and
never re-pins, yet trust moves to R2 in-band -

  1. R1 (active) signs a root record designating R2 (active successor). The target,
     pinning only R1, validates it and obtains R2's public key from the record.
  2. A key record signed by the DESIGNATED successor R2 is HONORED, though the
     target never pinned R2 - the rotation primitive.
  3. R1 signs its own retirement (its last act): a new root record marking R1
     retired (retired_at = T) and R2 active.
  4. A NEW key record signed by the now-retired R1 (issued after T) is REFUSED
     (REF_VERIFY_ROOT_RETIRED) - a retired root signs no new records.
  5. R1's PAST key record (issued before T) is still HONORED - past records age out
     via their own freshness, not by a status code.
  6. A key record signed by R2 is still HONORED after R1 retires.

What this runner does NOT demonstrate (the conservative single-hop boundary, spec
section 14 item 3): a ROOT record signed by R2 is not validated against a target
pinning only R1 - the root reader trusts root records signed by a PINNED root.
Letting R2 sign root records is the operator's eventual re-pin of R2 as the new
bootstrap once rotation completes; that re-pin is named, not performed here. The
COMPROMISE case stays out-of-band (spec section 2).
"""

import json
import sys
from datetime import datetime, timezone, timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from EVIDENCE.published_roots_gen import build_root_record, make_root_entry
from EVIDENCE.published_keys_gen import build_key_record, make_key_entry
from IMPLEMENTATION.root_record_source import load_root_record_from_bytes
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.verifier import REF_VERIFY_ROOT_RETIRED


def _fail(msg):
    print("FAIL: " + msg)
    raise SystemExit(1)


def main():
    now = datetime.now(timezone.utc)
    r1 = Ed25519PrivateKey.generate()
    r2 = Ed25519PrivateKey.generate()
    issuer = Ed25519PrivateKey.generate()

    pinned = {"root-1": r1.public_key()}  # the target pins ONLY R1, and never re-pins
    print("target pins ONLY root-1 (out-of-band); never re-pinned in this run")

    def root_rec(entries, signer, sid, serial):
        rec = build_root_record(sid, signer, entries, serial,
                                now + timedelta(hours=24), issued_at=now)
        return json.dumps(rec).encode("utf-8")

    def key_rec(signer, root_id, issued_at):
        entry = make_key_entry("issuer-a", issuer.public_key(),
                               not_before=now - timedelta(days=1),
                               not_after=now + timedelta(days=365))
        rec = build_key_record(root_id, signer, [entry], 1,
                               now + timedelta(hours=24), issued_at=issued_at)
        return json.dumps(rec).encode("utf-8")

    def active(rid, pk, successor_of=None):
        return make_root_entry(rid, pk, "active", now - timedelta(days=1),
                               now + timedelta(days=365), successor_of=successor_of)

    # --- 1. R1 designates R2 ---
    v1 = load_root_record_from_bytes(
        root_rec([active("root-1", r1.public_key()),
                  active("root-2", r2.public_key(), successor_of="root-1")],
                 r1, "root-1", 1),
        pinned, now=now)
    if v1["reason"] is not None:
        _fail("R1 designation record did not validate: %s" % v1["reason"])
    if v1["status_view"]["root-2"]["status"] != "active":
        _fail("R2 not active in the designation view")
    print("1. R1 (active) designates R2; target validates and learns R2's key")

    # --- 2. a key record signed by designated R2 is honored ---
    k = load_key_record_from_bytes(key_rec(r2, "root-2", now), pinned, now=now,
                                   root_status_view=v1["status_view"])
    if k["reason"] is not None or "issuer-a" not in k["trust_view"]:
        _fail("designated R2 key record not honored: %s" % k["reason"])
    print("2. key record signed by designated successor R2 HONORED "
          "(target never pinned R2)")

    # --- 3. R1 retires (its last act): R1 retired, R2 active ---
    t_ret = now - timedelta(minutes=1)  # retirement effective a moment ago
    v2 = load_root_record_from_bytes(
        root_rec([make_root_entry("root-1", r1.public_key(), "retired",
                                  now - timedelta(days=1), now + timedelta(days=365),
                                  retired_at=t_ret),
                  active("root-2", r2.public_key(), successor_of="root-1")],
                 r1, "root-1", 2),
        pinned, now=now)
    if v2["reason"] is not None:
        _fail("R1 retirement record did not validate: %s" % v2["reason"])
    if v2["status_view"]["root-1"]["status"] != "retired":
        _fail("R1 not retired in the retirement view")
    print("3. R1 signs its own retirement (retired_at set); R2 stays active")

    # --- 4. a NEW key record signed by retired R1 is refused ---
    k_new = load_key_record_from_bytes(
        key_rec(r1, "root-1", now), pinned, now=now,  # issued now > t_ret
        root_status_view=v2["status_view"])
    if k_new["reason"] != REF_VERIFY_ROOT_RETIRED:
        _fail("retired R1 NEW key record not refused as ROOT_RETIRED: %s"
              % k_new["reason"])
    print("4. NEW key record signed by retired R1 REFUSED (REF_VERIFY_ROOT_RETIRED)")

    # --- 5. R1's PAST key record still honored ---
    k_past = load_key_record_from_bytes(
        key_rec(r1, "root-1", now - timedelta(hours=2)), pinned, now=now,  # issued < t_ret
        root_status_view=v2["status_view"])
    if k_past["reason"] is not None or "issuer-a" not in k_past["trust_view"]:
        _fail("retired R1 PAST key record not honored: %s" % k_past["reason"])
    print("5. PAST key record signed by R1 (pre-retirement) still HONORED "
          "(ages out via freshness)")

    # --- 6. R2 key record still honored after R1 retires ---
    k_r2 = load_key_record_from_bytes(
        key_rec(r2, "root-2", now), pinned, now=now,
        root_status_view=v2["status_view"])
    if k_r2["reason"] is not None or "issuer-a" not in k_r2["trust_view"]:
        _fail("R2 key record not honored after R1 retires: %s" % k_r2["reason"])
    print("6. key record signed by R2 still HONORED after R1 retires")

    print("\nin-band rotation R1 -> R2 demonstrated; target pinned only R1, never "
          "re-pinned.")
    print("compromise recovery stays out-of-band (spec section 2); R2-signed ROOT "
          "records require the operator's eventual re-pin of R2 (single-hop boundary).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
