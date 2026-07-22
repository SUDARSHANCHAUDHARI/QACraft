# Changelog

All notable QACraft changes are documented here.

## 1.1.0 — 2026-07-22

### Added

- Dependency-free `qacraft` CLI for skill discovery and repository health checks.
- Preview-first install, verify, update, and uninstall lifecycle.
- Generic, Codex, and Claude Code installation adapters.
- Versioned manifests, SHA-256 verification, conflict protection, rollback, and safe cleanup.
- Deterministic behavior evaluation for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`.
- Candidate and evaluation-report schemas, versioned rubrics, example reports, and regression tests.
- Production installation, compatibility, demo, and release documentation.

### Safety

- No silent overwrite or force-delete mode.
- No automatic user-global installation or agent detection.
- No network, customer, production, or external-system access from the installer or evaluator.
- Agent adapters use independent manifests and preserve unrelated project files.
- Evaluations inspect supplied structured reports; they do not prove evidence authenticity or enforce runtime permissions.

## 1.0.0 — 2026-07-21

- Added 25 QA workflow skills.
- Added self-contained HTML documentation for every skill.
- Added shared evidence, security, approval, data, result, publication, and release policies.
- Added JSON Schemas for run context, approvals, events, evidence, findings, decisions, cleanup, and reports.
- Added generation, serving, validation, tests, and GitHub Actions.
