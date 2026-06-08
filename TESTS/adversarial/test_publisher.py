"""
Publisher-service tests for Elyon-Sol
(docs/restructure/12_g5_transport_design.md steps 2-3).

IMPLEMENTATION/publisher.py serves the committed published record. The
load-bearing property: it serves the bytes VERBATIM, so their sha256 equals the
anchor a target pins out-of-band and the fetch side anchor-verifies. Trust is not
placed in the publisher or the transport - the target anchors the bytes - but the
publisher must not mangle them.

Ledger: VL-063 (T-G5-transport; multi-process + real-TLS chain, artifact 12 steps 2-3 in-env).
"""

from fastapi.testclient import TestClient

from IMPLEMENTATION.publisher import app
from IMPLEMENTATION.published_source import anchor_sha256, load_record_from_bytes

PUBLISHED_HASHES_PATH = "EVIDENCE/published_hashes.json"


def _committed_bytes():
    with open(PUBLISHED_HASHES_PATH, "rb") as f:
        return f.read()


def test_publisher_serves_committed_record_verbatim():
    client = TestClient(app)
    r = client.get("/published_hashes.json")
    assert r.status_code == 200
    assert r.content == _committed_bytes()
    assert r.headers["content-type"].startswith("application/json")


def test_publisher_served_bytes_anchor_to_committed_record():
    """The served bytes hash to the committed record's anchor and parse as a
    valid record - i.e. a target fetching this publisher and anchor-verifying
    against the committed root accepts the result."""
    client = TestClient(app)
    served = client.get("/published_hashes.json").content
    root = anchor_sha256(_committed_bytes())
    assert anchor_sha256(served) == root
    assert load_record_from_bytes(served, root) is not None
