"""
A plain upstream for the Mode A example (deploy/docker-compose.authz.yml): the
service Envoy fronts, standing in for "the customer's app". It performs NO
admissibility check and NO cryptography - that is the point of the example:
the ext-authz chain in front of it (elyon-authz inline, then OPA) is what
decides, and this app only records what it was asked to execute.

    POST /act/<action>   -> "executes" the action: increments the counter and
                            keeps the last request's path, the sha256 of its
                            body bytes, and the decision headers Envoy passed on
    GET  /executed       -> {"count": N, "last": {...}}   (the proof reads this)

Reachable only on the compose network; no host port is published.
"""

import hashlib
import threading

from fastapi import FastAPI, Request

app = FastAPI(title="Elyon-Sol Mode A example upstream (plain)")
_lock = threading.Lock()
_state = {"count": 0, "last": None}


@app.post("/act/{action:path}")
async def act(action: str, request: Request):
    body = await request.body()
    record = {
        "path": request.url.path + (("?" + request.url.query) if request.url.query else ""),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "x_elyon_decision": request.headers.get("x-elyon-decision"),
        "x_elyon_reason": request.headers.get("x-elyon-reason"),
    }
    with _lock:
        _state["count"] += 1
        _state["last"] = record
        n = _state["count"]
    return {"executed": True, "action": action, "count": n}


@app.get("/executed")
def executed():
    with _lock:
        return dict(_state)
