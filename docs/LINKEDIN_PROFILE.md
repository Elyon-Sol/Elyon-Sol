# LinkedIn profile — Justin C. LaPorte (curated for Elyon-Sol)

Positioning: **Founder + independent researcher.** Voice: **builder / founder energy.**
Optimized to **attract researchers/collaborators** and **build credibility** in AI governance & security.

- **Name:** Justin C. LaPorte
- **Location (LinkedIn):** Chaplin, CT — set the field as "Hartford, Connecticut, United States" for reach
- **Contact:** jlaporte06374@gmail.com · 203-850-4354 · project intake: security@elyon-sol.io
- **ORCID:** https://orcid.org/0009-0008-3785-3089

---

## Headline  (220 char max — pick one)

**A. Veteran-to-frontier (recommended — leads with credibility)**
Founder, Elyon-Sol · 25 years in network & security engineering, now building a verifiable oversight layer for AI actions — deterministic, fail-closed admission control from a formal spec. AI governance · applied crypto · formal methods.

**B. Mission-forward**
Founder & independent researcher, Elyon-Sol — pre-execution admission control for AI actions: formal spec, cryptographic enforcement, human-in-the-loop oversight. Built on two decades of security & network engineering.

**C. Punchy**
Founder, Elyon-Sol · Security & network engineer (25 yrs) building the "is this AI action authorized?" boundary · AI governance · cryptography · formal methods

---

## About

For 25 years I built and secured the plumbing other people's businesses ran on — firewalls, IDS, Linux server fleets, VPN/PKI, wireless and WAN networks, data-center migrations. The throughline of that work was always the same question: *should this connection, this action, this request actually be allowed?* I'm now working on that question for the thing that's about to need it most — software that acts on the world on its own.

**Elyon-Sol is a deterministic, fail-closed admission gate for actions.** Given a request and a signed, hash-pinned policy, it returns ELIGIBLE only when the caller's authority and the operation actually satisfy that policy — and it refuses everything else, before the action runs. On approval it emits a cryptographically signed, single-use record bound to that exact action; on any doubt, it fails closed. On top of that sits a human-oversight layer: high-impact actions are held until a person signs off with a separate key, verified and audited.

I work in the open about what is and isn't proven. The canonical model is formally specified (v0.9.8.4) and published; every claim is traceable to a spec clause, code, a test, and a verification-ledger entry; and the honest limits are stated as plainly as the results. The current build passes its full adversarial suite (512/512) and the evidence is published on Zenodo — and I'm equally clear that it has **not** yet faced an external adversary on a live surface. Closing that gap is the point of the open challenge below.

**I'm looking to connect with:**
- Security researchers with auth / protocol / cryptography backgrounds who want to try to break it — credit, authorship, and a founding red-team seat, not a bounty.
- People working on AI governance, agent safety, and oversight infrastructure.
- Collaborators, design partners, and anyone who thinks a verifiable "is this action allowed?" boundary is worth getting right.

Try to break it, or just say hello: **security@elyon-sol.io** · site: https://elyon-sol.io · evidence: DOI 10.5281/zenodo.21107731

---

## Experience

**Founder & Independent Researcher — Elyon-Sol**
[Start month/year] – Present · Remote (Connecticut, US)
- Designed and built Elyon-Sol: a deterministic, fail-closed HTTP admission gate for AI/agent actions, derived from a formal admissibility specification (three canonical invariants — authority, coverage, continuity).
- Implemented cryptographic enforcement end to end: Ed25519-signed admissibility envelopes over canonical JSON, single-use replay defense, freshness/clock-skew handling, and a signed key-record trust chain — building directly on two decades of hands-on VPN/PKI and certificate work.
- Built a human-in-the-loop governance layer: high-impact actions are held (PENDING_APPROVAL) until a human approver signs a grant with a separate key — verified, single-use, audited, with separation of duties enforced by the signed record.
- Shipped deployment surfaces: an OPA/Envoy ext-authz sidecar, mutual-TLS non-bypass proof, shared-store hardening for horizontal scale, and an MCP server integration.
- Established a rigorous evidence practice: a public verification ledger, spec-to-code traceability, a 512-test adversarial suite, and honest-scope reporting; published six revisions of enforcement evidence on Zenodo (open access).
- Ran independent multi-model white-box reviews of the governance core and hardened against every finding.

**Senior Network & Security Engineer / Owner — Justin Laporte (independent consultancy)**
January 2010 – Present · Eastern Connecticut
- Design, implement, and maintain Cisco-centric infrastructure for SMB and enterprise clients: ASA firewalls, Catalyst switching, Aironet/Meraki wireless, and SIP/H.323 voice via Call Manager.
- Cisco Meraki wireless network designs and implementations; ongoing multi-platform IT support across OS, server, and network stacks.
- Security-first delivery: firewall policy, segmentation, disaster recovery, and as-built documentation.

**Senior Consultant / Management Team — Stenhouse Consulting**
May 2015 – November 2018 · Providence, RI
- Delivered daily client technology support across disaster recovery, wireless, server infrastructure, and end-user design engineering for large technical initiatives.
- Contributed to management strategy — personnel performance, policy/procedure, and client-relationship and billing analysis to raise productivity.
- Led small-to-mid enterprise network design and implementation.

