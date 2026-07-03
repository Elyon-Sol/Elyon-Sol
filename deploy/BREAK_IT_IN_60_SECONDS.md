# Break Elyon-Sol in 60 seconds

No signup, no email, no waiting. The public test surface is live — attack it right now.
The credited engagement is invite-only (that's about *reward and disclosure*, not access):
you can poke the surface this instant, and if you find something real, **then** email
security@elyon-sol.io to claim credit.

> **Honest scope.** Elyon-Sol has not been validated by any outside party yet — this
> challenge is how we seek that. A confirmed break is the first such result, not a
> re-confirmation of prior review. You need nothing but `curl` and `jq`.

The claim you're trying to break, in one line:
**without the gate's signing key, you cannot make the target act — or the sidecar say
ALLOW — unless your token is validly signed, currently valid, bound to exactly that
action and target, and not used before.**

---

## 0. The four hosts (the only things in scope)

```
gate    https://gate.elyon-sol.io:8443    # mints + signs tokens
target  https://target.elyon-sol.io:9443  # the thing that acts
authz   https://authz.elyon-sol.io:9243   # ALLOW / DENY sidecar
pub     https://pub.elyon-sol.io:9143     # serves the signed record
```

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
  "expected_manifest_sha256": "a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8"
}'

ENV=$(curl -s https://gate.elyon-sol.io:8443/governed-call \
  -H 'content-type: application/json' \
  -d "{\"target_url\":\"https://target.elyon-sol.io:9443/target\",\"interaction\":$INTERACTION}" \
  | jq -c '.envelope')

echo "$ENV" | jq '{tool: .interaction.context.tool, decision_sha256}'
```

Present it once to the target — it acts (this is the token working as intended):

```bash
curl -s https://target.elyon-sol.io:9443/target \
  -H "X-Elyon-Sol-Envelope: $ENV" \
  -H 'content-type: application/json' \
  -d "$INTERACTION" | jq
# expect: {"honored": true, "reason": "REASSERTED_AND_BOUND"}
```

Watch the counter tick — this is the side effect you're trying to trigger *without* a valid token:

```bash
curl -s https://target.elyon-sol.io:9443/received | jq
```

## 2. Now try to break it (any of these SHOULD be refused)

Each line is a distinct attack. If the target `honored:true` (or `/received` increments)
on any of them, or the sidecar returns ALLOW, **you have a finding.**

```bash
# a) No token at all — the A1 bypass
curl -s https://target.elyon-sol.io:9443/target -H 'content-type: application/json' -d "$INTERACTION" | jq

# b) Replay — present the SAME valid token a second time
curl -s https://target.elyon-sol.io:9443/target -H "X-Elyon-Sol-Envelope: $ENV" -H 'content-type: application/json' -d "$INTERACTION" | jq

# c) Forge — tamper one byte of the signed envelope
FORGED=$(echo "$ENV" | jq -c '.decision_sha256 = "deadbeef"')
curl -s https://target.elyon-sol.io:9443/target -H "X-Elyon-Sol-Envelope: $FORGED" -H 'content-type: application/json' -d "$INTERACTION" | jq

# d) Rebind — use this token but claim a different action in the body
REBIND=$(echo "$INTERACTION" | jq -c '.context.tool = "delete_database"')
curl -s https://target.elyon-sol.io:9443/target -H "X-Elyon-Sol-Envelope: $ENV" -H 'content-type: application/json' -d "$REBIND" | jq

# e) Sidecar — get authz to say ALLOW on any of the above
curl -s -o /dev/null -w "%{http_code}\n" https://authz.elyon-sol.io:9243/authz \
  -H "X-Elyon-Sol-Envelope: $FORGED" -H 'content-type: application/json' -d "$INTERACTION"
# 200 = ALLOW (a finding). 403 = DENY (working as intended).
```

Expected: **b–e all refuse** — `REF_VERIFY_REPLAY`, `REF_VERIFY_SIGNATURE_INVALID`,
`REF_VERIFY_BINDING_MISMATCH`, and a 403 from the sidecar. Make any of them act, and
you're on the wall of fame.

## 3. Go deeper

The obvious attacks above are the warm-up. The real edges: expired tokens, cross-target
swaps (present a token bound to target A against a different path), state-drift after the
published record rotates, key-window games, args that canonicalize collisions. Full
challenge, scope, and rewards: the site's Red-Team section. Confirm a break is real
before you send it — see `INSPECT_YOUR_BREAK.md` (the inspector decides, not us).

## 4. You found something

Email **security@elyon-sol.io** with: the category (target / sidecar), the exact requests
in order, and what you saw (status codes, the `/received` count). We reproduce it, and a
confirmed break is credited to you permanently — see the recognition model on the site.

Rules: the four hosts above only. No DoS/flooding (refusing is the design, not a break),
no attacking the host OS / cloud / CA outside the request protocol. Good-faith testing in
scope is authorized under the Authorization-to-Test on file.
