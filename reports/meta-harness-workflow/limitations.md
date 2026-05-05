# Meta-Harness Workflow: Limitations and Notes

Human-facing scan note. Not part of the installable skill payload.

Detailed report: [`report.md`](report.md)

Method: [`methods.md`](methods.md)

Benchmark shape: [`repo_shape.md`](repo_shape.md)

## What This Skill Is

`meta-harness-workflow` is a workflow skill for disciplined prompt and harness iteration. It models a meta-agent loop as explicit state transitions over harness versions, subagent runs, observations, deltas, and accept/reject decisions.

It is inspired by meta-harness work such as the Islo POC, but it is not an Islo wrapper, orchestrator, dashboard, or benchmark framework.

## What It Should Improve

- Better control/baseline handling.
- More explicit before/after comparison.
- Smaller and better-motivated prompt deltas.
- Clearer separation between observation and decision.
- Stronger regression and reward-hacking checks.
- Better audit trails for why a harness changed.

## Report Result

In this small comparison, the final run showed stronger auditability and prompt-transition discipline in the skill-guided condition. The skill-guided loop reached payload-correct final answers if the final newline is ignored, but the strict `diff -u` graders still failed because the persisted answer files lacked final trailing newlines.

It did not show improved subagent capability beyond what a clearer prompt can elicit.

The best-supported claim is narrow:

`meta-harness-workflow` helps a lead agent improve and audit intentionally misaligned prompts by recording observations, deltas, and decisions.

## Known Limitations

- The skill is procedural guidance, not a deterministic optimizer.
- It does not provide sandboxing, parallel execution, grading, or trace storage by itself.
- It cannot prove that a prompt change caused improvement unless the experiment design controls task and environment drift.
- It can add overhead for simple one-off prompt edits.
- The state-machine framing can become paperwork if deltas are too small or the benchmark is not worth optimizing.
- The final task used a deliberately bad starting prompt. That is useful for demonstrating prompt improvement, but it does not show value on already-good prompts.
- The final comparison reached payload-correct answers if final newlines are ignored, but remained blocked from strict grader success by trailing-newline behavior in the persisted answer files.
- The skill improved lead-agent process artifacts and prompt repair discipline, not subagent capability beyond clearer prompting.

## Practical Takeaway

Use this skill when prompt or harness iteration needs to be auditable and repeatable. Skip it for casual prompt polishing where there is no stable task contract or before/after evaluation surface.
