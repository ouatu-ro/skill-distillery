# Report: Meta-Harness Workflow

Human-facing report. Not part of the installable skill payload.

Method: [`methods.md`](methods.md)

Benchmark shape: [`repo_shape.md`](repo_shape.md)

Curated conversations: [`convos/`](convos/)

Short scan note: [`limitations.md`](limitations.md)

## What Was Tested

This tested a demonstrative skill based on the Meta-Harness idea: use a lead/meta-agent to improve a flawed agent harness prompt by running subagents, inspecting outputs and grader diffs, writing prompt deltas with motivation, and rerunning.

The tested question was narrow:

> Does `meta-harness-workflow` improve the lead agent's prompt-improvement process compared with the same lead agent receiving ordinary benchmark instructions?

It did not test whether subagents become more capable. The Spark subagents never received the skill.

## Why The Experiment Was Hard To Design

It was not obvious what the skill should improve. Early attempts either gave the baseline too much of the meta-harness method or gave tasks that Spark could solve on the first try.

The final meaningful setup used easy-to-medium exact-output tasks with a deliberately bad starting harness prompt. That made the test about whether the lead agent could correct an imprecise prompt from evidence.

## Final Setup

Lead-agent model:

`gpt-5.4`

Subagent model:

`gpt-5.3-codex-spark`

Final benchmark:

- `json-ledger`
- `pipe-escape`
- `manifest`

Starting prompt:

```text
Solve the task and include a brief explanation before the answer.

For structured outputs, prefer readable formatting over compact formatting.
Escape special characters so they are clear in markdown.
```

The baseline and skill-guided repos had the same contents. The only intended difference was that the skill-guided lead agent was told to use `$meta-harness-workflow`.

## Final Runs

| Condition | Result |
|---|---|
| Baseline | Ran `v000` and `v001`, wrote `v002`, but could not validate `v002` because subagent spawning hit a concurrency/quota limit. No observations, deltas, or decisions were recorded. |
| Skill-guided | Ran `v000`, `v001`, and `v002`; recorded observations, deltas, and decisions. `v002` fixed the visible payloads but still failed on missing trailing newlines. |

Because the baseline did not validate `v002`, the strongest comparison is auditability and artifact discipline, not final prompt quality.

## Outcome Summary

| Dimension | Baseline | Skill-guided |
|---|---|---|
| Real Spark subagents used | Yes | Yes |
| `harness/v000` preserved | Yes | Yes |
| Exact answers and grade outputs saved | Yes | Yes |
| New prompt versions created | Yes | Yes |
| Observations written | No | Yes |
| Prompt deltas written | No | Yes |
| Accept/reject/stop decisions written | No | Yes |
| Failure comparison across versions | Present in final prose only | Persisted in repo artifacts |
| Final validated pass | No | No |

## What Improved

The skill-guided lead agent produced a better audit trail. It recorded:

- what the control prompt did wrong
- why `v001` was a net improvement
- why `v002` targeted the remaining failures
- what changed between versions
- why the run stopped after `v002`

This is the clearest demonstrated value of the skill: it improves the meta-agent's transition discipline and makes prompt iteration inspectable after the fact.

## What Did Not Improve

The skill did not demonstrate that guided subagents perform better. The subagents never saw the skill; they only received clearer harness prompts produced by the lead agent.

The skill-guided loop produced the expected payload text if the final newline is ignored. It did not produce a strict green benchmark because the persisted answer files lacked final trailing newlines, so the `diff -u` graders still failed. This is a byte-level strict-output failure: useful evidence about exact-output brittleness, but not strong evidence about general reasoning or coding capability.

## Failed Experiment Attempts

Several earlier setups were not meaningful:

- A process-design task asked agents to design the meta-harness method itself. Both agents could satisfy it without actually running subagents.
- An issue-triage prompt-iteration task again encouraged process artifacts instead of a real optimization loop.
- A first exact-output suite was too easy, and the task prompts were clear enough that Spark passed all tasks on the first try. There was no prompt-improvement surface.
- A stricter exact-output suite initially failed for the wrong reason: neither condition could fix `pipe-escape` because the benchmark itself was inconsistent. The prompt implied checksum `35`, but the grader expected `34`.
- After fixing that grader bug, the baseline still passed on the first try because the starting harness prompt was not misleading enough.
- The final setup deliberately made `harness/v000/prompt.md` bad for exact-output work: it asked for explanations, readable formatting, and markdown-safe escaping. That created a real prompt-repair problem without making the tasks themselves hard.

These failures shaped the final test: easy-to-grade tasks, an intentionally misaligned harness prompt, real Spark runs, and before/after prompt versions. The final test therefore measures whether the skill helps repair an imprecise prompt from evidence, not whether it solves inherently hard tasks.

## Interpretation

The skill works as a prompt-improvement discipline. It helps a lead agent preserve evidence and explain why each prompt change exists.

It does not prove that a meta-agent improves guided-agent capabilities. The more defensible conclusion is:

> `meta-harness-workflow` helps improve intentionally misaligned or imprecise harness prompts by forcing explicit observations, deltas, and decisions. It was not shown to make subagents intrinsically better.

Practically, it is still better to write stronger prompts up front when possible. A meta-harness loop is useful when prompts are unclear, when failures need to be audited, or when repeated prompt changes need a causal ledger.

## Bottom Line

This is a successful smoke demonstration of auditability and disciplined prompt iteration, not benchmark proof of capability improvement.
