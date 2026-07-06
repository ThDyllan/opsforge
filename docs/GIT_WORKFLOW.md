# Git and GitHub Workflow

## Purpose

Git is used to track the history of the OpsForge project. GitHub stores the remote repository, and GitHub Actions automatically verifies pushed changes.

Each project phase must leave a clean, traceable state in the repository so the work, validation evidence, and phase history remain understandable.

## Before Starting a Phase

Run:

```powershell
git status
git pull
```

Checklist:

- [ ] Use `git status` to check whether the local repository contains uncommitted changes.
- [ ] Use `git pull` to synchronize the local repository with GitHub.
- [ ] Confirm that the starting state is clear before beginning phase work.

A new phase should not start from an unclear or dirty state unless the user explicitly decides what to do with the pending changes.

## During a Phase

- Keep changes small and understandable.
- Commit only when a meaningful step is complete.
- Do not mix unrelated changes in the same commit.
- Do not commit generated backup files, database dumps, secrets, `.env`, or local runtime artifacts.

## After Finishing a Phase

Run the standard commands after the phase Definition of Done has been verified and the user has validated the phase:

```powershell
git status
git add .
git commit -m "Validate Phase X <short phase name>"
git push
```

Use `git status` to review the final changes before staging them. The commit must represent the validated phase clearly. After `git push`, check the GitHub Actions result.

## GitHub Actions Verification

After each push, the user must check that:

- [ ] The GitHub Actions workflow started.
- [ ] Tests passed.
- [ ] The Docker build passed.
- [ ] The Trivy scan ran.
- [ ] The workflow result is green, or any non-blocking warnings are understood and documented.

## Commit Message Examples

- `Validate Phase 1 MVP1 local app`
- `Validate Phase 2 CI workflow`
- `Add project governance and risk tracking`
- `Validate Phase 3 backup and security`

## Current Workflow Choice

OpsForge currently uses a simple solo-project workflow with direct commits to `main`.

A branch and pull-request workflow can be added later if the user explicitly decides to adopt it, but it is not required for the current RNCP project scope.

## Forbidden Changes

This workflow documentation does not authorize implementation changes. Do not:

- modify application logic;
- modify GitHub Actions workflow behavior;
- modify the `Dockerfile`;
- modify `docker-compose.yml`;
- modify models, routes, schemas, runbooks, seed logic, or dashboard logic;
- add features;
- start Phase 3;
- refactor the project;
- introduce new technologies.
