"""
Three-domain synthetic POC runner (docs/restructure/25_three_domain_poc_spec.md, VL-096).

Drives the UNCHANGED production chain (pep gate -> signed envelope -> verify_envelope +
ReplayCache executor) across three domains (medical, legal, finance) with synthetic,
reviewer-legible inputs, and writes one human-readable report per domain.

Two modes (same case set, same expected outcomes; differ only in surface + currency source):

  inproc  (default, deterministic, hermetic, the self-verify + artifact generator)
          - admit via pep.app TestClient (injected gate signing key, mocked push)
          - executor via verify_envelope(record_source=None, pinned gate key) + replay cache
          - pins each domain's manifest by copying the committed manifest bytes onto
            MANIFEST/manifest.json under try/finally, then restores the original
  live    (the author's referent-bound run against the VMs; see RUNBOOK_live.md)
          - admit via a real gate URL, executor via a real reference-target URL over TLS
          - per-domain manifest pinned + republished + gate restarted by the operator

Run (from the repo root):
    PYTHONPATH=. python3 -m EVIDENCE.proofs.three_domain_poc.poc_runner            # inproc, all domains
    PYTHONPATH=. python3 -m EVIDENCE.proofs.three_domain_poc.poc_runner --domain medical
    PYTHONPATH=. python3 -m EVIDENCE.proofs.three_domain_poc.poc_runner --mode live \
        --gate-url https://10.0.0.101:8000 --target-url https://10.0.0.102:9000 \
        --domain medical --ca-bundle deploy/tls/certs/ca.crt --decision-max-age 1

Exit code is non-zero if any case's actual outcome != expected (a self-check). GR-3: in-loop
runs are characterization, not certification; this does not move G5.
"""

import argparse
import os
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from EVIDENCE.proofs.three_domain_poc.domains import DOMAINS, DOMAIN_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST_LIVE_PATH = "MANIFEST/manifest.json"  # cwd-relative, matching evaluator.MANIFEST_PATH
REPORTS_DIR = os.path.join(HERE, "reports")
MANIFESTS_DIR = os.path.join(HERE, "manifests")

EXPECT_HONORED = "REASSERTED_AND_BOUND"


# ---------------------------------------------------------------------------
# Manifest pinning helpers (shared by both modes for sha computation)
# ---------------------------------------------------------------------------

def committed_manifest_path(domain: str) -> str:
    return os.path.join(MANIFESTS_DIR, f"{domain}.json")


