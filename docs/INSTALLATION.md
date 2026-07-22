# QACraft installation and lifecycle guide

QACraft is dependency-free and requires Python 3.10 or newer.

## Install the source-checkout CLI

Phase 3.1 supports an editable installation from a QACraft checkout:

```bash
python3 -m pip install --no-deps -e .
qacraft doctor
qacraft list
python3 -m qacraft eval-list
```

The editable installation keeps the repository as the source of canonical skills, shared policies, schemas, rubrics, examples, and release files. The `qacraft` console command and `python -m qacraft` therefore work from any current directory while continuing to use the reviewed checkout.

This phase does **not** claim that a wheel or PyPI package contains the complete QACraft asset set. Wheel and source-distribution asset verification belong to Phase 3.2. Until that work is complete, use `pip install -e .` from a trusted checkout rather than `pip install .` or a package index.

The original script interface remains supported:

```bash
python3 scripts/qacraft.py list
```

Every command below may use either `qacraft` after editable installation or `python3 scripts/qacraft.py` from the checkout.

## Repository validation

```bash
qacraft doctor
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

## List available skills

```bash
qacraft list
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

Use the generic adapter when another agent or integration will load the files itself:

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

The supplied skills represent the desired final set:

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

Preview:

```bash
qacraft uninstall \
  --agent codex \
  --destination /path/to/project
```

Apply:

```bash
qacraft uninstall \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Only unchanged files recorded in the selected adapter manifest are removed. Unrelated project files and directories are preserved.

## Evaluate a candidate QA report

```bash
qacraft eval-list
qacraft evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Evaluation exit codes:

- `0`: all deterministic checks passed
- `1`: the report was readable but failed one or more checks
- `2`: the report or rubric could not be evaluated

## Source-only commands

`release-check` and `scripts/demo.py` validate the QACraft source release itself. Run them from the checkout:

```bash
qacraft release-check
python3 scripts/demo.py
```

## Operational boundaries

QACraft does not automatically grant filesystem, network, browser, repository, customer, or production permissions. Installed skills remain instruction files. The runtime that executes them must enforce least privilege, secrets isolation, approval gates, logging, evidence privacy, and safe external writes.
