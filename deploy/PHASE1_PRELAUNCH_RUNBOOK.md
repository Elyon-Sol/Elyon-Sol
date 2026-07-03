# Phase 1 — pre-launch hard gates (run before opening the private invite-only engagement)

All five gates must be GREEN before any researcher touches the surface. Gates 1–3 run on
your live hosts; gates 4–5 are documents. Host map (from `G5_GO_LIVE.md`):
- **Host A** = gate (`gate.elyon-sol.io:8443`).
- **Host B** = target (`:9443`) + publisher (`:9143`) + authz sidecar (`:9243`).

Public CA (Let's Encrypt) → leave `ELYON_TLS_CA_BUNDLE` **unset** everywhere (system trust).

---

## Gate 1 — rotate the exposed publisher key + re-pin (HOST B)

> **STATUS: CLOSED at VL-122** — key rotated live to `pub-2026-06-18` under a
> never-typed/no-history protocol; old key trusted by no node; the target additionally
> moved from byte-anchor to genuine SIGNED mode. Kept below for the method of record.

The publisher signing key was exposed in chat. Rotate it with the purpose-built tool (it
writes the private key to a 0600 file and never prints it):

```
# on HOST B (publisher), in the repo:
python deploy/rotate_publisher_key.py --key-id publisher-2026-06-18
# prints: ELYON_PUBLISHER_KEY_ID and ELYON_PUBLISHER_KEY_HEX (PUBLIC)
# writes:  ./publisher_signing_key.hex  (0600, PRIVATE — never paste anywhere)
```

Wire the new key (same host B, three services):

```
# PUBLISHER: set the PRIVATE key + new id, then restart
export ELYON_PUBLISHER_SIGNING_KEY_HEX=$(cat publisher_signing_key.hex)
export ELYON_PUBLISHER_KEY_ID=publisher-2026-06-18
# TARGET: pin the new PUBLIC key + id
export ELYON_PUBLISHER_KEY_HEX=<public hex printed above>
export ELYON_PUBLISHER_KEY_ID=publisher-2026-06-18
# SIDECAR (if running F-01 signed-record mode): same two as the target
export ELYON_PUBLISHER_KEY_HEX=<public hex>
export ELYON_PUBLISHER_KEY_ID=publisher-2026-06-18
```

Put these in each service's systemd env file (not the shell), then:

```
sudo systemctl restart elyon-pub elyon-target elyon-authz
shred -u publisher_signing_key.hex     # destroy the on-disk private key after wiring
```

**Verify:** the target/sidecar honor a record signed by the NEW key and refuse one signed by
the old key. The old `publisher-*` id must no longer be accepted.

- [ ] Gate 1 done: old key retired, new key pinned, private key shredded.

---

## Gate 2 — cert-renewal hooks on ALL FOUR nodes

Let's Encrypt certs are ~90 days; a silent expiry on any node breaks the surface mid-engagement.

```
# on EACH host, dry-run the renewal:
sudo certbot renew --dry-run
# confirm a deploy-hook restarts the matching service so the renewed cert is loaded, e.g.:
#   /etc/letsencrypt/renewal-hooks/deploy/elyon-restart.sh  ->  systemctl restart elyon-<svc>
```

Check expiry on every public endpoint from your laptop:

```
for hp in gate.elyon-sol.io:8443 target.elyon-sol.io:9443 pub.elyon-sol.io:9143 authz.elyon-sol.io:9243; do
  echo "== $hp =="; echo | openssl s_client -connect $hp -servername ${hp%%:*} 2>/dev/null | openssl x509 -noout -dates
done
```

- [ ] Gate 2 done: `renew --dry-run` passes and a deploy-hook restarts the unit on ALL FOUR
      nodes (gate, target, pub, authz).

---

## Gate 3 — live self-test GREEN (you, before any stranger)

> **STATUS: green runs on record** — attack suite exit 0 over the public surface at VL-108,
> re-run version-matched in signed mode at VL-122; sidecar live ALLOW/DENY closed at VL-122;
> REAL_TRANSPORT flipped at VL-108. RE-RUN inside the engagement window before opening.

From any machine (your laptop), run the author attack suite against the PUBLIC surface:

```
ELYON_LIVE_GATE_URL=https://gate.elyon-sol.io:8443 \
ELYON_LIVE_TARGET_URL=https://target.elyon-sol.io:9443 \
ELYON_LIVE_TARGET_ID=https://target.elyon-sol.io:9443/target \
python EVIDENCE/proofs/attack_suite_live_runner.py
# expected: every adversarial case DEFEATED + positive control honored; exit 0
```

Then the sidecar matrix against the public authz endpoint:

```
# mint_and_present.py pointed at authz.elyon-sol.io:9243
# expected: ALLOW on a valid attested request; DENY on forged / rebound / replayed / un-attested
```

- exit 0 → surface is real and the defenses transport. On all-green, flip the
  `REAL_TRANSPORT` readiness predicate naming this run log.
- exit 1 → **an attack succeeded. Do NOT expose.** Capture the case, fix, re-run. (A bug found
  now is the process working — the VirtualBox tier found four this way.)

- [ ] Gate 3 done: `attack_suite_live_runner.py` exit 0 + sidecar matrix clean; REAL_TRANSPORT
      flipped naming the run log.

---

## Gate 4 — counsel-approved safe harbor (HARD GATE)

The safe-harbor clause authorizes good-faith testing of the named hosts and waives legal
action for in-scope research. **Do not open the program without counsel sign-off.** Draft:
`deploy/SAFE_HARBOR_CLAUSE.md`. Once approved, paste the final wording into the SAFE HARBOR
section of `PRIVATE_INVITE_PROGRAM.md` and into the Authorization-to-Test.

- [ ] Gate 4 done: safe-harbor wording approved by counsel.

---

## Gate 5 — signed Authorization-to-Test on file

`deploy/AUTHORIZATION_TO_TEST.md` — names the four hosts, the window, the scope, and the
authorization. Sign it (you as the asset owner) and have it on file before any traffic. For
the private invite-only engagement, this signed document (with the researcher's written
acceptance) evidences the authorization.

- [ ] Gate 5 done: Authorization-to-Test signed and on file.

---

## Launch readiness — all five must be checked
- [ ] 1 publisher key rotated + re-pinned + private key shredded
- [ ] 2 cert-renewal hooks confirmed on all four nodes
- [ ] 3 live self-test exit 0 + REAL_TRANSPORT flipped
- [ ] 4 safe harbor counsel-approved
- [ ] 5 Authorization-to-Test signed

Only when all five are checked: send the first invitation per `SOLICITOR_INTAKE_CHEATSHEET.md`.
Record the green self-test as a VL entry (the REAL_TRANSPORT referent).
