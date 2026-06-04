"""WIRING-track readiness gate engine (T-readiness).

See docs/restructure/10_readiness_spec.md. The single source of readiness truth is
EVIDENCE/readiness.json. Every TRUE flag MUST name a proof test; a true flag with
no proof is a gate failure (validate_manifest). Whether a named test PASSES is
enforced by the suite itself (a failing proof test reds the run); this module
additionally checks that each named proof FILE exists on disk
(assert_proof_files_exist), which catches a flag naming a test that is not there.
built-but-unwired is ALLOWED; claimed-but-unwired is FORBIDDEN.

Pure stdlib, ASCII, offline, deterministic.
"""

import json
import os

FLAG_KEYS = ("built", "wired_to_default", "exercised_e2e", "transported")
PREDICATE_NAMES = ("DEFAULT_SECURE", "END_TO_END_NO_SHORTCUT", "ROOT_RECOVERY")

# The capabilities the END_TO_END_NO_SHORTCUT predicate depends on (the
# enumerated dependency set, VL-048; 10_readiness_spec.md section 4.2). The
# signed cross-host chain exercises exactly these end-to-end over transport;
# the other capabilities are not on the default signed chain.
END_TO_END_CAPABILITIES = ("issuer_signing", "enforcement_push")

# The capabilities the ROOT_RECOVERY predicate depends on (the enumerated
# dependency set, VL-049; 10_readiness_spec.md section 4 item 3). The signed
# cross-host rotation chain exercises exactly these end-to-end over transport:
# root_rotation (the target fetches the root record, builds the status view, and
# survives a planned in-band R1->R2 rotation) and issuer_key_revocation (the
# key-record path that lets the designated successor vouch the issuer key
# without a re-pin). The gate default forward is unchanged (rotation is
# target-side posture), so green requires exercised_e2e + transported, NOT
# wired_to_default - the same exercised_e2e/transported test as END_TO_END.
ROOT_RECOVERY_CAPABILITIES = ("root_rotation", "issuer_key_revocation")


def load_manifest(path):
    with open(path, "r", encoding="ascii") as f:
        return json.load(f)


def _test_file_of(proof):
    """A proof id is 'path/to/test_x.py' or 'path/to/test_x.py::node'. Return the file part."""
    if not proof:
        return None
    return proof.split("::", 1)[0]


def validate_manifest(m):
    """Return a list of error strings. Empty list means the manifest is well-formed
    and honest (no true flag lacks a proof; no false flag lacks a reason)."""
    errors = []

    if m.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    caps = m.get("capabilities", {})
    if not caps:
        errors.append("no capabilities declared")

    for name, cap in caps.items():
        for k in FLAG_KEYS:
            if k not in cap:
                errors.append("%s: missing flag '%s'" % (name, k))
                continue
            flag = cap[k]
            val = flag.get("value")
            if val not in (True, False):
                errors.append("%s.%s: value must be boolean" % (name, k))
                continue
            if val is True and not flag.get("proof"):
                errors.append(
                    "%s.%s is TRUE but names no proof test "
                    "(every true flag must be test-backed)" % (name, k)
                )
            if val is False and not flag.get("blocked_by"):
                errors.append(
                    "%s.%s is FALSE but names no blocked_by reason" % (name, k)
                )

    preds = m.get("deployment_predicates", {})
    for pname in PREDICATE_NAMES:
        if pname not in preds:
            errors.append("missing deployment_predicate '%s'" % pname)
    for pname, p in preds.items():
        g = p.get("green")
        if g not in (True, False):
            errors.append("predicate %s: green must be boolean" % pname)
            continue
        if g is True and not p.get("proof"):
            errors.append("predicate %s is GREEN but names no proof test" % pname)
        if g is False and not p.get("blocked_by"):
            errors.append("predicate %s is FALSE but names no blocked_by reason" % pname)

    errors.extend(_consistency(m))
    return errors


