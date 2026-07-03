# Did you actually break it? The inspector decides — not us.

The #1 fear with an unknown solo challenge is "the author will just wave my finding away."
So we don't adjudicate — the tool does. `envelope_inspector.py` is read-only audit code
that reads any token exactly the way the target does and tells you what it is. If it says
your token is invalid/expired/rebound/replayed and the target acted anyway, that gap **is**
the finding, and the tool's verdict is the shared referent we both accept.

## One command

```bash
# from a checkout of the repo, at the deployed commit:
git clone <repo-url> elyon && cd elyon && git checkout 3343e32
python -m pip install cryptography          # the only dependency
echo "$ENV" > token.json                    # $ENV = the envelope you got from the gate

# decode what the token is actually bound to + verify its signature + re-assert it:
PYTHONPATH=. python IMPLEMENTATION/envelope_inspector.py inspect token.json
```

Exit code `0` = the token is valid, currently in force, and bound as shown.
Exit code `1` = the tool rejects it (and prints why). **If the tool says `1` but the target
honored it, that's a break.**

## What each mode tells you

```bash
# inspect  — decode the bound scope (tool, args digest, target, freshness) + issuer signature
PYTHONPATH=. python IMPLEMENTATION/envelope_inspector.py inspect token.json

# reevaluate — re-run the production evaluator over the recorded request; proves the decision
#              was legitimately reached, not just well-formed
PYTHONPATH=. python IMPLEMENTATION/envelope_inspector.py reevaluate token.json

# reconcile — line up what was ISSUED against what was EXECUTED; a forwarded action with no
#             matching grant is a caught invariant violation
PYTHONPATH=. python IMPLEMENTATION/envelope_inspector.py reconcile --issued issued.jsonl --executed executed.jsonl
```

## The adjudication rule (so a "break" is unambiguous)

A finding is confirmed when the tool and the surface **disagree in your favor**:

- the target `honored:true` (or `/received` incremented) on a token the inspector rates
  invalid, expired, replayed, or bound to a different action/target; **or**
- the sidecar returned `200 / ALLOW` on a token the inspector does not rate as a
  currently-valid, correctly-bound, single-use, validly-signed token.

Reaching a *stated* boundary is not a finding — it confirms a limit we already publish:
declining to route through the gate at all (A1) against a target that hasn't adopted the
policy, stealing the signing key, or DoS. Those are documented, not defended.

Send the confirmed break — the token JSON, the inspector output, and the request sequence —
to **security@elyon-sol.io**. Because you ran the same tool we will, there's nothing to
argue about: the verdict is on the record before we even reply.
