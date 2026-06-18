"""
Publisher signing-key rotation helper (VL-108 pre-exposure checklist item 1).

Generates a FRESH Ed25519 publisher keypair for the SIGNED published-record
endpoint (publisher.py /published_hashes_signed.json). RUN THIS ON THE PUBLISHER
HOST. The new PRIVATE key is written to a 0600 file and is NEVER printed to stdout
(that is how the previous key was exposed); only the PUBLIC key is printed, which
is what you pin on the target and the authz sidecar.

    python deploy/rotate_publisher_key.py            # writes ./publisher_signing_key.hex (0600)
    python deploy/rotate_publisher_key.py --out /secure/path/pub.key --key-id publisher-2026-06-18

Output (safe to copy):
  - the new PUBLIC key in HEX        -> set ELYON_PUBLISHER_KEY_HEX on target + sidecar
  - a suggested key id               -> set ELYON_PUBLISHER_KEY_ID on ALL three nodes
The PRIVATE key (file contents)      -> set ELYON_PUBLISHER_SIGNING_KEY_HEX on the PUBLISHER only.

NEVER paste the private key into chat, a ticket, a commit, or any shared channel.
After wiring, shred the file: `shred -u <out>` (or delete once it is in the secret store).
"""

import argparse
import os
from datetime import date

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Rotate the publisher signing key (fresh Ed25519).")
    ap.add_argument("--out", default="publisher_signing_key.hex",
                    help="path to write the new PRIVATE key hex (0600). Default ./publisher_signing_key.hex")
    ap.add_argument("--key-id", default=f"publisher-{date.today().isoformat()}",
                    help="the new ELYON_PUBLISHER_KEY_ID (bump it so the exposed id is retired)")
    ap.add_argument("--print-private", action="store_true",
                    help="ALSO print the private key (discouraged; default writes file only)")
    args = ap.parse_args(argv)

    priv = Ed25519PrivateKey.generate()
    priv_hex = priv.private_bytes_raw().hex()
    pub_hex = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    # Write the private key with tight perms, never to stdout by default.
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(priv_hex + "\n")

    print("=== publisher key rotated ===")
    print(f"ELYON_PUBLISHER_KEY_ID         = {args.key_id}")
    print(f"ELYON_PUBLISHER_KEY_HEX (PUBLIC, pin on target + sidecar) = {pub_hex}")
    print(f"PRIVATE key written to         : {args.out}  (0600)")
    print(f"  -> set ELYON_PUBLISHER_SIGNING_KEY_HEX on the PUBLISHER host from that file,")
    print(f"     e.g.  export ELYON_PUBLISHER_SIGNING_KEY_HEX=$(cat {args.out})")
    print(f"  -> then SHRED it:  shred -u {args.out}")
    if args.print_private:
        print(f"ELYON_PUBLISHER_SIGNING_KEY_HEX (PRIVATE - do NOT share) = {priv_hex}")
    print("NEVER paste the private key into chat, a ticket, or a commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
