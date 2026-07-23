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
| Wheel installation | Yes | Self-contained `qacraft/bundle` is archive-inspected and lifecycle-tested |
| Source distribution | Yes | Contains canonical sources and builds the verified wheel layout |
| PyPI installation | Yes | `python3 -m pip install qacraft==1.4.1` |
| Standalone executable | No | Not implemented |

Build tooling may obtain the declared setuptools backend. Installed QACraft runtime behavior remains dependency-free and network-free.

Incomplete checkouts or installed bundles fail with an explicit missing-assets report. They do not silently act as complete distributions.

## Destination requirements

Every lifecycle command requires an explicit destination that already exists as a directory.

- A nonexistent path is rejected and remains nonexistent.
- A symbolic-link destination is rejected.
- A filesystem root is rejected.
- A non-directory destination is rejected.
- QACraft may create only its documented managed paths beneath the selected existing root.

This applies consistently to install planning, installation, update, verification, and uninstall.

## Agent adapters

| Adapter | CLI value | Discovery path | Manifest | Official basis |
|---|---|---|---|---|
| Generic | `generic` | `skills/<slug>/` | `.qacraft-manifest.json` | Platform-neutral export |
| Codex | `codex` | `.agents/skills/<slug>/` | `.agents/qacraft/manifest.json` | Codex project skills |
| Claude Code | `claude-code` | `.claude/skills/<slug>/` | `.claude/qacraft/manifest.json` | Claude Code project skills |
| GitHub Copilot | `github-copilot` | `.github/skills/<slug>/` | `.github/qacraft/manifest.json` | GitHub Copilot Agent Skills |
| Gemini CLI | `gemini-cli` | `.gemini/skills/<slug>/` | `.gemini/qacraft/manifest.json` | Gemini CLI workspace skills |
| OpenCode | `opencode` | `.opencode/skills/<slug>/` | `.opencode/qacraft/manifest.json` | OpenCode project skills |

The destination passed to the CLI is always an explicit existing project or installation root. QACraft does not guess global directories or change agent configuration files.

The product adapters use their native project paths even where compatible aliases also exist. This keeps ownership and uninstall behavior explicit. Do not install the same skill name through multiple adapters unless the target agents' precedence behavior has been reviewed.

Cursor and Windsurf are not listed as verified Agent Skills adapters because QACraft does not rely on undocumented discovery paths. Their instruction-file features are outside this adapter contract.

## Behavior evaluations

Deterministic rubrics are included for ten workflows:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`
- `/test-plan`
- `/regression-scope`
- `/customer-issue-repro`
- `/api-qa`
- `/staged-rollout-check`

Passing examples and targeted failure fixtures are declared in `evaluations/fixtures.json`. The catalog and all referenced files are included in the wheel and source distribution.

The evaluator checks structured candidate reports for schema conformance, grounding, approvals, evidence, verdict discipline, safety declarations, and output contracts. It does not call an AI model and does not authenticate evidence against external systems.

## Compatibility guarantees

- Existing unowned files are never overwritten.
- Nonexistent destination roots are never created.
- Modified managed files block update and uninstall.
- Agent manifests are independent and may coexist in one project.
- Canonical QACraft source files remain unchanged.
- Generated wheel bundles come from an explicit allowlist and temporary build directory.
- Distribution builds reject symbolic links.
- Cache, bytecode, VCS, environment, and build-output files are excluded.
- Agent copies receive deterministic standards-compatible frontmatter normalization.
- Failed installs and updates roll back QACraft-managed changes.
- All entry points delegate to the same reviewed runtime.
- Rubric gates, decisions, and outputs are release-bound to canonical skill contracts.
- Published fixture expectations are checked from source and installed artifacts.

## Publication compatibility

- GitHub Pages documentation is published through `.github/workflows/pages.yml`.
- PyPI uses Trusted Publishing through `.github/workflows/publish-pypi.yml`.
- Version tags must be annotated and must match `pyproject.toml`.
- The release workflow builds once and publishes the same wheel and source archive to GitHub Releases and PyPI.

## Intentionally unsupported

- Automatic agent detection
- User-global installation
- Force overwrite or force deletion
- Symlink-based installation
- Undocumented agent discovery paths
- Production/customer system access
- Runtime permission enforcement through prompt text

Published documentation: <https://sudarshanchaudhari.github.io/QACraft/>
