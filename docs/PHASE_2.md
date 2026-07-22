# Phase 2: Installable and behavior-tested QACraft

Phase 2 turns QACraft from a repository of QA workflow specifications into a production-ready source-controlled skill distribution and deterministic evaluation toolkit.

## Phase 2.1 — Foundation: complete

Delivered:

- `qacraft list`
- `qacraft doctor`
- complete read-only installation planning
- adapter safety contract
- source-file planning for skills and shared policies
- automated CLI and repository tests

## Phase 2.2 — Installer and lifecycle: complete

Delivered:

- generic filesystem adapter;
- verified Codex project adapter;
- verified Claude Code project adapter;
- preview-first installation;
- explicit `--apply` before mutations;
- conflict, containment, and symbolic-link protection;
- canonical-source and installed-output SHA-256 verification;
- separate versioned adapter manifests;
- installation verification;
- safe update with stale-state checks and rollback;
- safe manifest-driven uninstall;
- preservation of unrelated project files and directories.

### Adapter layouts

| Adapter | Skill path | Shared policies | Manifest |
|---|---|---|---|
| `generic` | `skills/<skill>/SKILL.md` | `shared/` | `.qacraft-manifest.json` |
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/shared/` | `.agents/qacraft/manifest.json` |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/shared/` | `.claude/qacraft/manifest.json` |

The explicit destination is always the project or installation root. QACraft does not guess user-global paths, detect agents automatically, or modify agent configuration files.

Canonical QACraft files remain unchanged. Codex and Claude Code installed copies normalize `command`, `version`, and `status` into Agent Skills `metadata` while preserving the complete Markdown instruction body.

## Phase 2.3 — Behavior evaluations: complete

Delivered:

- local deterministic evaluator with no external model or network calls;
- versioned candidate and report JSON Schemas;
- exact rubrics for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`;
- source-grounding and hallucination-control checks;
- timezone-aware approval and evidence binding;
- evidence reference, integrity, and privacy checks;
- ordered verdict and release-blocker checks;
- permission, secret, personal-data, external-write, cleanup, and output-contract checks;
- machine-readable JSON reports and deterministic exit codes;
- passing example and regression tests for every rubric and failure category.

The evaluator returns:

- exit code `0` when all seven checks pass;
- exit code `1` when the candidate is valid but one or more policy checks fail;
- exit code `2` when the input or rubric cannot be evaluated.

## Phase 2.4 — Documentation and release: complete for 1.1.0

Delivered:

- production quickstart in `README.md`;
- full installation and lifecycle guide;
- compatibility matrix;
- deterministic evaluation guide;
- isolated end-to-end demo;
- explicit production-readiness scope and boundaries;
- changelog and release checklist;
- semantic version and project metadata;
- deterministic `qacraft release-check` command;
- strengthened agent, Claude Code, contribution, and security guidance;
- lean pull-request-only GitHub Actions validation.

GitHub Pages automatic deployment is intentionally not included. The generated static documentation is committed and can be served locally or published manually without adding recurring Actions usage.

## Release acceptance

QACraft 1.1.0 must satisfy:

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/qacraft.py release-check
```

The release checker validates:

- required release files and versioned changelog;
- complete README lifecycle guidance;
- one-job PR/manual-only CI;
- exact five-skill rubric coverage;
- rubric gates, decisions, and outputs against canonical `SKILL.md`;
- the published passing evaluation example;
- package metadata and release links.

## Production-ready scope

QACraft 1.1.0 is production-ready for:

- source-controlled QA skill distribution;
- explicit project installation and lifecycle management;
- checksummed manifest ownership;
- deterministic structured-report policy evaluation;
- local documentation, validation, and release auditing.

It is not a runtime permission system, autonomous production QA executor, approval identity provider, or evidence-authenticity service. Those controls remain the responsibility of the adopting runtime and external integrations.

## Phase 2 completion decision

Phase 2 is complete when the 1.1.0 release pull request passes its single validation job, is merged into `main`, and the release check passes on the merged content. Issue #4 can then be closed as completed.
