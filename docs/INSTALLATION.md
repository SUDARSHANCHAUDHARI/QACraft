# QACraft installation and lifecycle guide

QACraft is dependency-free and requires Python 3.10 or newer.

## Repository validation

```bash
python3 scripts/qacraft.py doctor
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

## List available skills

```bash
python3 scripts/qacraft.py list
```

## Install into Codex

The destination is the target project root. QACraft installs selected skills under `.agents/skills/` and keeps its manifest under `.agents/qacraft/`.

Preview:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project
```

Apply:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project \
  --apply
```

## Install into Claude Code

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent claude-code \
  --destination /path/to/project \
  --apply
```

Claude Code skills are written under `.claude/skills/`; the manifest is stored under `.claude/qacraft/`.

## Generic installation

Use the generic adapter when another agent or integration will load the files itself:

```bash
python3 scripts/qacraft.py install feature-qa \
  --agent generic \
  --destination /path/to/install-root \
  --apply
```

## Verify an installation

```bash
python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination /path/to/project
```

A healthy installation returns exit code `0`. Missing or modified managed files return exit code `1`.

## Update the installed skill set

The supplied skills represent the desired final set:

```bash
python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project

python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project \
  --apply
```

QACraft refuses to update modified managed files or overwrite unrelated files. Failed updates restore managed files and the manifest.

## Uninstall

Preview:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination /path/to/project
```

Apply:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Only unchanged files recorded in the selected adapter manifest are removed. Unrelated project files and directories are preserved.

## Evaluate a candidate QA report

```bash
python3 scripts/qacraft.py eval-list
python3 scripts/qacraft.py evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Evaluation exit codes:

- `0`: all deterministic checks passed
- `1`: the report was readable but failed one or more checks
- `2`: the report or rubric could not be evaluated

## Operational boundaries

QACraft does not automatically grant filesystem, network, browser, repository, customer, or production permissions. Installed skills remain instruction files. The runtime that executes them must enforce least privilege, secrets isolation, approval gates, logging, evidence privacy, and safe external writes.
