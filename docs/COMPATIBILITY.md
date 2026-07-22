# QACraft compatibility

## Agent adapters

| Adapter | Verified project skill path | Manifest | Install | Verify | Update | Uninstall |
|---|---|---|---:|---:|---:|---:|
| `codex` | `.agents/skills/<skill>/SKILL.md` | `.agents/qacraft/manifest.json` | Yes | Yes | Yes | Yes |
| `claude-code` | `.claude/skills/<skill>/SKILL.md` | `.claude/qacraft/manifest.json` | Yes | Yes | Yes | Yes |
| `generic` | `skills/<skill>/SKILL.md` | `.qacraft-manifest.json` | Yes | Yes | Yes | Yes |

The Codex and Claude Code paths were verified before write support was enabled. QACraft uses project-level destinations only. Automatic agent detection and user-global installation are intentionally unsupported.

## Installed skill format

Canonical QACraft skills contain repository-specific frontmatter fields. Codex and Claude Code installed copies are normalized to the Agent Skills structure:

- `name` and `description` remain top-level fields;
- QACraft `command`, `version`, and `status` move under `metadata`;
- the complete Markdown instruction body is preserved;
- the manifest records both source and installed-output SHA-256 hashes.

The generic adapter copies canonical files without transformation.

## Python and operating systems

| Area | Status |
|---|---|
| Python 3.10 | Supported by project metadata |
| Python 3.11 | Supported by project metadata |
| Python 3.12 | Used by the automated validation job |
| Linux | Automated validation environment |
| macOS | Expected to work through Python `pathlib`; manual environment |
| Windows | Expected to work through Python `pathlib`; not continuously tested in CI |

QACraft has no third-party Python runtime dependencies.

## Behavior evaluation coverage

Deterministic behavior rubrics are available for:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

The remaining 20 skills are installable but do not yet have dedicated deterministic behavior rubrics. They remain governed by their canonical specifications and shared policies.

## Compatibility guarantees

QACraft guarantees only the behavior implemented by its filesystem and evaluation code:

- explicit destination containment;
- conflict and symbolic-link protection;
- preview-first mutation;
- checksummed manifests;
- safe update rollback;
- manifest-driven uninstall;
- deterministic structured-report evaluation.

QACraft does not guarantee that an agent will obey a skill, that external evidence is authentic, or that permissions described in Markdown are enforced. Those responsibilities belong to the agent runtime, tool sandbox, approval system, evidence store, and external integrations.

## Deliberate non-support

- automatic user-global installation;
- silent overwrite or force deletion;
- automatic modification of `AGENTS.md`, `CLAUDE.md`, agent settings, or permission files;
- network installation or remote package fetching;
- production, customer, ticketing, or publication access;
- runtime enforcement based only on prompt text;
- automatic GitHub Pages deployment.

Static documentation can be served locally with `python3 scripts/serve.py` or published manually without adding recurring Actions usage.
