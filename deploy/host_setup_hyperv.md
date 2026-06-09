# Provisioning checklist - VM-A (gate) and VM-B (target + publisher) on Hyper-V

A copy-paste stand-up of the Elyon-Sol cross-host TLS test on two local Hyper-V Linux VMs.
Companion to deploy/runbook.md (single-box) and deploy/tls/trust_bootstrap.md.

HONEST SCOPE: two Hyper-V VMs are distinct OS hosts with a real network + real TLS between them,
so this GREENS the REAL_TRANSPORT predicate (the cross-host referent, VL-083 / C4). It is NOT the
public-internet / external-attacker referent: one physical machine, a private virtual network, both
ends under your control. A real EXTERNAL attacker on a public surface remains the final G5 / GR-3
step. UNVALIDATED in the build sandbox (no Hyper-V/docker here); this is the author's stand-up.

Role split: VM-A runs ONLY the gate (pep, :8000). VM-B runs the target (:9000) + publisher
(:9100). The client (the live attack runner) hits VM-A's gate and VM-B's target directly. The gate
forwards admitted calls across the network to VM-B's target.

---

## 0. Windows host prerequisites

- Windows 10/11 Pro / Enterprise / Education (Home lacks Hyper-V - use WSL2 or VirtualBox instead).
- ~8 GB+ RAM and ~50 GB free disk (2 VMs x ~2 GB / ~20 GB).
- Download an Ubuntu Server 24.04 LTS ISO (e.g. to C:\iso\ubuntu-24.04-live-server-amd64.iso).
- Enable Hyper-V (admin PowerShell), then reboot:

    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

---

## 1. Virtual switch (once, admin PowerShell)

Use the built-in Default Switch (NAT: gives the VMs DHCP + internet for apt/clone) - simplest:

    Get-VMSwitch -Name "Default Switch"     # confirm it exists (it ships with Hyper-V)

(Alternative for stable LAN IPs: `New-VMSwitch -Name ElyonExt -NetAdapterName "Ethernet"` to bridge
to your physical NIC. The Default Switch's VM IPs can change on reboot - if you use it, re-read the
IPs each session, or assign static IPs via netplan inside the VM.)

---

