# MCP GitHub Discussion post (draft)

Post under **Ideas** or **Show and tell** at https://github.com/orgs/modelcontextprotocol/discussions

---

**Title:** Pattern: pre-execution admission control for `tools/call` — fail-closed, args-bound, elicitation-based human approval

**The problem**

As MCP tools become the default action surface for agents, "which tool, with which arguments, may run right now?" is increasingly a security question, not just a UX one. Allow/block lists and per-server config help, but they're coarse, mutable, and hard to audit — and they don't give you a tamper-evident record of *why* a call was permitted, or a clean way to require a human for the dangerous ones.

**A pattern I've been building**

Pre-execution admission control for `tools/call`: before a tool executes, the call is checked against a signed, hash-pinned policy and either admitted or refused (fail-closed).

- **Policy is pinned.** A manifest (version + SHA-256) declares which authorities/scopes may invoke which tools, and which tools are "high-impact." The decision is a function of named, hashed inputs — reproducible and auditable.
- **The decision is bound to the exact call.** The admission record is content-hashed over the tool name + canonical-JSON of the arguments (plus policy hashes), so a decision minted for args X can't be replayed or rebound to args Y — a direct answer to tool-poisoning / argument-tampering.
- **High-impact tools require a human — via elicitation.** Instead of a bespoke channel, a high-impact call is *held* and the server emits an **elicitation** request; a human approves; the approval is a single-use, separately-keyed signed grant bound to that exact decision; then the tool runs exactly once. This fits the 2026 rule that elicitation only happens during an active client request.
- **Fail-closed + audited.** Unknown/malformed calls are refused; every held-and-forwarded high-impact call reconciles against an issuance log (a forward without a recorded grant is a caught violation).

Authority can derive from the caller's OAuth 2.1 scopes (MCP servers as resource servers), so "who may call what" rides existing identity.

**Why I'm posting**

I have a working reference (a JSON-RPC MCP server that runs this gate on `tools/call`) and a formal spec, and I'd like the community's read on:

1. Does a **pre-execution admission / approval-binding pattern** belong as a documented pattern (or an SEP), or do existing auth + elicitation guidance already cover it?
2. Prior art I should build on rather than reinvent?
3. Gotchas with a **gateway/proxy** placement — it has to see the tool-call bytes inline to bind them. How are people handling inline interception cleanly?
4. Anything about the **elicitation-during-active-request** constraint that breaks a hold-then-approve flow at scale?

Honest scope: this is white-box / in-repo work — no external adversarial validation yet — and the guarantees are deployment-gated (the gate must be inline). Full construction + threat model, open access: https://doi.org/10.5281/zenodo.21147717

Happy to share the reference implementation if useful — mostly looking for where this breaks or duplicates existing work.
