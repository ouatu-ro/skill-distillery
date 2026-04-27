# Plan: Distill Dirac Into An AST-First Code Workflow Skill

## Goal

Create a compact Codex skill in `<repo>` that captures Dirac's reusable workflow discipline for structural code inspection, AST-aware symbol lookup, safe editing, and concise completion reporting without copying Dirac's runtime, database, parser loading, or provider-specific tooling.

## Scope

In scope:
- Create a workflow skill using the standard Codex skill structure.
- Keep `SKILL.md` concise and triggerable.
- Add one-level reference files only when they reduce context load.
- Capture Dirac-derived heuristics for skeleton-first inspection, symbol-level reads, reference mapping, safe symbol edits, batching, fallbacks, and verification.
- Validate the skill with the skill-creator validation script.
- Use GPT-5.4 subagents sequentially for bounded extraction/review subtasks.

Out of scope:
- Reimplement Dirac's tool handlers, symbol index, AST parser loading, persistence, or provider schema conversion.
- Build scripts, assets, or a runnable Dirac clone.
- Add broad documentation files such as README, changelog, or installation guide.

## Assumptions

- The skill will live as a nested skill folder under `<repo>`, likely `skills/ast-code-workflow`.
- The repo root plan file is the durable execution state.
- The source Dirac repo is `<dirac-repo>`.
- Skill initialization should use `<skill-creator>/scripts/init_skill.py`.

## Steps

- [x] S1: Commit this baseline plan.
- [x] S2: Use a GPT-5.4 subagent to extract concise Dirac workflow facts from source prompt/tool files.
- [ ] S3: Initialize the skill skeleton with references support.
- [ ] S4: Write `SKILL.md` and reference files.
- [ ] S5: Use a GPT-5.4 subagent to review the draft skill for trigger clarity, bloat, and missing safety rules.
- [ ] S6: Validate, revise, and commit the finished skill.

## Validation

- Skill validation: `<skill-creator>/scripts/quick_validate.py skills/ast-code-workflow`
- Content review: inspect generated `SKILL.md`, `references/dirac-tool-map.md`, and `references/examples.md`
- Git: `git -C <repo> status --short`

## Progress Log

- 2026-04-27 16:40: Plan created.
- 2026-04-27 16:41: Committed baseline plan as `736557a`.
- 2026-04-27 16:43: GPT-5.4 extraction subagent completed; findings will inform `SKILL.md` and references.

## Findings / Debt

- None yet.

## Completion Criteria

- `skills/ast-code-workflow/SKILL.md` exists with valid frontmatter.
- Optional references are one level deep and directly linked from `SKILL.md`.
- No unnecessary README/changelog/install docs are added.
- Skill validation passes.
- Work is committed in `<repo>`.
