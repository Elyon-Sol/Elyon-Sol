# Universal PDP-upstream / admissibility composition - design (DRAFT)

Status: DRAFT for review. Not ledgered. Grounded in the SHIPPED sidecar
(`IMPLEMENTATION/authz_sidecar.py`, VL-104/105) and `opa_sidecar_design.md`
(Mode A / Mode B). This is a CONCURRENT in-house track to G5, not a G5 item:
it is pure code with no external-world dependency, so it advances adoptability
while the external-validation track waits on real-world arrangement.

Reuse-only: introduces NO new admissibility logic and NO cryptography. It
generalizes the OPA-specific adapter into a Policy-Decision-Point-agnostic
composition surface. Build-then-wire: every piece ships default-off; no existing
path changes byte-behavior.

---

## 1. The thesis

Admissibility is upstream of, and orthogonal to, policy. Every policy engine -
OPA, Cedar, the Zanzibar family (SpiceDB / OpenFGA / Keto), Cerbos, Oso, Casbin -
answers one question in a uniform shape: "given this request, allow or deny?"
Elyon-Sol answers the PRIOR question - "is this request admissible to be
considered at all?" (authority, coverage, integrity, attestation) - once, the
same way, regardless of which PDP runs after it. Because admissibility is uniform
and the PDP call is the only thing that varies, ONE upstream surface composes
with ALL of them. The claim "upstream of any policy engine" is then true by
construction, not by writing N integrations.

## 2. Two composition idioms (generalized from Mode A / Mode B)

- CHAIN mode (Mode A, generalized). Admissibility is the FIRST fail-closed gate
  in the request path; the PDP is the SECOND. In a proxy with an ordered filter
  chain (Envoy ext_authz, or any gateway with pre-auth hooks), the two run as
  independent filters, each fail-closed, neither importing the other. ZERO code
  coupling: this works with ANY PDP that already has a proxy/gateway integration
  (OPA-Envoy, Cerbos, OpenFGA-via-filter, etc.). This is the "compatible with
  everything, for free" path - and it is already shipped (VL-104).

- COMPOSE mode (Mode B, generalized). The sidecar itself calls the PDP through a
  PolicyAdapter and ANDs the verdicts (admit AND permit), returning ALLOW only if
  BOTH allow. For stacks WITHOUT a filter chain: a single middleware hook, a
  non-Envoy gateway, an embedded library PDP, or a managed authz service. This is
  the only place a PDP-specific surface exists.

The decision rule for an integrator is one line: "Do you run Envoy or a gateway
with an ordered pre-auth chain? -> CHAIN mode, no adapter. Otherwise -> COMPOSE
mode, one adapter."

## 3. The universal upstream contract (already shipped, unchanged)

The request the sidecar accepts (envelope attestation header + the interaction,
via the default header-read extractor or an injected extractor) and the verdict
it returns (ALLOW 200 / DENY 403 + REF_* reason) are PDP-agnostic. No change.
This is the stable "shape and format" every agent integrates against.

## 4. The one new abstraction: PolicyAdapter

A small protocol - the single PDP-specific seam:

    class PolicyAdapter(Protocol):
        def permit(self, interaction: dict, request: Request) -> Decision: ...
        # Decision(honored: bool, reason: str) - the existing executor_sdk type.
        # Fail-closed: any error / timeout / unparseable verdict -> honored=False.

In COMPOSE mode the sidecar runs admissibility first (the existing ExecutorGate
path, fail-closed). If and only if admissible, it calls `adapter.permit(...)`,
then returns ALLOW iff BOTH the gate and the adapter allow. The adapter is
injected (parity with the existing `interaction_extractor` / `replay_cache`
seams); with no adapter configured, COMPOSE mode is unavailable and the sidecar
is admissibility-only (CHAIN mode), byte-identical to today.

Admissibility never depends on the adapter; the adapter never sees the gate's
internals. Same separation-of-planes the project already enforces.

## 5. Reference adapters (the long tail - build incrementally by momentum)

Each adapter does exactly three things: translate the manifest-normalized
interaction into the PDP's check shape; call the PDP; normalize the verdict to a
Decision. All fail-closed.

- WebhookAdapter (HTTP). POST a check body to any HTTP PDP, parse allow/deny.
  ONE adapter covers OPA's REST data API, Cerbos's REST PDP, and any generic
  decision webhook - by config (URL + a small request/response field map).
