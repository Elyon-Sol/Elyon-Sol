"""
VL-041 expiry killer demo: a signed envelope past its not_after is REFUSED;
the same envelope with a future not_after is HONORED; not_after cannot be
extended (it is inside the signed region); decision_sha256 is unchanged by
not_after (no-op property preserved from VL-040). Exercises the real
sign_envelope + verify_envelope end-to-end with a live Ed25519 keypair.
reassert() runs pure via record_source (no repo files). Exit 0 iff all hold.
"""
import sys
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.envelope import (
    canonical_json, _sha256_text, _HASH_EXCLUDED_KEYS, sign_envelope,
)
from IMPLEMENTATION.verifier import (
    verify_envelope, ACCEPT_REASSERTED_AND_BOUND,
    REF_VERIFY_SIGNATURE_EXPIRED, REF_VERIFY_SIGNATURE_INVALID,
)

CANON = "a" * 64
EVAL = "b" * 64
MAN = "c" * 64

def base_envelope():
    env = {
        "envelope_version": "1.0",
        "decision": "ELIGIBLE",
        "target_url": "https://target.example/act",
        "canon": {"version": "0.9.8.4", "canon_sha256": CANON},
        "evaluated_against": {"manifest_version": "1.0", "manifest_sha256": MAN},
        "request_context": {
            "AP": ["identity", "role"], "OP": ["session", "request"],
            "context": {"k": "v"},
            "expected_manifest_version": "1.0",
            "expected_manifest_sha256": MAN,
        },
        "evaluator": {"version": "0.9.8.4", "evaluator_sha256": EVAL},
        "condition_results": {"ac3": True, "t26": True, "manifest_integrity": True, "ccs": None},
        "timestamp_utc": "2026-06-02T00:00:00+00:00",
    }
    hashable = {k: v for k, v in env.items() if k not in _HASH_EXCLUDED_KEYS}
    env["decision_sha256"] = _sha256_text(canonical_json(hashable))
    return env

REC = {"canon_sha256": CANON, "evaluator_sha256": EVAL, "manifest_sha256": MAN}
INTER = {
    "AP": ["role", "identity"],  # unsorted on purpose; verifier normalizes
    "OP": ["request", "session"],
    "context": {"k": "v"},
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256": MAN,
}
TARGET = "https://target.example/act"

def vfy(env, **kw):
    return verify_envelope(env, INTER, TARGET, record_source=REC,
                           pinned_public_keys={"gate-key-1": PUB}, **kw)

priv = Ed25519PrivateKey.generate()
PUB = priv.public_key()
NOW = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)
ok = True
def check(label, cond):
    global ok
    ok = ok and cond
    print(("PASS" if cond else "FAIL"), "-", label)

# 1. no not_after -> honored (VL-040 compat)
e_none = sign_envelope(base_envelope(), priv, "gate-key-1")
check("signed, no expiry -> honored", vfy(e_none, now=NOW)["reason"] == ACCEPT_REASSERTED_AND_BOUND)

# 2. future not_after -> honored
e_future = sign_envelope(base_envelope(), priv, "gate-key-1", not_after=NOW + timedelta(hours=1))
check("signed, future not_after -> honored", vfy(e_future, now=NOW)["reason"] == ACCEPT_REASSERTED_AND_BOUND)

# 3. past not_after -> REFUSED expired (the killer: same key, expired window)
e_past = sign_envelope(base_envelope(), priv, "gate-key-1", not_after=NOW - timedelta(seconds=1))
check("signed, past not_after -> REFUSED EXPIRED", vfy(e_past, now=NOW)["reason"] == REF_VERIFY_SIGNATURE_EXPIRED)

# 4. exact boundary now == not_after -> REFUSED (strict: valid iff now < not_after)
e_edge = sign_envelope(base_envelope(), priv, "gate-key-1", not_after=NOW)
check("signed, now == not_after -> REFUSED EXPIRED", vfy(e_edge, now=NOW)["reason"] == REF_VERIFY_SIGNATURE_EXPIRED)

# 5. tamper: take the future-valid envelope, EXTEND not_after -> signature breaks
e_tamper = dict(e_future)
e_tamper["not_after"] = (NOW + timedelta(days=3650)).isoformat()
check("extend not_after on signed envelope -> REFUSED INVALID (tamper-proof)",
      vfy(e_tamper, now=NOW)["reason"] == REF_VERIFY_SIGNATURE_INVALID)

# 6. no-op property: decision_sha256 identical with and without not_after
check("decision_sha256 unchanged by not_after (VL-040 no-op preserved)",
      e_future["decision_sha256"] == e_none["decision_sha256"] == base_envelope()["decision_sha256"])

# 7. KILLER invariant: an expired signed envelope is refused while the same
#    decision with a live window is honored - time bounds a (possibly leaked) key.
killer = (vfy(e_past, now=NOW)["accepted"] is False
          and vfy(e_future, now=NOW)["accepted"] is True)
check("KILLER: expired refused while live honored (compromise is time-bounded)", killer)

print()
print("ALL PASS" if ok else "FAILURE")
sys.exit(0 if ok else 1)
