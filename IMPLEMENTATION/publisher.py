"""
Standing published-record publisher for Elyon-Sol
(docs/restructure/12_g5_transport_design.md steps 2-3).

Promotes the ephemeral http.server the cross-host runners spin up
(EVIDENCE/proofs/g5_*_runner.py `_serve`) into a real, deployable service: a
standing endpoint that serves the committed published hash record over HTTP (dev)
or HTTPS (real transport, via `uvicorn --ssl-*`). It is the publisher node of the
gate -> target -> publisher chain.

The record served is EVIDENCE/published_hashes.json (the committed, hash-locked
record; CANON/canon.lock -> published_hashes.json -> the pinned root anchor the
target holds out-of-band). The bytes are served verbatim so their sha256 equals
the anchor the target was configured with (published_source.anchor_sha256). The
path served is /published_hashes.json, matching the URL a target's
ELYON_PUBLISHER_URL points at and the `_REQUIRED_RECORD_KEYS` the fetch side
anchor-verifies.

No new canonical invariant (canon section 14): serving the record is verification
I/O; the publisher decides nothing and executes nothing. Trust is NOT placed in
the transport - the target anchor-verifies the fetched bytes against its pinned
root (published_source.load_record_from_bytes), so a substituted or tampered
record fails closed regardless of how it was served. Secure distribution of the
pinned anchor itself remains the named G5 floor (Decision F).

Configuration (out-of-band, never hard-coded):
  ELYON_PUBLISHED_RECORD - path to the published record bytes to serve
                           (default: EVIDENCE/published_hashes.json, relative to
                           the working directory).

Deploy:  uvicorn IMPLEMENTATION.publisher:app --host 0.0.0.0 --port 9100 \
             --ssl-certfile <cert> --ssl-keyfile <key>

Ledger: VL-063 (T-G5-transport; multi-process + real-TLS chain, artifact 12 steps 2-3 in-env).
"""

import os

from fastapi import FastAPI, HTTPException, Response

PUBLISHED_RECORD_PATH = os.environ.get(
    "ELYON_PUBLISHED_RECORD", "EVIDENCE/published_hashes.json"
)

app = FastAPI(title="Elyon-Sol published-record publisher")


@app.get("/published_hashes.json")
def published_hashes():
    """Serve the committed published record bytes verbatim (so their sha256
    equals the target's pinned anchor). A missing record file is a fail-closed
    503 rather than a fabricated body."""
    try:
        with open(PUBLISHED_RECORD_PATH, "rb") as f:
            data = f.read()
    except OSError:
        raise HTTPException(status_code=503, detail="published record unavailable")
    return Response(content=data, media_type="application/json")
