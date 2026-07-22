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
13. Use an officially documented project-level discovery path before writes are enabled.
14. Avoid user-global installation, automatic detection, and agent configuration modification.

## Verified adapter layouts

| Adapter | Skill discovery path | Shared QACraft policies | Manifest |
|---|---|---|---|
| `generic` | `skills/<skill>/SKILL.md` | `shared/` | `.qacraft-manifest.json` |
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/shared/` | `.agents/qacraft/manifest.json` |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/shared/` | `.claude/qacraft/manifest.json` |
| `github-copilot` | `.github/skills/<skill>/SKILL.md` | `.github/qacraft/shared/` | `.github/qacraft/manifest.json` |
| `gemini-cli` | `.gemini/skills/<skill>/SKILL.md` | `.gemini/qacraft/shared/` | `.gemini/qacraft/manifest.json` |
| `opencode` | `.opencode/skills/<skill>/SKILL.md` | `.opencode/qacraft/shared/` | `.opencode/qacraft/manifest.json` |

The explicit `--destination` is the project or installation root. QACraft never guesses a user-global path and never modifies agent configuration files.

Every product adapter uses a separate manifest, so verified adapters can coexist in the same project and can be verified, updated, or uninstalled independently. Native product paths are used even when a product supports compatible aliases such as `.agents/skills` or `.claude/skills`.

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

For every product adapter, the installed copy is normalized to the Agent Skills frontmatter contract:

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
qacraft plan-install feature-qa \
  --agent github-copilot \
  --destination ./my-project

qacraft install feature-qa \
  --agent github-copilot \
  --destination ./my-project \
  --apply

qacraft verify-install \
  --agent github-copilot \
  --destination ./my-project

qacraft update feature-qa bug-report \
  --agent github-copilot \
  --destination ./my-project \
  --apply

qacraft uninstall \
  --agent github-copilot \
  --destination ./my-project \
  --apply
```

Replace `github-copilot` with any verified adapter value as required.

## Verified documentation

- Codex skill discovery: `https://learn.chatgpt.com/docs/build-skills`
- Claude Code skills: `https://code.claude.com/docs/en/slash-commands`
- GitHub Copilot Agent Skills: `https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills`
- Gemini CLI Agent Skills: `https://geminicli.com/docs/cli/skills/`
- OpenCode Agent Skills: `https://opencode.ai/docs/skills`
- Agent Skills frontmatter: `https://agentskills.io/specification`

These paths and the frontmatter contract were verified before enabling writes. Cursor and Windsurf remain outside the verified adapter set until equivalent official Agent Skills discovery paths are documented.
