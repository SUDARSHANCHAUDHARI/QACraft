# QA Everyday Skill Pack

A repository of 25 detailed, evidence-based QA workflow specifications for everyday QA work.

Each skill contains:

- `SKILL.md`: platform-neutral operating specification
- `overview.html`: self-contained visual documentation
- `examples/request.md`: sample invocation
- `examples/expected-output.md`: sample controlled result
- `templates/report.yaml`: structured output starting point

The pack also includes shared policies, JSON Schemas, generated documentation, validation scripts, tests, and a GitHub Actions workflow.

## Skill catalog

### Planning and scope

- `/ticket-review`
- `/test-plan`
- `/regression-scope`
- `/platform-matrix`

### Execution and product behaviour

- `/feature-qa`
- `/exploratory-qa`
- `/smoke-test`
- `/permission-qa`
- `/api-qa`
- `/network-qa`
- `/offline-qa`
- `/playback-qa`

### Defects and verification

- `/bug-report`
- `/bug-triage`
- `/verify-fix`
- `/customer-issue-repro`
- `/flaky-test-triage`

### Release and operations

- `/release-qa`
- `/staged-rollout-check`
- `/incident-qa`

### Automation and maintenance

- `/automation-review`
- `/test-case-review`

### Communication and improvement

- `/qa-daily-summary`
- `/qa-handoff`
- `/qa-retrospective`

## Browse the HTML documentation

Open:

```text
docs/index.html
```

Or serve the repository locally:

```bash
python3 scripts/serve.py
```

Then open the URL printed by the script.

## Validate the repository

No third-party Python packages are required.

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

## Regenerate documentation

The machine-readable source is `catalog/skills.json`.

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
```

## Use with AI coding agents

### Claude Code

Copy or link the selected folder into your project or user skills directory:

```text
.claude/skills/<skill-name>/
```

Keep the shared policy files available and instruct the agent to read them before using a skill.

### Codex and repository-aware agents

Place this repository beside the project or copy the selected `SKILL.md` into the project. `AGENTS.md` explains how to resolve commands and shared policies.

### Other agents

Load the selected `SKILL.md` plus the shared policies as instructions. The workflow remains platform-neutral, but tool names and external-system actions need adapters.

## Important safety model

These documents are specifications, not security enforcement.

Production use requires:

- least-privilege runtime permissions,
- command and network allowlists,
- secret isolation,
- version-bound approvals,
- evidence privacy and integrity controls,
- safe data ownership and cleanup,
- idempotent external writes,
- conflict-aware publication,
- monitoring and audit logs.

Never grant production, customer, or security-sensitive access merely because a skill file describes safe behaviour.

## Repository structure

```text
qa-everyday-skill-pack/
├── catalog/
├── docs/
├── schemas/
├── scripts/
├── shared/
├── skills/
├── tests/
├── .github/workflows/
├── AGENTS.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## License

MIT
