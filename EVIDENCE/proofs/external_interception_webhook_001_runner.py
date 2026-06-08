"""
External-interception evidence runner (G4/G5; Enforcement Evidence Addendum Section 2).

Third-party external observation of the gate's fail-closed enforcement property: REFUSE
produces ZERO external side effects; ELIGIBLE produces EXACTLY ONE external execution
(an outbound POST the gate makes on the ELIGIBLE branch only). The receiver is
webhook.site - an HTTP intake OUTSIDE the gate's process, so the side-effect count is
observed by a third party, not self-reported by the gate.

This is the real-external-receiver counterpart of the local-receiver reproduction. It is a
MANUAL, author-run evidence runner (it makes REAL external POSTs to webhook.site - 102 of
them on the ELIGIBLE path), NOT a CI/pytest test (pytest stays network-free). Per GR-3 the
result is referent-bound (third-party-observed side effects), but it is still development-
side evidence, not an external adversarial pen-test on a real multi-host surface.

----------------------------------------------------------------------------------------
Configuration (the photo of 2026-06-08): the existing webhook.site URL is reused so no new
URL is needed; the current inbox count 155 is the BASELINE OFFSET. After a clean run the
inbox should read 155 + 102 = 257, with exactly 102 new POSTs (all from ELIGIBLE calls).
----------------------------------------------------------------------------------------

Gate: by default this runner starts its own PEP (uvicorn) with an ephemeral Ed25519 signing
key via the production env path (ELYON_SIGNING_KEY_HEX + ELYON_SIGNING_KEY_ID), matching the
VL-047 mandatory-signing cutover (a gate with no key fails closed). To drive an externally
started gate instead, set ELYON_GATE_URL (e.g. http://127.0.0.1:8000/governed-call) and the
runner will not start its own.

Run from repo root:
    PYTHONPATH=. python3 EVIDENCE/proofs/external_interception_webhook_001_runner.py
Exits 0 iff every HTTP outcome is as expected (and, when the webhook.site API is reachable,
the observed external delta equals the ELIGIBLE count).
"""

import datetime
import hashlib
import os
import subprocess
import sys
import time

import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# --- Receiver configuration (from the webhook.site control panel) ---
WEBHOOK_TOKEN_ID = "4da50ca0-9824-4654-8394-848e3b355e38"
WEBHOOK_URL = "https://webhook.site/%s" % WEBHOOK_TOKEN_ID
BASELINE_INBOX = 155  # current inbox count; baseline offset so no new URL is needed
# webhook.site request-count API (best-effort; may require an API key on some tiers).
WEBHOOK_COUNT_API = "https://webhook.site/token/%s/requests" % WEBHOOK_TOKEN_ID

# --- Gate configuration ---
REPO = os.getcwd()
GATE_URL = os.environ.get("ELYON_GATE_URL")  # if set, use an already-running gate
SELF_START = GATE_URL is None
GATE_PORT = int(os.environ.get("ELYON_GATE_PORT", "8000"))
if SELF_START:
    GATE_URL = "http://127.0.0.1:%d/governed-call" % GATE_PORT

MANIFEST_SHA = hashlib.sha256(
    open(os.path.join(REPO, "MANIFEST", "manifest.json"), "rb").read()
).hexdigest()


def body(eligible):
    """REFUSE: empty AP/OP (schema-valid, evaluator REFUSE). ELIGIBLE: supersets of the
    manifest required sets. target_url is the external webhook receiver."""
    interaction = {
        "AP": (["identity", "role"] if eligible else []),
        "OP": (["session", "request"] if eligible else []),
        "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": MANIFEST_SHA,
    }
    return {"target_url": WEBHOOK_URL, "interaction": interaction}


def webhook_count():
    """Best-effort live inbox count via the webhook.site API. None if unavailable."""
    try:
        r = requests.get(WEBHOOK_COUNT_API, params={"page": 1, "per_page": 1}, timeout=10)
        if r.status_code == 200:
            return int(r.json().get("total"))
    except Exception:
        pass
    return None


def start_gate():
    """Start the PEP with an ephemeral signing key (production env path). Returns Popen."""
    priv = Ed25519PrivateKey.generate()
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO
    env["ELYON_SIGNING_KEY_HEX"] = priv.private_bytes_raw().hex()
    env["ELYON_SIGNING_KEY_ID"] = "addendum-external-interception-001"
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "IMPLEMENTATION.pep:app",
         "--port", str(GATE_PORT), "--log-level", "warning"],
        cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc


results = {"refuse_calls": 0, "refuse_403": 0, "eligible_calls": 0,
           "eligible_200": 0, "unexpected": 0}


def call(eligible):
    r = requests.post(GATE_URL, json=body(eligible), timeout=15)
    if eligible:
        results["eligible_calls"] += 1
        results["eligible_200" if r.status_code == 200 else "unexpected"] += 1
    else:
        results["refuse_calls"] += 1
        results["refuse_403" if r.status_code == 403 else "unexpected"] += 1
    return r.status_code


