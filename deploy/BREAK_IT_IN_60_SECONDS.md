# Break Elyon-Sol in 60 seconds

> **Self-host edition.** The four public `elyon-sol.io` test hosts were retired on 2026-07-20 and
> are **offline**; the credited challenge is closed. Run this walkthrough
> against your own instance — stand one up with [`SPIN_UP_YOUR_OWN.md`](SPIN_UP_YOUR_OWN.md).
> You need nothing but `curl` and `jq`.

> **Honest scope.** Elyon-Sol has never been validated by any outside party (G5 is not met). A
> break you find on your own instance is your own result, not a recorded external validation.

The claim you're trying to break, in one line:
**without the gate's signing key, you cannot make the target act — or the sidecar say
ALLOW — unless your token is validly signed, currently valid, bound to exactly that
action and target, and not used before.**

---

## 0. Your instance

```bash
export GATE=http://localhost:8000     # mints + signs tokens, forwards to the target
export TARGET=http://localhost:9000   # the thing that acts
export AUTHZ=http://localhost:9200    # ALLOW / DENY sidecar (docker-compose.authz.yml overlay only)
```

(The former public hosts — `gate/target/authz/pub.elyon-sol.io` — are offline and out of scope.)

## 1. See a valid flow work (this is NOT a break — it's the control)

Mint a real token from the gate:

```bash
INTERACTION='{
  "AP": ["identity","role"],
  "OP": ["session","request"],
  "context": {
    "tool": "transfer_funds",
    "args_sha256": "ee0885070ca8ca1ff7df3e53275c4cadb3fbf747f3e0ea380a002f8c69ab8e9d"
  },
  "expected_manifest_version": "1.0",
  "expected_manifest_sha256": "ac18ac78c39dfed3d202964ab5e88d34a87ddebf8b41c1abda49bf75a0bcaeb1"
}'

# target_url is the target's IN-NETWORK identity (the compose gate only forwards to `target`)
ENV=$(curl -s $GATE/governed-call \
  -H 'content-type: application/json' \
  -d "{\"target_url\":\"http://target:9000/target\",\"interaction\":$INTERACTION}" \
  | jq -c '.envelope')

echo "$ENV" | jq '{tool: .request_context.context.tool, decision_sha256}'
```

That governed call already did the valid thing: the gate admitted, signed, **and forwarded** it,
and the target acted once (this is the token working as intended). The envelope is single-use, so
presenting `$ENV` again yourself is a replay — attack (b) below.

Watch the counter — it reads 1 after the governed call. This is the side effect you're trying to
trigger *without* a valid token:

```bash
curl -s $TARGET/received | jq
```

## 2. Now try to break it (any of these SHOULD be refused)

Each line is a distinct attack. A refusal body looks like
`{"detail": {"honored": false, "reason": "REF_..."}}`. If the target honors any of them (or
`/received` increments), or the sidecar returns ALLOW, **you have a finding.**

```bash
# a) No token at all — the A1 bypass
curl -s $TARGET/target -H 'content-type: application/json' -d "$INTERACTION" | jq

# b) Replay — present the SAME valid token a second time
curl -s $TARGET/target -H "X-Elyon-Sol-Envelope: $ENV" -H 'content-type: application/json' -d "$INTERACTION" | jq

# c) Forge — tamper one byte of the signed envelope
FORGED=$(echo "$ENV" | jq -c '.decision_sha256 = "deadbeef"')
curl -s $TARGET/target -H "X-Elyon-Sol-Envelope: $FORGED" -H 'content-type: application/json' -d "$INTERACTION" | jq

# d) Rebind — use this token but claim a different action in the body
REBIND=$(echo "$INTERACTION" | jq -c '.context.tool = "delete_database"')
curl -s $TARGET/target -H "X-Elyon-Sol-Envelope: $ENV" -H 'content-type: application/json' -d "$REBIND" | jq

# e) Sidecar — ALLOW/DENY only (it does not act). It reads the interaction from the
#    X-Elyon-Sol-Interaction HEADER (one line), not from the body.
I_HDR=$(echo "$INTERACTION" | jq -c .)
#    Control: a fresh, never-presented token -> 200 ALLOW (the sidecar working, not a break).
#    (Minting it goes through the gate, so the target acts once more: /received +1.)
FRESH=$(curl -s $GATE/governed-call -H 'content-type: application/json' \
  -d "{\"target_url\":\"http://target:9000/target\",\"interaction\":$INTERACTION}" | jq -c '.envelope')
curl -s -o /dev/null -D - -X POST $AUTHZ/authz -H "X-Elyon-Sol-Envelope: $FRESH" -H "X-Elyon-Sol-Interaction: $I_HDR" | grep -i '^x-elyon'
#    Now try to get ALLOW without a valid token — forged, replayed, rebound:
curl -s -o /dev/null -D - -X POST $AUTHZ/authz -H "X-Elyon-Sol-Envelope: $FORGED" -H "X-Elyon-Sol-Interaction: $I_HDR" | grep -i '^x-elyon'
curl -s -o /dev/null -D - -X POST $AUTHZ/authz -H "X-Elyon-Sol-Envelope: $FRESH" -H "X-Elyon-Sol-Interaction: $I_HDR" | grep -i '^x-elyon'
curl -s -o /dev/null -D - -X POST $AUTHZ/authz -H "X-Elyon-Sol-Envelope: $FRESH" -H "X-Elyon-Sol-Interaction: $(echo "$REBIND" | jq -c .)" | grep -i '^x-elyon'
# ALLOW on any of these three = a finding. DENY = working as intended.
```

Expected: **a–d all refuse** — `REF_VERIFY_ENVELOPE_ABSENT`, `REF_VERIFY_REPLAY`,
`REF_VERIFY_SIGNATURE_INVALID`, `REF_VERIFY_BINDING_MISMATCH`. For **e**, the control prints
`x-elyon-decision: ALLOW` and the three attempts print `DENY` with `REF_VERIFY_SIGNATURE_INVALID`,
`REF_VERIFY_REPLAY`, `REF_VERIFY_BINDING_MISMATCH`. (Run verbatim against `docker compose` with
the `docker-compose.authz.yml` overlay on 2026-09-27. Without the control, a DENY proves nothing:
a sidecar that never sees the interaction denies everything.)

## 3. Go deeper

The obvious attacks above are the warm-up. The real edges: expired tokens, cross-target
swaps (present a token bound to target A against a different path), state-drift after the
published record rotates, key-window games, args that canonicalize collisions. The site's
Red-Team section records how the (now-closed) challenge was run. Confirm a break is real
before you report it — see `INSPECT_YOUR_BREAK.md` (the inspector decides, not us).

## 4. You found something

Email **security@elyon-sol.io** with: the category (target / sidecar), the exact requests
in order, and what you saw (status codes, the `/received` count). Reports are handled
best-effort; the former credit / wall-of-fame mechanics are wound down (see
[`SECURITY.md`](../SECURITY.md)).

Test only instances you run yourself — there are no in-scope public hosts. Testing the
open-source code locally needs no authorization.
