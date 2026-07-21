## What changed

Describe the skill, policy, schema, documentation, or tooling change.

## Why

Explain the problem this change solves.

## Safety impact

- [ ] No external write permissions were added
- [ ] No production or customer access was added
- [ ] Approval gates remain explicit
- [ ] Evidence and uncertainty remain visible
- [ ] Generated files were regenerated

## Validation

- [ ] `python3 scripts/generate_docs.py`
- [ ] `python3 scripts/validate_repo.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Generated diffs were reviewed
