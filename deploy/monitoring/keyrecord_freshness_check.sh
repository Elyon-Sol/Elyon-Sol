#!/bin/bash
# Elyon-Sol key-record freshness monitor (SES-9a follow-up, VL-146).
#
# The sidecar reads a LOCAL signed key record (ELYON_KEY_RECORD_PATH) refreshed by
# elyon-keyrecord-sync.timer. If that sync dies, the file ages past its `not_after`
# (300s) and the sidecar fails CLOSED — correct, but an availability outage you want
# to hear about BEFORE 5 minutes of denials. This check runs on a short timer and:
#   - fails (exit 1) + logs an ERR-priority journal line if the file is missing,
#     older than STALE_MTIME_SECS, or already past its signed not_after (with skew).
#   - is silent + exit 0 when healthy.
# Wire real alerting via the journal (scrape tag 'elyon-keyrecord' priority err) or
# an OnFailure= alert unit on elyon-keyrecord-monitor.service (see README.md).
set -u

FILE="${ELYON_KEY_RECORD_PATH:-/etc/elyon/sidecar_keys.json}"
STALE_MTIME_SECS="${ELYON_KEYRECORD_STALE_MTIME_SECS:-240}"   # sync is 120s; alert well before the 300s not_after
TAG="elyon-keyrecord"

fail() { logger -p user.err -t "$TAG" "STALE key record: $1 (file=$FILE)"; echo "FAIL: $1" >&2; exit 1; }

[ -f "$FILE" ] || fail "file missing"

now=$(date +%s)
mtime=$(stat -c %Y "$FILE" 2>/dev/null) || fail "cannot stat file"
age=$(( now - mtime ))
[ "$age" -le "$STALE_MTIME_SECS" ] || fail "file mtime ${age}s old (> ${STALE_MTIME_SECS}s) — sync likely stalled"

# Parse the SIGNED record's own not_after and check real freshness (skew-tolerant).
python3 - "$FILE" <<'PY' || fail "record not_after in the past or unparseable"
import json, sys, datetime
skew = 5
d = json.load(open(sys.argv[1]))
na = d["not_after"]
na = na[:-1] + "+00:00" if na.endswith("Z") else na
exp = datetime.datetime.fromisoformat(na)
now = datetime.datetime.now(datetime.timezone.utc)
sys.exit(0 if now < exp + datetime.timedelta(seconds=skew) else 1)
PY

# Healthy: no output, exit 0.
exit 0
