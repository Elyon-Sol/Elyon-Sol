# Elyon-Sol vs capability-token systems

*The honest comparison — the one the pitch has to answer.*

The project's public comparison table pits Elyon-Sol against access-control
*styles* (allow/deny lists, policy engines like OPA/Rego, runtime guard hooks)
and wins on signed receipts, action-binding, single-use, and cryptographic
separation of duties. That table is fair but it dodges the sharper question a
serious reader asks first:

> Structurally, a signed, action-bound, single-use envelope is a capability
> token plus a replay cache. **Why not just use biscuit + an ext-authz layer +
> a signing step?**

This document answers that directly. The short version: **Elyon-Sol does not
claim a new cryptographic primitive.** An admissibility envelope *is* a
capability token. The value is not a novel token — it is a specific composition,
plus two behavioral properties most capability tokens do not have, plus the
falsifiability apparatus. It can run *on top of* one of these systems rather than
instead of one.

## The prior art (what already exists)

- **Macaroons** — HMAC-chained bearer tokens with embedded *caveats*; support
  attenuation and third-party caveats for delegation. Bearer: possession is
  authority. Not single-use by themselves.
- **Biscuit** — public-key (Ed25519), offline-attenuable tokens carrying Datalog
  authorization logic; anyone with the public key can verify. The closest analog
  to the envelope's signed, verifiable, action-scoped shape. Not inherently
  single-use, and valid until expiry regardless of policy drift.
- **SPIFFE / SVID** — workload *identity* (X.509 or JWT-SVID). Answers "which
  workload is calling," not "is this action allowed." Complementary: it can be
  the caller identity an Elyon-Sol policy checks, not a competitor to the gate.
- **GNAP** — the OAuth-successor grant protocol; supports key-bound access
  tokens, fine-grained access rights, and interaction/approval flows. Human
  interaction is part of the protocol, but approval is not a signed
  separation-of-duties artifact the way it is here.
- **IETF Transaction Tokens (Txn-Tokens)** — short-lived signed tokens capturing
  the immutable context of a specific call as it propagates through a
  microservice chain. Structurally the nearest neighbor to per-action binding.

## What an envelope shares with these — stated plainly

Signed and independently verifiable; bound to an exact action; single-use /
replay-resistant (with the replay cache). None of that is new. A biscuit with the
right caveats plus a replay check covers most of it. We say so.

## What an envelope adds over a raw capability token

Two of these are behavioral properties the systems above generally do **not**
have; two are packaging/positioning:

1. **It is a receipt of a policy *decision*, not just a grant of authority.** A
   capability token says "the bearer may do X." An envelope records *why the gate
   decided X was admissible* — pinned to the exact canon version, manifest hash,
   evaluator, and condition results that produced the decision. That is an
   attestation/provenance property, distinct from authority-to-act.
2. **Continuity / reassertion: it self-invalidates when the policy it depended on
   changes.** A macaroon or biscuit is valid until its expiry regardless of
   whether the policy behind it moved. An envelope can be re-tested against live
   state and returns *reasserted*, *invalidated*, or *re-evaluate-required* — a
   past "yes" is not honored after the canon, manifest, or evaluator it rested on
   changes. (Mechanically this is cache-invalidation-on-version-change; the point
   is that capability tokens usually don't do it at all.)
3. **Human approval as a cryptographic separation-of-duties primitive.** A
   high-impact action is held until a separate approver signs a grant *with their
   own key on their own device*; the grant is verified, single-use, and bound to
   the exact decision. There is no server-side approve-button to forge.
4. **A live, public falsifiability challenge and an AI/MCP-admission
   specialization.** The differentiated engineering is the break-it surface and
   the agent-action framing, not the crypto.

## Property matrix

| Property | Elyon-Sol | Macaroon | Biscuit | SPIFFE/SVID | GNAP | Txn-Tokens |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Signed / independently verifiable | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Bound to an exact action | ✓ | ✓ (caveats) | ✓ (logic) | ✗ | partial | ✓ |
| Single-use / replay-proof | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ (short TTL) |
| Attenuable / delegable | ✗ | ✓ | ✓ | ✗ | partial | ✗ |
| Carries authorization logic in-token | ✗ | partial | ✓ | ✗ | ✗ | ✗ |
| Workload identity | ✗ | ✗ | ✗ | ✓ | ✗ | partial |
| Human approval in-protocol | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Approval = crypto separation of duties | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Self-invalidates on policy-version change | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Decision-provenance receipt (pins policy + evaluator) | ✓ | ✗ | ✗ | ✗ | ✗ | partial |
| Live public break-it challenge | ✓ | — | — | — | — | — |

The rows where biscuit/macaroon match are the point of the honesty: the primitive
is shared. The rows only Elyon-Sol fills — continuity, decision-provenance,
crypto-SoD approval — are the actual delta, and they are behavioral, not
cryptographic.

## So — why not just use biscuit + ext-authz + a signing step?

You could, and for many use cases you should. What you would then build yourself
is: the decision-provenance envelope, the reassertion/continuity check, the
separately-keyed human-approval hold, the fail-closed admission topology, and the
adversarial test surface that proves it. Elyon-Sol is that assembly, pre-wired and
put up for public disproof, specialized for agent / MCP tool-calls. If a raw
capability token already meets your need, use it — this is for the case where you
also want the decision attested, self-invalidating on policy change, human-gated
with real separation of duties, and falsifiable in the open.

*No novelty of primitive is claimed. The claim is composition, two behavioral
properties, and falsifiability.*
