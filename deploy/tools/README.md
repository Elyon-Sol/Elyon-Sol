# deploy/tools — operator safety helpers

## safe_env.sh — never print a private key again (SES-9a follow-up, VL-146)

Twice during the SES-9a enablement a PRIVATE signing key was printed to the working chat by a broad
`grep '^ELYON_' deploy/.env` on a host that also held a signing key (VL-108's open-item (1) was the
first time). This helper makes the safe path the default: mask secret VALUES, or check presence
without printing the value.

```bash
# masked dump of a .env (private keys -> <redacted:N chars>, public keys/ids/urls shown):
deploy/tools/safe_env.sh dump /root/Elyon-Sol/deploy/.env

# presence-only check of one var (never prints the value):
deploy/tools/safe_env.sh check /root/Elyon-Sol/deploy/.env ELYON_KEY_RECORD_SIGNING_KEY_HEX
#   -> ELYON_KEY_RECORD_SIGNING_KEY_HEX: <set 64 chars>

# a running process's env, secrets masked:
sudo deploy/tools/safe_env.sh proc "$(systemctl show -p MainPID --value elyon-pub.service)"

# pipe any command whose output might contain a secret:
sudo tr '\0' '\n' < /proc/$PID/environ | deploy/tools/safe_env.sh mask
```

Rule (secret-precedence, fail-safe): a value is redacted if its KEY name contains `SIGNING_KEY`,
`PRIVATE`, `SECRET`, `PASSWORD`, `TOKEN`, `_SK`, or is any `*_KEY_HEX` not named `*PUBLIC*`. It
deliberately over-masks a non-`PUBLIC`-named public `*_KEY_HEX` rather than risk leaking a private
one. Suggested habit: alias the value-printing greps away.

```bash
# drop into ~/.bashrc on the hosts so the reflex is safe:
envcheck() { /root/Elyon-Sol/deploy/tools/safe_env.sh check /root/Elyon-Sol/deploy/.env "$1"; }
envdump()  { /root/Elyon-Sol/deploy/tools/safe_env.sh dump  /root/Elyon-Sol/deploy/.env; }
```
