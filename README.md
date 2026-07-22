# QACraft

Reusable AI skills, safe installation lifecycle, and deterministic behavior evaluations for everyday software QA work.

QACraft 1.3.0 includes:

- 25 detailed QA workflow skills
- shared QA, evidence, security, approval, data, result, publication, and release policies
- generic, Codex, Claude Code, GitHub Copilot, Gemini CLI, and OpenCode project adapters
- preview-first install, verify, update, and uninstall commands
- versioned manifests, SHA-256 verification, rollback, and conflict protection
- deterministic structured-report evaluations for five priority QA skills
- `qacraft` and `python -m qacraft` entry points
- verified self-contained wheel and source-distribution builds
- generated HTML documentation, schemas, examples, templates, tests, and release guidance

No third-party runtime Python packages are required. Python 3.10 or newer is supported.

## Start from a checkout

```bash
python3 -m pip install --no-deps -e .
qacraft doctor
qacraft list
python3 -m qacraft eval-list
qacraft release-check
python3 scripts/demo.py
```

Pip may create an isolated build environment to obtain the declared setuptools build backend. QACraft itself still installs with zero runtime dependencies because `--no-deps` is used.

The original `python3 scripts/qacraft.py ...` interface remains supported.

## Build verified artifacts

Use the standard build frontend:

```bash
python3 -m pip install build
python3 -m build --sdist --wheel --outdir dist
```

The test suite uses a dedicated build environment with `build`, setuptools, and wheel installed once. Compatibility commands such as `python3 setup.py sdist --dist-dir dist` and `python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir dist .` also remain available when those build tools are already installed.

Install the built wheel locally:

```bash
python3 -m pip install --no-deps dist/qacraft-1.3.0-py3-none-any.whl
qacraft doctor
```

The wheel contains a generated `qacraft/bundle/` assembled from an explicit allowlist during the temporary build. The repository keeps only one canonical copy of every skill, policy, schema, rubric, and document.

The source distribution contains the canonical source tree and build recipe. Both artifacts are inspected, installed into isolated environments, and exercised through release checks, evaluation, and the Codex lifecycle in the test suite.

No PyPI or other package-index publication is claimed or performed.

## Install into a verified agent

Each adapter uses an officially documented project skill location and a separate QACraft manifest.

| Agent | `--agent` value | Skill location | Manifest |
|---|---|---|---|
| Codex | `codex` | `.agents/skills/<skill>/` | `.agents/qacraft/manifest.json` |
| Claude Code | `claude-code` | `.claude/skills/<skill>/` | `.claude/qacraft/manifest.json` |
| GitHub Copilot | `github-copilot` | `.github/skills/<skill>/` | `.github/qacraft/manifest.json` |
| Gemini CLI | `gemini-cli` | `.gemini/skills/<skill>/` | `.gemini/qacraft/manifest.json` |
| OpenCode | `opencode` | `.opencode/skills/<skill>/` | `.opencode/qacraft/manifest.json` |

Preview:

```bash
qacraft install feature-qa bug-report \
  --agent github-copilot \
  --destination /path/to/project
```

Apply:

```bash
qacraft install feature-qa bug-report \
  --agent github-copilot \
  --destination /path/to/project \
  --apply
```

Replace `github-copilot` with any verified `--agent` value from the table. QACraft does not automatically detect an agent, install to user-global paths, or modify agent configuration files.

## Verify, update, and uninstall

```bash
qacraft verify-install \
  --agent github-copilot \
  --destination /path/to/project

qacraft update feature-qa bug-report release-qa \
  --agent github-copilot \
  --destination /path/to/project \
  --apply

qacraft uninstall \
  --agent github-copilot \
  --destination /path/to/project \
  --apply
```

Install, update, and uninstall are preview-only without `--apply`. Existing unowned files are never overwritten. Modified managed files block update and uninstall. Failed installs and updates roll back QACraft-managed changes. Independent manifests allow different adapters to coexist in one repository.

## Evaluate structured QA reports

```bash
qacraft eval-list
qacraft evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Deterministic rubrics are included for:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

The evaluator checks schema conformance, source grounding, approval gates, evidence quality, verdict discipline, safety declarations, and output contracts. It does not call an AI model and does not prove that external evidence is authentic.

## Validate the repository

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
qacraft release-check
python3 scripts/demo.py
```

Generated documentation must be committed. The pull-request workflow runs one Python 3.12 validation job and does not run again after merge.

## Documentation

- [Installation and lifecycle](docs/INSTALLATION.md)
- [Compatibility matrix](docs/COMPATIBILITY.md)
- [Behavior evaluations](docs/EVALUATIONS.md)
- [Production readiness](docs/PRODUCTION_READINESS.md)
- [Phase 2 architecture](docs/PHASE_2.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Changelog](CHANGELOG.md)
- HTML documentation: `docs/index.html`

Serve the HTML documentation locally:

```bash
python3 scripts/serve.py
```

The generated site already lives under `/docs`. GitHub Pages may be enabled manually using branch-based publishing when the repository plan and visibility support it. No additional automatic Pages workflow is required.

## Skill catalog

### Planning and scope

`/ticket-review` · `/test-plan` · `/regression-scope` · `/platform-matrix`

### Execution and product behaviour

`/feature-qa` · `/exploratory-qa` · `/smoke-test` · `/permission-qa` · `/api-qa` · `/network-qa` · `/offline-qa` · `/playback-qa`

### Defects and verification

`/bug-report` · `/bug-triage` · `/verify-fix` · `/customer-issue-repro` · `/flaky-test-triage`

### Release and operations

`/release-qa` · `/staged-rollout-check` · `/incident-qa`

### Automation and maintenance

`/automation-review` · `/test-case-review`

### Communication and improvement

`/qa-daily-summary` · `/qa-handoff` · `/qa-retrospective`

## Safety model

QACraft skills are instructions and specifications—not a permission system.

Production adopters must enforce:

- least-privilege filesystem, command, repository, browser, and network permissions
- secret isolation and customer-data controls
- authenticated, version-bound approval gates
- evidence privacy, integrity, access, retention, and deletion controls
- idempotent, conflict-aware external writes
- monitoring, audit logs, incident response, and rollback

Never grant production, customer, or security-sensitive access merely because a skill describes safe behavior.

## Repository structure

```text
QACraft/
├── adapters/
├── catalog/
├── docs/
├── evaluations/
├── qacraft/
├── schemas/
├── scripts/
├── shared/
├── skills/
├── tests/
├── .github/workflows/
├── MANIFEST.in
├── qacraft_build.py
├── setup.py
├── AGENTS.md
├── CLAUDE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## License

MIT
