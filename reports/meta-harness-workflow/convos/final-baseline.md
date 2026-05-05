# Final Baseline Run

## Prompt

```text
Work in this repo: <baseline-repo>

Do not use any local skill instructions.

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

## Response

```text
Changed files:

- Added harness/v001/prompt.md to force answer-only output, no prose, no fences, and exact template preservation.
- Added harness/v002/prompt.md to additionally require a terminating newline.
- Saved real Spark outputs and grader results under:
  - runs/v000
  - runs/v001

Validation summary:

- v000: all three tasks failed. Spark followed the baseline prompt and added explanations / markdown fencing, which the exact-output graders rejected.
- v001: payload text was otherwise correct for all three tasks, but every grader still failed because the persisted answer file had no trailing newline at EOF.
- v002: not executed. Attempting to spawn the required Spark subagents failed because the runtime hit a subagent concurrency/quota limit. The run stopped without simulating outputs or switching strategies.

Net result: prompt quality improved substantially from v000 to v001, and v002 was prepared specifically to address the remaining newline-only failure, but it could not be validated because Spark subagent spawning became unavailable.
```

## Curator Notes

The baseline agent produced prompt versions and saved run evidence, but it did not create observation files, delta records, or accept/reject decisions. Its final response contained the only explicit comparison between versions.
