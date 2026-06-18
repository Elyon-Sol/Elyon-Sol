# Non-bypassable enforcement - topology + the bypass-refused proof (Feature 2)

**Scope.** "Non-bypassable" (closing adversary A1: a caller that ignores the gate and hits the
target directly) is a **network-layer** property, not an app-layer one. App-layer adoption (the
reference target refusing envelope-less calls, VL-061) is *necessary but not sufficient* - it
only helps if the target **cannot be reached except through the gate**. That requires three
composable, each-fail-closed layers. This file is the deployment discipline for all three and
states, honestly, which layer is proven in-repo and which is operator-locus.

## The three layers

1. **Inline eligibility (app).** The ext-authz sidecar runs **inline** in front of the target
   using `build_request_body_extractor` (VL-111) + Envoy `with_request_body`, so the decision
   binds the executed bytes (not a client-supplied header). **Status: the body extractor is built
   (VL-111); wiring it inline with Envoy `with_request_body` is deployment config (operator).**
   Until that wiring exists, the default header-read sidecar mode must not front a body-carrying
   upstream.

2. **mTLS client-auth, gate -> target (transport).** The target requires a CA-signed **client**
   certificate at the TLS layer and refuses any client that is not the gate **before any app
   logic runs**. The leaves already carry the `CLIENT_AUTH` EKU (`deploy/tls/gen_certs.py`); the
   seam supports it; this turns it ON (it is one-way TLS by default per the TLS dossier 9.5).
   **Status: BUILT + PROVEN in-repo** - see "The proof" below.

3. **Network isolation + egress control (topology).** The target's port is reachable **only**
   from the gate (private network / firewall ACL), and the agent's egress is restricted so it can
   reach **only** the gate. Now there is no network path from caller to target that bypasses the
   gate. **Status: operator-locus** (real hosts / cloud security groups / firewall rules); the
   recipe is below.

Non-bypassable holds **only within the network boundary you control.** A target that does not
adopt the policy *and* is not network-isolated remains bypassable - that residue is explicit and
**deployment-gated**, not a silent gap.

## The proof that actually matters (design 2.3)

A bypass test that fails at the **TLS layer**, not the app layer:

- a direct connection to the target **without the gate client cert** is rejected at the TLS
  handshake (the target never reaches app logic);
- a call **through the gate** (presenting the client cert) is honored.

In-repo this pair is proven two ways:
- hermetic (MemoryBIO, CI-friendly): `TESTS/deploy/test_mtls_required.py` - the bare connection is
  refused, the gate connection is honored (and the target sees the gate's identity), a
  wrong-CA client is refused, and a **contrast** test shows that under one-way TLS the same bare
  connection *would* be accepted (so mTLS is exactly the layer that closes A1).
- real sockets: `EVIDENCE/proofs/nonbypass_direct_call_refused_runner.py` - a loopback TLS target
  with `CERT_REQUIRED`; the bare connection is `REFUSED_AT_TLS` server-side, the gate connection
  `ACCEPTED`. Exit 0.

## Operator recipe (layers 1 and 3)

Transport (layer 2, enable mTLS on the real deployment):
- Target server: require client auth -> `ssl_verify_mode = CERT_REQUIRED`, trust the gate's CA
  (`ELYON_TLS_CA_BUNDLE`). In Envoy/nginx terms: `require_client_certificate: true` with the CA
  as the validation context.
- Gate client: present `ELYON_TLS_CLIENT_CERT` (+ key) on the gate->target hop (the transport.py
  client-cert hook).

Topology (layer 3, the network ACL + egress restriction):
- Put the target on a private network/subnet; open its port **only** to the gate's address
  (security group / firewall rule: `allow from <gate> to <target:port>`, deny all else).
- Restrict the agent's egress so it can reach **only** the gate (egress allowlist), so there is
  no route from the agent to the target except through the gate.
- Verify: from any host that is NOT the gate, a direct connection to the target port must fail to
  connect (refused/timeout) - run the bypass-refused procedure above from an off-gate host and
  confirm the target never logs an app-layer request.

Inline (layer 1, the body binding):
- Front the target with the ext-authz sidecar configured with the **body** extractor
  (`build_request_body_extractor`) and Envoy `with_request_body`, so the decision digests the same
  bytes the upstream executes.

## Honest-scope note (update on landing the operator pieces)

When layers 1 and 3 are wired on a real deployment, update `docs/restructure/04_current_vs_claimed.md`
G4 and the A1 line to reflect "non-bypassable within the controlled boundary"; do **not** mark G4
blanket-RESOLVED. White-box in-repo proofs are not external validation (GR-3).
