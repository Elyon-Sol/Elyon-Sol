# Provisioning checklist - VM-A (gate) and VM-B (target + publisher) on Oracle VirtualBox

A full, self-contained stand-up of the Elyon-Sol cross-host TLS test on two local VirtualBox Linux
VMs. Companion to deploy/runbook.md (single-box) and deploy/tls/trust_bootstrap.md.

HONEST SCOPE: two VirtualBox VMs are distinct OS hosts with a real network + real TLS between them,
so this GREENS the REAL_TRANSPORT predicate (the cross-host referent, VL-083 / C4). It is NOT the
public-internet / external-attacker referent: one physical machine, a private virtual network, both
ends under your control. A real EXTERNAL attacker on a public surface remains the final G5 / GR-3
step. UNVALIDATED in the build sandbox (no VirtualBox/docker here); the author's stand-up.

Role split: VM-A runs ONLY the gate (pep, :8000). VM-B runs the target (:9000) + publisher
(:9100). The client (the live attack runner, run from the host or VM-A) hits VM-A's gate and VM-B's
target directly; the gate forwards admitted calls across the network to VM-B's target.

The networking is the one VirtualBox-specific piece: each VM gets TWO adapters - NAT (for internet:
apt + git clone) and Host-only (for VM<->VM<->host on stable IPs). That is the robust, standard
VirtualBox pattern.

---

## 0. Host prerequisites

- Oracle VirtualBox 7.x installed (the host can be Windows / macOS / Linux).
- ~8 GB+ RAM and ~50 GB free disk (2 VMs x ~2 GB / ~20 GB).
- An Ubuntu Server 24.04 LTS ISO (ubuntu-24.04-live-server-amd64.iso).

---

## 1. Create the Host-only network (once)

GUI: VirtualBox main window -> File (or Tools) -> Host Network Manager / Network -> Create a
Host-only network. Set IPv4 192.168.56.1 / 255.255.255.0; optionally enable its DHCP server. Note
the adapter name (vboxnet0 on Linux/macOS, "VirtualBox Host-Only Ethernet Adapter" on Windows).

CLI alternative:
    VBoxManage hostonlyif create
    VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0
    # VirtualBox 7.1 uses host-only NETWORKS instead:
    # VBoxManage hostonlynet add --name elyon-hostnet --netmask 255.255.255.0 \
    #     --lower-ip 192.168.56.1 --upper-ip 192.168.56.254 --enable

We will give VM-A 192.168.56.101 and VM-B 192.168.56.102 (in VirtualBox's default-allowed
192.168.56.0/21 range).

---

## 2. Create the VMs (GUI is easiest; run once for VM-A, once for VM-B)

GUI: Machine -> New -> Ubuntu (64-bit), 2048 MB RAM, 2 CPUs, create a 20 GB VDI, attach the ISO.
Then Settings -> Network:
  - Adapter 1: Enabled, Attached to = NAT
  - Adapter 2: Enabled, Attached to = Host-only Adapter -> select vboxnet0 (the one from step 1)
Start the VM and install Ubuntu Server (enable "Install OpenSSH server").

CLI alternative (per VM; VM = "VM-A" then "VM-B"):
    VM="VM-A"
    VBoxManage createvm --name "$VM" --ostype Ubuntu_64 --register
    VBoxManage modifyvm "$VM" --memory 2048 --cpus 2 --firmware efi
    VBoxManage createmedium disk --filename "$HOME/VirtualBox VMs/$VM/$VM.vdi" --size 20000
    VBoxManage storagectl "$VM" --name SATA --add sata --controller IntelAhci
    VBoxManage storageattach "$VM" --storagectl SATA --port 0 --device 0 --type hdd \
        --medium "$HOME/VirtualBox VMs/$VM/$VM.vdi"
    VBoxManage storageattach "$VM" --storagectl SATA --port 1 --device 0 --type dvddrive \
        --medium /path/to/ubuntu-24.04-live-server-amd64.iso
    VBoxManage modifyvm "$VM" --nic1 nat --nic2 hostonly --hostonlyadapter2 vboxnet0
    VBoxManage startvm "$VM"

---

## 3. Base setup - run on BOTH VMs (over the console or SSH)

    sudo apt-get update && sudo apt-get -y upgrade
    sudo apt-get -y install docker.io docker-compose-v2 git
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER && newgrp docker
    sudo timedatectl set-ntp true                      # clocks must agree (freshness check)

