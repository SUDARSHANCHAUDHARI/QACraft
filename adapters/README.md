# QACraft adapter contract

Adapters translate QACraft's platform-neutral skill layout into an agent-specific installation plan.

Phase 2.1 does not install files. It defines the rules every future adapter must follow.

## Required adapter behavior

An adapter must:

1. Accept an explicit destination.
2. Resolve only paths inside that destination.
3. Produce a complete preview before any write.
4. Identify every skill file and shared policy that would be installed.
5. Detect conflicts and existing files.
6. Never overwrite, delete, or replace files without explicit approval.
7. Record a versioned installation manifest.
8. Support rollback and uninstall using that manifest.
9. Preserve QACraft source files unchanged.
10. Avoid claiming that prompt instructions enforce runtime permissions.

## Initial adapter identifiers

- `generic`
- `claude-code`
- `codex`

The identifiers are accepted by the read-only planner, but agent-specific destination assumptions are intentionally not implemented yet.

## Planned manifest fields

```json
{
  "qacraft_version": "",
  "agent": "",
  "destination": "",
  "installed_at": "",
  "skills": [],
  "shared_policies": [],
  "files": [
    {
      "path": "",
      "source": "",
      "sha256": "",
      "previous_sha256": null,
      "operation": "create"
    }
  ]
}
```

## Non-goals for Phase 2.1

- No copying or symlinking
- No automatic agent detection
- No modification of user configuration
- No network access
- No package publishing
- No update or uninstall execution
