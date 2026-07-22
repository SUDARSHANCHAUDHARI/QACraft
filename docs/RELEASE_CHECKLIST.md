# QACraft production release checklist

## Repository integrity

- [ ] `python3 scripts/generate_docs.py` produces no uncommitted changes.
- [ ] `python3 scripts/validate_repo.py` passes.
- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `python3 scripts/qacraft.py doctor` passes.
- [ ] `python3 scripts/qacraft.py release-check` passes all release gates.
- [ ] `python3 scripts/demo.py` passes in an isolated temporary project.
- [ ] The pull request's single Python 3.12 validation job passes.

## Installer lifecycle

- [ ] Generic install, verify, update, and uninstall tests pass.
- [ ] Codex install uses `.agents/skills/` and its independent manifest.
- [ ] Claude Code install uses `.claude/skills/` and its independent manifest.
- [ ] Preview commands perform no writes.
- [ ] Existing unowned files are treated as conflicts.
- [ ] Modified managed files block update and uninstall.
- [ ] Failed mutation tests prove rollback.
- [ ] Unrelated project files and directories remain untouched.

## Evaluations

- [ ] Rubrics load for exactly the five priority skills.
- [ ] Each rubric's gates, decisions, and outputs remain bound to canonical `SKILL.md`.
- [ ] The published passing example returns exit code `0`.
- [ ] Invalid structure returns exit code `2`.
- [ ] Policy failures return exit code `1`.
- [ ] Grounding, approvals, evidence, verdict, safety, and output checks are covered.
- [ ] Documentation states that evaluation does not prove evidence authenticity.

## Documentation and release

- [ ] README commands match the CLI.
- [ ] Installation, compatibility, evaluation, and production-readiness documentation is current.
- [ ] Changelog contains the release version and date.
- [ ] `pyproject.toml` version matches the changelog.
- [ ] Project metadata includes README, MIT license, author, classifiers, and repository URLs.
- [ ] Security boundaries and unsupported capabilities are visible.
- [ ] Phase 2 roadmap is marked complete.
- [ ] CI remains PR/manual only with exactly one Python 3.12 job.

## Publication

- [ ] Merge using a reviewed, green pull request.
- [ ] Create a signed or annotated `v1.1.0` tag when ready to publish.
- [ ] Create GitHub release notes from `CHANGELOG.md`.
- [ ] Enable `/docs` branch-based GitHub Pages only when desired and supported.
- [ ] Do not add recurring or duplicate Actions workflows solely for publication.

## Runtime deployment responsibility

A QACraft repository release does not make an AI runtime safe by itself. Production adopters remain responsible for least-privilege permissions, secret handling, customer-data controls, network and command allowlists, evidence storage, approval enforcement, logging, monitoring, and incident response.
