# Contributing

## Change source

`catalog/skills.json` is the source for generated skill documentation.

## Workflow

1. Create a focused branch.
2. Update the catalog or generator.
3. Update shared policies or schemas when the rule is cross-skill.
4. Run:

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

5. Review every changed `SKILL.md` and HTML page.
6. Explain compatibility and safety impact in the pull request.

## Content requirements

- Preserve platform-neutral wording.
- Define scope and non-goals.
- Use explicit phases and approval gates.
- Separate attempts, verdicts, decisions, publication, and overrides.
- Define evidence appropriate to each claim.
- Avoid absolute guarantees that depend on the model.
- State known limits.
- Keep examples synthetic.
- Do not include credentials, private URLs, customer data, or machine-specific paths.

## Generated files

Generated HTML and skill files are committed so users can browse the repository without a build step.