**System Administrator / TSC Level III — SAP**
January 2006 – January 2010 · Cambridge, MA
- Installed, configured, and maintained Linux server fleets running IBM Apache and J2EE/JBOSS application stacks fronting the SAP CRM web application; automated the Java/JBOSS stack and uptime/availability reporting.
- Managed multi-vendor site-to-site VPNs (Cisco, Checkpoint, Nortel) with CA-based and pre-shared-key configs across 3DES/SHA/MD5 and 128/168-bit — hands-on applied cryptography and key management.
- Ran load-balanced certificate VIPs on Cisco CSS 11500; administered L1–L3 data-center networking (Catalyst 6500, FWSM ACLs, VLANs); BASH/Perl automation.

**Network Architect — The Apex Technology Group**
January 2001 – June 2005 · Cranston, RI
- Designed and installed voice and data networks for clients from small municipalities to large financial institutions.
- Delivered assessments and recommendations across networking, storage, security, and identity/account administration.
- Led the development of an IDS and security initiative for the client base.

**Selected projects**
- WaterFire Providence — Cisco/Meraki wireless engineered for 1,000+ concurrent connections, segmented from corporate networks, with a captive-portal guest-authentication flow.
- SRM e-commerce data-center migration at MIT (Cambridge, MA) — relocated 130 servers, network electronics, email, and security under client SLA.
- Merger/acquisition IT lead — relocated two data centers, managed vendors, and produced as-built documentation.
- Multi-state VOIP Frame-Relay network (CT/MA/NH) with QoS traffic prioritization; 150 WAN-circuit rollout for the Fleet Bank/Boston ATM network across MA/NY/CT/RI.

---

## Certifications
- Linux Professional Institute Certified (LPIC-1)
- Cisco Certified Network Associate (CCNA)
- Cisco Certified Design Associate (CCDA)
- Microsoft Certified Professional (MCP)
- 3Com NBX Voice Certified · Cisco VOIP Essentials

---

## Education
- Three Rivers Community College — Mohegan Campus (coursework)
- Plainfield High School — graduate
- Ongoing professional training: Cisco, Microsoft, 3Com, LPIC · mentored under the URI MIS Director · PC Systems Technician internship, Mountain Computer Support

---

## Featured  (add these as links/media)
- **Elyon-Sol — the project & open challenge** → https://elyon-sol.io
- **Enforcement Evidence Addendum (Rev 6), Zenodo** → https://doi.org/10.5281/zenodo.21107731
- **ORCID** → https://orcid.org/0009-0008-3785-3089
- (optional) a pinned post announcing the red-team challenge (draft below)

---

## Skills  (reorder by what you want surfaced)
**AI & security research:** AI Governance · Applied Cryptography (Ed25519, PKI, IPsec/VPN) · Access Control · Formal Specification & Verification · Adversarial Testing / Red Teaming · Threat Modeling · Protocol Design · Technical Writing
**Infrastructure & networks:** Firewalls (Cisco ASA, Meraki MX, SonicWall, Checkpoint, SOPHOS UTM) · IDS/IPS (SNORT) · Cisco Routing & Switching (Catalyst, EIGRP/OSPF) · Meraki Wireless · Linux (Debian/SUSE, LAMP/Apache) · BASH / Perl / PowerShell automation · Active Directory / DNS / GPO / IIS · Virtualization (VMware / Hyper-V / Xen) · Windows Server · Wireshark / SolarWinds · Network Design · Disaster Recovery

---

## Starter posts (to seed the profile)

### Post 1 — the open challenge (pin this)
I built a gate that decides whether an action is allowed to happen — before it happens — and refuses anything without a valid, signed, single-use permission bound to that exact action.

I think you can't make it act on something it shouldn't. I'd like you to try.

It's live, it's a real formal protocol (not a web app), and a confirmed break is a real result: permanent named credit in the public record, co-authorship on the next published evidence, a CVE where it applies, and a founding seat on the red team. No cash bounty — credit and ownership, for people who want to help build a verifiable oversight layer for AI actions.

Private, invite-only. If you've got an auth / protocol / crypto background, email security@elyon-sol.io.
Evidence + details: https://elyon-sol.io · DOI 10.5281/zenodo.21107731
#AISafety #AIGovernance #Security #Cryptography #RedTeam

### Post 2 — thought leadership (the idea)
Most "AI safety" controls ask whether an output is good. I'm interested in a narrower, more mechanical question: was this *action* authorized to happen at all?

After 25 years building firewalls, IDS, and PKI for other people's networks, that question feels very familiar — it's admission control, moved up the stack to autonomous software. Elyon-Sol answers it before the action runs: deterministically, and fail-closed. It guarantees an action is authorized and attested; it makes no claim about whether an authorized action is *wise*. That boundary is the whole point.

Full spec + published evidence: DOI 10.5281/zenodo.21107731. It has not yet met an external adversary on a live surface — that's the next milestone, and it's open. https://elyon-sol.io
#AIGovernance #FormalMethods #Security

---

## Notes on curation
- **Your edge:** the 25-year infrastructure-security background is a credibility multiplier for a security protocol — lead with it. The SAP VPN/PKI/cert work and the Apex IDS initiative are the strongest bridges to Elyon-Sol; drawn explicitly above.
- **Consistency:** keep LinkedIn language matched to the site and Zenodo — same claims, same honest-scope caveats.
- **One CTA everywhere:** security@elyon-sol.io.
- Site URL (https://elyon-sol.io), the Rev 6 DOI (10.5281/zenodo.21107731), and your ORCID (0009-0008-3785-3089) are filled in. Still to add: the Elyon-Sol **start date**, and set your LinkedIn location to a metro ("Hartford, Connecticut, United States") for reach.
- Add a professional headshot + the Gargoyle banner (site/assets/linkedin_banner.png).
