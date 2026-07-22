# Contributing

## Sources of truth

- `catalog/skills.json` is the source for generated skill documentation.
- `scripts/generate_docs.py` renders canonical `SKILL.md` and HTML files.
- `shared/` contains cross-skill policies.
- `schemas/` contains versioned structured-data contracts.
- `evaluations/rubrics.json` contains deterministic behavior rules for the five priority skills.
- `scripts/qacraft_adapters.py` defines verified installation layouts.
- `qacraft_build.py` defines the reviewed wheel bundle allowlist.
- `MANIFEST.in` defines source-distribution inputs.

Do not hand-edit generated skill or HTML files unless the generator or catalog is changed too. Do not commit a generated `qacraft/bundle` directory; it is created only in temporary build output.

## Development workflow

1. Create a focused branch from current `main`.
2. Change the smallest correct source area.
3. Add or update focused tests.
4. Update compatibility, safety, and usage documentation when behavior changes.
5. Run:

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
qacraft release-check
python3 scripts/demo.py
```

6. Review generated and hand-written diffs.
7. Explain behavior, compatibility, safety, rollback, artifact, and GitHub Actions impact in the pull request.

Complete branch edits before opening the pull request when practical. QACraft intentionally runs one automatic Python 3.12 job per PR and no automatic post-merge validation.

## Skill content requirements

- Preserve platform-neutral canonical wording.
- Define scope and non-goals.
- Use explicit phases and approval gates.
- Separate attempts, result states, workflow decisions, publication, and overrides.
- Define evidence appropriate to each claim.
- Avoid absolute guarantees that depend on the model.
- State known limits.
- Keep examples synthetic.
- Do not include credentials, private URLs, customer data, or machine-specific paths.

## Installer and lifecycle requirements

Changes to install, verify, update, rollback, or uninstall behavior must preserve:

- explicit destination roots;
- preview-first mutation;
- `--apply` for writes;
- source and target containment;
- symbolic-link refusal;
- unowned-file conflict protection;
- checksum-bound sources, outputs, and manifests;
- rollback of managed update changes;
- refusal to delete modified or missing managed files;
- preservation of unrelated project content;
- independent generic, Codex, and Claude Code manifests.

Do not add force-overwrite, force-delete, automatic global installation, automatic agent detection, or agent configuration modification without an independently reviewed security design.

## Distribution requirements

Changes to packaging must preserve:

- one canonical repository source tree;
- generation of `qacraft/bundle` only under temporary build output;
- an explicit reviewed bundle allowlist;
- rejection of symbolic links and source paths outside the repository;
- exclusion of VCS metadata, caches, bytecode, environments, build output, and egg metadata;
- complete wheel and source-distribution archive inspection;
- isolated installation and lifecycle tests for both artifact types;
- explicit failure for missing installed assets;
- zero QACraft runtime dependencies;
- no package-index publication without separate approval.

Every path required by installed `doctor`, lifecycle commands, evaluation, demo, or release checks must be represented in the build allowlist and source manifest.

## Evaluation requirements

A behavior rubric must remain bound to its canonical skill:

- approval gates must match `SKILL.md`;
- allowed decisions must exist in result states or ordered decision policy;
- required outputs must match the output contract;
- checks must remain deterministic and explain exact failures;
- evaluation must remain local, read-only, and network-free;
- evaluation must not claim to authenticate evidence or enforce runtime permissions.

Add tests for every new rule and at least one targeted failure case.

## Schema changes

- Use semantic schema versions.
- Keep schemas and runtime validation aligned.
- Document compatibility and migration impact.
- Never silently reinterpret an existing field.

## Release changes

Update `CHANGELOG.md`, `docs/COMPATIBILITY.md`, and `docs/PRODUCTION_READINESS.md` when preparing a release. Follow `docs/RELEASE_CHECKLIST.md`. A release branch must not be merged when `qacraft release-check`, artifact verification, the demo, or the pull-request validation job fails.
