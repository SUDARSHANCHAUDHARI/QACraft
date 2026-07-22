# Installing QACraft skills

QACraft installs selected QA skills into an explicit project or installation root. Every mutation is preview-first, checksum-bound, and recorded in an adapter-specific manifest.

## Requirements

- Python 3.10 or newer
- A local checkout of QACraft
- An explicit destination directory that you own
- No third-party Python dependencies

Validate the QACraft checkout before installing anything:

```bash
python3 scripts/qacraft.py doctor
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

## List available skills

```bash
python3 scripts/qacraft.py list
```

Skill names are passed without the leading slash. For example, `/feature-qa` is selected as `feature-qa`.

## Codex project installation

Codex skills are installed under `.agents/skills/<skill>/` inside the explicit destination project.

Preview:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project
```

Apply the reviewed plan:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Manifest:

```text
/path/to/project/.agents/qacraft/manifest.json
```

## Claude Code project installation

Claude Code skills are installed under `.claude/skills/<skill>/` inside the explicit destination project.

Preview:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent claude-code \
  --destination /path/to/project
```

Apply:

```bash
python3 scripts/qacraft.py install feature-qa bug-report \
  --agent claude-code \
  --destination /path/to/project \
  --apply
```

Manifest:

```text
/path/to/project/.claude/qacraft/manifest.json
```

Codex and Claude Code installations can coexist because their skill paths and manifests are independent.

## Generic installation

The generic adapter preserves QACraft's repository-relative `skills/` and `shared/` layout. It is useful for inspection, custom adapters, and agents that do not have a verified built-in layout.

```bash
python3 scripts/qacraft.py install feature-qa \
  --agent generic \
  --destination /path/to/installation \
  --apply
```

Generic manifest:

```text
/path/to/installation/.qacraft-manifest.json
```

## Install all skills

```bash
python3 scripts/qacraft.py install --all \
  --agent codex \
  --destination /path/to/project \
  --apply
```

## Verify an installation

Verification reads the adapter manifest and recalculates every managed file checksum.

```bash
python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination /path/to/project
```

Exit code `0` means every managed file matches the manifest. Exit code `1` means the manifest is missing, unsafe, unreadable, or one or more files are missing or modified.

## Update an installation

The selected skills are the desired final installed set. Update preview shows files that would be created, replaced, or deleted.

```bash
python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project
```

Apply only after reviewing the plan:

```bash
python3 scripts/qacraft.py update feature-qa bug-report release-qa \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Update is refused when a managed file was modified, a source changed after preview, the manifest changed after preview, or an unowned destination file conflicts with a planned create. Failed updates restore created, replaced, deleted, and manifest content.

## Uninstall

Preview:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination /path/to/project
```

Apply:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination /path/to/project \
  --apply
```

Uninstall removes only unchanged files recorded in the selected adapter manifest. Unrelated files and directories are preserved. Modified or missing managed files block deletion.

## Safety behavior

QACraft intentionally has no force-overwrite or force-delete option.

- Existing files are conflicts.
- Symbolic-link redirection is rejected.
- Sources and targets must remain inside their approved roots.
- Installed copies are checksum-verified.
- Agent-specific `SKILL.md` frontmatter is normalized without changing canonical QACraft files.
- Failed installation and update operations roll back managed changes.
- User-global paths are not guessed or modified.
- Agent configuration files are not edited.

## Troubleshooting

**Destination parent does not exist**

Create the project or installation root first. QACraft does not guess a missing parent path.

**Destination files already exist**

Review the reported conflicts. QACraft will not overwrite unowned files. Remove or relocate them manually only after confirming ownership.

**Managed file is modified**

Preserve the local change, compare it with the canonical QACraft source, and decide whether to restore the managed file or uninstall manually. QACraft will not delete or replace it automatically.

**Wrong adapter selected**

Run verification with the adapter that created the installation. Each adapter uses a different manifest location.
