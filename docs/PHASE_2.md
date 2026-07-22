# Phase 2 development plan

Phase 2 turns QACraft from a repository of QA workflow specifications into an installable and behavior-tested platform.

## Phase 2.1 — Foundation

Completed:

- `scripts/qacraft.py list`
- `scripts/qacraft.py doctor`
- read-only installation planning
- adapter safety contract
- complete source-file planning
- automated CLI tests

## Phase 2.2 — Installer and lifecycle

Completed capabilities:

- generic filesystem adapter
- verified Codex project adapter
- verified Claude Code project adapter
- preview-first installation
- explicit `--apply` before mutations
- conflict and symbolic-link protection
- SHA-256 verification
- separate versioned manifests
- install verification
- safe update with rollback
- safe manifest-driven uninstall
- preservation of unrelated project files and directories

### Adapter layouts

| Adapter | Skill path | Shared policies | Manifest |
|---|---|---|---|
| `generic` | `skills/<skill>/SKILL.md` | `shared/` | `.qacraft-manifest.json` |
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/shared/` | `.agents/qacraft/manifest.json` |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/shared/` | `.claude/qacraft/manifest.json` |

The explicit destination is always the project or installation root. QACraft does not guess user-global paths, detect agents automatically, or modify agent configuration files.

Canonical QACraft files remain unchanged. Codex and Claude Code installed copies normalize `command`, `version`, and `status` into the standard Agent Skills `metadata` mapping while preserving the complete Markdown instruction body. The manifest records both canonical-source and installed-output checksums.

### Lifecycle commands

```bash
python3 scripts/qacraft.py plan-install feature-qa bug-report \
  --agent codex \
  --destination ./my-project

python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination ./my-project \
  --apply

python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination ./my-project

python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination ./my-project \
  --apply

python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination ./my-project \
  --apply
```

Replace `codex` with `claude-code` or `generic` as required.

## Phase 2.3 — Behavior evaluations

Completed capabilities:

- local deterministic evaluator with no external model or network calls
- versioned candidate and report JSON Schemas
- exact rubrics for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`
- source-grounding and hallucination-control checks
- version-bound approval-gate checks
- evidence reference, integrity, and privacy checks
- ordered verdict and release-blocker checks
- permission, secret, personal-data, external-write, and cleanup safety checks
- skill-specific output-contract checks
- machine-readable JSON reports and deterministic exit codes
- passing example and regression tests for every rubric and failure category

### Evaluation commands

```bash
python3 scripts/qacraft.py eval-list

python3 scripts/qacraft.py evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

The evaluator returns:

- exit code `0` when all checks pass,
- exit code `1` when the candidate is valid but one or more policy checks fail,
- exit code `2` when the input or rubric cannot be evaluated.

See `docs/EVALUATIONS.md` for the candidate format, check definitions, and limitations.

## Safety model

- Preview is the default for install, update, and uninstall.
- Existing or unowned target files are conflicts.
- Canonical sources and rendered outputs are checksum-bound to the preview.
- Managed files must still match their manifest checksums before update or uninstall.
- Manifests and files are rechecked immediately before mutation.
- Failed installs and updates roll back their managed changes.
- Cleanup removes only empty ancestors of QACraft-managed paths.
- Codex, Claude Code, and generic manifests are independent.
- Behavior evaluation is local and read-only.
- No network, customer, production, or external-system access is performed.

## Next slice: Phase 2.4 — Documentation and release

Production-readiness work remaining:

- replace legacy manual copy instructions with the supported CLI workflow
- add an installation and compatibility guide
- add a complete end-to-end demo
- add changelog and release notes
- strengthen repository validation for evaluation assets and release metadata
- bump the package version and prepare the release
- complete a final production-readiness audit

GitHub Pages remains optional because enabling an automatic deployment workflow would add Actions usage. The existing static documentation can be served locally or published manually without consuming recurring Actions minutes.
