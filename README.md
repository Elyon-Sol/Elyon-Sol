# Elyon-Sol

**A deterministic, fail-closed admission gate for actions.** Before an action runs, Elyon-Sol
decides — cryptographically — whether it is *authorized* under an explicit, hash-pinned policy,
and refuses everything else. Every allowed action leaves a signed, single-use receipt of exactly
why it was allowed.

Open-core (AGPL-3.0) · canon v0.9.8.4 · full test suite green · live public test surface ·
**not yet externally validated** (that's the open challenge — see below).

---

## The claim (what a "break" is)

> Without the gate's signing key, there is no request you can craft that (a) makes the target
> perform an action, or (b) makes the ext-authz sidecar answer `ALLOW`, unless the token in the
> `X-Elyon-Sol-Envelope` header is **validly signed**, **currently valid**, **bound to exactly
> that action and target**, and **not previously used**.

Using a real token once, as intended, is not a break — that's the gate working. We ship a live
target and a read-only token inspector (`IMPLEMENTATION/envelope_inspector.py`) that adjudicates a
token the way the target does, so you can self-check before you submit. Try to break it — see
[`SECURITY.md`](SECURITY.md).

## Try it (the live surface is open — no signup)

Four public nodes run under real TLS:

| Node | Role | Host |
|---|---|---|
| Gate | mints/signs tokens | `https://gate.elyon-sol.io:8443` (`POST /governed-call`) |
| Target | the thing that acts | `https://target.elyon-sol.io:9443` (`POST /target`, `GET /received`) |
| Sidecar | ALLOW / DENY | `https://authz.elyon-sol.io:9243` |
| Publisher | serves the signed record | `https://pub.elyon-sol.io:9143` |

Mint a token from the gate, present it once to the target/sidecar to see a valid flow, then attack
the edges — drop the header, alter a field, replay it, expire it, point it at a different action or
target. A confirmed break is credited and published (`SECURITY.md`). Copy-paste "break it in 60
seconds" commands live on the project site.

---

## Run it locally

```bash
python -m uvicorn IMPLEMENTATION.pep:app --reload      # serves http://127.0.0.1:8000
python -m pytest TESTS/                                # full suite (count pinned in STATE.md)
```

**Endpoint:** `POST /governed-call`. Send one JSON object; the gate returns `ELIGIBLE` (and forwards
to `target_url`, returning the signed envelope) or `REFUSE` (403, upstream never called).

```json
{
  "target_url": "https://upstream.example/path",
  "interaction": {
    "AP":                        ["identity", "role"],
    "OP":                        ["session", "request"],
    "context":                   {},
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256":  "<sha256 of MANIFEST/manifest.json>"
  }
}
```

`AP` (the caller's authorities) and `OP` (the operations) must satisfy the manifest's required sets,
and the asserted manifest version + hash must match the live manifest — otherwise it's a refusal, not
a silent accept. The required sets are derived from `MANIFEST/manifest.json`, **not** caller-supplied,
so a caller can't weaken what's required. Full wire schema and refusal codes: [`SPEC/request_schema.md`](SPEC/request_schema.md).

## Use it: admission control for agent / MCP tool calls

The same gate fronts autonomous-agent actions. It ships as:

- an **MCP server** (`IMPLEMENTATION/mcp_server.py`) that runs the admission check on every `tools/call`, and
- an **OPA/Envoy ext-authz sidecar** (`IMPLEMENTATION/authz_sidecar.py`) that answers ALLOW/DENY in front of any HTTP target, reusing the production verifier.

So a tool call, an API call, or an agent action only executes if it carries a valid, signed,
single-use authorization bound to exactly that call.

---

## How it works (in plain terms)

An allowed decision must pass three checks:

- **Authority** — the caller's authorities satisfy what the policy requires for this action.
- **Coverage** — the operations are covered by what the policy allows.
- **Continuity** — a past "yes" is not honored after the policy or decision logic it depended on changes.

On an allowed decision the gate builds an **admissibility envelope** — a content-hashed, Ed25519-signed
record binding the decision to the exact policy, action, arguments, and evaluator that produced it.
That envelope is the receipt: the target (or anyone) can verify it, and it's **single-use**, so it
can't be replayed. A **reassertion** check re-tests it against live state and returns *reasserted*,
*invalidated*, or *re-evaluate-required* — a stale authorization can never silently persist.

For high-impact actions, the gate **holds** the request and requires a human approver to sign a grant
**with their own key on their own device**. There is no server-side approve-button the gate could
forge — separation of duties is a cryptographic property, not a UI checkbox.

## How it compares

|  | **Elyon-Sol** | Allow/deny lists | Policy engines (OPA/Rego) | Runtime guard hooks |
|---|:---:|:---:|:---:|:---:|
| Decides *before* the action runs | ✓ | ✓ | ✓ | ✓ |
| Fail-closed by default | ✓ | partial | configurable | partial |
| **Signed, verifiable receipt** per allowed action | ✓ | ✗ | ✗ | ✗ |
| Decision **bound to the exact action + arguments** | ✓ | ✗ | ✗ | partial |
| **Single-use / replay-proof** authorization | ✓ | ✗ | ✗ | ✗ |
| Human approval with **cryptographic separation of duties** | ✓ | ✗ | ✗ | server-side prompt |
| Policy **pinned by hash + version** (tamper-evident) | ✓ | ✗ | partial | ✗ |
| **Falsifiable**: live target + inspector + open break-it challenge | ✓ | — | — | — |

This compares *design properties in the authorization-attestation niche* — not a claim that policy
engines or runtime hooks are worse at what they do. They're complementary: Elyon-Sol runs happily as
an ext-authz layer alongside OPA.

### vs capability-token systems (the honest comparison)

The table above is against access-control *styles*. The sharper question is against systems that
already issue signed, bound tokens — **macaroons, biscuit, SPIFFE/SVID, GNAP, and the IETF
Transaction Tokens draft**. Stated plainly: an admissibility envelope *is* a capability token —
signed, action-bound, single-use — and Elyon-Sol claims **no new cryptographic primitive**. What it
adds over a raw capability token is behavioral: the envelope is a **receipt of a policy decision**
(it pins the exact canon, manifest, and evaluator that decided), it **self-invalidates when that
policy changes** (reassertion/continuity — most capability tokens stay valid until expiry regardless
of policy drift), it makes **human approval a cryptographic separation-of-duties primitive**, and it
ships with a **live public break-it challenge**. It composes *with* these systems — it can run on top
of a biscuit rather than instead of one. Full treatment, including "why not just use biscuit +
ext-authz + a signing step?": [`docs/COMPARISON_capability_tokens.md`](docs/COMPARISON_capability_tokens.md).

---

## What's proven — and what isn't

We report exactly what we can back with a referent, and no more.

- **Proven in-repo:** the full test suite passes (541 at HEAD; the authoritative count is pinned in
  `STATE.md`), including revert-catchers that fail when the guard they defend is removed. A carried-forward
  enforcement run showed 102 refusals → 403 with zero external executions and 102 eligible calls → 200
  with exactly 102 executions, each gate-signed.
- **Live self-test:** the four public nodes pass the author's attack suite (positive control honored,
  adversarial cases refused).
- **NOT yet proven:** **no external, third-party adversary has broken — or failed to break — the live
  surface.** That external validation is the single open finish line, and the reason the challenge above
  exists. The human-oversight guarantee is also deployment-gated (it holds inside a deployment that wires
  the non-bypass layers). And the gate is **opt-in**: a caller that doesn't route through it isn't
  governed by it — non-bypass is a deployment-topology property (mTLS + network isolation), not the gate
  alone.

If you find a gap between a claim here and the code, that's a bug in the claim — tell us.

## Formal model & provenance (for those who want the depth)

Elyon-Sol is derived from a locked formal specification (the "canon", v0.9.8.4), whose model
`G(I) = AC³ ∧ T²⁶ ∧ CCS` conjoins the three invariants above (Authority = AC³, Coverage = T²⁶,
Continuity = CCS). The canon is immutable and changes only by version increment.

Every project claim is traceable to a spec clause, an implementation construct, a test, and an entry
in an append-only **verification ledger** (`EVIDENCE/verification_ledger.md`) that records how each
claim became trusted. Start with:

- [`STATE.md`](STATE.md) — current verified state, next action, and open gaps (read first).
- [`SPEC/request_schema.md`](SPEC/request_schema.md) — the locked wire shape and refusal vocabulary.
- [`CANON/canon.md`](CANON/canon.md) — the specification the code is derived from.
- [`docs/MAINTENANCE_PROTOCOL.md`](docs/MAINTENANCE_PROTOCOL.md) — the governance rules the repo changes under.

## Layout

```
CANON/           the locked specification (source of record)
SPEC/            wire-shape and derivation-faithful specs
IMPLEMENTATION/  the gate (pep.py), evaluator, envelope, verifier, MCP server, ext-authz sidecar, inspector
MANIFEST/        the SHA-256-pinned policy manifest
TESTS/           the adversarial + regression suite
EVIDENCE/        the verification ledger and runnable proofs
deploy/          deployment artifacts (TLS, compose, runbooks, key ceremony)
docs/            protocols, specs, and design notes
site/            the public one-pager
```

## License

**Open-core.** The core here — admission gate, admissibility envelope, target-side verifier, ext-authz
sidecar, and supporting modules — is licensed under **AGPL-3.0** (see `LICENSE`), including the network-use
source-disclosure obligation. A **commercial license** is available for uses that can't accept AGPL's terms
(`COMMERCIAL.md`); a separate administration/tooling SDK is proprietary and sold separately. Full model:
`LICENSING.md`. Contributions require a DCO sign-off (`CONTRIBUTING.md`). "Elyon-Sol" is a trademark of
Justin Laporte (application pending); the license covers the code, not the name.

## Security & contact

Report findings privately to **security@elyon-sol.io** — coordinated disclosure, 90-day window, credited
by name or handle. Please don't open public issues for security findings. Full policy and the in/out-of-scope
list: [`SECURITY.md`](SECURITY.md).
