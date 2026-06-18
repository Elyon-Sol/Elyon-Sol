# Governance-substrate deployment - the claimable-oversight recipe

How to deploy Elyon-Sol as a governance substrate where the ONLY path to executing a
high-impact action is **through the gate** (Feature 2, non-bypassable) **and** with a
**human-authorized grant** (Feature 1). The in-repo BUILD is complete - Feature 1
mechanism (1a-1d), R1 (approver provenance + role, VL-119), R2 (shared store, VL-120),
Feature 2 mTLS layer (VL-117), and the in-process integration proof (VL-118). What
remains is this OPERATOR-LOCUS wiring. None of it is new code; it is configuration,
key custody, and network topology on real hosts.

> **Honest claimability gate (read first).** The oversight GUARANTEE is claimable ONLY
> inside a deployment that wires ALL of: R1 (role-distinct approver trust), R2 (a real
> shared store), and Feature-2 layers 1 + 2 + 3 (inline body-binding, mTLS, network
> isolation). Any one missing re-opens a bypass. White-box in-repo proofs are NOT
> external validation (GR-3); only an external attacker on the live surface certifies
> G5. Until then this is "built and wired", not "externally validated".

---

## 0. Prerequisites

- The base packaging + TLS stand-up from `deploy/runbook.md` + `deploy/tls/trust_bootstrap.md`
  (gate / target / publisher reachable; real or dev CA issued by `deploy/tls/gen_certs.py`).
- Three keypairs, generated and held **out-of-band** (never in the repo, never in chat):
  1. the gate **issuer** key (`ELYON_SIGNING_KEY_*`) - on the gate host;
  2. the **approver** key (`ELYON_APPROVER_KEY_*`) - on the SEPARATE approver host ONLY;
  3. the **publisher/root** key that signs the key record - on the publisher host.
- One Redis reachable from every gate replica (the R2 shared store).

---

## 1. R1 - approver provenance + role (signed key-record chain)

The gate must trust approver keys ONLY through the signed key record, by an explicit
`approver` role - never a static pin. This closes [FIX H5]: an issuer-role (or role-less)
key, even if well-signed and carrying a different key_id, can NEVER authorize an approval.

1. **Publish a key record with an `approver`-role entry.** Add the approver public key to
   the publisher-signed key record (the same record format `key_record_source` validates),
   with `"role": "approver"`. The gate's issuer key, if present in the record, carries
   `"role": "issuer"`. Sign the record with the pinned root/publisher key.
2. **Pin the root out-of-band** on each gate: `ELYON_PINNED_ROOT_KEY_ID` +
   `ELYON_PINNED_ROOT_PUBKEY_B64` (base64 raw Ed25519 of the root pubkey).
