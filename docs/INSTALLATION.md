# QACraft installation and lifecycle guide

QACraft 1.2.0 has no third-party runtime dependencies and requires Python 3.10 or newer.

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
python3 -m pip install --no-deps dist/qacraft-1.2.0-py3-none-any.whl
qacraft doctor
```

Install a local source distribution:

```bash
python3 -m pip install --no-deps dist/qacraft-1.2.0.tar.gz
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

## Install into Codex

The destination is the target project root. QACraft installs selected skills under `.agents/skills/` and keeps its manifest under `.agents/qacraft/`.

Preview:

```bash
qacraft install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project
```

Apply:

```bash
qacraft install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project \
  --apply
```

## Install into Claude Code

```bash
qacraft install feature-qa bug-report \
  --agent claude-code \
  --destination /path/to/project \
  --apply
```

Claude Code skills are written under `.claude/skills/`; the manifest is stored under `.claude/qacraft/`.

## Generic installation

```bash
qacraft install feature-qa \
  --agent generic \
  --destination /path/to/install-root \
  --apply
```

## Verify an installation

```bash
qacraft verify-install \
  --agent codex \
  --destination /path/to/project
```

A healthy installation returns exit code `0`. Missing or modified managed files return exit code `1`.

## Update the installed skill set

```bash
qacraft update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project

qacraft update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project \
  --apply
```

QACraft refuses to update modified managed files or overwrite unrelated files. Failed updates restore managed files and the manifest.

## Uninstall

```bash
qacraft uninstall \
  --agent codex \
  --destination /path/to/project

qacraft uninstall \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Only unchanged files recorded in the selected adapter manifest are removed. Unrelated project files and directories are preserved.

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
5. performs Codex install, verification, and uninstall;
6. confirms unrelated project content remains intact.

## Operational boundaries

QACraft does not automatically grant filesystem, network, browser, repository, customer, or production permissions. Installed skills remain instruction files. The runtime that executes them must enforce least privilege, secret isolation, approval gates, logging, evidence privacy, and safe external writes.
