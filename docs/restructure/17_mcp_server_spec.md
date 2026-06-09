# 17 - Real MCP server: the admissibility gate on tool execution

Repo path: docs/restructure/17_mcp_server_spec.md. Increment VL-077 (B4, artifact 13 Phase B).
Promotes the in-process wedge demo (`EVIDENCE/proofs/wedge_agent_toolcall_001_runner.py`,
VL-066) to a real MCP server: a JSON-RPC 2.0 server speaking the MCP `initialize` handshake and
`tools/call` over real stdio transport, with the production admissibility gate on tool
execution.

## 1. Purpose and scope

The wedge demo proved the executor-side wedge property (a side-effecting tool fires ONLY for a
call carrying a valid, bound, current, fresh admissibility envelope) but states its own fidelity
gap: "it does NOT implement the full MCP protocol (no initialize handshake, capability
negotiation, or stdio transport)." B4 closes that gap. The acceptance (artifact 13 B4): "a
runnable MCP server refusing un-admitted / replayed / drifted / stale tool calls."

In scope (VL-077):
- A runnable MCP server (`IMPLEMENTATION/mcp_server.py`) over stdio: the `initialize` /
  `notifications/initialized` handshake, `tools/list`, and `tools/call`, as JSON-RPC 2.0.
- The executor-side admissibility gate on `tools/call`, reusing the production `verify_envelope`
  (signature -> reassert/currency -> binding -> freshness) and the VL-076 `ReplayCache` seam
  (`InMemoryReplayCache`) for exactly-once. No gate logic is re-implemented.
- The tool fires exactly once for the admitted call; un-attested / rebound (different tool or
  args) / drifted / stale / replayed calls are refused and the tool does NOT fire.

Out of scope (named, not built):
- Real cross-host TLS transport (the G5 floor; `g5_multiprocess_tls_001_runner.py` and Phase C).
  stdio is a real transport and a real process boundary, but it is local.
- The MCP server is NOT the gate. Admission is still performed by `pep.py` (the client/agent
  calls the gate to obtain a signed envelope, then calls the tool with it). This server is the
  EXECUTOR that verifies.
- HTTP/SSE MCP transport, auth, and full capability negotiation beyond tools.

## 2. The envelope on the wire (MCP-idiomatic)

The admissibility envelope rides in the `tools/call` params `_meta` block, under the key
`elyon-sol/envelope` (MCP reserves `_meta` for out-of-band metadata, so the tool `arguments`
stay byte-clean - the parallel of the HTTP `X-Elyon-Sol-Envelope` header the gate pushes). An
absent / unparseable envelope is treated as un-attested (`REF_VERIFY_ENVELOPE_ABSENT`).

The binding: the executor reconstructs the expected interaction from the ACTUAL call (the tool
`name` and a canonical digest of `arguments`, carried in canon-11.1 `context`, with the fixed
AP/OP authority/operation sets), exactly as the admitting client did, then calls
`verify_envelope`. A rebind (envelope admitted for tool A, or args A, presented for B) fails the
binding check (`REF_VERIFY_BINDING_MISMATCH`).

## 3. Protocol and refusal mapping

- `initialize` -> a CallResult with `protocolVersion`, `capabilities.tools`, and `serverInfo`.
  The server tracks an initialized flag; `tools/list` and `tools/call` before the handshake
  return a JSON-RPC error (`-32002`, server not initialized) and never touch a tool.
- `tools/call` is a SUCCESSFUL protocol exchange whose RESULT carries the verdict: on admit, a
  CallToolResult with `isError=false` and `_meta["elyon-sol/executed"]=true`; on refusal,
  `isError=true`, `_meta["elyon-sol/executed"]=false`, and `_meta["elyon-sol/reason"]=<REF_*>`.
  (A refusal is a tool-level outcome, not a protocol error - the MCP-faithful shape.) The tool
  side effect occurs only on the admit branch.
- Parse errors / unknown methods map to JSON-RPC errors (`-32700`, `-32601`).

The refusal vocabulary is the production `REF_VERIFY_*` set verify_envelope returns, surfaced
unchanged: `REF_VERIFY_ENVELOPE_ABSENT` (un-attested), `REF_VERIFY_BINDING_MISMATCH` (rebound),
`REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED` (drifted), `REF_VERIFY_SIGNATURE_EXPIRED` (stale),
`REF_VERIFY_REPLAY` (replayed). The server adds no new reason code.

## 4. Fail-closed (canon section 9)

Every undecidable path refuses and leaves the tool un-fired: a missing/anchor-mismatched
published record, an unconfigured server (no pinned key / record), a malformed envelope, a
`verify_envelope` non-accept, or a replay-cache claim that does not return a fresh honor. The
tool executes only on a positive `accepted` verdict followed by a fresh replay claim.

## 5. No new canonical invariant (canon section 14)

The server implements no canon section; it consumes `verify_envelope` (the target-side
revalidation step, canon section 13) and the replay seam. It changes WHERE the gate runs (a real
MCP surface) not WHAT it decides. No canon / evaluator / MANIFEST / envelope contract change.

## 6. Build-then-wire scope

`IMPLEMENTATION/mcp_server.py` is a NEW module with no caller on the default `pep.py` path;
evaluator.py / pep.py / verifier.py / envelope.py / reference_target.py / published_hashes.json
are byte-unchanged (no `evaluator_sha256` roll). The server is the first real consumer of the
VL-076 `ReplayCache` seam, giving that seam a live caller without touching `reference_target.py`.

## 7. Honest ceiling

This is a real MCP server over a real (stdio) transport and a real process boundary, but local:
it does not establish cross-host TLS, real certificates, or trust bootstrap (the G5 floor / Phase
C). It demonstrates that the wedge property holds on a genuine MCP `tools/call` surface with the
real handshake; it does not certify the property against a real external attacker on a real
network. That remains the author-arranged finish line.

## 8. Acceptance (VL-077)

- `TESTS/adversarial/test_mcp_server.py`: the initialize handshake; tools/list; the admitted
  call fires the tool once; un-attested / rebound-tool / rebound-args / drifted / stale /
  replayed calls refused with the named reason and the tool un-fired; tools/call before
  initialize is a protocol error; the tool fires exactly once across the whole matrix.
- `EVIDENCE/proofs/mcp_server_001_runner.py`: a real subprocess speaking JSON-RPC over stdio -
  the handshake, the admitted-fires / un-attested / replay / rebind cases against a live server
  process, plus drifted (a re-published record under a moved anchor) and stale (a short-window
  admission) against fresh server processes. Exit 0 iff the tool fires exactly once and every
  adversarial call is refused with the expected reason.
- Full suite green; the default path byte-unchanged.