## 2. Create the VMs (admin PowerShell; run the block once per VM with $vm = "VM-A" then "VM-B")

    $vm  = "VM-A"                                  # then re-run with "VM-B"
    $iso = "C:\iso\ubuntu-24.04-live-server-amd64.iso"
    New-VM -Name $vm -Generation 2 -MemoryStartupBytes 2GB `
           -NewVHDPath "C:\HyperV\$vm.vhdx" -NewVHDSizeBytes 20GB -SwitchName "Default Switch"
    Set-VMProcessor -VMName $vm -Count 2
    Set-VMMemory -VMName $vm -DynamicMemoryEnabled $true -MinimumBytes 1GB -MaximumBytes 4GB
    Add-VMDvdDrive -VMName $vm -Path $iso
    Set-VMFirmware -VMName $vm -EnableSecureBoot On -SecureBootTemplate "MicrosoftUEFICertificateAuthority"
    Set-VMFirmware -VMName $vm -FirstBootDevice (Get-VMDvdDrive -VMName $vm)
    Start-VM -Name $vm
    vmconnect.exe localhost $vm                    # opens the console; install Ubuntu

In the Ubuntu installer: accept defaults, enable "Install OpenSSH server", no extra snaps needed.
After install, in the VM firmware set the disk first (or remove the DVD) so it boots the OS:

    Set-VMDvdDrive -VMName $vm -Path $null
    Set-VMFirmware -VMName $vm -FirstBootDevice (Get-VMHardDiskDrive -VMName $vm)

---

## 3. Base setup - run on BOTH VMs (over SSH or the console)

    sudo apt-get update && sudo apt-get -y upgrade
    sudo apt-get -y install docker.io docker-compose-v2 git
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER && newgrp docker     # so docker runs without sudo
    sudo timedatectl set-ntp true                      # clocks must agree (freshness check)
    ip -4 addr show | grep -v 127.0.0.1 | grep inet    # NOTE this VM's IP
    git clone https://github.com/Elyon-Sol/Elyon-Sol.git && cd Elyon-Sol

Record the two IPs now and use them everywhere below:

    VMA_IP = <VM-A address>     # the gate
    VMB_IP = <VM-B address>     # the target + publisher

---

## 4. Generate config + certs (do this ONCE, on VM-A, then copy parts to VM-B)

    cd ~/Elyon-Sol
    python3 deploy/bootstrap_config.py                          # writes deploy/.env (gate key + anchor)
    python3 deploy/tls/gen_certs.py $VMA_IP $VMB_IP             # CA + leaves with both IPs in the SAN

Edit deploy/.env so the URLs point at VM-B over TLS (replace the compose service names):

    ELYON_TARGET_URL=https://$VMB_IP:9000/target
    ELYON_PUBLISHER_URL=https://$VMB_IP:9100/published_hashes.json

Copy to VM-B (it needs the certs, the CA, the public key + anchor - NOT the gate private key):

    scp deploy/.env deploy/tls/certs/ca.crt deploy/tls/certs/target.* deploy/tls/certs/publisher.* \
        user@$VMB_IP:~/Elyon-Sol/deploy/...                     # place under deploy/ and deploy/tls/certs/

(The gate private key in .env stays on VM-A. VM-B only needs ELYON_GATE_PUBLIC_KEY_HEX,
ELYON_GATE_KEY_ID, ELYON_PINNED_ROOT_SHA256 from .env, plus ca.crt + its own leaf certs.)

---

## 5. A two-host compose override (the committed compose is single-box)

The committed docker-compose.yml uses compose SERVICE NAMES (target:9000) that only resolve inside
one host's compose network. For two hosts, add a small override that points the gate's forward and
the target's identity at the REAL VM-B IP. Create deploy/docker-compose.hosts.yml on BOTH VMs:

    services:
      target:
        environment:
          ELYON_TARGET_URL: https://VMB_IP:9000/target          # <- put VM-B's IP
      gate:
        environment:
          ELYON_TLS_CA_BUNDLE: /certs/ca.crt

(Replace VMB_IP literally. The publisher is co-located with the target, so the target reaches it on
the VM-B compose network via the service name `publisher` - unchanged.)

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

Open the ports in the VM firewall if enabled (ufw): VM-A 8000; VM-B 9000 and 9100.

---

## 7. Run the live attack suite (from VM-A, the Windows host, or any box that can reach both)

    cd ~/Elyon-Sol
    ELYON_LIVE_GATE_URL=https://$VMA_IP:8000 \
    ELYON_LIVE_TARGET_URL=https://$VMB_IP:9000 \
    ELYON_LIVE_TARGET_ID=https://$VMB_IP:9000/target \
    ELYON_TLS_CA_BUNDLE=deploy/tls/certs/ca.crt \
    PYTHONPATH=. python3 EVIDENCE/proofs/attack_suite_live_runner.py

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

    curl --cacert deploy/tls/certs/ca.crt https://$VMB_IP:9100/published_hashes.json   # publisher serves the record
    curl --cacert deploy/tls/certs/ca.crt https://$VMB_IP:9000/received                # target up (count: 0)

## Troubleshooting

- TLS handshake / hostname errors: the IP you connect to must be in the cert SAN - regenerate with
  `gen_certs.py $VMA_IP $VMB_IP` if an IP changed (Default Switch IPs can change on reboot).
- Gate returns no envelope / fail-closed: check ELYON_SIGNING_KEY_HEX/ID are set on VM-A (in .env).
- Target REF_TARGET_NOT_CONFIGURED: VM-B is missing ELYON_GATE_PUBLIC_KEY_HEX / ELYON_GATE_KEY_ID /
  ELYON_PINNED_ROOT_SHA256 / ELYON_TARGET_URL, or the anchor does not match the served record.
- REF_VERIFY_SIGNATURE_EXPIRED on a valid call: the VM clocks disagree - confirm `timedatectl` NTP
  on both, or set a non-zero clock_skew.
- Binding mismatch on the positive control: ELYON_LIVE_TARGET_ID must EXACTLY equal the target's
  ELYON_TARGET_URL (scheme, IP, port, /target).
