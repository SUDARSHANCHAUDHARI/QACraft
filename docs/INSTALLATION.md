# QACraft installation and lifecycle guide

QACraft 1.4.1 has no third-party runtime dependencies and requires Python 3.10 or newer.

## Install from PyPI

```bash
python3 -m pip install qacraft==1.4.1
qacraft doctor
```

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
python3 -m pip install --no-deps dist/qacraft-1.4.1-py3-none-any.whl
qacraft doctor
```

Install a local source distribution:

```bash
python3 -m pip install --no-deps dist/qacraft-1.4.1.tar.gz
qacraft doctor
```

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

## Destination safety boundary

`--destination` is always the target project or install root and **must already exist as a directory**.

QACraft does not create a missing destination root. This prevents a misspelled path from silently creating and populating an unintended directory. Create or select the project directory yourself, then pass that existing directory to QACraft.

QACraft may create only its documented managed subdirectories and files inside the selected existing root. Filesystem roots, symbolic-link destinations, non-directory destinations, path traversal, unowned conflicts, and modified managed files remain blocked.

## Install a skill pack

Preview is the default:

```bash
qacraft install feature-qa bug-report \
  --agent github-copilot \
  --destination /path/to/existing-project
```

Apply only after reviewing the plan:

```bash
qacraft install feature-qa bug-report \
  --agent github-copilot \
  --destination /path/to/existing-project \
  --apply
```

## Generic installation

```bash
qacraft install feature-qa \
  --agent generic \
  --destination /path/to/existing-install-root \
  --apply
```

## Verify an installation

```bash
qacraft verify-install \
  --agent github-copilot \
  --destination /path/to/existing-project
```

A healthy installation returns exit code `0`. Missing or modified managed files return exit code `1`.

## Update the installed skill set

```bash
qacraft update feature-qa bug-report release-qa \
  --agent github-copilot \
  --destination /path/to/existing-project

qacraft update feature-qa bug-report release-qa \
  --agent github-copilot \
  --destination /path/to/existing-project \
  --apply
```

QACraft refuses to update modified managed files or overwrite unrelated files. Failed updates restore managed files and the manifest.

## Uninstall

```bash
qacraft uninstall \
  --agent github-copilot \
  --destination /path/to/existing-project

qacraft uninstall \
  --agent github-copilot \
  --destination /path/to/existing-project \
  --apply
```

Only unchanged files recorded in the selected adapter manifest are removed. Unrelated project files and directories are preserved.

## Evaluate a candidate QA report

```bash
qacraft eval-list
qacraft evaluate --input evaluations/examples/api-qa-pass.json
```

Published examples and negative cases are indexed by `evaluations/fixtures.json`. Negative fixtures intentionally return exit code `1` and are used to prove specific policy checks.

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
5. performs an agent install, verification, and uninstall lifecycle;
6. verifies all declared evaluation fixtures through the installed release check;
7. confirms unrelated project content remains intact;
8. confirms preview and apply reject nonexistent destination roots without creating them.

## Operational boundaries

QACraft does not automatically grant filesystem, network, browser, repository, customer, or production permissions. Installed skills remain instruction files. The runtime that executes them must enforce least privilege, secret isolation, approval gates, logging, evidence privacy, and safe external writes.
