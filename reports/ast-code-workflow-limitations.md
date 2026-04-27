# AST Code Workflow: Limitations and Dogfood Notes

Human-facing scan note. Not part of the installable skill payload.

## Commits Covered

| Commit | Role |
|---|---|
| `91600e0` | Packaged `ast-code-workflow` as an installable skill and added the first Dirac dogfood report. |
| `04f9699` | Added execution tactics and clearer guidance for batching, opportunistic context, and helper invocation. |

## What This Skill Is

`ast-code-workflow` is a workflow skill inspired by [dirac-run/dirac](https://github.com/dirac-run/dirac). It distills structural-code habits from Dirac into portable agent instructions plus a small optional Python AST helper.

It is not a Dirac clone. It does not include Dirac's runtime, index, editor integration, hash-anchor editing engine, task loop, or persistence layer.

## Quantitative Snapshot

Dogfood question:

> How does Dirac's `replace_symbol` flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

| Metric | Run 1 skill snapshot | Run 2 skill snapshot |
|---|---:|---:|
| Commit represented | `91600e0` | `04f9699` |
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

| Fixture | AST refs | `rg` refs | `rg`-only refs |
|---|---:|---:|---:|
| `python_basic` | 5 | 6 | 2 |
| `ts_basic` | 4 | 6 | 2 |

Interpretation: the AST helper usually returns narrower, more symbol-shaped context than raw text search, but `rg` still finds useful surrounding material and non-symbol references.

## Small Impressions

The skill-guided agents tended to produce stronger risk analysis than baseline agents. They were more explicit about structural-vs-semantic limits, wrapper/comment over-capture, ambiguous symbol matches, and missing overlap-focused tests.

The baseline agents were often faster and more economical on a narrow, already well-named question. Plain `rg` plus targeted reads is hard to beat when the question points directly at `replace_symbol`.

The skill became materially more usable after `04f9699`: the second run successfully invoked the helper through a dependency-provisioned `uv` command instead of failing on ambient Python.

## Known Limitations

- The helper is syntactic, not semantic. It does not resolve overloads, aliases, imports, re-exports, inheritance, or dynamic dispatch like an LSP/indexed runtime could.
- The helper is optional. Agents still need normal shell search, file reads, tests, and repo-specific instructions.
- The workflow can increase tool calls on small questions because it asks agents to inspect structure before reading bodies.
- The Python helper covers common Python/TypeScript/JavaScript shapes, not every language or every grammar edge case.
- Symbol-level replacement guidance does not implement Dirac's hash-anchor/Myers-diff editing strategy.
- Comment/decorator/doc preservation is guidance plus helper support, not a guarantee across all languages.
- Quantitative numbers are from small read-only dogfood runs, not a benchmark.

## Practical Takeaway

Use this skill when structural code context matters: refactors, symbol rewrites, impact analysis, and multi-file edits. For a tiny one-file question, raw `rg` may be faster. For work where the cost of a wrong edit is higher than the cost of extra inspection, the skill's AST-first discipline is the useful part.
