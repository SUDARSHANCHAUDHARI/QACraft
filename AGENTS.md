# Agent Instructions

## Repository purpose

QACraft contains 25 versioned QA workflow skills, safe project installation adapters, and deterministic behavior evaluations. Skill documents describe controlled behavior but do not replace runtime permission enforcement.

## Command resolution inside this repository

When the user invokes `/name` or asks for work matching a canonical skill:

1. Locate `skills/name/SKILL.md`.
2. Read the selected skill completely.
3. Read the shared policies referenced by this repository:
   - `shared/qa-standards.md`
   - `shared/security-boundaries.md`
   - `shared/approval-policy.md`
   - `shared/evidence-policy.md`
   - `shared/data-safety.md`
   - `shared/result-model.md`
   - `shared/publication-policy.md`
   - `shared/release-policy.md` when a release outcome is involved.
4. Resolve tool and connector capabilities before claiming an action is enforceable.
5. Default to drafting and read-only analysis.
6. Require the documented gate before any external write, destructive action, production access, customer-data access, or publication.
7. Preserve invalid, blocked, error, aborted, cancelled, inconclusive, and not-tested states.
8. Never invent evidence, execution, approvals, or source content.
9. Validate structured output against repository schemas where applicable.
10. Keep manual overrides separate from calculated QA outcomes.

## Project installation

Do not manually copy QACraft skills when the supported CLI can be used.

Preview and apply through:

```bash
python3 scripts/qacraft.py install <skill> \
  --agent <codex|claude-code|generic> \
  --destination /explicit/project/root
```

Add `--apply` only after reviewing the plan. The same explicit adapter and destination must be used for `verify-install`, `update`, and `uninstall`.

Never add force-overwrite, force-delete, user-global path guessing, automatic agent detection, or configuration-file modification without a separately reviewed design and safety model.

## Behavior evaluation

Use deterministic evaluation only for supplied structured candidate reports:

```bash
python3 scripts/qacraft.py evaluate --input candidate.json
```

The evaluator does not prove evidence authenticity or runtime permission enforcement. Do not convert a failed check into a pass through narrative interpretation.

Priority rubrics currently exist for:

- `feature-qa`
- `ticket-review`
- `bug-report`
- `verify-fix`
- `release-qa`

## Repository changes

When editing a skill:

- change `catalog/skills.json` or the generator rather than hand-editing generated files;
- update shared policies or schemas when a rule applies across skills;
- regenerate documentation;
- review every generated diff.

When editing adapters, lifecycle code, schemas, rubrics, evaluation logic, or release metadata:

- preserve preview-first behavior and containment checks;
- add focused regression tests;
- update compatibility and safety documentation;
- keep canonical skill sources unchanged unless the catalog or generator intentionally changes them.

Run before proposing a release:

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/qacraft.py release-check
```

Complete branch edits before opening a pull request when practical. The repository intentionally uses one Python 3.12 validation job per PR and no automatic post-merge workflow.
