# Security Policy

## Supported use

This repository is a local departmental pilot. It is not a hardened public service and has no production hosting or support commitment. Use synthetic data for demonstrations. Before any institutional use, complete a security, privacy, authorization, and operational review with the institution.

## Reporting a vulnerability

Do not post exploitable details, credentials, personal information, or confidential institutional records in a public issue or pull request. No private security contact address has been supplied for this project. The repository owner should establish a monitored private reporting channel before publishing the repository broadly. Until then, do not include sensitive details in public submissions.

There is no stated response-time or coordinated-disclosure commitment.

## Known security boundaries

- The optional MCP server accepts role/scope values as tool arguments and does not authenticate its caller. Its SSE listener rejects non-loopback bind addresses, but this does not authenticate local callers. Use only with synthetic data; do not connect it to real appraisal data or expose it to untrusted clients.
- The default application binds to loopback. Network access requires TLS, `COOKIE_SECURE=1`, restricted filesystem/database access, institution-managed identity controls, and deployment testing.
- SQLite databases, uploaded evidence, and backups are not encrypted by the application. Protect them as confidential data.
- The application's hash-linked audit trail is not tamper-proof against an actor with full database access.
- The application has not been independently penetration-tested or approved for a production environment.

See [the architecture notes](./docs/ARCHITECTURE.md) and [operations guidance](./docs/OPERATIONS.md) for additional limitations.