### 3a. Give the Host-only adapter a static IP (the second NIC)

The first NIC (NAT, usually enp0s3) gets DHCP + internet automatically. The second NIC (host-only,
usually enp0s8) needs an address. Identify it:

    ip -o link show | awk -F': ' '{print $2}'          # find the second iface name (e.g. enp0s8)

Create /etc/netplan/99-hostonly.yaml (VM-A uses .101; VM-B uses .102):

    sudo tee /etc/netplan/99-hostonly.yaml >/dev/null <<'YAML'
    network:
      version: 2
      ethernets:
        enp0s8:
          dhcp4: false
          addresses: [192.168.56.101/24]
    YAML
    sudo chmod 600 /etc/netplan/99-hostonly.yaml
    sudo netplan apply
    ip -4 addr show enp0s8                              # confirm 192.168.56.101 (or .102 on VM-B)

(Replace enp0s8 with the real second-NIC name if different, and 101 -> 102 on VM-B.)

Then clone the repo on both VMs:

    git clone https://github.com/Elyon-Sol/Elyon-Sol.git && cd Elyon-Sol

Use these throughout:  VMA_IP=192.168.56.101   VMB_IP=192.168.56.102

---

## 4. Generate config + certs (ONCE, on VM-A, then copy parts to VM-B)

    cd ~/Elyon-Sol
    python3 deploy/bootstrap_config.py                          # writes deploy/.env (gate key + anchor)
    python3 deploy/tls/gen_certs.py 192.168.56.101 192.168.56.102   # CA + leaves with both IPs in the SAN

Edit deploy/.env so the URLs point at VM-B over TLS (replace the compose service names):

    ELYON_TARGET_URL=https://192.168.56.102:9000/target
    ELYON_PUBLISHER_URL=https://192.168.56.102:9100/published_hashes.json

Copy to VM-B (it needs the certs, the CA, and the public key + anchor - NOT the gate private key):

    scp deploy/.env deploy/tls/certs/ca.crt deploy/tls/certs/target.* deploy/tls/certs/publisher.* \
        user@192.168.56.102:~/Elyon-Sol/deploy/

On VM-B, move the copied certs under deploy/tls/certs/ and the .env under deploy/ (the gate private
key in .env stays unused on VM-B; only ELYON_GATE_PUBLIC_KEY_HEX / ELYON_GATE_KEY_ID /
ELYON_PINNED_ROOT_SHA256 / ELYON_TARGET_URL / ELYON_PUBLISHER_URL are read there).

---

## 5. A two-host compose override (the committed compose is single-box)

The committed docker-compose.yml uses compose SERVICE NAMES (target:9000) that only resolve inside
one host's compose network. For two hosts, add a small override pointing the gate's forward and the
target's identity at the real VM-B IP. Create deploy/docker-compose.hosts.yml on BOTH VMs:

    services:
      target:
        environment:
          ELYON_TARGET_URL: https://192.168.56.102:9000/target
      gate:
        environment:
          ELYON_TLS_CA_BUNDLE: /certs/ca.crt

(The publisher is co-located with the target on VM-B, so the target reaches it via the compose
service name `publisher` - unchanged.)

---

## 6. Bring the services up

On VM-B (target + publisher only):

    cd ~/Elyon-Sol/deploy
    docker compose -f docker-compose.yml -f docker-compose.tls.yml -f docker-compose.hosts.yml \
        up --build publisher target

On VM-A (gate only):

    cd ~/Elyon-Sol/deploy
    docker compose -f docker-compose.yml -f docker-compose.tls.yml -f docker-compose.hosts.yml \
        up --build gate

If ufw is enabled inside the VMs, open the ports (or `sudo ufw disable` for the test):
VM-A: `sudo ufw allow 8000/tcp` ; VM-B: `sudo ufw allow 9000/tcp && sudo ufw allow 9100/tcp`.

---

## 7. Run the live attack suite (from the host, VM-A, or any box on 192.168.56.0/24)

    cd ~/Elyon-Sol
    ELYON_LIVE_GATE_URL=https://192.168.56.101:8000 \
    ELYON_LIVE_TARGET_URL=https://192.168.56.102:9000 \
    ELYON_LIVE_TARGET_ID=https://192.168.56.102:9000/target \
    ELYON_TLS_CA_BUNDLE=deploy/tls/certs/ca.crt \
    PYTHONPATH=. python3 EVIDENCE/proofs/attack_suite_live_runner.py

