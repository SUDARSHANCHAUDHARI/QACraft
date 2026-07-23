# Publishing QACraft

## GitHub Pages

QACraft documentation is published from the `docs/` directory through `.github/workflows/pages.yml`.

The workflow runs when documentation, `mkdocs.yml`, or the Pages workflow changes on `main`. It can also be run manually from GitHub Actions.

Published site:

- <https://sudarshanchaudhari.github.io/QACraft/>

## PyPI Trusted Publishing

QACraft uses OpenID Connect through `.github/workflows/publish-pypi.yml`. No long-lived PyPI API token is required.

The PyPI publisher uses these exact values:

| Field | Value |
|---|---|
| PyPI project | `qacraft` |
| GitHub owner | `SUDARSHANCHAUDHARI` |
| Repository | `QACraft` |
| Workflow | `publish-pypi.yml` |
| Environment | `pypi` |

## Annotated release tags

`.github/workflows/create-release-tag.yml` creates an annotated tag for the version already declared in `pyproject.toml`, verifies that the changelog contains that version, and explicitly starts the publisher.

The workflow runs once when first added to `main`. Later releases use its manual input after the version change has passed pull-request validation. If the tag already exists, the workflow verifies that it points to the selected `main` commit instead of moving it.

## Build-once publication

A release starts from an annotated version tag such as `v1.4.1`, or from a manual workflow run selecting an existing annotated tag.

The publication workflow:

1. checks out the tagged source;
2. verifies that the tag matches the version in `pyproject.toml`;
3. runs documentation generation, repository validation, and `release-check`;
4. builds one wheel and one source distribution into `dist/`;
5. creates or updates the GitHub Release with those files;
6. publishes the exact same files from `dist/` to PyPI.

Building once prevents the GitHub Release and PyPI copies from differing because of archive timestamps or other build-time metadata. Published SHA-256 values can therefore be compared directly.

## Release safety

- Publish only an annotated version tag that matches `pyproject.toml`.
- Run repository generation, validation, tests, and `release-check` before tagging.
- Never move an existing release tag.
- Build wheel and source distribution once per version.
- Upload the same build directory to GitHub Releases and PyPI.
- Use the protected `pypi` GitHub environment for the Trusted Publisher identity.
- Never commit a PyPI token to the repository.
- Never replace an already published PyPI version; use a patch release for corrections.
