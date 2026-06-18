# Publisher signing-key rotation (VL-108 pre-exposure checklist, item 1)

The publisher signing key was exposed in a working chat. Rotate it before any real external
engagement. The publisher signs the SIGNED published record live at `/published_hashes_signed.json`;
the target and the authz sidecar pin the publisher PUBLIC key and refuse a record that does not
verify. Rotation = new keypair on the publisher + re-pin the new public key on the two consumers.

> **Do the keygen on the PUBLISHER host, not in chat.** The whole point is the new private key
> never enters a shared channel. `deploy/rotate_publisher_key.py` writes the private key to a 0600
> file and prints only the public key.

## The three nodes and their vars
| Node | Var | Value |
|------|-----|-------|
| publisher | `ELYON_PUBLISHER_SIGNING_KEY_HEX` | new **private** key (hex) - publisher ONLY |
| publisher | `ELYON_PUBLISHER_KEY_ID` | new key id (bump it) |
| target | `ELYON_PUBLISHER_KEY_HEX` | new **public** key (hex) |
| target | `ELYON_PUBLISHER_KEY_ID` | same new key id |
| authz sidecar | `ELYON_PUBLISHER_KEY_ID` + `ELYON_PUBLISHER_KEY_HEX` | same new id + public key (if in signed mode) |

## Steps

1. **Generate (publisher host).**
   ```
   python deploy/rotate_publisher_key.py --out /run/secrets/pub_signing.key --key-id publisher-2026-06-18
   ```
   Note the printed `ELYON_PUBLISHER_KEY_HEX` (PUBLIC) and `ELYON_PUBLISHER_KEY_ID`.

2. **Publisher: install the private key + new id, restart.**
   ```
   export ELYON_PUBLISHER_SIGNING_KEY_HEX=$(cat /run/secrets/pub_signing.key)
   export ELYON_PUBLISHER_KEY_ID=publisher-2026-06-18
   # restart the publisher service, then shred the file:
   shred -u /run/secrets/pub_signing.key
   ```

3. **Target + sidecar: re-pin the PUBLIC key + new id, restart.**
   ```
   export ELYON_PUBLISHER_KEY_ID=publisher-2026-06-18
   export ELYON_PUBLISHER_KEY_HEX=<the public hex from step 1>
   # restart the target (and the authz sidecar if it runs signed mode)
   ```

4. **Verify the rotation.**
   - `curl -s https://pub.<domain>:9143/published_hashes_signed.json | jq .publisher_key_id`
     -> the NEW id.
   - The target/sidecar fetch and verify the fresh record against the new pinned key (a successful
     admit through the gate is the positive proof). A record under the OLD id, or signed by the OLD
     (exposed) key, no longer validates -> the exposed key is retired.
   - Re-run the live self-test (the gate-2 attack suite over the public surface):
     ```
     ELYON_LIVE_GATE_URL=https://gate.<domain>:8443 \
     ELYON_LIVE_TARGET_URL=https://target.<domain>:9443 \
     python EVIDENCE/proofs/attack_suite_live_runner.py
     ```
     Expect: positive control honored + every gate-2 attack refused, exit 0.

5. **Confirm retirement.** Grep every node's env/compose/.env for the OLD key id and the OLD
   private/public hex; ensure none remain anywhere (including shell history, CI, and the chat the
   key leaked into - it stays leaked, but it must no longer be TRUSTED by any node).

## Notes
- Bumping `ELYON_PUBLISHER_KEY_ID` (not just the key bytes) makes retirement unambiguous: a consumer
  pinned to the new id will not even look up a record presented under the old id.
- This rotates the PUBLISHED-RECORD publisher key. It is independent of the gate issuer key
  (`ELYON_SIGNING_KEY_*`) and the key-record root pin (`ELYON_PINNED_ROOT_*`); rotate those
  separately only if they were also exposed.
- After rotation, this closes VL-108 pre-exposure item 1. Items 2-7 (sidecar live ALLOW/DENY
  re-check, cert-renewal hooks, counsel sign-off, bounty/window/channel, publish, recruit) remain.
