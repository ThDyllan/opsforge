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
4. Run the fast SQLite unit tests.
5. Run a PostgreSQL integration test against a GitHub Actions service container.
6. Build the Docker image from the project `Dockerfile`.
7. Run a Trivy image scan against the built Docker image.

## Why Tests Run Before Docker Build

Tests run before the Docker build so application behavior is verified early.

SQLite tests provide fast feedback, while the separate PostgreSQL integration test creates a temporary database and proves the core `Service -> Alert -> Incident -> RunbookExecution -> AuditLog` flow against the runtime database engine. The temporary database is dropped after the test, so CI does not depend on or populate demonstration data. If either test step fails, the pipeline stops before spending time building and scanning a Docker image.

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

This remains intentional after the Phase 3 security review. Findings are visible and documented, but the local educational project has not defined a justified blocking threshold. A future policy change must define its acceptance criteria explicitly.

## Phase 2 Validation

Phase 2 can be validated after pushing the workflow to GitHub and confirming that:

- GitHub Actions runs on push or pull request.
- The test step runs and passes.
- The Docker image build step runs and succeeds.
- The Trivy image scan runs and is visible in CI logs.
- The CI result is documented.
- The user explicitly validates Phase 2 as complete.

## GitHub Actions Validation Result

The `CI` workflow was executed successfully on GitHub for repository `ThDyllan/opsforge`, branch `main`, commit `ad9b9df`.

Workflow run details:

- Run name: `Add Phase 2 CI workflow`
- Job: `Test, build, and scan`
- Trigger: push
- Result: succeeded

The test step passed, the Docker image build succeeded, and the Trivy image scan ran and appeared in the GitHub Actions logs.

The Trivy annotation / exit code 1 behavior is non-blocking by design because the workflow uses `continue-on-error: true`. The scan findings remain visible; Phase 3 documented the choice to keep this policy non-blocking for the current local scope.

The user explicitly validated Phase 2 after this successful GitHub Actions run.
