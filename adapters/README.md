# QACraft adapter contract

Adapters translate QACraft's platform-neutral source layout into a verified agent-specific installation plan while preserving every canonical source file unchanged.

## Required adapter behavior

Every adapter must:

1. Accept an explicit project or installation root.
2. Resolve only paths inside that destination.
3. Produce a complete preview before any write.
4. Identify every source, target, and deterministic transform.
5. Detect conflicts, existing files, and symbolic links.
6. Never overwrite, delete, or replace files without explicit `--apply`.
7. Record a versioned, adapter-specific installation manifest.
8. Verify source and installed checksums before mutation.
9. Support rollback and safe uninstall using that manifest.
10. Preserve unrelated project files and directories.
11. Preserve canonical QACraft source files unchanged.
12. Avoid claiming that prompt instructions enforce runtime permissions.

## Verified adapter layouts

| Adapter | Skill discovery path | Shared QACraft policies | Manifest |
|---|---|---|---|
| `generic` | `skills/<skill>/SKILL.md` | `shared/` | `.qacraft-manifest.json` |
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/shared/` | `.agents/qacraft/manifest.json` |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/shared/` | `.claude/qacraft/manifest.json` |

The explicit `--destination` is the project or installation root. QACraft never guesses a user-global path and never modifies agent configuration files.

Codex and Claude Code use separate manifests, so both adapters can coexist in the same project and can be verified, updated, or uninstalled independently.

## Source-to-target mapping

QACraft keeps the canonical source files under:

```text
skills/<slug>/SKILL.md
skills/<slug>/templates/report.yaml
skills/<slug>/examples/request.md
skills/<slug>/examples/expected-output.md
shared/*.md
```

The adapter maps those canonical sources into the selected agent layout. Each manifest records the original source path, installed target path, optional transform, canonical source checksum, and installed checksum.

### Agent Skills frontmatter normalization

Canonical QACraft `SKILL.md` files keep project metadata such as `command`, `version`, and `status` as top-level fields because they are also repository specifications.

For `codex` and `claude-code`, the installed copy is normalized to the Agent Skills frontmatter contract:

```yaml
---
name: "feature-qa"
description: "..."
metadata:
  qacraft-command: "/feature-qa"
  qacraft-version: "1.0.0"
  qacraft-status: "specification"
---
```

The Markdown instruction body is preserved exactly. The generic adapter performs no transform and remains byte-for-byte equivalent to the canonical files.

## Lifecycle commands

Every adapter supports the same preview-first lifecycle:

```bash
python3 scripts/qacraft.py plan-install feature-qa \
  --agent codex \
  --destination ./my-project

python3 scripts/qacraft.py install feature-qa \
  --agent codex \
  --destination ./my-project \
  --apply

python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination ./my-project

python3 scripts/qacraft.py update feature-qa bug-report \
  --agent codex \
  --destination ./my-project \
  --apply

python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination ./my-project \
  --apply
```

Replace `codex` with `claude-code` or `generic` as required.

## Verified documentation

- Codex skill discovery: `https://learn.chatgpt.com/docs/build-skills`
- Claude Code skills: `https://code.claude.com/docs/en/slash-commands`
- Agent Skills frontmatter: `https://agentskills.io/specification`

These paths and the frontmatter contract were verified before enabling writes. Automatic agent detection and user-global installation remain intentionally unsupported.