(To run from the Windows/macOS host instead of a VM, install Python 3 + `pip install requests
cryptography fastapi`, clone the repo there, copy ca.crt over, and run the same command. The host is
192.168.56.1 on the host-only net, so it can reach .101 and .102.)

Expect: the positive control HONORED and every adversarial attack DEFEATED over real transport,
exit 0.

---

## 8. Record the result (C4)

On a green run, flip the REAL_TRANSPORT predicate in EVIDENCE/readiness.json to:

    "REAL_TRANSPORT": { "green": true,
      "proof": "EVIDENCE/proofs/<your captured run log>.log",
      "blocked_by": null }

and (optionally) add "REAL_TRANSPORT" to PREDICATE_NAMES in IMPLEMENTATION/readiness.py so it is
counted (3-of-4 -> 4-of-4). Commit with a ledger entry naming the run. That closes C4.

---

## Smoke test (before the attack suite)

    curl --cacert deploy/tls/certs/ca.crt https://192.168.56.102:9100/published_hashes.json   # publisher serves the record
    curl --cacert deploy/tls/certs/ca.crt https://192.168.56.102:9000/received                # target up (count: 0)

## Troubleshooting

- VMs cannot reach each other / no host-only IP: confirm Adapter 2 is attached to the host-only
  network and `ip addr show enp0s8` shows 192.168.56.10x; re-apply netplan. Check the host firewall
  is not blocking the vboxnet interface.
- No internet for apt/clone: that is Adapter 1 (NAT) - confirm enp0s3 has a DHCP address.
- TLS handshake / hostname errors: the IP you connect to must be in the cert SAN - regenerate with
  `gen_certs.py 192.168.56.101 192.168.56.102` if an IP changed.
- Gate returns no envelope / fail-closed: ELYON_SIGNING_KEY_HEX/ID must be set on VM-A (in .env).
- Target REF_TARGET_NOT_CONFIGURED: VM-B is missing ELYON_GATE_PUBLIC_KEY_HEX / ELYON_GATE_KEY_ID /
  ELYON_PINNED_ROOT_SHA256 / ELYON_TARGET_URL, or the anchor does not match the served record.
- REF_VERIFY_SIGNATURE_EXPIRED on a valid call: the VM clocks disagree - confirm `timedatectl` NTP
  on both, or set a non-zero clock_skew.
- Binding mismatch on the positive control: ELYON_LIVE_TARGET_ID must EXACTLY equal the target's
  ELYON_TARGET_URL (scheme, IP, port, /target).

---

## Appendix - signed-record freshness (A3b-b, VL-091) + the stale-record attack

By default the target uses the byte-anchor record: a stale-but-anchor-matching published record is
honored. VL-091 wires the SIGNED-record freshness reader as an opt-in mode - a target configured
with a pinned publisher key refuses a stale record (`REF_VERIFY_PUBLISHED_RECORD_STALE`). Enable it
to demonstrate the "approved then the underlying record goes stale" defense over real transport.

1. Generate a publisher keypair (once):
       ~/elyon-venv/bin/python - <<'PY'
       from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
       from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
       k = Ed25519PrivateKey.generate()
       print("PRIV", k.private_bytes_raw().hex())
       print("PUB ", k.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex())
       PY

2. Publisher (VM-B) signs records - add to its environment, restart:
       ELYON_PUBLISHER_SIGNING_KEY_HEX=<PRIV>
       ELYON_PUBLISHER_KEY_ID=pub-1
       ELYON_RECORD_MAX_AGE_SECONDS=300

3. Target (VM-B) consults the signed record - add (the PUBLIC half), restart:
       ELYON_PUBLISHER_KEY_HEX=<PUB>
       ELYON_PUBLISHER_KEY_ID=pub-1
       ELYON_SIGNED_RECORD_URL=https://192.168.56.102:9100/published_hashes_signed.json
   A valid call is now honored against the freshness-checked signed record (the live attack suite
   stays green - re-run it to confirm).

