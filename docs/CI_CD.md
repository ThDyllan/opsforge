# OpsForge CI/CD

## Purpose

Phase 2 adds the first CI/CD pipeline for OpsForge using GitHub Actions.

The pipeline checks that the MVP1 application can be tested, packaged as a Docker image, and scanned for container vulnerabilities before later deployment phases are added.

## When the Pipeline Runs

The workflow runs on:

- `push`
- `pull_request`

This means changes are checked when they are pushed to GitHub and when a pull request is opened or updated.

## Workflow Steps

The workflow is defined in `.github/workflows/ci.yml`.

It performs these steps:

1. Checkout the repository.
2. Set up Python 3.12.
3. Install dependencies from `requirements.txt`.
4. Run `pytest`.
5. Build the Docker image from the project `Dockerfile`.
6. Run a Trivy image scan against the built Docker image.

## Why Tests Run Before Docker Build

Tests run before the Docker build so basic application behavior is verified early.

If tests fail, the pipeline stops before spending time building and scanning a Docker image. This keeps the CI feedback loop simple and easy to explain.

## Docker Image Build

The workflow builds the API image with a tag based on the GitHub commit SHA:

```text
opsforge-api:${{ github.sha }}
```

The image is built only inside CI for validation.

## Why the Image Is Not Pushed in Phase 2

Phase 2 does not push the Docker image to a registry.

This is intentional because the current phase is CI/CD preparation only. Registry publishing, deployment, and release strategy should be decided later when the project needs them.

Keeping the image local to the CI runner avoids adding credentials, registry configuration, and release policy before they are needed.

## Trivy Image Scan

The workflow uses Trivy to scan the built Docker image for operating system and library vulnerabilities.

The scan is visible in GitHub Actions logs and currently checks `HIGH` and `CRITICAL` vulnerabilities.

## Blocking Policy

For this first Phase 2 implementation, the Trivy scan is non-blocking.

The scan is configured to report findings, but the workflow continues even if Trivy detects vulnerabilities.

This is intentional for MVP1 because the project does not yet define a formal vulnerability acceptance policy. Phase 3 will define stricter security expectations, including how security findings should be handled.

## Phase 2 Validation

Phase 2 can be validated after pushing the workflow to GitHub and confirming that:

- GitHub Actions runs on push or pull request.
- The test step runs and passes.
- The Docker image build step runs and succeeds.
- The Trivy image scan runs and is visible in CI logs.
- The CI result is documented.
- The user explicitly validates Phase 2 as complete.
