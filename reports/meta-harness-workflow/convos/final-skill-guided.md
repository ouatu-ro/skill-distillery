# Final Skill-Guided Run

## Prompt

```text
Work in this repo: <skill-guided-repo>

Use $meta-harness-workflow.

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
Created two new harness versions at harness/v001/prompt.md and harness/v002/prompt.md, with transition records at harness/v001/delta.md and harness/v002/delta.md. The run also recorded observations at observations/v000.md, observations/v001.md, and observations/v002.md, plus stop/accept decisions at decisions/v001.md and decisions/v002.md. Exact Spark answers and grader outputs were saved under runs/. Nothing under tasks/ or harness/v000/prompt.md was edited.

Validation used real gpt-5.3-codex-spark subagents with fork_context=false, one per task per version. v000 failed on explanation/markdown behavior, v001 fixed output shape but still missed trailing newlines and got one checksum wrong, and v002 fixed the checksum so all three answers were payload-correct if final newlines are ignored. The remaining failure at v002 was consistent across all tasks: the persisted answer files still lacked final trailing newlines, so all three graders failed only on EOF newline. With the three-version budget exhausted, the run stops there.
```

## Curator Notes

The skill-guided agent produced the same basic prompt-version and run artifacts as the baseline, plus a transition ledger: observations, deltas, and decisions. It did not produce a strict green benchmark.
