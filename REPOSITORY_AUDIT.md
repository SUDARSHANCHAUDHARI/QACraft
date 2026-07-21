# Repository Audit

## Included

- 25 QA skill packages
- 25 platform-neutral `SKILL.md` specifications
- 25 source `overview.html` files
- 25 generated documentation pages plus repository indexes
- 8 shared policy documents
- 9 JSON Schemas
- example requests, expected outputs, and report templates for every skill
- generator, local server, validator, unit tests, and GitHub Actions

## Validation performed

```bash
python3 scripts/generate_docs.py
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

Validation checks include:

- catalog completeness and unique commands,
- required file presence,
- exactly eight phases per skill,
- minimum evidence, control, decision, boundary, and output depth,
- HTML doctype, unique IDs, valid ARIA references, table captions, CSP, robots policy, print CSS, and local links,
- no external scripts or unsafe remote resources,
- local links cannot escape the repository,
- generated pages meet minimum content depth,
- malicious renderer-input escaping tests,
- JSON syntax validation for schemas and catalog.

## Result

All repository validation and unit tests pass.

Representative index and skill pages were also rendered through a print engine and visually inspected. Final screen rendering should still be reviewed in the browsers and embedded webviews used by each adopter because browser engines and local security policies differ.
