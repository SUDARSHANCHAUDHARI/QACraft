# QACraft production release checklist

## Repository integrity

- [ ] `python3 scripts/generate_docs.py` produces no uncommitted changes.
- [ ] `python3 scripts/validate_repo.py` passes.
- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `qacraft doctor` passes.
- [ ] `qacraft release-check` passes all release gates.
- [ ] `python3 scripts/demo.py` passes in an isolated temporary project.
- [ ] The pull request's single Python 3.12 validation job passes.

## CLI and artifact distribution

- [ ] `python -m qacraft list` works from the source checkout.
- [ ] `pip install --no-deps -e .` succeeds in a clean temporary environment.
- [ ] `qacraft`, `python -m qacraft`, and `python3 scripts/qacraft.py` remain compatible.
- [ ] A wheel and source distribution build from a temporary clean source copy.
- [ ] The wheel contains `qacraft/bundle` with every required runtime and canonical asset.
- [ ] The source distribution contains the canonical sources, tests, manifest, and build recipe.
- [ ] Neither archive contains VCS metadata, bytecode, caches, virtual environments, or build output.
- [ ] Each artifact installs into a separate environment.
- [ ] Each installed artifact passes doctor, evaluation, release-check, and lifecycle smoke tests.
- [ ] The installed release check validates the evaluation fixture catalog.
- [ ] Incomplete installed assets fail explicitly.
- [ ] No package-index publication is claimed unless an upload is separately reviewed and performed.

## Verified adapters

- [ ] Generic export uses `skills/` and `.qacraft-manifest.json`.
- [ ] Codex uses `.agents/skills/` and `.agents/qacraft/manifest.json`.
- [ ] Claude Code uses `.claude/skills/` and `.claude/qacraft/manifest.json`.
- [ ] GitHub Copilot uses `.github/skills/` and `.github/qacraft/manifest.json`.
- [ ] Gemini CLI uses `.gemini/skills/` and `.gemini/qacraft/manifest.json`.
- [ ] OpenCode uses `.opencode/skills/` and `.opencode/qacraft/manifest.json`.
- [ ] Every product adapter path is supported by official product documentation.
- [ ] Installed `SKILL.md` files contain valid `name` and `description` frontmatter.
- [ ] All product adapters can coexist with independent manifests.
- [ ] Update and uninstall affect only the selected adapter.
- [ ] Conflicts, modified files, symlinks, and unsafe paths remain blocked.
- [ ] Unrelated project files and directories remain untouched.
- [ ] No automatic agent detection, user-global installation, or agent configuration modification was added.

## Evaluations

- [ ] Rubrics load for exactly the ten priority skills.
- [ ] Candidate schema skill enumeration exactly matches the rubric catalog.
- [ ] Each rubric's gates, decisions, and outputs remain bound to canonical `SKILL.md`.
- [ ] `evaluations/fixtures.json` has unique, safe paths.
- [ ] Every published passing example returns exit code `0`.
- [ ] Every targeted failure fixture returns exit code `1`.
- [ ] Each negative fixture includes its expected failed policy check.
- [ ] Invalid structure returns exit code `2`.
- [ ] Grounding, approvals, evidence, verdict, safety, and output checks are covered.
- [ ] Planning and scoping outcomes are not presented as product execution passes.
- [ ] Customer `NOT REPRODUCED` outcomes retain recorded uncertainty.
- [ ] Rollout `CONTINUE` rejects required failed results.
- [ ] Documentation states that evaluation does not prove evidence authenticity.

## Documentation and release

- [ ] README commands match the CLI and artifact build recipe.
- [ ] Installation, compatibility, evaluation, and production-readiness documentation is current.
- [ ] Changelog contains the release version and date.
- [ ] `pyproject.toml` version matches the changelog.
- [ ] Project metadata includes README, MIT license, author, classifiers, repository URLs, build backend, entry point, bundle builder, and source manifest.
- [ ] Security boundaries and unsupported capabilities are visible.
- [ ] Completed roadmaps are marked complete and new work is tracked separately.
- [ ] CI remains PR/manual only with exactly one Python 3.12 job.

## Publication

- [ ] Merge using a reviewed, green pull request.
- [ ] Create a signed or annotated tag matching the release version when ready to publish.
- [ ] Create GitHub release notes from `CHANGELOG.md`.
- [ ] Publish to a package index only through a separately approved release process.
- [ ] Enable `/docs` branch-based GitHub Pages only when desired and supported.
- [ ] Do not add recurring or duplicate Actions workflows solely for publication.

## Runtime deployment responsibility

A QACraft repository release does not make an AI runtime safe by itself. Production adopters remain responsible for least-privilege permissions, secret handling, customer-data controls, network and command allowlists, evidence storage, approval enforcement, logging, monitoring, and incident response.
