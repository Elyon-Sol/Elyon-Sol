# Licensing — Elyon-Sol

Elyon-Sol uses an **open-core** model.

## The open core (this repository)

The core — the admission gate, admissibility envelope, target-side verifier, the
ext-authz sidecar, and supporting modules in this repository — is licensed under the
**GNU Affero General Public License v3.0 (AGPL-3.0)**. See `LICENSE`.

What AGPL-3.0 means for you, in plain terms:
- You may use, run, study, modify, and redistribute the core, for free.
- If you modify it and either distribute it OR offer its functionality to others over a
  network (SaaS), you must make your modified source available under AGPL-3.0.
- If you do not want those obligations — for example, you want to embed the core in a
  closed-source product or service — you need a commercial license (see `COMMERCIAL.md`).

ELYON-SOL is a trademark of Justin Laporte. The license covers the code; it does not grant
rights to the name or marks.

## The closed layer (sold separately, not in this repo)

The administration and tooling SDK — management, operations, and related tooling — is
**proprietary and not open source.** It is offered commercially and is not covered by
AGPL. It interoperates with the open core strictly across the core's public API
(HTTP / JSON-RPC); it does not incorporate AGPL-licensed code, and is therefore an
independent work.

## Dual licensing of the core

Because the copyright in the core is held by a single author, the core is available under
EITHER:
1. AGPL-3.0 (free, with the obligations above), or
2. a commercial license (paid, without the copyleft obligations).

Pick whichever fits your use. Commercial terms: `COMMERCIAL.md`.

## Why this model

The open core is meant to be inspected, adopted, and attacked — a governance substrate has
to be verifiable to be trusted. The closed admin SDK and commercial core licenses fund that
work. Contributions are welcome under the terms in `CONTRIBUTING.md`.
