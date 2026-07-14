# Key-record freshness monitoring (SES-9a follow-up, VL-146)

After SES-9a enablement, key-record freshness is on the critical path: the sidecar reads a local
signed record (`ELYON_KEY_RECORD_PATH`) refreshed by `elyon-keyrecord-sync.timer`. If that sync
stalls, the file ages past its 300s `not_after` and the sidecar fails **closed**
(`REF_VERIFY_KEY_RECORD_STALE`) — correct, but a silent availability outage. This adds a short-cycle
monitor that alerts *before* the surface starts denying.

## Files
- `keyrecord_freshness_check.sh` → install to `/usr/local/bin/` (chmod +x). Fails (exit 1) + logs an
  ERR journal line under tag `elyon-keyrecord` if the local record is missing, older than
  `ELYON_KEYRECORD_STALE_MTIME_SECS` (default 240s), or already past its signed `not_after`.
- `elyon-keyrecord-monitor.service` + `.timer` → run the check every 60s.
- `elyon-alert@.service` → optional generic notifier for `OnFailure=` (webhook via `ELYON_ALERT_WEBHOOK`,
  else an ERR journal line under tag `elyon-alert`).

## Install (on the sidecar host, `authz`)
```bash
sudo install -m 0755 deploy/monitoring/keyrecord_freshness_check.sh /usr/local/bin/keyrecord_freshness_check.sh
sudo install -m 0644 deploy/monitoring/elyon-keyrecord-monitor.service /etc/systemd/system/
sudo install -m 0644 deploy/monitoring/elyon-keyrecord-monitor.timer   /etc/systemd/system/
sudo install -m 0644 deploy/monitoring/elyon-alert@.service            /etc/systemd/system/   # optional
sudo systemctl daemon-reload
sudo systemctl enable --now elyon-keyrecord-monitor.timer
```

## Turn on alerting (pick one)
1. **Journal scrape (no webhook):** point your log pipeline at ERR-priority lines with tags
   `elyon-keyrecord` / `elyon-alert`:
   ```bash
   journalctl -t elyon-keyrecord -p err -f
   ```
2. **OnFailure webhook:** set `ELYON_ALERT_WEBHOOK=<url>` in `/root/Elyon-Sol/deploy/.env`, then add a
   drop-in so a stale check pages you:
   ```bash
   sudo systemctl edit elyon-keyrecord-monitor.service
   #   [Unit]
   #   OnFailure=elyon-alert@%n.service
   ```
   Do the same for `elyon-keyrecord-sync.service` so a *sync* failure (the root cause) also alerts.

## Verify it actually fires
```bash
# Simulate a stall: pause the sync, backdate the file, run the check by hand.
sudo systemctl stop elyon-keyrecord-sync.timer
sudo touch -d '10 minutes ago' /etc/elyon/sidecar_keys.json
sudo /usr/local/bin/keyrecord_freshness_check.sh; echo "exit=$?"   # expect FAIL + exit 1 + journal ERR
# restore:
sudo systemctl start elyon-keyrecord-sync.timer && sudo /usr/local/bin/sync_key_record.sh
sudo /usr/local/bin/keyrecord_freshness_check.sh; echo "exit=$?"   # expect exit 0
```

The publisher (`pub`) can run the same check against a locally-written copy if you also want
endpoint-side coverage; the sidecar is the surface that fails closed, so it's the priority.
