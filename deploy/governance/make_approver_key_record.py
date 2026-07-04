"""
R1 key ceremony - generate the approver keypair + root keypair, build the
publisher-SIGNED key record with an approver-ROLE entry, and SELF-CHECK the
whole chain before anything ships (deploy/GOVERNANCE_DEPLOYMENT.md section 1).

Run on the OPERATOR/APPROVER machine (never the gate):

    python deploy/governance/make_approver_key_record.py [--out-dir DIR]

Writes (PRIVATE halves 0600, never printed, never leave this machine):
    <out>/approver_signing_key.hex   -> ELYON_APPROVER_KEY_HEX for approver_cli ONLY
    <out>/root_signing_key.hex       -> re-signing the record later (revoke/rotate/serial bump)
    <out>/approver_key_record.json   -> ship THIS to the gate (public material only)

Prints (safe to copy): the pinned-root env pair, key ids, and the gate .env lines.

Custody law ([FIX H5]): the gate receives ONLY the record (public keys + roles +
signature) and the root PUBLIC key pin. The approver private key stays with the
human approver's CLI; the root private key stays with whoever governs the record.

Fail-closed self-check: before exiting, the script re-reads the record it wrote
through IMPLEMENTATION.key_record_source.load_key_record_from_bytes with the same
pin the gate will use, resolves the role-distinct approver map
(IMPLEMENTATION.approver_trust.resolve_approver_keys), and refuses (exit 1,
artifacts removed) unless the approver key - and ONLY approver-role keys - resolve.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from EVIDENCE.published_keys_gen import (
    build_key_record, make_key_entry, public_key_b64, write_key_record,
)
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.approver_trust import resolve_approver_keys


def _write_private_hex(path: str, key: Ed25519PrivateKey) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(key.private_bytes_raw().hex() + "\n")


def main(argv=None) -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    ap = argparse.ArgumentParser(description="R1 ceremony: approver key + signed key record.")
    ap.add_argument("--out-dir", default=".", help="where the three artifacts are written")
    ap.add_argument("--approver-key-id", default=f"approver-{today}")
    ap.add_argument("--root-key-id", default="root-1")
    ap.add_argument("--gate-key-id", default=os.environ.get("ELYON_SIGNING_KEY_ID"),
                    help="the gate issuer key id (excluded from the approver map; "
                         "default: $ELYON_SIGNING_KEY_ID)")
    ap.add_argument("--serial", type=int, default=1,
                    help="record serial; BUMP on every re-issue (rollback protection)")
    ap.add_argument("--record-days", type=int, default=30,
                    help="record validity; the gate loads it at startup - re-issue "
                         "(serial+1) and restart the gate before it expires")
    ap.add_argument("--key-days", type=int, default=365, help="approver key window")
    args = ap.parse_args(argv)

    now = datetime.now(timezone.utc)
    out = args.out_dir
    os.makedirs(out, exist_ok=True)
    p_approver = os.path.join(out, "approver_signing_key.hex")
    p_root = os.path.join(out, "root_signing_key.hex")
    p_record = os.path.join(out, "approver_key_record.json")
    for p in (p_approver, p_root, p_record):
        if os.path.exists(p):
            print(f"refusing to overwrite {p} - move it away first", file=sys.stderr)
            return 2

    approver_priv = Ed25519PrivateKey.generate()
    root_priv = Ed25519PrivateKey.generate()

    entry = make_key_entry(args.approver_key_id, approver_priv.public_key(),
                           not_before=now - timedelta(minutes=5),
                           not_after=now + timedelta(days=args.key_days))
    entry["role"] = "approver"          # the SIGNED role - the load-bearing SoD bit
    record = build_key_record(root_key_id=args.root_key_id, root_private_key=root_priv,
                              keys=[entry], serial=args.serial,
                              not_after=now + timedelta(days=args.record_days))

    _write_private_hex(p_approver, approver_priv)
    _write_private_hex(p_root, root_priv)
    write_key_record(p_record, record)
    root_pub_b64 = public_key_b64(root_priv.public_key())

    # ---- fail-closed self-check: the exact read path the gate shim uses ----
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    import base64 as _b64
    pinned = {args.root_key_id: Ed25519PublicKey.from_public_bytes(
        _b64.b64decode(root_pub_b64, validate=True))}
    loaded = load_key_record_from_bytes(open(p_record, "rb").read(), pinned)
    view = loaded.get("trust_view")
    approvers = resolve_approver_keys(view, gate_key_id=args.gate_key_id) if view else {}
    if loaded.get("reason") or set(approvers) != {args.approver_key_id}:
        for p in (p_approver, p_root, p_record):
            os.unlink(p)
        print(f"SELF-CHECK FAILED ({loaded.get('reason')}; resolved={sorted(approvers)}) - "
              f"artifacts removed, nothing to ship.", file=sys.stderr)
        return 1

    print("=== R1 ceremony complete (self-check passed) ===")
    print(f"approver key id : {args.approver_key_id}")
    print(f"record          : {p_record}  (serial={args.serial}, "
          f"expires {record['not_after']})")
    print()
    print("GATE deploy/.env additions (public material only):")
    print(f"  ELYON_APPROVER_KEY_RECORD_PATH=/root/Elyon-Sol/deploy/governance/approver_key_record.json")
    print(f"  ELYON_PINNED_ROOT_KEY_ID={args.root_key_id}")
    print(f"  ELYON_PINNED_ROOT_PUBKEY_B64={root_pub_b64}")
    print("  (and REMOVE any ELYON_APPROVER_PUBKEY_HEX / ELYON_APPROVER_KEY_ID line)")
    print()
    print("APPROVER machine only (never the gate):")
    print(f"  export ELYON_APPROVER_KEY_ID={args.approver_key_id}")
    print(f"  export ELYON_APPROVER_KEY_HEX=$(cat {p_approver})")
    print()
    print(f"Ship {os.path.basename(p_record)} to the gate; keep both .hex files here (0600).")
    print("Re-issue before the record expires: rerun with --serial "
          f"{args.serial + 1} (root key file must be moved back in place).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
