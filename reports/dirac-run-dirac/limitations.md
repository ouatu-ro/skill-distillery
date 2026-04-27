# Dirac Workflow: Limitations and Dogfood Notes

Human-facing scan note. Not part of the installable skill payload.

Detailed report: [`dogfood.md`](dogfood.md)

Method: [`methods.md`](methods.md)

## Commits Covered

| Commit | Role |
|---|---|
| `691b6a7` | Packaged the workflow skill as an installable skill and added Dirac dogfood reporting. |
| `7ae96fb` | Added execution tactics and clearer guidance for batching, opportunistic context, and helper invocation. |

## What This Skill Is

`dirac-workflow` is a workflow skill inspired by [dirac-run/dirac](https://github.com/dirac-run/dirac). It distills structural-code habits from Dirac into portable agent instructions plus a small optional Python AST helper.

It is not a Dirac clone. It does not include Dirac's runtime, index, editor integration, hash-anchor editing engine, task loop, or persistence layer.

Dogfood target:

- Target repo: [dirac-run/dirac](https://github.com/dirac-run/dirac)
- Target Dirac commit: `9b134e57189cf233f28a31b035949b8b7a192bf6`
- Observed date: 2026-04-27

## Clean Dogfood Result

Four Spark agents answered the same `replace_symbol` question:

- baseline at skill snapshot `691b6a7`
- skill-guided at skill snapshot `691b6a7`
- baseline at skill snapshot `7ae96fb`
- skill-guided at skill snapshot `7ae96fb`

Agents were not asked to report process metrics. The parent agent compared the returned answers.

| Finding | Result |
|---|---|
| Correct core answer | 4/4 |
| Skill changed factual correctness | No clear effect on this narrow question |
| Skill improved answer organization | Yes |
| Skill improved safety/risk framing | Yes |
| Skill eliminated citation hygiene problems | No |

## Practical Impressions

The baseline agents already found the relevant implementation because the question named `replace_symbol`. They produced strong answers on parser/query lookup, extended ranges, overlap rejection, bottom-up application, diff/save flow, and diagnostics.

The skill-guided agents were more consistent about framing the answer as an operating model. They emphasized that wrapper/comment/decorator capture only expands the replaced span; preserving that metadata still depends on the replacement text.

The execution-tactics update in `7ae96fb` did not change the factual answer much for this narrow question. Its value is more likely to show up on broader refactors where batching, proactive context, and structural inspection reduce edit risk.

## Known Limitations

- The helper is syntactic, not semantic. It does not resolve overloads, aliases, imports, re-exports, inheritance, or dynamic dispatch like an LSP/indexed runtime could.
- The helper is optional. Agents still need normal shell search, file reads, tests, and repo-specific instructions.
- The workflow can add overhead on small questions because it encourages structure-first inspection before reading exact bodies.
- The Python helper covers common Python/TypeScript/TSX/JavaScript shapes, not every language or every grammar edge case.
- Symbol-level replacement guidance does not implement Dirac's hash-anchor/Myers-diff editing strategy.
- Decorator/export wrapper capture has limited helper support; comment and documentation preservation remain procedural guidance and must be checked by source inspection.
- The helper covers common TypeScript classes, functions, methods, interfaces, type aliases, enums, and namespaces, but still omits overload signatures, re-export declarations, object-literal methods, and deeper semantic relationships.
- Dogfood results are small read-only comparisons, not benchmark evidence.

## Practical Takeaway

Use `dirac-workflow` when structural code context matters: refactors, symbol rewrites, impact analysis, and multi-file edits. For a tiny one-file question, raw search may be faster. For work where a wrong edit is costly, the skill's AST-first discipline and safety framing are the useful parts.