3. **Run the gate via the R1 wiring shim**, not bare pep:
   `uvicorn deploy.governance.approver_trust_bootstrap:app`. At startup the shim loads the
   record, validates it against the pinned root, resolves the role-distinct approver map
   (`approver_trust.resolve_approver_keys`, excluding the gate's own `ELYON_SIGNING_KEY_ID`),
   and injects it into pep. Misconfig (bad record, no approver role) -> EMPTY map ->
   every grant is `REF_APPROVAL_KEY_UNKNOWN` (fail-closed).
4. **Custody:** the approver PRIVATE key lives ONLY in the approver-CLI process
   (`ELYON_APPROVER_KEY_*`), on a host the gate cannot read. The gate holds only PUBLIC keys.

**Acceptance (R1).**
- A grant signed by the `approver`-role key for the held decision -> forwarded (200).
- A grant signed by the gate's `issuer`-role key (a self-approval) -> `REF_APPROVAL_KEY_UNKNOWN`
  (the role-distinct map never contains it), even though `approver_key_id != gate_key_id`
  alone would pass. A role-less key -> same refusal.
- Revoke the approver key in the record (or expire its window) -> its grants stop being
  honored without any gate redeploy beyond re-reading the record.

---

## 2. R2 - shared store (single-use + the 202 pending-set across replicas)

A horizontally-scaled gate must keep ONE shared store, or it must refuse to start.

1. Stand up Redis reachable from every replica.
2. On EVERY gate replica set: `ELYON_REPLAY_MULTI_INSTANCE=1`,
   `ELYON_PENDING_REDIS_URL=redis://<redis>:6379/0`,
   `ELYON_REPLAY_REDIS_URL=redis://<redis>:6379/0`.
   (`docker-compose.governance.yml` wires `gate` + `gate2` + `redis` this way.)

**Acceptance (R2).**
- **Declare-or-fail guard:** start a replica with `ELYON_REPLAY_MULTI_INSTANCE=1` but
  WITHOUT a redis URL -> the gate FAILS TO START (RuntimeError at import). This is the
  desired fail-closed: no per-process pending set / replay cache under declared scale.
- **Cross-instance single-use:** issue a 202 on `gate` (instance A); present the approved
  grant to `gate2` (instance B) -> forwarded EXACTLY once. Replay the SAME grant to either
  replica -> `REF_APPROVAL_REPLAY`, no second execution. Without the shared store each
  replica would honor it once (the gap R2 closes).
- **Pending visibility:** a 202 issued on A is consumable on B (no `REF_APPROVAL_REQUEST_UNKNOWN`
  purely from hitting a different replica).

---

## 3. Feature 2 - non-bypassable (layers 1 + 2 + 3)

Full recipe + the bypass-refused proof live in `deploy/NONBYPASS_TOPOLOGY.md`. Summary:

- **Layer 2 (mTLS gate->target) - BUILT + PROVEN in-repo.** Enable it: target
  `ssl_verify_mode = CERT_REQUIRED` trusting the gate CA (`ELYON_TLS_CA_BUNDLE`); gate
  presents `ELYON_TLS_CLIENT_CERT` (+ key). Proof: `TESTS/deploy/test_mtls_required.py` +
  `EVIDENCE/proofs/nonbypass_direct_call_refused_runner.py`.
- **Layer 1 (inline body-binding) - operator wiring.** Front the target with the ext-authz
  sidecar configured with the BODY extractor (`build_request_body_extractor`, VL-111) +
  Envoy `with_request_body`, so the decision digests the same bytes the upstream executes.
  See `deploy/envoy.example.yaml` for the ext-authz filter shape; add `with_request_body`
  and point the sidecar at the body extractor. Until wired, do NOT front a body-carrying
  upstream with the default header-read mode.
- **Layer 3 (network ACL + egress) - operator topology.** Target port reachable ONLY from
  the gate (security group / firewall: `allow <gate> -> <target:port>`, deny all else);
  agent egress restricted to ONLY the gate. Verify: from any off-gate host a direct
  connection to the target port must fail to connect AND the target must log no app request.

**Acceptance (F2).** From an off-gate host, a direct call to the target is refused at the
TLS handshake (layer 2) and unroutable (layer 3); a routed call carrying a tampered body is
refused at binding (layer 1, `REF_VERIFY_BINDING_MISMATCH`).

---

## 4. End-to-end composition check (the integration proof, live)

Reproduce VL-118's four legs against the LIVE surface:
- **A** direct bypass -> refused at TLS (F2 layer 2 + 3).
- **B** routed but UNAPPROVED high-impact call -> `202 PENDING_APPROVAL`, target NEVER called.
- **C** routed + APPROVED (grant minted by the approver CLI) -> executes EXACTLY once; the
  issuance + approval logs `reconcile_approvals` clean (no `FORWARDED_WITHOUT_GRANT`).
- **D** REPLAYED grant -> refused, no second execution (now across replicas, via R2).

Only when A-D all hold on the live, all-layers-wired surface is the oversight guarantee
deployment-claimable. Then arrange the external attacker (G5) per `deploy/BREAK_IT.md` +
`deploy/SAFE_HARBOR_DRAFT.md`; G5 stays NOT-MET until a blind external party engages.

---

## 5. Acceptance checklist (sign-off)

| # | Property | Check | Status |
|---|----------|-------|--------|
| R1-a | Only signed `approver`-role keys authorize | issuer/role-less grant -> KEY_UNKNOWN | [ ] |
| R1-b | Approver private key off the gate (custody) | gate host cannot read approver key | [ ] |
| R1-c | Revocation via the record | revoked approver -> grants refused, no redeploy | [ ] |
| R2-a | Declare-or-fail guard | MULTI_INSTANCE w/o redis -> gate won't start | [ ] |
| R2-b | Cross-instance single-use | 202 on A, approve on B -> once; replay -> refused | [ ] |
| F2-1 | Inline body-binding | tampered body -> REF_VERIFY_BINDING_MISMATCH | [ ] |
| F2-2 | mTLS gate->target | off-gate direct call -> refused at TLS | [ ] |
| F2-3 | Network isolation + egress | target port unreachable off-gate | [ ] |
| INT | Live integration A-D | all four legs hold on the live surface | [ ] |
| G5 | External attacker | blind external party engages the live surface | [ ] |

When the operator pieces are wired, update `docs/restructure/04_current_vs_claimed.md`
(G4 / the A1 line) to "non-bypassable within the controlled boundary" - do NOT mark G4
blanket-RESOLVED, and keep the guarantee claim scoped to the wired deployment (GR-3).
