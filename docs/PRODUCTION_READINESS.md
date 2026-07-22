# QACraft production readiness

QACraft 1.1.0 is production-ready as a **source-controlled skill distribution and deterministic evaluation toolkit**. It is not a production permission system, autonomous QA executor, or evidence-authenticity service.

## Supported production use

- maintain 25 versioned QA workflow specifications;
- install selected skills into explicit Codex, Claude Code, or generic project layouts;
- preview and safely apply installation changes;
- verify installed files against checksummed manifests;
- update an installed skill set with conflict detection and rollback;
- uninstall only unchanged manifest-owned files;
- evaluate structured reports for five priority QA skills with deterministic policy checks;
- regenerate and validate static documentation;
- run all validation locally without third-party Python dependencies.

## Release acceptance criteria

The release is acceptable only when all of the following pass:

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/qacraft.py release-check
```

The pull-request workflow runs the first three checks plus generated-file consistency in one Python 3.12 job. `release-check` is covered by the unit suite and can also be run directly before tagging.

## Safety properties

### Filesystem lifecycle

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
- unrelated project files and directories are preserved.

### Behavior evaluation

- evaluation is local and read-only;
- no external model or network call is made;
- observed claims require evidence references;
- evidence records require source provenance, timestamps, privacy review, and integrity hashes;
- approvals require approver, role, timestamps, context hash, document hash, and validity;
- expired or post-generated approvals are rejected;
- required non-pass results and open release blockers prevent success outcomes where applicable;
- conditional outcomes require recorded risk, assumption, or uncertainty according to the skill rubric;
- external-write declarations require approval and idempotency;
- output paths must remain safe and skill output contracts must be complete.

## Operational boundaries

QACraft does not:

- enforce runtime filesystem, command, network, repository, secret, tenant, or production permissions;
- authenticate approvers or evidence producers;
- prove that screenshots, logs, traces, hashes, or source references are genuine;
- execute product tests or connect to customer environments;
- modify tickets, repositories, deployment systems, or publication targets;
- automatically install into user-global agent directories;
- silently overwrite or force-delete files;
- deploy documentation automatically.

Adopters must provide the runtime sandbox, identity, authorisation, evidence storage, external-system integrations, and audit controls described by the shared policies.

## Compatibility status

- Python 3.10 or newer is required.
- Python 3.12 is continuously validated on Ubuntu.
- macOS and Windows use cross-platform `pathlib` operations but are not both continuously tested in GitHub Actions.
- Codex and Claude Code project paths are explicitly mapped; user-global paths remain unsupported.
- Five skills have deterministic behavior rubrics; all 25 skills remain installable.

See `docs/COMPATIBILITY.md` for the complete matrix.

## Actions usage policy

The repository intentionally uses:

- one automatic job per pull request;
- Python 3.12 only;
- no automatic post-merge run;
- no scheduled workflow;
- no automatic Pages deployment;
- concurrency cancellation for superseded PR runs.

Release and documentation publishing can be performed manually to avoid recurring GitHub Actions usage.

## Release decision

A release must not be tagged when `qacraft release-check` reports any failed check, when the pull-request validation job is not successful, or when generated documentation differs from committed files.