def committed_manifest_sha256(domain: str) -> str:
    import hashlib
    with open(committed_manifest_path(domain), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Surfaces
# ---------------------------------------------------------------------------

class InProcSurface:
    """Production gate (pep.app) + production executor (verify_envelope + replay cache),
    in-process. Pins each domain's manifest onto MANIFEST/manifest.json (copying the committed
    bytes) so the live evaluator/envelope/reassert path is byte-faithful, and restores it."""

    mode = "inproc"

    def __init__(self, gate_key_id: str = "poc-gate-key-001"):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import IMPLEMENTATION.pep as pep
        from fastapi.testclient import TestClient
        from IMPLEMENTATION.replay_cache import InMemoryReplayCache

        self._pep = pep
        self._sk = Ed25519PrivateKey.generate()
        self.gate_key_id = gate_key_id
        pep._INJECTED_SIGNING_KEY = (self._sk, gate_key_id)
        self._pinned_keys = {gate_key_id: self._sk.public_key()}
        self._client = TestClient(pep.app)
        self._replay = InMemoryReplayCache()
        self._manifest_backup: Optional[bytes] = None

    # -- manifest pinning (inproc only) --
    def pin_manifest(self, domain: str) -> None:
        with open(MANIFEST_LIVE_PATH, "rb") as f:
            self._manifest_backup = f.read()
        shutil.copyfile(committed_manifest_path(domain), MANIFEST_LIVE_PATH)

    def restore_manifest(self) -> None:
        if self._manifest_backup is not None:
            with open(MANIFEST_LIVE_PATH, "wb") as f:
                f.write(self._manifest_backup)
            self._manifest_backup = None

    def manifest_sha256(self, domain: str) -> str:
        # the live on-disk sha (== committed bytes, since pin copies them)
        from IMPLEMENTATION.evaluator import manifest_sha256
        return manifest_sha256()

    def domain_targets(self, domain: Dict[str, Any]) -> Tuple[str, str]:
        return domain["target_primary"], domain["target_swap"]

    def admit(self, target_url: str, interaction: Dict[str, Any], max_age: int = 300):
        pep = self._pep

        class _R:
            status_code = 200
            text = "{}"

        def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
            return _R()

        prev_age, prev_post = pep.DECISION_MAX_AGE_SECONDS, pep.requests.post
        pep.DECISION_MAX_AGE_SECONDS = max_age
        pep.requests.post = fake_post
        try:
            r = self._client.post(
                "/governed-call",
                json={"target_url": target_url, "interaction": interaction},
            )
        finally:
            pep.DECISION_MAX_AGE_SECONDS = prev_age
            pep.requests.post = prev_post
        if r.status_code == 200:
            return "ELIGIBLE", r.json()["envelope"]
        detail = r.json().get("detail", {})
        return "REFUSE", detail

    def attempt(self, envelope, interaction, target_url, now: Optional[datetime] = None):
        from IMPLEMENTATION.verifier import verify_envelope, REF_VERIFY_REPLAY
        result = verify_envelope(
            envelope if isinstance(envelope, dict) else None,
            interaction,
            target_url,
            record_source=None,  # local-disk currency: valid, the domain manifest IS live on disk
            pinned_public_keys=self._pinned_keys,
            now=now,
        )
        if not result["accepted"]:
            return False, result["reason"]
        did = envelope.get("decision_id") if isinstance(envelope, dict) else None
        if did is not None:
            exp = _parse_not_after(envelope)
            if not self._replay.check_and_claim(did, exp, now=now):
                return False, REF_VERIFY_REPLAY
        return True, result["reason"]

    def condition_diagnosis(self, interaction: Dict[str, Any]) -> Dict[str, bool]:
        """Which production admissibility condition(s) a gate-refused interaction fails.
        The gate's HTTP body does not disclose this; these are the same functions evaluate()
        short-circuits on."""
        from IMPLEMENTATION.evaluator import (
            load_manifest, safe_manifest, ac3_valid, t26_valid, manifest_integrity_valid,
        )
        m = safe_manifest(load_manifest())
        if m is None:
            return {}
        return {
            "ac3": ac3_valid(interaction, m["AR"]),
            "t26": t26_valid(interaction, m["R"]),
            "manifest_integrity": manifest_integrity_valid(interaction, m),
        }

    def positive_control(self, target_url, interaction):
        """A valid admitted call IS honored. In-process the push is mocked (no real target acts),
        so present-then-honor as normal."""
        dec, env = self.admit(target_url, interaction)
        if dec != "ELIGIBLE":
            return None, "admit-refused", env, dec
        hon, reason = self.attempt(env, interaction, target_url)
        return hon, reason, env, dec


class LiveSurface:
    """A real gate URL + a real reference-target URL over HTTP/TLS (the author's adapter; not
    exercised in-sandbox).

    Two distinct target values (the live deployment separates them, matching
    attack_suite_live_runner.py's ELYON_LIVE_TARGET_URL vs ELYON_LIVE_TARGET_ID):
      - target_base: the reference-target client base URL (e.g. https://host:9000); requests POST
        to base + "/target".
      - target_id:   the BOUND identity (e.g. https://host:9000/target) == the target's
        ELYON_TARGET_URL env. Envelopes bind to this; the gate is admitted against it and pushes
        to it. The swap case admits against target_id + "-SWAP" (a reachable different path on the
        same host, so the gate's push does not fail closed; the executor still refuses the binding).

    The production gate uses PUSH delivery (VL-038): it forwards the admitted envelope to the
    target on ELIGIBLE, so a valid admit ACTS at the target. The positive controls therefore
    observe the target acting (its /received count) rather than re-presenting (which would replay)."""

    mode = "live"

    def __init__(self, gate_url: str, target_base: str, target_id: str, ca_bundle: Optional[str]):
        from EVIDENCE.proofs.attack_harness import RequestsClient
        verify = ca_bundle if ca_bundle else True
        self._gate = RequestsClient(gate_url, verify=verify)
        self._target = RequestsClient(target_base, verify=verify)
        self.target_id = target_id

    def pin_manifest(self, domain: str) -> None:
        pass  # the operator pins + republishes + rebuilds out of band (RUNBOOK_live.md)

    def restore_manifest(self) -> None:
        pass

    def manifest_sha256(self, domain: str) -> str:
        return committed_manifest_sha256(domain)  # == the deployed bytes the operator copied

    def domain_targets(self, domain: Dict[str, Any]) -> Tuple[str, str]:
        # the real deployed target is the bound identity; swap = a reachable different path
        return self.target_id, self.target_id + "-SWAP"

    def acted_count(self) -> int:
        r = self._target.get("/received")
        return r.json()["count"]

    def admit(self, target_url: str, interaction: Dict[str, Any], max_age: int = 300):
        r = self._gate.post(
            "/governed-call",
            json={"target_url": target_url, "interaction": interaction},
        )
        if r.status_code == 200:
            return "ELIGIBLE", r.json()["envelope"]
        try:
            detail = r.json().get("detail", {})
        except Exception:
            detail = {}
        return "REFUSE", detail

    def attempt(self, envelope, interaction, target_url, now: Optional[datetime] = None):
        from IMPLEMENTATION.envelope import canonical_json
        headers = {}
        if isinstance(envelope, dict):
            headers["X-Elyon-Sol-Envelope"] = canonical_json(envelope)
        r = self._target.post("/target", json=interaction, headers=headers)
        if r.status_code == 200:
            body = r.json()
            return body["honored"], body["reason"]
        return False, r.json()["detail"]["reason"]

    def positive_control(self, target_url, interaction):
        """Under PUSH delivery the gate forwards the admitted envelope to the target on ELIGIBLE,
        so the honor happens AT ADMIT. Observe the target acting (its /received count) rather than
        re-presenting (which would be a replay)."""
        before = self.acted_count()
        dec, env = self.admit(target_url, interaction)
        if dec != "ELIGIBLE":
            return None, "admit-refused", env, dec
        acted = self.acted_count() == before + 1
        return acted, (EXPECT_HONORED if acted else "NOT_ACTED"), env, dec

    def condition_diagnosis(self, interaction: Dict[str, Any]) -> Dict[str, bool]:
        # if the operator pinned the same manifest locally, the local condition functions
        # diagnose faithfully; otherwise fall back to no diagnosis.
        try:
            return InProcSurface.condition_diagnosis(self, interaction)  # type: ignore[arg-type]
        except Exception:
            return {}

    def condition_diagnosis(self, interaction: Dict[str, Any]) -> Dict[str, bool]:
        # if the operator pinned the same manifest locally, the local condition functions
        # diagnose faithfully; otherwise fall back to no diagnosis.
        try:
            return InProcSurface.condition_diagnosis(self, interaction)  # type: ignore[arg-type]
        except Exception:
            return {}


def _parse_not_after(envelope: Dict[str, Any]) -> Optional[datetime]:
    na = envelope.get("not_after")
    if isinstance(na, str):
        try:
            return datetime.fromisoformat(na)
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Case record
# ---------------------------------------------------------------------------

class Case:
    def __init__(self, name, layer, ap, op, context, gate_decision, conditions,
                 envelope, executor_verdict, reason, expect_honored, expect_reason,
                 gloss):
        self.name = name
        self.layer = layer  # "gate" or "executor"
        self.ap = ap
        self.op = op
        self.context = context
        self.gate_decision = gate_decision
        self.conditions = conditions  # dict or {}
        self.envelope = envelope  # dict or None
        self.executor_verdict = executor_verdict  # True/False/None
        self.reason = reason
        self.expect_honored = expect_honored
        self.expect_reason = expect_reason
        self.gloss = gloss

    @property
    def passed(self) -> bool:
        if self.layer == "gate":
            # expect a gate REFUSE
            return self.gate_decision == "REFUSE"
        # executor layer: compare verdict + reason
        if self.executor_verdict != self.expect_honored:
            return False
        if self.expect_reason is not None and self.reason != self.expect_reason:
            return False
        return True


# ---------------------------------------------------------------------------
# Domain run (the 13-case suite of section 3)
# ---------------------------------------------------------------------------

def run_domain(spec: Dict[str, Any], surface, decision_max_age: Optional[int]) -> List[Case]:
    from IMPLEMENTATION.verifier import (
        REF_VERIFY_ENVELOPE_ABSENT, REF_VERIFY_SIGNATURE_INVALID,
        REF_VERIFY_BINDING_MISMATCH, REF_VERIFY_REPLAY, REF_VERIFY_SIGNATURE_EXPIRED,
    )

    ver = spec["manifest"]["version"]
    sha = surface.manifest_sha256(spec["name"])
    primary_target, swap_target = surface.domain_targets(spec)
    g = spec["glosses"]
    cases: List[Case] = []

    def interaction(ap, op, ctx, version=ver, manifest_sha=sha):
        return {
            "AP": list(ap),
            "OP": list(op),
            "context": ctx,
            "expected_manifest_version": version,
            "expected_manifest_sha256": manifest_sha,
        }

    def env_or_none(dec, env):
        return env if dec == "ELIGIBLE" else None

    # ---- Admitted positive controls ----
    for cname, ap, op, ctx in [
        ("admit_primary", spec["ap_full"], spec["op_required"], spec["ctx_primary"]),
        ("admit_secondary", spec["ap_full"], spec["op_required"], spec["ctx_secondary"]),
        ("admit_minimal_authority", spec["ap_minimal"], spec["op_required"], spec["ctx_primary"]),
    ]:
        i = interaction(ap, op, ctx)
        hon, reason, env, dec = surface.positive_control(primary_target, i)
        cases.append(Case(cname, "executor", ap, op, ctx, dec, {},
                          env_or_none(dec, env), hon, reason, True, EXPECT_HONORED, g[cname]))

    # ---- Gate refusals (evaluator REFUSE; report the failing condition) ----
    gate_cases = [
        ("insufficient_authority", spec["ap_insufficient"], spec["op_required"], spec["ctx_primary"], ver),
        ("wrong_operation", spec["ap_full"], spec["op_wrong"], spec["ctx_primary"], ver),
        ("stale_policy_pin", spec["ap_full"], spec["op_required"], spec["ctx_primary"], spec["superseded_version"]),
    ]
    for cname, ap, op, ctx, version in gate_cases:
        i = interaction(ap, op, ctx, version=version)
        dec, detail = surface.admit(primary_target, i)
        conditions = surface.condition_diagnosis(i) if dec == "REFUSE" else {}
        cases.append(Case(cname, "gate", ap, op, ctx, dec, conditions,
                          None, None, "REFUSE", False, None, g[cname]))

    # ---- Executor refusals (verify_envelope / replay) ----
    base_i = interaction(spec["ap_full"], spec["op_required"], spec["ctx_primary"])

    # unattested (A1): no envelope reaches the executor
    hon, reason = surface.attempt(None, base_i, primary_target)
    cases.append(Case("unattested", "executor", spec["ap_full"], spec["op_required"], spec["ctx_primary"],
                      "n/a", {}, None, hon, reason, False, REF_VERIFY_ENVELOPE_ABSENT, g["unattested"]))

    # forged: tamper a signed field (the authorized payload) of a genuine envelope
    dec, env = surface.admit(primary_target, base_i)
    forged = None
    if dec == "ELIGIBLE":
        import copy
        forged = copy.deepcopy(env)
        # edit the authorized payload inside the signed envelope (dose/filing/size)
        _tamper_payload(forged, spec)
    hon, reason = surface.attempt(forged, base_i, primary_target)
    cases.append(Case("forged_envelope", "executor", spec["ap_full"], spec["op_required"], spec["ctx_primary"],
                      "ELIGIBLE", {}, forged, hon, reason, False, REF_VERIFY_SIGNATURE_INVALID, g["forged_envelope"]))

    # replay: present the same admitted envelope twice
    dec, env_r = surface.admit(primary_target, base_i)
    if dec == "ELIGIBLE":
        surface.attempt(env_r, base_i, primary_target)  # first: honored + claims decision_id
        hon, reason = surface.attempt(env_r, base_i, primary_target)  # second: refused
    else:
        hon, reason = (None, "admit-failed")
    cases.append(Case("replay", "executor", spec["ap_full"], spec["op_required"], spec["ctx_primary"],
                      "ELIGIBLE", {}, env_r if dec == "ELIGIBLE" else None, hon, reason,
                      False, REF_VERIFY_REPLAY, g["replay"]))

    # rebind_operation: genuine envelope (op_required) presented for a different operation
    dec, env = surface.admit(primary_target, base_i)
    other_i = interaction(spec["ap_full"], spec["op_other"], spec["ctx_primary"])
    hon, reason = surface.attempt(env if dec == "ELIGIBLE" else None, other_i, primary_target)
    cases.append(Case("rebind_operation", "executor", spec["ap_full"], spec["op_other"], spec["ctx_primary"],
                      "ELIGIBLE", {}, env if dec == "ELIGIBLE" else None, hon, reason,
                      False, REF_VERIFY_BINDING_MISMATCH, g["rebind_operation"]))

    # rebind_context: genuine envelope presented against an altered payload
    dec, env = surface.admit(primary_target, base_i)
    mutated_i = interaction(spec["ap_full"], spec["op_required"], spec["ctx_mutated"])
    hon, reason = surface.attempt(env if dec == "ELIGIBLE" else None, mutated_i, primary_target)
    cases.append(Case("rebind_context", "executor", spec["ap_full"], spec["op_required"], spec["ctx_mutated"],
                      "ELIGIBLE", {}, env if dec == "ELIGIBLE" else None, hon, reason,
                      False, REF_VERIFY_BINDING_MISMATCH, g["rebind_context"]))

    # target_swap: envelope bound to a different target presented to this one
    swap_i = interaction(spec["ap_full"], spec["op_required"], spec["ctx_primary"])
    dec, env = surface.admit(swap_target, swap_i)
    hon, reason = surface.attempt(env if dec == "ELIGIBLE" else None, swap_i, primary_target)
    cases.append(Case("target_swap", "executor", spec["ap_full"], spec["op_required"], spec["ctx_primary"],
                      "ELIGIBLE", {}, env if dec == "ELIGIBLE" else None, hon, reason,
                      False, REF_VERIFY_BINDING_MISMATCH, g["target_swap"]))

    # stale_decision: admitted envelope presented past its freshness window
    hon, reason, env_s = _run_stale(surface, base_i, primary_target, decision_max_age)
    cases.append(Case("stale_decision", "executor", spec["ap_full"], spec["op_required"], spec["ctx_primary"],
                      "ELIGIBLE", {}, env_s, hon, reason, False, REF_VERIFY_SIGNATURE_EXPIRED, g["stale_decision"]))

    return cases


def _tamper_payload(envelope: Dict[str, Any], spec: Dict[str, Any]) -> None:
    """Edit the authorized payload inside the (signed) envelope so the signature no longer
    verifies. Legible: an attacker who alters the authorized dose/filing/size is caught."""
    ctx = envelope["request_context"]["context"]
    if spec["name"] == "medical":
        ctx["dose"] = "5000 mg"
    elif spec["name"] == "legal":
        ctx["filing_type"] = "stipulation_of_dismissal"
    else:
        ctx["quantity"] = 100000


def _run_stale(surface, interaction, target_url, decision_max_age):
    """Trigger SIGNATURE_EXPIRED. inproc: inject now = not_after + 1s (no sleep). live: admit
    against a short-window gate (--decision-max-age) and sleep past it."""
    if surface.mode == "inproc":
        dec, env = surface.admit(target_url, interaction, max_age=1)
        if dec != "ELIGIBLE":
            return None, "admit-failed", None
        na = _parse_not_after(env)
        now = (na + timedelta(seconds=1)) if na else datetime.now(timezone.utc)
        hon, reason = surface.attempt(env, interaction, target_url, now=now)
        return hon, reason, env
    # live
    if not decision_max_age:
        return None, "SKIPPED (pass --decision-max-age to match the gate window)", None
    dec, env = surface.admit(target_url, interaction)
    if dec != "ELIGIBLE":
        return None, "admit-failed", None
    time.sleep(decision_max_age + 1)
    hon, reason = surface.attempt(env, interaction, target_url)
    return hon, reason, env


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def _short(s: Optional[str], n: int = 16) -> str:
    if not isinstance(s, str):
        return "-"
    return s[:n] + ("…" if len(s) > n else "")


def _fmt_payload(ctx: Dict[str, Any], digest_field: str) -> str:
    parts = []
    for k, v in ctx.items():
        if k == digest_field:
            parts.append(f"{k}: {_short(str(v), 16)}")
        else:
            parts.append(f"{k}: {v}")
    return "; ".join(parts)


def write_report(spec: Dict[str, Any], cases: List[Case], mode: str, sha: str) -> str:
    m = spec["manifest"]
    digest_field = spec["digest_field"]
    n_pass = sum(1 for c in cases if c.passed)
    lines: List[str] = []
    lines.append(f"# Elyon-Sol POC — {spec['title']}")
    lines.append("")
    lines.append(f"_Mode: **{mode}** · cases: {len(cases)} · passed: {n_pass}/{len(cases)} · "
                 f"generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}_")
    lines.append("")
    lines.append("> **Synthetic data.** All identifiers (patient/account/matter/bar/NPI numbers, "
                 "URLs) are fictional and resolve to nothing real. This is a characterization run "
                 "of the production admission chain (GR-3), not an external validation.")
    lines.append("")
    lines.append("## Policy manifest (what this domain requires to admit)")
    lines.append("")
    lines.append(f"- **version**: `{m['version']}`")
    lines.append(f"- **manifest sha256**: `{sha}`")
    lines.append(f"- **required authority set (AR)** — the caller's authorities must cover this: "
                 f"`{', '.join(m['AR'])}`")
    lines.append(f"- **required operation set (R)** — the operation must cover this: "
                 f"`{', '.join(m['R'])}`")
    lines.append("")
    lines.append("A call is **admitted** only if its authority set ⊇ AR (AC³), its operation set ⊇ R "
                 "(T²⁶), and it is pinned to this exact manifest version+sha (manifest-integrity); "
                 "otherwise the gate **refuses**. An admitted call carries a signed envelope the "
                 "executor re-checks (signature → currency → binding → freshness → replay) before acting.")
    lines.append("")
    lines.append("## Cases")
    lines.append("")
    for c in cases:
        status = "✅ PASS" if c.passed else "❌ FAIL"
        lines.append(f"### {c.name} — {status}")
        lines.append("")
        lines.append(f"_{c.gloss}_")
        lines.append("")
        lines.append(f"- **actor (AP)**: `{', '.join(c.ap)}`")
        lines.append(f"- **operation (OP)**: `{', '.join(c.op)}`")
        lines.append(f"- **{spec['payload_label'].lower()} (context)**: {_fmt_payload(c.context, digest_field)}")
        if c.layer == "gate":
            cond = c.conditions or {}
            failed = [k.upper() for k, v in cond.items() if v is False]
            cond_str = (", ".join(failed) + " unsatisfied") if failed else "refused"
            lines.append(f"- **gate decision**: REFUSE — {cond_str}")
            if cond:
                lines.append(f"  - AC³={cond.get('ac3')} · T²⁶={cond.get('t26')} · "
                             f"manifest-integrity={cond.get('manifest_integrity')}")
            lines.append("- **executor**: not reached (refused at the gate)")
        else:
            if c.envelope is not None:
                e = c.envelope
                lines.append(f"- **gate decision**: ELIGIBLE — signed envelope issued")
                lines.append(f"  - decision_id: `{e.get('decision_id')}`")
                lines.append(f"  - bound target_url: `{e.get('target_url')}`")
                lines.append(f"  - manifest pin: `{e.get('evaluated_against', {}).get('manifest_version')}` / "
                             f"`{_short(e.get('evaluated_against', {}).get('manifest_sha256'), 12)}`")
                lines.append(f"  - not_after: `{e.get('not_after')}`")
                lines.append(f"  - issuer_key_id: `{e.get('issuer_key_id')}` · "
                             f"signature: `{_short(e.get('issuer_signature'), 16)}`")
                lines.append(f"  - decision_sha256: `{_short(e.get('decision_sha256'), 16)}`")
            else:
                lines.append(f"- **gate decision**: (no envelope — A1 / un-attested path)")
            verdict = "HONORED — acted" if c.executor_verdict else "REFUSED — not acted"
            lines.append(f"- **executor verdict**: {verdict} (`{c.reason}`)")
            exp = EXPECT_HONORED if c.expect_honored else c.expect_reason
            lines.append(f"- **expected**: {'honored' if c.expect_honored else 'refused'} "
                         f"(`{exp}`)")
        lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Three-domain synthetic POC runner")
    p.add_argument("--mode", choices=["inproc", "live"], default="inproc")
    p.add_argument("--domain", choices=DOMAIN_ORDER + ["all"], default="all")
    p.add_argument("--gate-url", help="live mode: gate base URL (e.g. https://host-a:8000)")
    p.add_argument("--target-url", help="live mode: reference-target client base URL "
                                        "(e.g. https://host-b:9000) == ELYON_LIVE_TARGET_URL")
    p.add_argument("--target-id", help="live mode: the BOUND target identity "
                                       "(e.g. https://host-b:9000/target) == the target's "
                                       "ELYON_TARGET_URL / ELYON_LIVE_TARGET_ID")
    p.add_argument("--ca-bundle", help="live mode: CA bundle path for TLS verification")
    p.add_argument("--decision-max-age", type=int, default=None,
                   help="live mode: the gate's decision window (s) for the stale case")
    p.add_argument("--no-write", action="store_true", help="do not write report files")
    args = p.parse_args(argv)

    if not os.path.exists(MANIFEST_LIVE_PATH):
        print(f"ERROR: run from the repo root (no {MANIFEST_LIVE_PATH}).", file=sys.stderr)
        return 2

    domains = DOMAIN_ORDER if args.domain == "all" else [args.domain]
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if args.mode == "inproc":
        surface = InProcSurface()
    else:
        if not (args.gate_url and args.target_url and args.target_id):
            print("ERROR: live mode requires --gate-url, --target-url (client base), and "
                  "--target-id (the bound /target identity).", file=sys.stderr)
            return 2
        surface = LiveSurface(args.gate_url, args.target_url, args.target_id, args.ca_bundle)

    total_pass = total = 0
    try:
        for name in domains:
            spec = DOMAINS[name]
            surface.pin_manifest(name)
            try:
                sha = surface.manifest_sha256(name)
                cases = run_domain(spec, surface, args.decision_max_age)
            finally:
                surface.restore_manifest()
            report = write_report(spec, cases, surface.mode, sha)
            n_pass = sum(1 for c in cases if c.passed)
            total_pass += n_pass
            total += len(cases)
            path = os.path.join(REPORTS_DIR, f"{name}_report.md")
            if not args.no_write:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
            print(f"[{name}] {n_pass}/{len(cases)} passed -> {os.path.relpath(path)}")
            for c in cases:
                flag = "ok " if c.passed else "XX "
                detail = (c.reason if c.layer == "executor" else "REFUSE")
                print(f"    {flag}{c.name:24s} {detail}")
    finally:
        surface.restore_manifest()

    print(f"\nTOTAL: {total_pass}/{total} passed (mode={surface.mode})")
    return 0 if total_pass == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
