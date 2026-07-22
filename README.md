# QACraft

Reusable QA skills with safe project installers and deterministic behavior evaluations for everyday software testing work.

QACraft provides:

- 25 detailed, evidence-based QA workflow skills;
- verified project adapters for Codex and Claude Code;
- a platform-neutral generic adapter;
- preview-first install, verify, update, rollback, and uninstall lifecycle management;
- deterministic behavior evaluation for five priority QA skills;
- shared approval, evidence, security, data, result, publication, and release policies;
- versioned schemas, examples, templates, generated static documentation, validation, and tests.

QACraft skill files describe controlled QA behavior. Runtime permissions, identities, secrets, network access, production access, and external-system writes must still be enforced by the surrounding tool and approval layer.

## Quick start

Requirements:

- Python 3.10 or newer
- A local QACraft checkout
- No third-party Python dependencies

Validate QACraft:

```bash
python3 scripts/qacraft.py doctor
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/qacraft.py release-check
```

List the available skills:

```bash
python3 scripts/qacraft.py list
```

## Install skills into a project

### Codex

Preview:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project
```

Apply after reviewing the JSON plan:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Codex layout:

```text
/path/to/project/.agents/skills/<skill>/
/path/to/project/.agents/qacraft/manifest.json
```

### Claude Code

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent claude-code \
  --destination /path/to/project \
  --apply
```

Claude Code layout:

```text
/path/to/project/.claude/skills/<skill>/
/path/to/project/.claude/qacraft/manifest.json
```

Both adapters can coexist in one project because their paths and manifests are independent.

### Generic

```bash
python3 scripts/qacraft.py install feature-qa \
  --agent generic \
  --destination /path/to/installation \
  --apply
```

The generic adapter preserves `skills/` and `shared/` paths and uses `.qacraft-manifest.json`.

See `docs/INSTALLATION.md` for complete setup, safety behavior, and troubleshooting.

## Manage an installation

Verify every managed checksum:

```bash
python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination /path/to/project
```

Update to the desired final skill set:

```bash
python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Uninstall only unchanged manifest-owned files:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination /path/to/project \
  --apply
```

QACraft has no force-overwrite or force-delete option. Existing unowned files, symbolic-link redirection, changed sources, stale manifests, and modified managed files are rejected.

## Evaluate structured QA behavior

Deterministic rubrics are included for:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

List evaluation rubrics:

```bash
python3 scripts/qacraft.py eval-list
```

Evaluate the included passing example:

```bash
python3 scripts/qacraft.py evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Every candidate is checked for:

1. schema conformance;
2. source grounding and hallucination control;
3. version-bound approval gates;
4. evidence references, integrity, timestamps, and privacy review;
5. verdict discipline and release-blocker handling;
6. permission, secret, personal-data, external-write, and cleanup safety;
7. the skill-specific output contract.

Evaluation is local, deterministic, read-only, and makes no external model or network calls. It checks supplied structured data; it does not prove evidence authenticity or runtime permission enforcement.

See `docs/EVALUATIONS.md` for the full contract.

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

## Documentation

- `docs/INSTALLATION.md` — supported installation and lifecycle commands
- `docs/COMPATIBILITY.md` — agent, Python, operating-system, and evaluation coverage
- `docs/DEMO.md` — isolated end-to-end walkthrough
- `docs/EVALUATIONS.md` — structured behavior-evaluation contract
- `docs/PRODUCTION_READINESS.md` — supported production use and deliberate boundaries
- `RELEASE_CHECKLIST.md` — release acceptance process
- `CHANGELOG.md` — version history

Browse the generated static documentation at `docs/index.html`, or serve it locally:

```bash
python3 scripts/serve.py
```

Automatic GitHub Pages deployment is intentionally not included, avoiding recurring Actions usage. Static files can be published manually.

## Repository maintenance

`catalog/skills.json` is the machine-readable source for generated skill documentation.

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/qacraft.py release-check
```

Generated `SKILL.md` and HTML files are committed so users can inspect the repository without a build step.

## Important safety model

QACraft documents and validates workflow structure. It does not independently enforce:

- filesystem, command, repository, secret, or network permissions;
- authenticated approval identity;
- tenant and customer-data boundaries;
- evidence authenticity;
- production access;
- ticket, repository, deployment, or publication writes.

Adopters must implement least privilege, identity, authorisation, evidence privacy, idempotency, audit logging, and external-system safeguards through the runtime.

Never grant production, customer, or security-sensitive access merely because a skill describes safe behavior.

## Compatibility

See `docs/COMPATIBILITY.md` for the supported adapter matrix and deliberate non-support. Python 3.12 is continuously validated in one pull-request job; project metadata supports Python 3.10 and newer.

## License

MIT
