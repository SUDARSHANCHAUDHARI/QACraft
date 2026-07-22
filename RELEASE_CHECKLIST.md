# QACraft release checklist

Use this checklist for every tagged QACraft release.

## Scope and version

- [ ] The release scope is documented in `CHANGELOG.md`.
- [ ] `pyproject.toml` contains the intended semantic version.
- [ ] The changelog contains a dated heading for that exact version.
- [ ] Compatibility changes and deliberate limitations are documented.

## Generated content and repository validation

Run from the repository root:

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/qacraft.py release-check
```

- [ ] Documentation generation succeeds.
- [ ] Repository validation succeeds.
- [ ] The full unit and integration suite succeeds.
- [ ] `qacraft release-check` reports every check as PASS.
- [ ] `git diff --exit-code` is clean after generation and validation.

## Installer lifecycle

- [ ] Generic installation preview and apply are covered by tests.
- [ ] Codex installation uses `.agents/skills/` and its independent manifest.
- [ ] Claude Code installation uses `.claude/skills/` and its independent manifest.
- [ ] Verification detects missing and modified managed files.
- [ ] Update supports create, replace, delete, conflict refusal, and rollback.
- [ ] Uninstall removes only unchanged manifest-owned files.
- [ ] Unrelated project files and directories remain untouched.
- [ ] No force-overwrite or force-delete path was introduced.

## Behavior evaluation

- [ ] Rubrics cover the five published priority skills.
- [ ] Rubric approval gates match canonical `SKILL.md` files.
- [ ] Rubric decisions match canonical result states or ordered decisions.
- [ ] Rubric required outputs match canonical output contracts.
- [ ] The published passing example passes all seven evaluation checks.
- [ ] Failed candidates return deterministic findings and exit code `1`.
- [ ] Invalid input returns exit code `2`.
- [ ] Evaluation remains local, deterministic, read-only, and network-free.

## Security and privacy

- [ ] No credential, private URL, customer data, or machine-specific path was committed.
- [ ] Symbolic-link and path-containment protections remain tested.
- [ ] Source and installed-output checksums remain verified.
- [ ] Approval and evidence timestamp binding remains tested.
- [ ] Documentation does not claim that prompt text enforces runtime permissions.
- [ ] Security reporting instructions remain current.

## GitHub Actions usage

- [ ] The workflow is pull-request/manual only.
- [ ] Exactly one Python 3.12 validation job runs automatically per PR.
- [ ] No automatic post-merge, scheduled, or Pages deployment workflow was added.
- [ ] All branch edits were completed before opening the release PR when practical.

## Pull request and release

- [ ] The release PR explains features, safety impact, compatibility, and Actions usage.
- [ ] The single validation job succeeds on the final release commit.
- [ ] The PR is merged using the intended commit SHA.
- [ ] The release tag points to the merged release commit.
- [ ] Release notes match `CHANGELOG.md`.
- [ ] Phase or milestone issues are updated and closed only after merge.