def _consistency(m):
    """A predicate cannot be green while the capability flags it depends on are false."""
    errs = []
    preds = m.get("deployment_predicates", {})
    caps = m.get("capabilities", {})

    ds = preds.get("DEFAULT_SECURE", {})
    if ds.get("green") is True:
        sig = caps.get("issuer_signing", {})
        if sig.get("wired_to_default", {}).get("value") is not True:
            errs.append(
                "DEFAULT_SECURE is green but issuer_signing.wired_to_default is not true"
            )

    e2e = preds.get("END_TO_END_NO_SHORTCUT", {})
    if e2e.get("green") is True:
        # The predicate depends ONLY on the capabilities exercised by the
        # signed cross-host chain (VL-048): issuer_signing (gate signs;
        # target verifies the signature) and enforcement_push (the envelope
        # is delivered and verified over real transport). issuer_key_expiry,
        # issuer_key_revocation, and root_rotation are NOT on the default
        # signed chain (expiry: the default forward stamps no not_after;
        # revocation/rotation: target-side record posture, ROOT_RECOVERY).
        # Quantifying over all capabilities would make green require
        # ROOT_RECOVERY's work and is incoherent with it being a separate
        # red. See 10_readiness_spec.md section 4.2 (the enumerated set).
        for name in END_TO_END_CAPABILITIES:
            cap = caps.get(name, {})
            if cap.get("exercised_e2e", {}).get("value") is not True:
                errs.append(
                    "END_TO_END_NO_SHORTCUT is green but %s.exercised_e2e is not true" % name
                )
            if cap.get("transported", {}).get("value") is not True:
                errs.append(
                    "END_TO_END_NO_SHORTCUT is green but %s.transported is not true" % name
                )

    rr = preds.get("ROOT_RECOVERY", {})
    if rr.get("green") is True:
        # Mirrors the END_TO_END narrowing (VL-049): ROOT_RECOVERY green requires
        # the rotation chain's enumerated capabilities exercised end-to-end over
        # transport. The gate default forward is unchanged (rotation is
        # target-side posture), so this does NOT require wired_to_default - the
        # same exercised_e2e + transported test as END_TO_END. See
        # 10_readiness_spec.md section 4 item 3 (the enumerated set).
        for name in ROOT_RECOVERY_CAPABILITIES:
            cap = caps.get(name, {})
            if cap.get("exercised_e2e", {}).get("value") is not True:
                errs.append(
                    "ROOT_RECOVERY is green but %s.exercised_e2e is not true" % name
                )
            if cap.get("transported", {}).get("value") is not True:
                errs.append(
                    "ROOT_RECOVERY is green but %s.transported is not true" % name
                )
    return errs


def predicate_summary(m):
    preds = m.get("deployment_predicates", {})
    green = [n for n in PREDICATE_NAMES if preds.get(n, {}).get("green") is True]
    red = [n for n in PREDICATE_NAMES if preds.get(n, {}).get("green") is not True]
    return {"n_green": len(green), "total": len(PREDICATE_NAMES), "green": green, "red": red}


def summary_line(m):
    s = predicate_summary(m)
    line = "readiness: %d of %d deployment predicates green" % (s["n_green"], s["total"])
    if s["red"]:
        line += "  |  RED: " + ", ".join(s["red"])
    return line


def assert_proof_files_exist(m, repo_root):
    """Return a list of (proof_id, exists) for every named proof. In-repo check:
    a named proof whose FILE is missing is a lie the gate must catch."""
    results = []
    seen = set()

    def check(proof):
        f = _test_file_of(proof)
        if not f or f in seen:
            return
        seen.add(f)
        results.append((f, os.path.isfile(os.path.join(repo_root, f))))

    for cap in m.get("capabilities", {}).values():
        for k in FLAG_KEYS:
            check(cap.get(k, {}).get("proof"))
    for p in m.get("deployment_predicates", {}).values():
        check(p.get("proof"))
    return results
