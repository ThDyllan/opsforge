# Phase Synchronization Protocol

## Purpose

This protocol keeps the user, ChatGPT, Claude, and Codex aligned before starting and after finishing each OpsForge project phase.

The goal is not only to deliver a working project. The process must also ensure that the user understands, learns, and can explain the project during the RNCP oral exam.

## Roles

- User: project owner and final decision-maker. The user validates scope, direction, and phase completion.
- ChatGPT: provides architecture guidance, scope control, explanation, RNCP alignment, and prompt preparation.
- Claude: provides review, scope challenge, and risk analysis.
- Codex: implementation assistant that executes explicit, validated tasks only.
- Repository documentation: source of truth for project state, decisions, evidence, and scope.

## Before Starting a Phase

- [ ] Read `PROJECT_CONTEXT.md`.
- [ ] Read `ROADMAP.md`.
- [ ] Read `DECISIONS.md`.
- [ ] Read `RISKS_AND_TECHNICAL_DEBT.md` if it exists.
- [ ] Read the previous phase verification document.
- [ ] Confirm the phase objective and Definition of Done.
- [ ] Ask for review or challenge if useful.
- [ ] Decide the exact scope with the user.
- [ ] Prepare a strict Codex prompt.
- [ ] Do not implement until the user validates the direction.

## During a Phase

- [ ] Keep changes small and verifiable.
- [ ] Do not expand scope.
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
- [ ] Commit and push the validated phase.
- [ ] Confirm GitHub Actions status if CI is affected.

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
