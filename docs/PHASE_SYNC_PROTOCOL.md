# Phase Synchronization Protocol

## Purpose

This protocol keeps the user, ChatGPT, Claude, and Codex aligned before starting and after finishing each OpsForge project phase.

The goal is not only to deliver a working project. The process must also ensure that the user understands, learns, and can explain the project during the RNCP oral exam.

## Roles

- User: project owner and final decision-maker. The user validates scope, direction, and phase completion.
- ChatGPT: provides architecture guidance, scope control, explanation, RNCP alignment, and prompt preparation.
- Claude: provides review, scope challenge, and risk analysis.
- Codex: primary technical engineering partner. It performs discovery, gives an engineering recommendation, implements approved work, and explains the resulting tradeoffs.
- Repository documentation: source of truth for project state, decisions, evidence, and scope.

## Before Starting a Phase

- [ ] Read `PROJECT_CONTEXT.md`.
- [ ] Read `ROADMAP.md`.
- [ ] Read `DECISIONS.md`.
- [ ] Read `RISKS_AND_TECHNICAL_DEBT.md` if it exists.
- [ ] Read `GIT_WORKFLOW.md`.
- [ ] Read the previous phase verification document.
- [ ] Run `git status` and confirm that pending changes are understood.
- [ ] Run `git pull` to synchronize the local repository with GitHub.
- [ ] Do not start from an unclear or dirty state unless the user explicitly decides how to handle pending changes.
- [ ] Confirm the phase objective and Definition of Done.
- [ ] Ask for review or challenge if useful.
- [ ] Decide the exact scope with the user.
- [ ] Prepare an engineering brief with evidence, recommendation, verification plan, and rollback path.
- [ ] Do not make a broad implementation change until the user validates the direction.

## During a Phase

- [ ] Keep changes small and verifiable.
- [ ] Do not expand scope without explicitly recording and validating the reason.
- [ ] Stop and ask if a decision is not covered.
- [ ] Update documentation when behavior, decisions, or validation evidence changes.
- [ ] Preserve the distinction between educational MVP scope and production-ready scope.

## After Finishing a Phase

- [ ] Verify the phase Definition of Done.
- [ ] Document evidence in a phase verification file.
- [ ] Update `ROADMAP.md`.
- [ ] Update `PROJECT_CONTEXT.md`.
- [ ] Update `INDEX.md` if new documentation files were added.
- [ ] Update `DECISIONS.md` if new architecture or technical decisions were made.
- [ ] Ask for review or challenge if useful.
- [ ] The user explicitly validates the phase as complete.
- [ ] Run `git status` and review the final phase changes.
- [ ] Commit and push the validated phase according to `GIT_WORKFLOW.md`.
- [ ] After the push, confirm that GitHub Actions started, tests passed, the Docker build passed, and the Trivy scan ran.
- [ ] Confirm that the workflow is green or that any non-blocking warnings are understood and documented.

## Anti-Scope-Creep Rule

New ideas discovered during a phase must be handled in one of three ways:

- rejected as out of scope;
- documented as future work;
- explicitly approved by the user before implementation.

No new idea should silently enter the current phase.

## Oral Exam Learning Rule

After each phase, the user should be able to answer:

- What was built?
- Why was it built?
- How does it work?
- How was it verified?
- What are its limits?
- What would be improved later?

If these questions cannot be answered clearly, the phase documentation and explanation are not yet complete.
