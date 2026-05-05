---
name: meta-harness-workflow
description: "Use when designing, running, or improving a meta-harness: an agent workflow that iteratively improves prompts, tools, or scaffolding by comparing before/after agent runs. Prefer explicit state, transition logs, prompt deltas, expected-vs-actual observations, regression checks, and accepted-version tracking."
---

# Meta-Harness Workflow

Use this skill when an agent is improving another agent's harness: prompts, tool access, scaffolding, task instructions, grading shape, or evaluation workflow.

The core discipline is state-machine thinking. A prompt change is not valid just because it feels better; it must be recorded as a transition from a known before-state to an observed after-state.

Operational rule: do not mutate a prior harness version in place. If the current prompt is `harness/v000/prompt.md`, a change creates `harness/v001/prompt.md` plus a transition record. The old version remains the auditable before-state.

## Core Model

A meta-harness has these state variables:

- `TaskSpec`: immutable task prompt, grading contract, fixtures, and success criteria.
- `EnvSnapshot`: immutable or reproducible runtime environment.
- `Plan`: the meta-agent's current strategy for improving the harness.
- `Harness[v]`: prompt, tools, scaffolding, and instructions used by subagents at version `v`.
- `Run[v, task]`: subagent output, logs, artifacts, grade result, and notable failures for a specific harness version and task.
- `Observation[v]`: expected behavior vs actual behavior for `Harness[v]`.
- `Delta[v -> v+1]`: exact harness change plus the reason for it.
- `Decision[v+1]`: accept, reject, branch, retry, or stop.
- `Current`: the accepted harness version used as the next baseline.

The minimum useful transition record is:

```text
HarnessBefore
RunsBefore
ObservedFailure
Delta
ExpectedAfterBehavior
HarnessAfter
RunsAfter
Comparison
Decision
```

## Invariants

- Freeze `TaskSpec` and `EnvSnapshot` before comparing harness versions.
- Treat `Harness[0]` plus `Run[0]` as the control condition.
- Harness versions are immutable. Never relabel, overwrite, or edit `Harness[v]` after it has been run.
- Do not edit graders, fixtures, or task inputs during a harness optimization loop.
- Record both before and after behavior for every accepted or rejected prompt change.
- Persist the exact subagent outputs and grader results before proposing a change.
- Make deltas small enough that the motivation can name the targeted failure mode.
- Accept a new harness only after checking improvements and regressions against the previous accepted version.
- Preserve raw traces; summaries are useful, but the proposer should be able to inspect original stdout, stderr, logs, and artifacts.
- Separate observations from decisions: first say what happened, then decide whether the change is good.
- If subagent runs or grader results cannot be persisted, stop and report the blocker instead of making an unverified prompt edit.

## Workflow

1. Initialize the control.
   - Write `TaskSpec`.
   - Capture or describe `EnvSnapshot`.
   - Write `Harness[0]`.
   - Run subagents with `Harness[0]`.
   - Store `Run[0, task]` and `Observation[0]`.

2. Propose one harness transition.
   - Inspect raw traces from the current accepted version.
   - Identify one primary failure mode or missed opportunity.
   - Write `Harness[v+1]` as a new version, not by editing `Harness[v]`.
   - Write `Delta[v -> v+1]` with the exact change, motivation, expected behavior, and non-regression expectations.

3. Evaluate the after-state.
   - Run the same task contract under the same environment.
   - Store `Run[v+1, task]` and `Observation[v+1]`.
   - Compare before and after traces, not just aggregate scores.

4. Decide.
   - Accept if the change improves the target behavior without unacceptable regressions.
   - Reject if it fails to improve, causes regressions, leaks grader details, or makes the harness less general.
   - Branch if two plausible changes target different failure modes.
   - Stop on convergence, budget exhaustion, or no defensible next delta.

## Suggested Artifact Layout

Use monotonic versions for machine references and timestamps for human audit context.

```text
meta-harness/
  task.md
  plan.md
  harness/
    v000/prompt.md
    v001/prompt.md
    v001/delta.md
  runs/
    v000/<task-id>/result.json
    v000/<task-id>/stdout.txt
    v000/<task-id>/stderr.txt
    v001/<task-id>/result.json
  observations/
    v000.md
    v001.md
  decisions/
    v001.md
```

If timestamps are useful, include them in frontmatter or filenames, but do not use timestamps as the only version identity.

When adapting to an existing repo layout, keep the same logical artifacts even if names differ. The minimum acceptable evidence for a real run is:

- current harness prompt version
- exact prompt sent to each subagent, or enough data to reconstruct it
- exact subagent response per task
- exact grader or reviewer result per task
- observation summary for that version
- new harness version for any prompt change
- delta record explaining that change

Do not collapse these into a final prompt edit only; that erases the experiment.

## Delta Template

```markdown
# Delta vNNN -> vNNN+1

## Change

Describe the exact prompt/tool/scaffold change.

## Observed Before Behavior

What the subagent was expected to do, what it actually did, and which traces show that.

## Motivation

Why this change should address the observed failure mode.

## Expected After Behavior

What should improve on the next run.

## Non-Regression Expectations

What already-working behavior must remain stable.

## Decision Criteria

What evidence will make this change accepted or rejected.
```

## Comparison Checklist

- Did the target failure improve?
- Did any previously passing task regress?
- Did output quality improve without overfitting to a single trace?
- Did the new prompt leak grader details or encourage reward hacking?
- Did the change make the harness more specific than necessary?
- Are remaining failures now clearer than before?

## Backend Guidance

The workflow is backend-agnostic. Isolated sandboxes, snapshots, durable logs, and parallel forks are implementation details that make the model easier to run, but the state and transition ledger are the essential part.

When using a backend such as Islo, map the model as follows:

- snapshot or base image -> `EnvSnapshot`
- per-task agent fork -> `Run[v, task]`
- log storage -> raw traces for `Observation[v]`
- proposer agent -> transition writer for `Delta[v -> v+1]`
- dashboard or report -> comparison and decision surface

## Failure Modes

- Score-only optimization hides why behavior changed.
- Editing `harness/v000` in place destroys the control state.
- Making a prompt change without saved subagent outputs or grader results is not a harness iteration.
- Changing prompts and task contracts together destroys the control.
- Large prompt rewrites make causal attribution weak.
- The proposer can overfit to visible grader details.
- A single aggregate improvement can hide regressions.
- Summarized traces can erase the clue needed for the next useful delta.
- Rejected deltas are often more informative than accepted ones; keep them.
