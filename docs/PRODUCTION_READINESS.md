# QACraft production readiness

QACraft 1.3.0 is production-ready as a **source-controlled skill distribution, locally buildable package, verified multi-agent adapter set, and deterministic evaluation toolkit**. It is not a production permission system, autonomous QA executor, evidence-authenticity service, or published package-index release.

## Supported production use

- maintain 25 versioned QA workflow specifications;
- run QACraft from a checkout, editable installation, local wheel, or local source distribution;
- build a self-contained wheel from an explicit canonical-source allowlist;
- inspect and install wheel and source-distribution artifacts in isolated environments;
- install selected skills into explicit Codex, Claude Code, GitHub Copilot, Gemini CLI, OpenCode, or generic project layouts;
- run multiple adapters in one project using independent manifests;
- preview and safely apply installation changes;
- verify installed files against checksummed manifests;
- update an installed skill set with conflict detection and rollback;
- uninstall only unchanged manifest-owned files;
- evaluate structured reports for five priority QA skills with deterministic policy checks;
- regenerate and validate static documentation.

## Verified adapter acceptance

An agent adapter is added only when its project-level `SKILL.md` discovery path is supported by official product documentation. Each adapter must have:

- an explicit project skill root;
- an independent QACraft shared-policy root and manifest;
- deterministic Agent Skills frontmatter transformation;
- install, verify, update, uninstall, conflict, and cleanup coverage;
- coexistence tests with other verified adapters;
- no automatic global installation or product configuration modification.

The verified native roots are `.agents/skills`, `.claude/skills`, `.github/skills`, `.gemini/skills`, and `.opencode/skills`. Cursor and Windsurf are excluded from the verified adapter set until equivalent official Agent Skills discovery paths are available.

## Release acceptance criteria

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
qacraft release-check
python3 scripts/demo.py
```

The unit suite builds and validates both distribution artifacts. The pull-request workflow runs repository validation, the complete unit suite, and generated-file consistency in one Python 3.12 job.

## Distribution safety properties

- the repository keeps one canonical source copy;
- wheel bundles are generated only in temporary build directories;
- copied paths come from an explicit allowlist;
- symbolic links and paths outside the repository are rejected;
- cache, bytecode, VCS, virtual-environment, build, and egg-info files are excluded;
- incomplete installed bundles produce an explicit missing-assets error;
- wheel and source-distribution archives are inspected before acceptance;
- each artifact is installed and lifecycle-tested in an isolated environment;
- no package-index upload occurs automatically.

## Filesystem lifecycle safety

- every destination is explicit;
- preview is the default;
- writes require `--apply`;
- existing unowned files are conflicts;
- symbolic-link path redirection is rejected;
- sources and targets are path-contained;
- source and installed output checksums are verified;
- agent manifests are independent;
- update failures restore managed state;
- uninstall refuses modified or missing managed files;
- unrelated project files, directories, and other adapter installations are preserved.

## Behavior evaluation safety

- evaluation is local and read-only;
- no external model or runtime network call is made;
- observed claims require evidence references;
- evidence records require provenance, timestamps, privacy review, and integrity hashes;
- approvals require identity fields, timestamps, context hash, document hash, and validity;
- expired or post-generated approvals are rejected;
- success outcomes are blocked by required non-pass results or open release blockers;
- conditional outcomes require recorded risk, assumption, or uncertainty;
- external-write declarations require approval and idempotency;
- output paths must remain safe and output contracts complete.

## Operational boundaries

QACraft does not:

- enforce runtime filesystem, command, network, repository, secret, tenant, or production permissions;
- authenticate approvers or evidence producers;
- prove that screenshots, logs, traces, hashes, or source references are genuine;
- execute product tests or connect to customer environments;
- modify tickets, repositories, deployment systems, agent configuration files, or publication targets;
- automatically detect agents or install into user-global directories;
- silently overwrite or force-delete files;
- publish packages or documentation automatically.

Adopters must provide the runtime sandbox, identity, authorisation, evidence storage, external-system integrations, and audit controls described by the shared policies.

## Compatibility status

- Python 3.10 or newer is required.
- Python 3.12 is continuously validated on Ubuntu.
- macOS and Windows use cross-platform `pathlib` operations but are not both continuously tested in GitHub Actions.
- editable, local wheel, and local source-distribution installation are supported.
- no PyPI/package-index publication is claimed.
- five product-native project adapters are explicitly mapped; user-global paths remain unsupported.
- five skills have deterministic behavior rubrics; all 25 skills remain installable.

See `docs/COMPATIBILITY.md` for the complete matrix.

## Actions usage policy

The repository intentionally uses:

- one automatic job per pull request;
- Python 3.12 only;
- no automatic post-merge run;
- no scheduled workflow;
- no automatic package or Pages deployment;
- concurrency cancellation for superseded PR runs.

## Release decision

A release must not be tagged or published when `qacraft release-check` reports any failed check, adapter lifecycle tests fail, artifact tests fail, the pull-request validation job is unsuccessful, the demo fails, or generated documentation differs from committed files.