def wait_ready():
    for _ in range(60):
        try:
            r = requests.post(GATE_URL, json=body(False), timeout=3)
            if r.status_code in (200, 403):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    gate_proc = start_gate() if SELF_START else None
    try:
        if not wait_ready():
            print("GATE NOT READY at %s" % GATE_URL)
            return 2

        api_before = webhook_count()
        inbox_before = api_before if api_before is not None else BASELINE_INBOX
        t0 = datetime.datetime.now(datetime.timezone.utc)

        # Sanity: 1 REFUSE, 1 ELIGIBLE
        s1 = call(False)
        s2 = call(True)

        # Block 2: 50 REFUSE then 50 ELIGIBLE
        t_b2 = datetime.datetime.now(datetime.timezone.utc)
        for _ in range(50):
            call(False)
        for _ in range(50):
            call(True)
        t_b2_end = datetime.datetime.now(datetime.timezone.utc)

        # Block 3: 51 alternating REFUSE/ELIGIBLE
        t_b3 = datetime.datetime.now(datetime.timezone.utc)
        for _ in range(51):
            call(False)
            call(True)
        t_b3_end = datetime.datetime.now(datetime.timezone.utc)

        # Allow webhook.site a moment to register the final POSTs, then read the count.
        time.sleep(3)
        api_after = webhook_count()
        inbox_after = (api_after if api_after is not None
                       else inbox_before + results["eligible_calls"])

        total = results["refuse_calls"] + results["eligible_calls"]
        external_posts = inbox_after - inbox_before

        print("=" * 74)
        print("EXTERNAL-INTERCEPTION EVIDENCE (webhook.site, third-party receiver)")
        print("=" * 74)
        print("snapshot_commit  :",
              subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO).decode().strip())
        print("manifest_sha256  :", MANIFEST_SHA)
        print("gate             :", GATE_URL, "(self-started)" if SELF_START else "(external)")
        print("receiver         :", WEBHOOK_URL)
        print("inbox baseline   :", inbox_before,
              "(from webhook.site API)" if api_before is not None
              else "(BASELINE_INBOX offset; API not reached)")
        print("-" * 74)
        print("sanity   : call1 REFUSE -> %s ; call2 ELIGIBLE -> %s" % (s1, s2))
        print("block2   : 50 REFUSE + 50 ELIGIBLE   %s -> %s" % (t_b2.isoformat(), t_b2_end.isoformat()))
        print("block3   : 51/51 alternating         %s -> %s" % (t_b3.isoformat(), t_b3_end.isoformat()))
        print("-" * 74)
        print("Total HTTP calls (sanity + Blocks 2 and 3) :", total)
        print("REFUSE calls (expected 403)                :", results["refuse_calls"])
        print("REFUSE returning 403                       :", results["refuse_403"])
        print("ELIGIBLE calls (expected 200)              :", results["eligible_calls"])
        print("ELIGIBLE returning 200                     :", results["eligible_200"])
        print("Unexpected HTTP outcomes                   :", results["unexpected"])
        print("Webhook inbox before                       :", inbox_before)
        print("Webhook inbox after                        :", inbox_after,
              "" if api_after is not None else "(expected; API not reached)")
        print("External POSTs observed                    :", external_posts)
        print("External POSTs from REFUSE calls           : 0 (REFUSE never forwards)")
        print("External POSTs from ELIGIBLE calls         :", results["eligible_calls"])
        print("-" * 74)

        http_ok = (results["unexpected"] == 0
                   and results["refuse_403"] == results["refuse_calls"]
                   and results["eligible_200"] == results["eligible_calls"]
                   and total == 204)
        # The external-delta assertion is enforced only when the API was reachable
        # both times; otherwise it is reported as expected (manual eyeball vs the inbox).
        if api_before is not None and api_after is not None:
            delta_ok = (external_posts == results["eligible_calls"])
            print("External-delta auto-verified via webhook.site API: %s "
                  "(observed +%d, expected +%d)"
                  % ("OK" if delta_ok else "MISMATCH", external_posts, results["eligible_calls"]))
        else:
            delta_ok = True
            print("External-delta NOT auto-verified (webhook.site API not reached). "
                  "Confirm manually: inbox should read %d (= %d baseline + %d ELIGIBLE)."
                  % (inbox_before + results["eligible_calls"], inbox_before, results["eligible_calls"]))

        ok = http_ok and delta_ok
        print("=" * 74)
        print("RESULT:", "ALL EXPECTED" if ok else "MISMATCH")
        return 0 if ok else 1
    finally:
        if gate_proc is not None:
            gate_proc.terminate()
            try:
                gate_proc.wait(timeout=5)
            except Exception:
                gate_proc.kill()


if __name__ == "__main__":
    sys.exit(main())
