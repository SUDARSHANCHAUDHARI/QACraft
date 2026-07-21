# Security Policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose credentials, customer data, cross-tenant access, authentication bypass, arbitrary command execution, or unsafe production actions.

Use the private security-reporting mechanism of the repository host.

## Scope

Security-relevant components include:

- generator escaping and path handling,
- schemas and validation,
- agent instructions,
- connector and runtime adapters,
- evidence storage and redaction,
- approval and publication integrations.

## Safety note

The skill documents do not enforce permissions. Adopters must implement the runtime controls described in `shared/security-boundaries.md`.
