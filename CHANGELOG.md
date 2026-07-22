# Changelog

All notable QACraft changes are documented in this file.

## [1.1.0] - 2026-07-22

### Added

- Preview-first generic filesystem installer.
- Verified Codex project adapter using `.agents/skills/<skill>/`.
- Verified Claude Code project adapter using `.claude/skills/<skill>/`.
- Independent adapter manifests with canonical-source and installed-output SHA-256 records.
- Safe installation verification, update rollback, and manifest-driven uninstall.
- Standards-compliant installed `SKILL.md` frontmatter normalization for agent adapters.
- Deterministic behavior evaluation for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`.
- Versioned evaluation candidate and report JSON Schemas.
- Approval, source-grounding, evidence, verdict, safety, cleanup, and output-contract checks.
- Installation, compatibility, evaluation, end-to-end demo, and production-readiness documentation.
- Deterministic `qacraft release-check` command.

### Changed

- QACraft now provides an installable and behavior-tested QA skill platform rather than specifications alone.
- GitHub Actions validation is limited to one Python 3.12 job per pull request, with no automatic post-merge run.
- Canonical QACraft skill files remain unchanged while Codex and Claude Code installed copies use normalized Agent Skills metadata.

### Security and safety

- Refuses silent overwrite, force deletion, unsafe paths, symbolic-link redirection, modified managed files, and stale preview state.
- Preserves unrelated project files and directories.
- Keeps behavior evaluation local, deterministic, read-only, and free of external model or network calls.

## [1.0.0] - 2026-07-21

### Added

- Initial catalog of 25 detailed QA workflow specifications.
- Self-contained HTML documentation for every skill.
- Shared evidence, security, approval, data, result, publication, and release policies.
- JSON Schemas for run context, approvals, events, evidence, findings, decisions, cleanup, and reports.
- Documentation generation, local serving, repository validation, tests, and GitHub Actions.