- ZanzibarCheckAdapter. Translate the interaction into an object/relation/subject
  tuple and call a Zanzibar-family check: SpiceDB CheckPermission, OpenFGA
  /check, Ory Keto. ONE adapter, the three engines via config (endpoint +
  payload dialect). This is the highest-leverage adapter: it collapses three of
  the ten targets into one.
- CedarAdapter. Translate to principal / action / resource / context and call
  Cedar (or AWS Verified Permissions isAuthorized).
- (Optional) GrpcExtAuthzAdapter for OPA-Envoy gRPC / SpiceDB gRPC, after the
  HTTP forms prove out.

## 6. The mapping seam (the one piece the integrator authors)

Admissibility binds to the manifest-normalized interaction (AP, OP, context).
Each PDP wants its own input vocabulary. So COMPOSE mode needs a per-deployment
"interaction -> PDP input" mapping - which is exactly the declarative CUSTOM
interaction-mapping format deferred from the OPA build (phase 4). It is now
SHARED across every adapter: the integrator maps their request shape once, and
the adapter family formats that mapped context into its dialect. Authored config,
not code, documented - the single piece of per-deployment work.

## 7. Uniform vs. varying (the load-bearing table)

- UNIFORM (build once, already built): the admissibility check; the upstream
  request/verdict contract; the fail-closed AND in compose mode; the trust /
  replay / clock-skew config; the REF_* vocabulary.
- VARIES (thin, per PDP family): the check-call shape (HTTP body vs. tuple-check
  vs. Cedar isAuthorized vs. gRPC) and the verdict parse - isolated entirely
  inside one PolicyAdapter each.

## 8. Deployment matrix (which mode each target uses)

- CHAIN mode, no adapter (works today): OPA-Envoy, Cerbos (Envoy), OpenFGA via a
  filter - anything with an ordered proxy pre-auth chain.
- COMPOSE mode, one adapter: SpiceDB / OpenFGA / Keto (ZanzibarCheckAdapter),
  Cedar / AWS Verified Permissions (CedarAdapter), a generic HTTP PDP or a
  non-Envoy app (WebhookAdapter), embedded library PDPs like Casbin / Oso (a thin
  in-process adapter calling the library).

## 9. Build plan (build-then-wire, concurrent to G5; each step its own VL)

1. Lift the PolicyAdapter protocol + the compose-mode fail-closed AND into the
   sidecar (Mode B is named in `opa_sidecar_design.md` but unbuilt). Default-off:
   no adapter -> admissibility-only, byte-identical to VL-104.
2. WebhookAdapter + tests (covers OPA REST / Cerbos / generic in one).
3. ZanzibarCheckAdapter + tests (SpiceDB / OpenFGA / Keto via config) - the
   three-for-one increment; build this before Cedar (more open-source momentum).
4. The declarative interaction -> PDP mapping format + tests (the deferred
   phase-4 piece, now shared across adapters).
5. CedarAdapter (+ AWS Verified Permissions) + tests.
6. (Optional) gRPC adapter forms.

Each increment: reuse-only, fail-closed everywhere, default-off, ledgered once
verified in-container. None touches the gate, the verifier, the crypto, or any
existing default path.

## 10. Scope, limits, open questions

- CHAIN mode is the truthful "works with everything" claim and needs NO adapters -
  lead every conversation with it. The adapters are for the non-Envoy long tail.
- "Zanzibar" is a model, not a deployable; the ZanzibarCheckAdapter targets its
  implementations. Do not claim a "Zanzibar integration" beyond those.
- Embedded-library PDPs (Casbin, Oso-as-library) compose only in-process, not over
  the network; the adapter for those is a thin in-process call, documented as a
  different deployment shape.
- Managed services (AWS Verified Permissions) add an auth/credentials dimension to
  the adapter; out of scope for the first build, named here.
- Open: whether to ALSO expose the admissibility verdict as data the PDP's own
  policy can reference (OPA external-data, Cedar entities) - a third "data" mode,
  deferred, so Rego/Cedar authors could write `admissible == true` into policy.

## 11. The one-person framing

This is what lets "upstream of any policy engine" be honest from a solo builder:
CHAIN mode already is universal (zero per-PDP work), and COMPOSE mode is ONE
protocol plus a handful of thin, fail-closed adapters - not ten integrations.
Demonstrate it against OPA (have it) and one Zanzibar-family engine, and the
field is credibly covered. It is a category-shaped surface, not a vendor list,
and it advances entirely in-house - the right concurrent track while G5's
external arrangement is pending.
