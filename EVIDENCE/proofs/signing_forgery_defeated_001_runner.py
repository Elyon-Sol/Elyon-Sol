"""
VL-040 issuer-signing evidence runner (T-signing).

Reproduces the VL-039 follow-up 2 three-model forgery construction verbatim and
shows it is now REFUSED on the signed path, while a genuinely gate-signed
envelope is HONORED. A live Ed25519 keypair is generated in-process; the
private key is never written to disk (constraint i: nothing hand-copied, no key
material persisted).

Unlike the G5 cross-host runner, this is a single-process demonstration: issuer
signing is a PROVENANCE property (did the gate mint this?), verifiable wholly
in-process via verify_envelope(..., pinned_public_keys=...), which is exactly
the target's admission policy. No divergent disk, subprocess, or loopback is
required (those were the G5 cross-host TRANSPORT property). The target's policy
here is "verify the issuer signature against my pinned public key."

Opt-in scope (honest): this demonstrates the signing CAPABILITY. pep.py's
default forward remains UNSIGNED per the VL-040 opt-in decision; the mandatory
cutover (signature required on the gate's default path) is the named follow-on.
The unsigned-path contrast below is included to make the boundary explicit:
the same forge is still ACCEPTED when no public key is pinned.

Trust note (parallel to B-prime-1): signing does not make verification
trustless. Trust moves from "anyone can recompute decision_sha256" to "the
target trusts the pinned issuer public key, distributed out-of-band." Key
distribution / rotation / compromise / revocation are the named floor, pending
the key-governance cross-model evaluate; "forgery-resistant" is not asserted as
a settled claim until that verdict is in.

Run from repo root:  PYTHONPATH=. python3 EVIDENCE/proofs/signing_forgery_defeated_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.
"""

import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from IMPLEMENTATION.envelope import (
    build_envelope,
    canonical_json,
    reassert,
    sign_envelope,
    _HASH_EXCLUDED_KEYS,
    _read_canon_lock,
    _evaluator_sha256,
    _sha256_text,
)
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.verifier import verify_envelope

TARGET_URL = "http://127.0.0.1:9000/target"
GATE_KEY_ID = "gate-ed25519-001"


def _interaction(context=None):
    return {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {} if context is None else context,
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }


def _unsigned(interaction):
    return build_envelope(
        decision="ELIGIBLE", target_url=TARGET_URL,
        normalized_interaction=interaction, manifest=load_manifest(),
        ac3=True, t26=True, manifest_integrity=True,
        timestamp_utc="2026-05-31T00:00:00+00:00",
    )


def _three_model_forge(interaction):
    """The verbatim VL-039 follow-up 2 construction: public knowledge only."""
    forge = {
        "envelope_version": "1.0",
        "decision": "ELIGIBLE",
        "target_url": TARGET_URL,
        "canon": {"version": "0.9.8.4", "canon_sha256": _read_canon_lock()},
        "evaluated_against": {"manifest_version": "1.0", "manifest_sha256": manifest_sha256()},
        "request_context": {
            "AP": interaction["AP"], "OP": interaction["OP"], "context": interaction["context"],
            "expected_manifest_version": "1.0", "expected_manifest_sha256": manifest_sha256(),
        },
        "evaluator": {"version": "0.9.8.4", "evaluator_sha256": _evaluator_sha256()},
        "condition_results": {"ac3": True, "t26": True, "manifest_integrity": True, "ccs": None},
        "timestamp_utc": "2026-05-31T00:00:00+00:00",
    }
    hashable = {k: v for k, v in forge.items() if k not in _HASH_EXCLUDED_KEYS}
    forge["decision_sha256"] = _sha256_text(canonical_json(hashable))
    return forge


def main():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    pinned = {GATE_KEY_ID: pub}

    interaction = _interaction()
    signed = sign_envelope(_unsigned(interaction), priv, GATE_KEY_ID)

    # The VL-039 follow-up 2 forge, with an adversary-chosen interaction.
    forge_interaction = _interaction(context={"exfil": "yes"})
    forge = _three_model_forge(forge_interaction)

    # Tampered genuine envelope (request_context mutated, not re-signed).
    tampered = sign_envelope(_unsigned(interaction), priv, GATE_KEY_ID)
    tampered["request_context"]["AP"] = ["identity", "role", "admin"]

    print("=" * 74)
    print("VL-040 issuer-signing: the three-model forge, now defeated")
    print("=" * 74)
    print("Gate public key id : %s" % GATE_KEY_ID)
    print("Pinned public key  : %s (raw, hex)" % pub.public_bytes_raw().hex())
    print("decision_sha256 identical signed-vs-unsigned: %s"
          % (signed["decision_sha256"] == _unsigned(interaction)["decision_sha256"]))
    print("signed envelope reasserts: %s" % reassert(signed)["outcome"])
    print("-" * 74)

    cases = [
        # (label, envelope, interaction, pinned_public_keys, exp_accepted, exp_reason)
        ("genuine gate-signed envelope (signed path)",
         signed, interaction, pinned, True, "REASSERTED_AND_BOUND"),
        ("three-model forge, no signature (signed path)",
         forge, forge_interaction, pinned, False, "REF_VERIFY_SIGNATURE_INVALID"),
        ("forge with unknown key_id (signed path)",
         {**forge, "issuer_key_id": "attacker-999", "issuer_signature": "00" * 64},
         forge_interaction, pinned, False, "REF_VERIFY_SIGNATURE_UNKNOWN_KEY"),
        ("tampered signed envelope (signed path)",
         tampered, interaction, pinned, False, "REF_VERIFY_SIGNATURE_INVALID"),
        ("three-model forge, UNSIGNED path (no pinned key) - honest contrast",
         forge, forge_interaction, None, True, "REASSERTED_AND_BOUND"),
    ]

    ok = True
    for label, env, inter, keys, exp_acc, exp_reason in cases:
        res = verify_envelope(env, inter, TARGET_URL, pinned_public_keys=keys)
        passed = (res["accepted"] == exp_acc and res["reason"] == exp_reason)
        ok = ok and passed
        print("[%s] %s" % ("PASS" if passed else "FAIL", label))
        print("       accepted=%s reason=%s" % (res["accepted"], res["reason"]))

    print("-" * 74)
    # Killer invariant: the forge that the unsigned path accepts is refused on
    # the signed path. Both halves must hold.
    signed_refuses_forge = (
        verify_envelope(forge, forge_interaction, TARGET_URL, pinned_public_keys=pinned)["accepted"] is False
    )
    unsigned_accepts_forge = (
        verify_envelope(forge, forge_interaction, TARGET_URL)["accepted"] is True
    )
    killer = signed_refuses_forge and unsigned_accepts_forge
    print("KILLER PROPERTY (signed path refuses the forge the unsigned path accepts): %s"
          % ("HOLDS" if killer else "FAILED"))
    ok = ok and killer

    print("=" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    print("Scope: forgery closed on the SIGNED path only (opt-in). Trust moves to")
    print("the pinned issuer public key; 'forgery-resistant' as a settled claim")
    print("awaits the key-governance cross-model evaluate. pep.py default unsigned.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
