# Security Policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose credentials, customer data, cross-tenant access, authentication bypass, arbitrary command execution, unsafe filesystem writes, manifest bypass, or unsafe production actions.

Use GitHub's private vulnerability-reporting or security-advisory mechanism for this repository. Include:

- affected QACraft version and commit;
- operating system and Python version;
- adapter and destination layout when relevant;
- minimal reproduction steps using synthetic data;
- expected and actual safety behavior;
- whether any real secret, personal data, customer system, or production environment was involved.

Do not attach real credentials, private customer URLs, access tokens, or unredacted evidence.

## Supported versions

Security fixes are applied to the current release line. Users should reproduce issues against the latest `main` or latest tagged release before reporting, unless doing so would create additional risk.

## Security-relevant scope

Security-relevant components include:

- source and destination path containment;
- symbolic-link detection;
- installer conflict and exclusive-file creation behavior;
- manifest creation, parsing, path validation, and checksum verification;
- update race checks and rollback;
- uninstall ownership and modified-file protection;
- canonical-to-agent `SKILL.md` transformation;
- schema and rubric parsing;
- behavior-evaluation source, evidence, approval, verdict, output, and safety checks;
- generator escaping and local HTML validation;
- agent instructions and shared security policies;
- evidence storage, redaction, approval, publication, and external integrations implemented by adopters.

## Deliberate boundaries

QACraft does not provide a runtime sandbox or authenticate approvals and evidence. Skill documents and structured evaluation cannot enforce:

- filesystem, command, network, repository, secret, tenant, or production permissions;
- external-system identity and authorisation;
- evidence authenticity;
- customer-data isolation;
- safe ticket, deployment, repository, or publication writes.

Adopters must implement the runtime controls described in `shared/security-boundaries.md`, use least privilege, and keep external writes version-bound, approved, idempotent, and auditable.

## Safe reproduction

Use temporary directories, synthetic candidate reports, and local files. The repository test suite and `docs/DEMO.md` demonstrate the supported isolated workflow without network, customer, or production access.
