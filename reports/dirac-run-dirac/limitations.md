# Dirac Workflow: Limitations and Dogfood Notes

Human-facing scan note. Not part of the installable skill payload.

## Commits Covered

| Commit | Role |
|---|---|
| `691b6a7` | Packaged `dirac-workflow` as an installable skill and added the first Dirac dogfood report. |
| `7ae96fb` | Added execution tactics and clearer guidance for batching, opportunistic context, and helper invocation. |
| `a5b2311` | Added this scan note before the parent-assessed dogfood rerun and cleanup pass. |

## What This Skill Is

`dirac-workflow` is a workflow skill inspired by [dirac-run/dirac](https://github.com/dirac-run/dirac). It distills structural-code habits from Dirac into portable agent instructions plus a small optional Python AST helper.

It is not a Dirac clone. It does not include Dirac's runtime, index, editor integration, hash-anchor editing engine, task loop, or persistence layer.

Dogfood target:

- Target repo: [dirac-run/dirac](https://github.com/dirac-run/dirac)
- Target Dirac commit: `9b134e57189cf233f28a31b035949b8b7a192bf6`
- Observed date: 2026-04-27

## Quantitative Snapshot

Approximate/self-reported metrics from the first two read-only dogfood runs. These are not benchmark results.

Dogfood question:

> How does Dirac's `replace_symbol` flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

| Metric | Run 1 skill snapshot | Run 2 skill snapshot |
|---|---:|---:|
| Commit represented | `691b6a7` | `7ae96fb` |
| Baseline files inspected | ~23 | ~15 |
| Skill-guided files inspected | ~19 | 15 |
| Baseline key files used | 14 | 8 |
| Skill-guided key files used | 7 | 6 |
| Baseline shell/search/tool calls | ~25 shell commands across ~12 batches | ~21 estimated calls |
| Skill-guided shell/search/tool calls | ~35 shell calls | ~31 estimated calls |
| AST helper attempted by skill-guided agent | yes, 2 attempts | yes |
| AST helper succeeded | no | yes, 5 uses via `uv run --with tree-sitter-language-pack` |
| Final answer correctness | good | good |
| Limitation coverage | skill-guided stronger | skill-guided slightly stronger |

Mini harness result for the bundled fixture repo:

Counts are raw occurrences, not unique lines. For example, an import like `from helper import helper` can produce multiple AST identifier nodes on one source line.

| Fixture | AST identifier occurrences | `rg` word hits | `rg`-only lines |
|---|---:|---:|---:|
| `python_basic` | 5 | 6 | 2 |
| `ts_basic` | 4 | 6 | 2 |

Interpretation: the AST helper usually returns narrower, more symbol-shaped context than raw text search, but `rg` still finds useful surrounding material and non-symbol references.

## Parent-Assessed Rerun

After the first two runs, the dogfood method was changed: agents were asked only to answer the code question, not to report on their own process. The parent agent compared the returned answers.

Result: both answers were correct. The skill-guided answer was slightly stronger on safety framing: it emphasized that expanded wrapper/comment/decorator ranges are overwritten by supplied replacement text, so metadata is preserved only if the caller re-emits it. It also stated verification limits more sharply: diagnostics are not a semantic proof and Dirac does not re-resolve/reparse the edited symbol after save.

## Small Impressions

The skill-guided agents tended to produce stronger risk analysis than baseline agents. They were more explicit about structural-vs-semantic limits, wrapper/comment over-capture, ambiguous symbol matches, and missing overlap-focused tests.

The baseline agents were often faster and more economical on a narrow, already well-named question. Plain `rg` plus targeted reads is hard to beat when the question points directly at `replace_symbol`.

The skill became materially more usable after `7ae96fb`: the second run successfully invoked the helper through a dependency-provisioned `uv` command instead of failing on ambient Python.

## Known Limitations

- The helper is syntactic, not semantic. It does not resolve overloads, aliases, imports, re-exports, inheritance, or dynamic dispatch like an LSP/indexed runtime could.
- The helper is optional. Agents still need normal shell search, file reads, tests, and repo-specific instructions.
- The workflow can increase tool calls on small questions because it asks agents to inspect structure before reading bodies.
- The Python helper covers common Python/TypeScript/JavaScript shapes, not every language or every grammar edge case.
- Symbol-level replacement guidance does not implement Dirac's hash-anchor/Myers-diff editing strategy.
- Decorator/export wrapper capture has limited helper support; comment and documentation preservation remain procedural guidance and must be checked by source inspection.
- The helper covers common TypeScript classes, functions, methods, interfaces, type aliases, enums, and namespaces, but still omits overload signatures, re-export declarations, object-literal methods, and deeper semantic relationships.
- Quantitative numbers are from small read-only dogfood runs, not a benchmark.

## Practical Takeaway

Use this skill when structural code context matters: refactors, symbol rewrites, impact analysis, and multi-file edits. For a tiny one-file question, raw `rg` may be faster. For work where the cost of a wrong edit is higher than the cost of extra inspection, the skill's AST-first discipline is the useful part.
