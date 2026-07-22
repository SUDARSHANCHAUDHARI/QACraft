# QACraft

Reusable AI skills, safe installation lifecycle, and deterministic behavior evaluations for everyday software QA work.

QACraft 1.1.0 includes:

- 25 detailed QA workflow skills
- shared QA, evidence, security, approval, data, result, publication, and release policies
- generic, Codex, and Claude Code project adapters
- preview-first install, verify, update, and uninstall commands
- versioned manifests, SHA-256 verification, rollback, and conflict protection
- deterministic structured-report evaluations for five priority QA skills
- generated HTML documentation, schemas, examples, templates, tests, and release guidance

No third-party Python packages are required. Python 3.10 or newer is supported.

## Start here

```bash
python3 scripts/qacraft.py doctor
python3 scripts/qacraft.py list
python3 scripts/qacraft.py release-check
python3 scripts/demo.py
```

The release check validates production documentation, version metadata, lean CI, rubric coverage, rubric-to-skill binding, and the published passing evaluation example. The end-to-end demo uses a temporary local project. It installs and updates a Codex skill pack, verifies the manifest, evaluates the passing fixture, uninstalls the pack, and confirms unrelated files remain untouched.

## Install into Codex

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

Skills are installed under `.agents/skills/`. QACraft stores an independent manifest under `.agents/qacraft/`.

## Install into Claude Code

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent claude-code \
  --destination /path/to/project \
  --apply
```

Skills are installed under `.claude/skills/`. The Claude Code manifest is stored under `.claude/qacraft/`.

## Verify, update, and uninstall

```bash
python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination /path/to/project

python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project \
  --apply

python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Install, update, and uninstall are preview-only without `--apply`. Existing unowned files are never overwritten. Modified managed files block update and uninstall. Failed installs and updates roll back QACraft-managed changes.

## Evaluate structured QA reports

```bash
python3 scripts/qacraft.py eval-list
python3 scripts/qacraft.py evaluate \
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
python3 scripts/qacraft.py release-check
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
├── schemas/
├── scripts/
├── shared/
├── skills/
├── tests/
├── .github/workflows/
├── AGENTS.md
├── CLAUDE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## License

MIT
