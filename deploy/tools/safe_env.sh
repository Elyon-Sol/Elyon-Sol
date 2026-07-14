#!/bin/bash
# Elyon-Sol secret-safe env helpers (SES-9a follow-up, VL-146).
#
# WHY: twice this session a PRIVATE key was printed to the working chat by a broad
# `grep '^ELYON_...' deploy/.env` on a host that also held a signing key (and it was
# VL-108's open-item-(1) the first time). These helpers make the safe path the easy
# path: mask secret VALUES, and check presence WITHOUT printing the value.
#
# Use:
#   source deploy/tools/safe_env.sh          # get the functions, or:
#   deploy/tools/safe_env.sh dump  <file>    # cat a .env with secret values masked
#   deploy/tools/safe_env.sh check <file> VAR # presence-only: <set N chars> / <EMPTY> / <absent>
#   deploy/tools/safe_env.sh proc  <pid>     # a process's env, secrets masked
#   <anything> | deploy/tools/safe_env.sh mask   # filter stdin, masking KEY=secret lines
#
# Secret rule (SECRET-PRECEDENCE, fail-safe — case-insensitive on the KEY name):
#   redact if the key name contains SIGNING_KEY, PRIVATE, SECRET, PASSWORD, TOKEN, or _SK,
#   OR it is any *_KEY_HEX whose name does NOT contain the literal token PUBLIC.
# This deliberately over-masks a public *_KEY_HEX that isn't named *PUBLIC* (e.g. a pinned
# publisher public key) — safe — rather than risk showing a private one. NOTE: matching on
# "_PUB" was WRONG (it matches PUBLISHER, which leaked a SIGNING key); only literal PUBLIC
# is a show-exception. Ids/urls/ROOT_HEX/ROOT_ID pins are shown (not secret material).

# mask: read KEY=VALUE lines from stdin; redact VALUE (show only length) for secret keys.
elyon_mask() {
  awk '
    {
      eq = index($0, "=");
      if (eq == 0) { print; next }
      key = substr($0, 1, eq-1);
      val = substr($0, eq+1);
      upk = toupper(key);
      secret = (upk ~ /SIGNING_KEY|PRIVATE|SECRET|PASSWORD|TOKEN|_SK/) \
               || (upk ~ /KEY_HEX/ && upk !~ /PUBLIC/);
      if (secret) { printf "%s=<redacted:%d chars>\n", key, length(val); next }
      print;                                                    # non-secret: show
    }'
}

# dump: a .env (or any KEY=VALUE file) with secret values masked.
elyon_dump() { [ -f "$1" ] || { echo "no such file: $1" >&2; return 2; }; elyon_mask < "$1"; }

# check: presence-only for one VAR in a file. Never prints the value.
elyon_check() {
  local f="$1" var="$2" line val
  [ -f "$f" ] || { echo "$var: <no such file>"; return 2; }
  line=$(grep -E "^${var}=" "$f" | tail -1)
  if [ -z "$line" ]; then echo "$var: <absent>"; return 1; fi
  val="${line#*=}"
  if [ -z "$val" ]; then echo "$var: <EMPTY>"; return 1; fi
  echo "$var: <set ${#val} chars>"
}

# proc: a running process's environ, secrets masked (needs root for another user's pid).
elyon_proc() {
  local pid="$1"
  [ -r "/proc/$pid/environ" ] || { echo "cannot read /proc/$pid/environ (root?)" >&2; return 2; }
  tr '\0' '\n' < "/proc/$pid/environ" | elyon_mask
}

# CLI dispatch when executed (not sourced).
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  cmd="${1:-}"; shift 2>/dev/null || true
  case "$cmd" in
    mask)  elyon_mask ;;
    dump)  elyon_dump "$@" ;;
    check) elyon_check "$@" ;;
    proc)  elyon_proc "$@" ;;
    *) echo "usage: $0 {mask|dump <file>|check <file> VAR|proc <pid>}" >&2; exit 2 ;;
  esac
fi
