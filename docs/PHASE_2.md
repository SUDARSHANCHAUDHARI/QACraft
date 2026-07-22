# Phase 2 delivery record

Phase 2 turns QACraft from a repository of QA workflow specifications into an installable, verifiable, and behavior-tested platform.

## Phase 2.1 — Foundation: complete

- Dependency-free CLI
- Skill catalog and repository doctor
- Read-only installation planning
- Adapter safety contract
- Complete source-file planning
- Automated CLI tests

## Phase 2.2 — Installer and lifecycle: complete

- Generic filesystem adapter
- Verified Codex project adapter
- Verified Claude Code project adapter
- Preview-first install, update, and uninstall
- Explicit `--apply` before mutation
- Conflict and symbolic-link protection
- Canonical-source and installed-output SHA-256 verification
- Separate versioned manifests
- Install verification
- Safe update with rollback
- Safe manifest-driven uninstall
- Preservation of unrelated project files and directories

### Adapter layouts

| Adapter | Skill path | Shared policies | Manifest |
|---|---|---|---|
| `generic` | `skills/<skill>/SKILL.md` | `shared/` | `.qacraft-manifest.json` |
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/shared/` | `.agents/qacraft/manifest.json` |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/shared/` | `.claude/qacraft/manifest.json` |

The explicit destination is always the project or installation root. QACraft does not guess user-global paths, detect agents automatically, or modify agent configuration files.

Canonical QACraft files remain unchanged. Codex and Claude Code installed copies normalize QACraft-specific frontmatter into the standard Agent Skills `metadata` mapping while preserving the complete instruction body.

## Phase 2.3 — Behavior evaluations: complete

- Local deterministic evaluator with no external model or network calls
- Versioned candidate and report JSON Schemas
- Exact rubrics for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`
- Source-grounding and hallucination-control checks
- Version-bound approval-gate checks
- Evidence reference, integrity, timestamp, and privacy checks
- Ordered verdict and release-blocker checks
- Permission, secret, personal-data, external-write, and cleanup safety checks
- Skill-specific output-contract checks
- Machine-readable JSON reports and deterministic exit codes
- Passing example and regression tests for every rubric and failure category

```bash
python3 scripts/qacraft.py eval-list
python3 scripts/qacraft.py evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Exit codes:

- `0`: every evaluation category passed
- `1`: candidate was readable but one or more checks failed
- `2`: candidate or rubric could not be evaluated

## Phase 2.4 — Documentation and release: complete

- Supported CLI workflow replaces legacy manual-copy instructions
- Installation and lifecycle guide
- Compatibility matrix
- End-to-end temporary-project demo
- Changelog and release checklist
- Version `1.1.0`
- Production safety and unsupported-capability boundaries
- Optional branch-based `/docs` publication without another automatic Actions workflow

## Production-readiness command set

```bash
python3 scripts/generate_docs.py
python3 scripts/qacraft.py doctor
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/demo.py
```

## Safety model

- Existing or unowned target files are conflicts.
- Canonical sources and rendered outputs are checksum-bound to the preview.
- Managed files must match their manifest before update or uninstall.
- Manifests and files are rechecked immediately before mutation.
- Failed installs and updates roll back their managed changes.
- Cleanup removes only empty ancestors of QACraft-managed paths.
- Codex, Claude Code, and generic manifests are independent.
- Behavior evaluation is local and read-only.
- No network, customer, production, or external-system access is performed.
- Runtime permissions, evidence authenticity, and external-system controls remain the adopter's responsibility.

Phase 2 is complete. Future work belongs to post-1.1 improvements such as additional evaluation rubrics, optional package distribution, and independently verified support for more agents.
