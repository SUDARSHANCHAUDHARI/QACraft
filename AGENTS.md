# Agent Instructions

## Command resolution

When the user invokes `/name` or asks for work matching a skill:

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
9. Validate structured output against the repository schemas.
10. Keep manual overrides separate from calculated QA outcomes.

## Repository changes

When editing a skill:

- change `catalog/skills.json`,
- run `python3 scripts/generate_docs.py`,
- run `python3 scripts/validate_repo.py`,
- run the unit tests,
- review generated diffs,
- do not hand-edit generated HTML unless the generator is changed too.
