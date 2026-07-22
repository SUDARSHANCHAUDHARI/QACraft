# Phase 2 development plan

Phase 2 turns QACraft from a repository of QA workflow specifications into an installable and behavior-tested platform.

## Phase 2.1 — Foundation

This first slice is intentionally read-only.

Included:

- `scripts/qacraft.py list`
- `scripts/qacraft.py doctor`
- `scripts/qacraft.py plan-install`
- adapter safety contract
- automated CLI tests

Not included:

- file installation
- symlink creation
- overwrite handling
- automatic agent detection
- update or uninstall
- behavior evaluation execution

## Commands

List available skills:

```bash
python3 scripts/qacraft.py list
```

Check repository health:

```bash
python3 scripts/qacraft.py doctor
```

Preview an installation plan without changing files:

```bash
python3 scripts/qacraft.py plan-install feature-qa bug-report \
  --agent generic \
  --destination ./example-agent-skills
```

Preview all skills:

```bash
python3 scripts/qacraft.py plan-install --all \
  --agent generic \
  --destination ./example-agent-skills
```

## Safety model

Phase 2.1 performs no writes to the selected destination. The planner exists to make future installation behavior reviewable before mutation support is introduced.

A later installer must provide:

- destination containment checks
- a complete dry-run preview
- conflict detection
- explicit overwrite approval
- versioned manifests
- checksums
- rollback
- idempotent update behavior
- safe uninstall

## Next slice

Phase 2.2 should implement a generic adapter first. Agent-specific adapters should follow only after their destination formats and instruction-loading behavior are verified.

The generic installer must remain opt-in and should refuse ambiguous or unsafe destinations.
