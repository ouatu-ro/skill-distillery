# Experiment Design: Meta-Harness Workflow

Human-facing experiment plan. Not part of the installable skill payload.

Installable skill: [`../../skills/meta-harness-workflow/SKILL.md`](../../skills/meta-harness-workflow/SKILL.md)

## Goal

Evaluate whether the `meta-harness-workflow` skill changes agent behavior when designing or operating a harness-improvement loop.

The expected improvement is not just factual recall of the meta-harness idea. The skill should make agents:

- define explicit state variables
- preserve a control run
- write small, auditable prompt deltas
- compare before and after traces
- separate observations from accept/reject decisions
- name regression and reward-hacking risks

## Source Inspiration

The motivating external example is Yossi Eliaz's "Meta-harness on Islo" POC:

- Project page: <https://zozo123.github.io/meta-harness-on-islo-page/>
- Code: <https://github.com/zozo123/meta-harness-on-islo>

That POC demonstrates the backend mapping: snapshot a base environment, fork candidate/task runs, preserve logs, and let a proposer improve the harness from diagnostic traces. This experiment tests whether a portable skill captures the workflow discipline independently of that implementation.

## Conditions

Run matched agents under two conditions:

| Condition | Guidance |
|---|---|
| Baseline | No local skill instructions. |
| Skill-guided | Use `skills/meta-harness-workflow/SKILL.md` as guidance. |

Use the same target prompt, target artifacts, and answer constraints for every run.

## Primary Test Prompt

```text
Read-only design task. Do not modify files.

You are designing a meta-harness for improving coding-agent prompts over repeated subagent runs.

The meta-agent starts with a plan and a prompt scratchpad. It writes the prompt for subagents, runs the task, observes what went wrong, writes a new prompt plus a delta from the old prompt, explains why it changed the prompt, and tries again.

Write a concise spec for this workflow. Think in a Lamport-style state-machine way: define the state, transitions, invariants, and audit artifacts. The meta-agent should be able to inspect both before and after states.

Return the spec plus an experiment design for testing whether this workflow improves prompt iteration quality.
```

## Secondary Test Prompt

Use this when the primary prompt is too close to the skill text and may overfit.

```text
Read-only design task. Do not modify files.

A team wants to optimize the prompt and scaffolding used by subagents on a small benchmark. The first prompt is the control. Each later prompt should be justified by observed behavior from prior runs.

Design the run ledger and acceptance process. Include what files should be written, what each run must record, how prompt changes should be reviewed, and when a new prompt version should be accepted or rejected.
```

## Reviewer Rubric

Assess returned answers only. Do not reward reported process, command counts, or self-evaluation.

| Dimension | Strong answer |
|---|---|
| State model | Names durable state: task spec, environment, harness versions, runs, observations, deltas, decisions. |
| Transition clarity | Describes init, run, observe, propose, compare, accept/reject, and stop transitions. |
| Control integrity | Treats the first prompt/run as the baseline and prevents task/grader drift. |
| Before/after reasoning | Requires the meta-agent to inspect both prior and candidate states. |
| Delta quality | Requires exact prompt diffs, motivation, expected behavior, and non-regression expectations. |
| Trace discipline | Preserves raw logs/artifacts and avoids score-only optimization. |
| Regression handling | Explicitly checks previously passing behavior and rejects harmful changes. |
| Reward-hacking controls | Warns against leaking graders, changing task contracts, or overfitting traces. |
| Experiment usefulness | Proposes baseline vs skill-guided comparison with a practical scoring rubric. |

## Suggested Matrix

Run at least four agents:

| Run | Condition | Prompt |
|---|---|---|
| 1 | Baseline | Primary |
| 2 | Skill-guided | Primary |
| 3 | Baseline | Secondary |
| 4 | Skill-guided | Secondary |

If comparing skill snapshots, repeat the baseline near each skill-guided run to reduce provider/runtime drift. Skill snapshots are commits in this repository, not target-project commits.

## Output Capture

Store sanitized outputs in:

```text
reports/meta-harness-workflow/convos/
  <snapshot>-baseline-primary.md
  <snapshot>-skill-guided-primary.md
  <snapshot>-baseline-secondary.md
  <snapshot>-skill-guided-secondary.md
```

Do not ask answering agents to report shell command counts, timing, or file counts. If those metrics matter, measure them externally.

## Parent Assessment

The parent reviewer should produce a short report with:

- setup and date
- skill snapshot
- prompt matrix
- answer-quality table
- examples of improved or missing state-machine discipline
- bottom line on whether the skill changed behavior

Do not claim benchmark evidence from this small comparison. Treat it as evidence about answer shape, risk framing, and workflow completeness.
