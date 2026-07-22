# Phase 2 development plan

Phase 2 turns QACraft from a repository of QA workflow specifications into an installable and behavior-tested platform.

## Phase 2.1 — Foundation

Completed:

- `scripts/qacraft.py list`
- `scripts/qacraft.py doctor`
- `scripts/qacraft.py plan-install`
- adapter safety contract
- automated CLI tests
- complete source-file planning for skills and shared policies

## Phase 2.2a — Generic installer

The generic adapter can install QACraft files into an explicit destination without assuming any AI-agent-specific folder structure.

Safety properties:

- preview is the default
- writes require `--apply`
- existing files and manifests are treated as conflicts
- no overwrite, deletion, replacement, or symlink support
- source and destination containment checks
- SHA-256 verification after every copy
- destination-local `.qacraft-manifest.json`
- partial writes are removed if installation fails
- Claude Code and Codex remain preview-only

Update and uninstall are not included yet. They require manifest verification and modified-file protection before they can be implemented safely.

## Commands

List available skills:

```bash
python3 scripts/qacraft.py list
```

Check repository health:

```bash
python3 scripts/qacraft.py doctor
```

Preview a platform-neutral plan:

```bash
python3 scripts/qacraft.py plan-install feature-qa bug-report \
  --agent generic \
  --destination ./example-agent-skills
```

Preview the generic installer, including checksums and conflicts:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent generic \
  --destination ./example-agent-skills
```

Apply the reviewed generic installation:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent generic \
  --destination ./example-agent-skills \
  --apply
```

Install all skills:

```bash
python3 scripts/qacraft.py install --all \
  --agent generic \
  --destination ./example-agent-skills \
  --apply
```

## Installed layout

The generic adapter preserves repository-relative paths:

```text
example-agent-skills/
├── .qacraft-manifest.json
├── shared/
│   └── ...
└── skills/
    ├── feature-qa/
    │   ├── SKILL.md
    │   ├── examples/
    │   └── templates/
    └── ...
```

The generic layout is intentionally neutral. It does not claim that a particular agent will automatically discover or load these files.

## Next slices

### Phase 2.2b — Lifecycle management

- verify installed manifests
- detect locally modified files
- safe update preview and apply
- safe uninstall preview and apply
- refuse deletion of modified or untracked files

### Phase 2.2c — Verified agent adapters

Add Claude Code and Codex adapters only after their current instruction-loading formats and destinations are verified. Each adapter must retain preview, conflict detection, checksums, manifests, and rollback.

### Phase 2.3 — Behavior evaluations

Build rubric-based evaluations for `/feature-qa`, `/ticket-review`, `/bug-report`, `/verify-fix`, and `/release-qa`.
