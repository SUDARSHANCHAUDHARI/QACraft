# QACraft compatibility matrix

## Runtime

| Component | Supported | Notes |
|---|---:|---|
| Python | 3.10+ | Standard-library runtime only |
| macOS | Yes | Filesystem lifecycle and evaluator supported |
| Linux | Yes | Primary CI environment |
| Windows | Expected | Uses `pathlib`; validate locally before release-critical use |
| Network access | Not required at runtime | Installer and evaluator are local-only |

## CLI distribution modes

| Mode | Supported | Notes |
|---|---:|---|
| `python3 scripts/qacraft.py` | Yes | Direct source-checkout interface |
| `python -m qacraft` from checkout | Yes | Uses the local canonical asset tree |
| `pip install --no-deps -e .` | Yes | Provides entry points backed by the trusted checkout |
| Local wheel installation | Yes | Self-contained `qacraft/bundle` is archive-inspected and lifecycle-tested |
| Local source distribution | Yes | Contains canonical sources and builds the verified wheel layout |
| PyPI/package-index installation | Not published | No public package has been uploaded or claimed |
| Standalone executable | No | Not implemented |

Build tooling may obtain the declared setuptools backend. Installed QACraft runtime behavior remains dependency-free and network-free.

Incomplete checkouts or installed bundles fail with an explicit missing-assets report. They do not silently act as complete distributions.

## Agent adapters

| Adapter | CLI value | Discovery path | Manifest | Official basis |
|---|---|---|---|---|
| Generic | `generic` | `skills/<slug>/` | `.qacraft-manifest.json` | Platform-neutral export |
| Codex | `codex` | `.agents/skills/<slug>/` | `.agents/qacraft/manifest.json` | Codex project skills |
| Claude Code | `claude-code` | `.claude/skills/<slug>/` | `.claude/qacraft/manifest.json` | Claude Code project skills |
| GitHub Copilot | `github-copilot` | `.github/skills/<slug>/` | `.github/qacraft/manifest.json` | GitHub Copilot Agent Skills |
| Gemini CLI | `gemini-cli` | `.gemini/skills/<slug>/` | `.gemini/qacraft/manifest.json` | Gemini CLI workspace skills |
| OpenCode | `opencode` | `.opencode/skills/<slug>/` | `.opencode/qacraft/manifest.json` | OpenCode project skills |

The destination passed to the CLI is always an explicit project or installation root. QACraft does not guess global directories or change agent configuration files.

The three 1.3.0 adapters use their product-native project paths even where an agent also supports `.agents/skills` or `.claude/skills` aliases. This keeps ownership and uninstall behavior explicit. Do not install the same skill name through multiple adapters in one project unless the target agents' precedence behavior has been reviewed.

Cursor and Windsurf are not listed as verified Agent Skills adapters because this release does not rely on undocumented discovery paths. Their instruction-file features are outside this adapter contract.

## Behavior evaluations

Deterministic rubrics are included for:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

The evaluator checks structured candidate reports for schema conformance, grounding, approvals, evidence, verdict discipline, safety declarations, and output contracts. It does not call an AI model and does not authenticate evidence against external systems.

## Compatibility guarantees

- Existing unowned files are never overwritten.
- Modified managed files block update and uninstall.
- Agent manifests are independent and may coexist in one project.
- Canonical QACraft source files remain unchanged.
- Generated wheel bundles come from an explicit allowlist and temporary build directory.
- Distribution builds reject symbolic links.
- Cache, bytecode, VCS, environment, and build-output files are excluded.
- Agent copies receive deterministic standards-compatible frontmatter normalization.
- Failed installs and updates roll back QACraft-managed changes.
- All entry points delegate to the same reviewed runtime.

## Intentionally unsupported

- Automatic agent detection
- User-global installation
- Force overwrite or force deletion
- Symlink-based installation
- Undocumented agent discovery paths
- Unreviewed package-index publication
- Production/customer system access
- Runtime permission enforcement through prompt text
- Automatic GitHub Pages deployment

The generated documentation already lives under `/docs`. Repository owners may enable branch-based GitHub Pages manually when their GitHub plan and repository visibility support it, without adding another automatic Actions workflow.