4. Stale-record attack (the freshness refusal): make the target consult an EXPIRED record.
       # capture a record under a short window, let it expire:
       # (publisher temporarily with ELYON_RECORD_MAX_AGE_SECONDS=2)
       mkdir -p /tmp/stalepub
       curl --cacert deploy/tls/certs/ca.crt \
         https://192.168.56.102:9100/published_hashes_signed.json \
         -o /tmp/stalepub/published_hashes_signed.json
       sleep 3
       cd /tmp/stalepub && python3 -m http.server 9200 &     # a 'stale publisher' (plain http ok)
       # point the target at the stale publisher and restart it:
       #   ELYON_SIGNED_RECORD_URL=http://192.168.56.102:9200/published_hashes_signed.json
       # then present a valid call (the live runner, or a single admitted envelope)
   -> the target refuses REF_VERIFY_PUBLISHED_RECORD_STALE: it cannot obtain a fresh record, so the
   approved call is NOT honored against a stale published state. That is A3b sub-case (b) closed for
   a configured deployment.

Honest bound: the publisher key is now the load-bearing trust floor (out-of-band, parity with the
key/root records); making signed mode the BARE default is a deployment posture, not the default.

---

## Appendix - cross-instance exactly-once (B3, VL-094): shared replay cache

By default each target instance keeps its own in-memory replay set, so a horizontally-scaled
executor (N instances) could honor the same decision once PER instance. VL-094 wires the replay
defense to the ReplayCache seam; point it at a shared store (Redis) and a decision_id honored on
one instance is refused on every other.

Create deploy/docker-compose.replay.yml (adds Redis + a SECOND target on :9001, both sharing it):
    services:
      redis:
        image: redis:7-alpine
      target:
        environment:
          ELYON_REPLAY_REDIS_URL: redis://redis:6379/0
      target2:
        build: { context: .., dockerfile: deploy/Dockerfile }
        command: ["uvicorn","IMPLEMENTATION.reference_target:app","--host","0.0.0.0","--port","9001",
                  "--ssl-certfile","/certs/target.crt","--ssl-keyfile","/certs/target.key"]
        environment:
          ELYON_TARGET_URL: https://192.168.56.102:9000/target
          ELYON_PUBLISHER_URL: https://publisher:9100/published_hashes.json
          ELYON_PINNED_ROOT_SHA256: ${ELYON_PINNED_ROOT_SHA256}
          ELYON_GATE_KEY_ID: ${ELYON_GATE_KEY_ID}
          ELYON_GATE_PUBLIC_KEY_HEX: ${ELYON_GATE_PUBLIC_KEY_HEX}
          ELYON_TLS_CA_BUNDLE: /certs/ca.crt
          ELYON_REPLAY_REDIS_URL: redis://redis:6379/0
        volumes: [ "./tls/certs:/certs:ro" ]
        ports: [ "9001:9001" ]

Bring it up (add the new -f):
    docker compose -f docker-compose.yml -f docker-compose.tls.yml -f docker-compose.hosts.yml \
        -f docker-compose.replay.yml up -d --build redis target target2

Demonstrate (from the laptop) - admit once, present to BOTH instances; the second is a replay:
    PYTHONPATH=. ~/elyon-venv/Scripts/python - <<'PY'
    from EVIDENCE.proofs.attack_harness import HttpSurface, RequestsClient
    ca = "deploy/tls/certs/ca.crt"
    def surface(port):
        return HttpSurface(
            gate_client=RequestsClient("https://192.168.56.101:8000", verify=ca),
            target_client=RequestsClient("https://192.168.56.102:%d" % port, verify=ca),
            target_url="https://192.168.56.102:9000/target")
    a, b = surface(9000), surface(9001)
    a0, b0 = a.acted_count(), b.acted_count()
    # admit: the gate signs + PUSHES to instance A (:9000), which honors and claims the
    # decision_id in the SHARED Redis.
    env = a.admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    a1 = a.acted_count()
    # present the SAME decision directly to instance B (:9001) - a different process:
    hb, rb = b.attempt("transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    print("instance A acted (push honored):", a1 - a0)        # 1
    print("instance B verdict (same decision):", (hb, rb))    # (False, REF_VERIFY_REPLAY)
    print("instance B acted:", b.acted_count() - b0)          # 0
    PY
Expect: A acted = 1 (it honored the gate's push and claimed the decision_id in Redis), B verdict =
(False, REF_VERIFY_REPLAY), B acted = 0. Instance B refused a decision it never saw, because the
SHARED Redis made the claim global - cross-instance exactly-once. (With a per-instance in-memory
cache, B would have honored it - that is the gap this closes.) Ensure the publisher is in a healthy
state (300s window, not the stale-demo negative window) so A's signed-mode fetch honors.
