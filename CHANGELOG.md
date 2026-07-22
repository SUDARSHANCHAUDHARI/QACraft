# Changelog

All notable QACraft changes are documented here.

## 1.4.0 — 2026-07-22

### Added

- Deterministic rubrics for `/test-plan`, `/regression-scope`, `/customer-issue-repro`, `/api-qa`, and `/staged-rollout-check`.
- Candidate-schema support for all ten evaluated skills.
- Passing examples for every Phase 3.4 rubric.
- Targeted negative fixtures for output contracts, source grounding, approval gates, safety boundaries, and verdict discipline.
- `evaluations/fixtures.json` as the authoritative fixture expectation catalog.
- Release validation for fixture existence, expected pass/fail outcomes, and declared failed checks.
- Regression tests for conditional planning risk, customer uncertainty, rollout decisions, schema/rubric alignment, and installed-artifact fixture coverage.

### Safety

- Evaluation remains local, deterministic, read-only, dependency-free, and network-free.
- Rubrics remain bound to canonical approval gates, decisions, and output contracts.
- Planning and scoping decisions are not treated as proof of product execution success.
- `NOT REPRODUCED` requires visible uncertainty instead of dismissing a customer report.
- Rollout `CONTINUE` cannot hide required failed results.
- Published negative fixtures contain synthetic data only.

## 1.3.0 — 2026-07-22

### Added

- Verified GitHub Copilot project adapter using `.github/skills/<skill>/SKILL.md`.
- Verified Gemini CLI workspace adapter using `.gemini/skills/<skill>/SKILL.md`.
- Verified OpenCode project adapter using `.opencode/skills/<skill>/SKILL.md`.
- Independent manifests and shared-policy directories for every new adapter.
- Install, verify, update, uninstall, conflict, frontmatter, and multi-adapter coexistence tests.
- Official documentation references for every newly verified discovery path.

### Safety

- No automatic agent detection or user-global installation.
- No agent configuration-file modification.
- Native project paths are used even where compatible alias paths also exist.
- Cursor and Windsurf remain unverified until equivalent official Agent Skills discovery paths are documented.
- Duplicate skill names across multiple adapter paths are not recommended without reviewing agent precedence behavior.

## 1.2.0 — 2026-07-22

### Added

- Editable source-checkout installation with `python -m pip install --no-deps -e .`.
- `qacraft` console command and `python -m qacraft` module entry point.
- Self-contained wheel and source-distribution build recipes.
- Explicit allowlisted copying of canonical runtime assets into `qacraft/bundle` during wheel builds.
- Archive inspection for required skills, policies, schemas, rubrics, documentation, runtime modules, and build files.
- Isolated wheel and source-distribution installation tests.
- Installed-artifact smoke coverage for doctor, evaluation, release checks, and the Codex install/verify/uninstall lifecycle.

### Safety

- Distribution builds reject symbolic links and paths outside the repository.
- Generated bundles are created only in temporary build directories and are not committed as duplicate source.
- Cache files, bytecode, VCS metadata, virtual environments, build output, and egg metadata are excluded from bundles.
- Incomplete installed artifacts fail with an explicit missing-assets report.
- No package-index publication is claimed or performed.

## 1.1.0 — 2026-07-22

### Added

- Dependency-free `qacraft` CLI for skill discovery and repository health checks.
- Preview-first install, verify, update, and uninstall lifecycle.
- Generic, Codex, and Claude Code installation adapters.
- Versioned manifests, SHA-256 verification, conflict protection, rollback, and safe cleanup.
- Deterministic behavior evaluation for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`.
- Candidate and evaluation-report schemas, versioned rubrics, example reports, and regression tests.
- Deterministic `release-check` covering release files, metadata, lean CI, rubric coverage, rubric-to-skill binding, and the published example.
- Production installation, compatibility, production-readiness, demo, and release documentation.

### Safety

- No silent overwrite or force-delete mode.
- No automatic user-global installation or agent detection.
- No network, customer, production, or external-system access from the installer or evaluator.
- Agent adapters use independent manifests and preserve unrelated project files.
- Evaluations inspect supplied structured reports; they do not prove evidence authenticity or enforce runtime permissions.
- Release validation fails when behavior rubrics drift from canonical skill gates, decisions, or output contracts.

## 1.0.0 — 2026-07-21

- Added 25 QA workflow skills.
- Added self-contained HTML documentation for every skill.
- Added shared evidence, security, approval, data, result, publication, and release policies.
- Added JSON Schemas for run context, approvals, events, evidence, findings, decisions, cleanup, and reports.
- Added generation, serving, validation, tests, and GitHub Actions.
