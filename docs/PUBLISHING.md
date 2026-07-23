# Publishing QACraft

## GitHub Pages

QACraft documentation is published from the `docs/` directory through `.github/workflows/pages.yml`.

The workflow runs when documentation, `mkdocs.yml`, or the Pages workflow changes on `main`. It can also be run manually from GitHub Actions.

Published site:

- <https://sudarshanchaudhari.github.io/QACraft/>

## PyPI Trusted Publishing

QACraft uses OpenID Connect through `.github/workflows/publish-pypi.yml`. No long-lived PyPI API token is required.

The PyPI publisher must use these exact values:

| Field | Value |
|---|---|
| PyPI project | `qacraft` |
| GitHub owner | `SUDARSHANCHAUDHARI` |
| Repository | `QACraft` |
| Workflow | `publish-pypi.yml` |
| Environment | `pypi` |

For the first publication, create a pending Trusted Publisher in the PyPI account before re-running the workflow for `v1.4.0`. A pending publisher does not reserve the project name until publication succeeds.

The workflow validates the tag and repository, builds a wheel and source distribution, and publishes both artifacts. Future GitHub Releases trigger the workflow automatically.

## Release safety

- Publish only an existing annotated release tag.
- Keep the version in `pyproject.toml` identical to the tag without the `v` prefix.
- Run repository generation, validation, and `release-check` before upload.
- Use the protected `pypi` GitHub environment for the Trusted Publisher identity.
- Never commit a PyPI token to the repository.
