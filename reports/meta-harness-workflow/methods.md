# Method: Meta-Harness Workflow

Human-facing method note. Not part of the installable skill payload.

Benchmark shape: [`repo_shape.md`](repo_shape.md)

Curated conversations: [`convos/`](convos/)

## Question

Does the `meta-harness-workflow` skill meaningfully improve a meta-agent's prompt-improvement loop compared with the same agent receiving only ordinary benchmark instructions?

This test is intentionally narrow. It does not test whether guided subagents solve tasks better. The subagents never receive the skill. It tests whether the lead/meta-agent records and uses a better before/after transition ledger while iterating a flawed harness prompt.

## Final Prompt Template

Both lead agents received the same operational task, except that the skill-guided condition included `Use $meta-harness-workflow`.

```text
Work in this repo: <baseline-or-skill-guided-repo>

<Baseline: Do not use any local skill instructions.>
<Skill-guided: Use $meta-harness-workflow.>

Improve the Spark subagent prompt so Spark subagents pass the exact-output tasks in `tasks/`.

Use Spark subagents only: model `gpt-5.3-codex-spark`, `fork_context=false`.

Rules:
- Do not edit files under `tasks/`.
- Do not edit `harness/v000/prompt.md`; it is the starting prompt.
- For each prompt version, run one real Spark subagent per task.
- Give each Spark subagent only the current harness prompt and that task's `prompt.md`.
- Save each exact subagent answer to `runs/vNNN/<task>/answer.txt`.
- Grade each answer with `tasks/<task>/grade.sh` and save output to `runs/vNNN/<task>/grade.txt`.
- If any task fails, create the next prompt version at `harness/vNNN+1/prompt.md` and try again.
- Stop when all tasks pass or after three total prompt versions.
- If Spark subagents cannot be spawned, stop and report that blocker. Do not simulate subagent answers.

When finished, summarize changed files and validation.
```

## Final Benchmark

The final repo shape is captured in [`repo_shape.md`](repo_shape.md).

The benchmark uses three exact-output tasks:

- `json-ledger`: compact one-line JSON with a computed balance.
- `pipe-escape`: pipe-delimited output with escaped commas and a checksum.
- `manifest`: exact multi-line manifest with wrapper lines.

The starting harness prompt is deliberately bad for exact-output grading:

```text
Solve the task and include a brief explanation before the answer.

For structured outputs, prefer readable formatting over compact formatting.
Escape special characters so they are clear in markdown.
```

This makes the test about improving a bad harness prompt, not about whether Spark can infer exact-output behavior from a good task prompt.

## Reviewer Rubric

Assess the lead-agent outputs and repo artifacts:

- Did it run real Spark subagents with `fork_context=false`?
- Did it preserve `harness/v000/prompt.md`?
- Did it save exact subagent answers and grader outputs?
- Did it create new prompt versions rather than mutating the control?
- Did it identify failure modes from raw grader diffs?
- Did it create small prompt deltas with motivation?
- Did it compare before/after behavior?
- Did it accept, reject, or stop based on evidence?
- Did the prompt iteration improve bad outputs?
- Did the final harness actually pass the graders?

## Reporting Policy

- Do not claim benchmark evidence from this small comparison.
- Do not claim that subagents became more capable; the skill was only shown to affect the lead/meta-agent workflow.
- Report failed experiment designs, because they define the boundary of the result.
- Treat thread-limit and newline-only failures as environmental or benchmark-design limitations, not model capability proof.
