# QACraft installation and lifecycle guide

QACraft 1.3.0 has no third-party runtime dependencies and requires Python 3.10 or newer.

## Editable installation from a checkout

```bash
python3 -m pip install --no-deps -e .
qacraft doctor
qacraft list
python3 -m qacraft eval-list
```

The editable installation uses the reviewed checkout as its runtime and asset root.

## Build local artifacts

Use the standard build frontend from a clean checkout:

```bash
python3 -m pip install build
python3 -m build --sdist --wheel --outdir dist
```

The test suite creates a dedicated build environment and installs `build`, setuptools, and wheel once before running `python -m build --no-isolation`. Compatibility commands such as `python3 setup.py sdist --dist-dir dist` and `python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir dist .` remain available when those build tools are already installed.

The wheel build creates `qacraft/bundle/` only inside setuptools' temporary build directory. It copies an explicit allowlist of canonical runtime files and rejects symbolic links. The generated bundle is not committed to the repository.

The source distribution contains the canonical source tree, tests, manifest, and build recipe. Installing the source distribution builds the same self-contained wheel layout.

Install a local wheel:

```bash
python3 -m pip install --no-deps dist/qacraft-1.3.0-py3-none-any.whl
qacraft doctor
```

Install a local source distribution:

```bash
python3 -m pip install --no-deps dist/qacraft-1.3.0.tar.gz
qacraft doctor
```

No package-index publication is currently claimed. Use artifacts built from a trusted commit.

## Legacy checkout interface

```bash
python3 scripts/qacraft.py list
```

## Repository validation

```bash
qacraft doctor
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
qacraft release-check
python3 scripts/demo.py
```

## Verified project adapters

| Agent | CLI value | Skills | QACraft manifest |
|---|---|---|---|
| Codex | `codex` | `.agents/skills/<skill>/` | `.agents/qacraft/manifest.json` |
| Claude Code | `claude-code` | `.claude/skills/<skill>/` | `.claude/qacraft/manifest.json` |
| GitHub Copilot | `github-copilot` | `.github/skills/<skill>/` | `.github/qacraft/manifest.json` |
| Gemini CLI | `gemini-cli` | `.gemini/skills/<skill>/` | `.gemini/qacraft/manifest.json` |
| OpenCode | `opencode` | `.opencode/skills/<skill>/` | `.opencode/qacraft/manifest.json` |

These are project-level locations documented by their respective agent platforms. QACraft deliberately uses the native path for each adapter and does not install into user-global directories.

## Install a skill pack

The destination is the target project root. Preview is the default:

```bash
qacraft install feature-qa bug-report \
  --agent gemini-cli \
  --destination /path/to/project
```

Apply the reviewed plan:

```bash
qacraft install feature-qa bug-report \
  --agent gemini-cli \
  --destination /path/to/project \
  --apply
```

Replace `gemini-cli` with any verified CLI value in the table. Installed `SKILL.md` files receive deterministic Agent Skills frontmatter while preserving the complete canonical instruction body.

## Generic installation

Use the generic adapter only when another integration will load the exported files itself:

```bash
qacraft install feature-qa \
  --agent generic \
  --destination /path/to/install-root \
  --apply
```

## Verify an installation

```bash
qacraft verify-install \
  --agent gemini-cli \
  --destination /path/to/project
```

A healthy installation returns exit code `0`. Missing or modified managed files return exit code `1`.

## Update the installed skill set

The supplied skills represent the desired final set:

```bash
qacraft update feature-qa bug-report release-qa \
  --agent gemini-cli \
  --destination /path/to/project

qacraft update feature-qa bug-report release-qa \
  --agent gemini-cli \
  --destination /path/to/project \
  --apply
```

QACraft refuses to update modified managed files or overwrite unrelated files. Failed updates restore managed files and the manifest.

## Uninstall

```bash
qacraft uninstall \
  --agent gemini-cli \
  --destination /path/to/project

qacraft uninstall \
  --agent gemini-cli \
  --destination /path/to/project \
  --apply
```

Only unchanged files recorded in the selected adapter manifest are removed. Unrelated project files, other adapters, and non-empty directories are preserved.

## Adapter coexistence

Every verified adapter owns a separate manifest and shared-policy directory. Different adapters may coexist in one repository and can be verified, updated, or uninstalled independently.

Avoid installing the same skill slug through multiple adapters unless you have reviewed how the target agents resolve duplicate skill names across native and alias paths.

## Evaluate a candidate QA report

```bash
qacraft eval-list
qacraft evaluate --input /path/to/candidate.json
```

Evaluation exit codes:

- `0`: all deterministic checks passed
- `1`: the report was readable but failed one or more checks
- `2`: the report or rubric could not be evaluated

## Distribution verification

The test suite:

1. builds the wheel and source distribution from a temporary source copy;
2. inspects both archives for required and forbidden files;
3. installs each artifact into a separate environment;
4. runs `doctor`, `eval-list`, `evaluate`, and `release-check`;
5. performs lifecycle verification for agent adapters;
6. confirms unrelated project content remains intact.

## Operational boundaries

QACraft does not automatically grant filesystem, network, browser, repository, customer, or production permissions. Installed skills remain instruction files. The runtime that executes them must enforce least privilege, secret isolation, approval gates, logging, evidence privacy, and safe external writes.
