# QACraft adapter contract

Adapters translate QACraft's platform-neutral source layout into a verified agent-specific installation plan while preserving every source file unchanged.

## Required adapter behavior

Every adapter must:

1. Accept an explicit project or installation root.
2. Resolve only paths inside that destination.
3. Produce a complete preview before any write.
4. Identify every source and target file.
5. Detect conflicts, existing files, and symbolic links.
6. Never overwrite, delete, or replace files without explicit `--apply`.
7. Record a versioned, adapter-specific installation manifest.
8. Verify checksums before update or uninstall.
9. Support rollback and safe uninstall using that manifest.
10. Preserve unrelated project files and directories.
11. Preserve QACraft source files unchanged.
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

The adapter maps those immutable sources into the selected agent layout. The installation manifest records both the original source path and the installed target path with a SHA-256 checksum.

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

These paths were verified before enabling writes. Automatic agent detection and user-global installation remain intentionally unsupported.
