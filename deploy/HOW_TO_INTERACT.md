# How to interact - Gargoyle challenge appendix

DRAFT - public, uncommitted. Operational reference for the "break it" challenge:
endpoints, request/response shapes, a working sample, and the self-check tool.
No theory - just enough to send a request and read the answer. Fill the elyon-sol.io
placeholders before publishing.

## Endpoints (TLS, public CA)

- Gate:      https://gate.elyon-sol.io:8443    POST /governed-call
- Target:    https://target.elyon-sol.io:9443  POST /target ; GET /received
- Sidecar:   https://authz.elyon-sol.io:9243   POST /authz  ; GET /healthz
- Publisher: https://pub.elyon-sol.io:9143/published_hashes.json

## The flow in one breath

The gate mints and SIGNS a one-time token for one specific action, and immediately
forwards that action to the target - so a successful mint causes exactly one
legitimate action (the target's `/received` count goes up by one; that is the
positive control). The signed token also rides a header you can alter or replay
against the target or the sidecar. Your goal: cause an action the gate did not
mint, or a second use of one it did, or an ALLOW the conditions do not justify.

## 1. Get the current manifest pin (needed to mint)

    curl -sS https://pub.elyon-sol.io:9143/published_hashes.json

Use the manifest hash it reports as `expected_manifest_sha256` in step 2;
`expected_manifest_version` is "1.0" (or the operator's deployed version).

## 2. Mint a token (a legitimate, allowed call)

    curl -sS -X POST https://gate.elyon-sol.io:8443/governed-call \
      -H 'content-type: application/json' \
      -d '{"target_url":"https://target.elyon-sol.io:9443/target",
           "interaction":{"AP":["identity","role"],"OP":["session","request"],
                          "context":{"demo":"hello"},
                          "expected_manifest_version":"1.0",
                          "expected_manifest_sha256":"<from step 1>"}}'

200 response:

    {"decision":"ELIGIBLE","envelope":{ ...signed one-time token... }}

A 403 with `{"refusal_reason_code":"REF_..."}` means the gate refused (e.g. your
interaction did not satisfy the manifest, or the pin was wrong). The codes are
self-describing. That mint already caused ONE honored action at the target -
confirm with `curl https://target.elyon-sol.io:9443/received` -> `{"count":N}`.

## 3. Present the token to the target

Put the envelope object (verbatim, from step 2) into the `X-Elyon-Sol-Envelope`
header; send the SAME interaction as the body:

    ENV='<the envelope JSON from step 2>'
    curl -sS -i -X POST https://target.elyon-sol.io:9443/target \
      -H "X-Elyon-Sol-Envelope: $ENV" \
      -H 'content-type: application/json' \
      -d '{"AP":["identity","role"],"OP":["session","request"],"context":{"demo":"hello"},"expected_manifest_version":"1.0","expected_manifest_sha256":"<from step 1>"}'

- 200 `{"honored":true,...}` = it acted (and `/received` increments).
- 403 `{"reason":"REF_VERIFY_..."}` = refused. Presenting the SAME token a second
  time SHOULD refuse as a replay - that is correct. A SECOND honored action is a
  break.

## 4. Present the token to the sidecar (allow/deny only; it does not act)

    curl -sS -i -X POST https://authz.elyon-sol.io:9243/authz \
      -H "X-Elyon-Sol-Envelope: $ENV" \
      -H 'X-Elyon-Sol-Interaction: {"AP":["identity","role"],"OP":["session","request"],"context":{"demo":"hello"},"expected_manifest_version":"1.0","expected_manifest_sha256":"<from step 1>"}'

- 200, `x-elyon-decision: ALLOW` = judged admissible.
- 403, `x-elyon-decision: DENY`, `x-elyon-reason: REF_...` = refused.

A break is ALLOW (200) for a token that is absent, forged, expired, replayed,
altered, or bound to a different action or target.

## 5. Check a token yourself (the inspector)

Decode a token's exact bound scope, independent of the gate's say-so:

    echo "$ENV" > env.json
    python -m IMPLEMENTATION.envelope_inspector inspect env.json
    python -m IMPLEMENTATION.envelope_inspector reevaluate env.json

A disputed break is settled by running the inspector on the artifacts and reading
the verdict.

## Where to push (ideas, not a limit)

- Drop the `X-Elyon-Sol-Envelope` header entirely (steps 3/4).
- Change one character of any field inside the token.
- Replay the exact token a second time.
- Use a token minted for one action/target against a different one.
- Wait past the freshness window, then present the token; or fabricate one.

Each refusal names the guard that fired. Make one of those guards ALLOW or ACT
when it should not - with steps we can re-run - and you have a break.
