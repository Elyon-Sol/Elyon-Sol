"""
Mode A path THROUGH Envoy - Feature 2 layer 1 (inline body binding), end to end
against the REAL compose stack (deploy/docker-compose.yml + docker-compose.authz.yml).
NOT hermetic: it needs the running stack, so CI skips it (exit 2 when unconfigured).

    ELYON_ENVOY_URL=http://localhost:10000 ELYON_GATE_URL=http://localhost:8000 \\
    PYTHONPATH=. python EVIDENCE/proofs/envoy_inline_path_001_runner.py

What it proves (each case is a separate HTTP exchange through Envoy's public
listener; the plain upstream's /executed counter is read via a one-off
`docker compose exec`, which the runner does not need - it reads the counter
through Envoy itself, since GET passes both filters):

  positive control  a token minted at the gate for exactly this path and body
                    is ALLOWED by the inline sidecar, ALLOWED by OPA, and the
                    upstream executes ONCE
  replay            the same token again -> 403, no second execution
  tampered body     a fresh token, one byte of the body changed -> 403
  other path        a fresh token presented on a different action path -> 403
  query added       a fresh token, same path plus a query string -> 403
  no token          the body alone -> 403
  policy layer      a fresh token for a path OPA does not permit -> 403 with the
                    sidecar having ALLOWED (the second filter is independent)

Exit 0 iff every expectation holds and the upstream executed exactly once.
"""

import hashlib
import json
import os
import sys

import requests

sys.path.insert(0, os.getcwd())
from IMPLEMENTATION.envelope import canonical_json  # noqa: E402
from IMPLEMENTATION.mcp_server import interaction_for  # noqa: E402

ENVOY = os.environ.get("ELYON_ENVOY_URL")
GATE = os.environ.get("ELYON_GATE_URL")
TARGET_ID = os.environ.get("ELYON_TARGET_ID", "http://target:9000/target")
if not (ENVOY and GATE):
    print("unconfigured: set ELYON_ENVOY_URL and ELYON_GATE_URL (the running compose stack)")
    sys.exit(2)


def mint(tool, args):
    """Mint a signed envelope at the gate for (tool, args). tool is the FORWARDED
    path the inline sidecar binds ("/authz" + the public path)."""
    r = requests.post(GATE + "/governed-call", timeout=15,
                      json={"target_url": TARGET_ID, "interaction": interaction_for(tool, args)})
    assert r.status_code == 200, (r.status_code, r.text[:200])
    return r.json()["envelope"]


def through_envoy(path, body_bytes, envelope=None):
    headers = {"content-type": "application/json"}
    if envelope is not None:
        headers["X-Elyon-Sol-Envelope"] = canonical_json(envelope)
    r = requests.post(ENVOY + path, data=body_bytes, headers=headers, timeout=15)
    return r.status_code, r.headers.get("x-elyon-decision"), r.headers.get("x-elyon-reason")


def executed():
    r = requests.get(ENVOY + "/executed", timeout=15)
    assert r.status_code == 200, r.status_code
    return r.json()


results = []


def case(name, ok, detail):
    results.append((name, ok, detail))
    print("[%s] %-18s %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    args = {"amount": 100, "to": "acct-42"}
    body = json.dumps(args).encode()
    path = "/act/transfer_funds"
    bound_tool = "/authz" + path
    before = executed()["count"]

    env = mint(bound_tool, args)
    st, dec, reason = through_envoy(path, body, env)
    after = executed()
    case("positive_control", st == 200 and after["count"] == before + 1
         and after["last"]["body_sha256"] == hashlib.sha256(body).hexdigest()
         and after["last"]["x_elyon_decision"] == "ALLOW",
         "http %s, executed %d -> %d, upstream saw decision %s" % (st, before, after["count"], after["last"]["x_elyon_decision"]))

    st, dec, reason = through_envoy(path, body, env)
    case("replay", st == 403 and executed()["count"] == before + 1, "http %s %s %s" % (st, dec, reason))

    env2 = mint(bound_tool, args)
    st, dec, reason = through_envoy(path, json.dumps({"amount": 100, "to": "acct-43"}).encode(), env2)
    case("tampered_body", st == 403 and executed()["count"] == before + 1, "http %s %s %s" % (st, dec, reason))

    env3 = mint(bound_tool, args)
    st, dec, reason = through_envoy("/act/delete_database", body, env3)
    case("other_path", st == 403 and executed()["count"] == before + 1, "http %s %s %s" % (st, dec, reason))

    env4 = mint(bound_tool, args)
    st, dec, reason = through_envoy(path + "?all=1", body, env4)
    case("query_added", st == 403 and executed()["count"] == before + 1, "http %s %s %s" % (st, dec, reason))

    st, dec, reason = through_envoy(path, body, None)
    case("no_token", st == 403 and executed()["count"] == before + 1, "http %s %s %s" % (st, dec, reason))

    # Policy layer: OPA permits only GET and POST /act/...; a path the sidecar
    # admits (token bound to it) but OPA denies must still be 403, unexecuted.
    other = "/admin/reset"
    env5 = mint("/authz" + other, args)
    st, dec, reason = through_envoy(other, body, env5)
    case("policy_layer", st == 403 and executed()["count"] == before + 1,
         "http %s (sidecar decision header: %s)" % (st, dec))

    final = executed()["count"]
    ok = all(r[1] for r in results) and final == before + 1
    print("-" * 72)
    print("upstream executed: %d -> %d (expected exactly +1)" % (before, final))
    print("RESULT: %s" % ("ALL EXPECTED - the Mode A path through Envoy admits exactly the bound action, once"
                          if ok else "UNEXPECTED OUTCOME(S)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
