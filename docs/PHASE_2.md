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

## Adapter layouts

| Adapter | Skill path | Shared policies | Manifest |
|---|---|---|---|
| `generic` | `skills/<skill>/SKILL.md` | `shared/` | `.qacraft-manifest.json` |
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/shared/` | `.agents/qacraft/manifest.json` |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/shared/` | `.claude/qacraft/manifest.json` |

The explicit destination is always the project or installation root. QACraft does not guess user-global paths, detect agents automatically, or modify agent configuration files.

Canonical QACraft files remain unchanged. Codex and Claude Code installed copies normalize `command`, `version`, and `status` into the standard Agent Skills `metadata` mapping while preserving the complete Markdown instruction body. The manifest records both canonical-source and installed-output checksums.

## Commands

List available skills:

```bash
python3 scripts/qacraft.py list
```

Check repository health:

```bash
python3 scripts/qacraft.py doctor
```

Preview an adapter installation:

```bash
python3 scripts/qacraft.py plan-install feature-qa bug-report \
  --agent codex \
  --destination ./my-project
```

Apply the reviewed installation:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination ./my-project \
  --apply
```

Verify installed files:

```bash
python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination ./my-project
```

Update the desired installed skill set:

```bash
python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination ./my-project \
  --apply
```

Preview or apply uninstall:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination ./my-project

python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination ./my-project \
  --apply
```

Replace `codex` with `claude-code` or `generic` as required.

## Safety model

- Preview is the default for install, update, and uninstall.
- Existing or unowned target files are conflicts.
- Canonical sources and rendered outputs are checksum-bound to the preview.
- Managed files must still match their manifest checksums before update or uninstall.
- Manifests and files are rechecked immediately before mutation.
- Failed installs and updates roll back their managed changes.
- Cleanup removes only empty ancestors of QACraft-managed paths.
- Codex, Claude Code, and generic manifests are independent.
- No network, customer, production, or external-system access is performed.

## Next slice: Phase 2.3 — Behavior evaluations

Build a local, deterministic evaluation schema and runner for:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

The initial evaluation runner should inspect supplied candidate outputs without calling external models or systems. Rubrics should check hallucination control, approval gates, evidence quality, verdict discipline, safety boundaries, and output-schema conformance.
