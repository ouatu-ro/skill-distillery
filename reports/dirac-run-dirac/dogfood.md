# Dogfood Report: Dirac Workflow

Human-facing report. Not part of the installable skill payload.

Method: [`methods.md`](methods.md)

Short scan note: [`limitations.md`](limitations.md)

## Setup

Target repo:

[dirac-run/dirac](https://github.com/dirac-run/dirac)

Target Dirac commit:

`9b134e57189cf233f28a31b035949b8b7a192bf6`

Observed date:

2026-04-27

Question:

> How does Dirac's `replace_symbol` flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Method:

- Four Spark agents were run with the same question.
- Two agents were baseline agents with no skill guidance.
- Two agents were skill-guided agents, one using skill snapshot `691b6a7` and one using skill snapshot `7ae96fb`.
- Agents were told to answer normally and not report command counts, file counts, process notes, or self-evaluation.
- The parent agent compared the returned answers.

## Runs

| Skill snapshot | Condition | Result |
|---|---|---|
| `691b6a7` | baseline | Correct and detailed. Strong on implementation flow and diagnostics. Included one malformed citation and local-style file URLs in citations. |
| `691b6a7` | skill-guided | Correct and concise. Stronger structure around resolve, validate, apply, verify. Used portable-but-abbreviated citation targets. |
| `7ae96fb` | baseline | Correct and detailed. Strong on operational details, including hash stripping, diagnostics, stale anchors, and partial-failure risk. Included local-style file paths in citations. |
| `7ae96fb` | skill-guided | Correct and concise. Strongest on post-save mismatch risk, caller responsibility for complete replacement text, and verification limits. Included some malformed/partial citation syntax. |

## Parent Assessment

| Dimension | Baseline answers | Skill-guided answers |
|---|---|---|
| Core flow correctness | Strong | Strong |
| Symbol range explanation | Strong: parser/query loading, query captures, suffix matching, optional type compatibility | Strong: same core details, usually organized into explicit resolve/validate/apply/verify phases |
| Wrapper/comment/decorator nuance | Good: explained wrapper expansion and preceding-sibling capture | Slightly stronger: emphasized the tool replaces the expanded range and callers must re-emit metadata |
| Overlap handling | Strong: sorted ranges, reject overlaps, apply bottom-up | Strong: same, usually more compact |
| Apply/verify explanation | Strong: diff view, save path, diagnostics providers | Strong: more explicit that verification is advisory and not semantic proof |
| Risk framing | Strong: ambiguity, parser/query coverage, partial failure, diagnostics blind spots | Stronger on metadata loss, post-save mutation, non-transactional edits, and semantic limits |
| Citation quality | More citations, but included local-style paths and one malformed link | Fewer citations; some were portable/abbreviated, but one answer had partial citation syntax |
| Practical usefulness | Better if the reader wants many exact implementation anchors | Better if the reader wants a short operating model and safety caveats |

## Findings

Both baseline and skill-guided agents answered the code question correctly. The skill did not change the factual core of the answer on this well-named task; `replace_symbol`, `ASTAnchorBridge`, and diagnostics code are easy to find with ordinary search.

The skill-guided answers were more consistently organized around a workflow model:

- resolve symbol ranges structurally
- widen ranges to wrappers/metadata
- reject overlapping edits
- apply bottom-up
- verify with diagnostics while treating diagnostics as incomplete

The most useful skill-guided improvement was not additional facts. It was better boundary-setting: comments/decorators/exports are included in the replacement span, but they are not automatically preserved unless the replacement text includes them.

## Quantitative Summary

These are parent-assessed answer-quality counts, not benchmark scores.

| Metric | Baseline | Skill-guided |
|---|---:|---:|
| Agents run | 2 | 2 |
| Correct core answer | 2/2 | 2/2 |
| Explicit caller-responsibility for metadata | 1/2 | 2/2 |
| Explicit diagnostics-not-semantic-proof framing | 1/2 | 2/2 |
| Mentioned partial/non-transactional failure risk | 2/2 | 2/2 |
| Citation hygiene issues | 2/2 | 2/2 |

## Bottom Line

For this question, the Dirac workflow skill improves answer shape and risk framing more than raw factual accuracy. It is most useful when the task benefits from disciplined structural inspection and safety checks. It is less visibly useful when the target symbol and implementation files are already obvious.
