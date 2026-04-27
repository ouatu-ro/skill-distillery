# Dogfood Report: Dirac Original Repo

Human-facing report. Not part of the installable skill payload.

Short scan note: [`ast-code-workflow-limitations.md`](ast-code-workflow-limitations.md)

## Setup

Simulated question:

> How does Dirac's `replace_symbol` flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Target repo:

[dirac-run/dirac](https://github.com/dirac-run/dirac)

Agents:

- **Baseline agent**: normal exploration, no special instruction to use the local skill.
- **Skill-guided agent**: explicitly told to use the local `ast-code-workflow` skill.

Both agents were read-only.

## Quantitative Findings

| Metric | Baseline agent | Skill-guided agent |
|---|---:|---:|
| Files inspected, self-reported | ~23 | ~19 |
| Key files used | 14 | 7 |
| Shell/search/tool calls, self-reported | ~25 shell commands across ~12 batches | ~35 shell calls |
| `rg` searches, self-reported | not separately counted | ~10 |
| AST helper attempted | no | yes, 2 attempts |
| AST helper succeeded | n/a | no, missing `tree_sitter_language_pack` in active Python env |
| Final answer correctness | good | good |
| Limitation coverage | good | stronger |

Shared key files both agents used:

- `src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts`
- `src/utils/ASTAnchorBridge.ts`
- `src/core/prompts/system-prompt/tools/replace_symbol.ts`
- `src/services/tree-sitter/languageParser.ts`
- `src/services/tree-sitter/queries/typescript.ts`
- `src/integrations/editor/DiffViewProvider.ts`

## Qualitative Differences

### Baseline Agent

The baseline agent found the correct flow efficiently. It focused on the central handler and AST bridge, then followed diagnostics and parser support.

Strengths:

- More efficient tool use.
- Clear step-by-step answer.
- Good explanation of range resolution, wrapper/comment inclusion, overlap prevention, bottom-up application, approval/save, and diagnostics.

Weaknesses:

- Less explicit about semantic limits such as import aliasing, overloads, re-exports, and language-server identity.
- Less direct about over-capture risk from preceding comments.

### Skill-Guided Agent

The skill-guided agent also found the correct flow, but gave a stronger risk analysis. It explicitly called out that metadata is included in the range but not automatically preserved, that matching is structural not semantic, and that ambiguity handling is weak.

Strengths:

- Better limitation analysis.
- More directly aligned with the skill's safety framing.
- Explicitly noted wrapper coverage is heuristic and previous-comment extension can over-capture.

Weaknesses:

- More expensive exploration.
- Tried to use `scripts/ast_tool.py`, but did not use a dependency-provisioned runner, so the helper failed due missing `tree_sitter_language_pack`.
- Because the helper failed, the final answer still relied mostly on targeted `rg` and file reads rather than AST-helper output.

## What This Says About The Skill

The workflow guidance appears useful: the skill-guided answer was more careful about risks and boundaries. However, the optional AST helper did not improve this particular run because it was not successfully executed.

The main practical gap is not the helper code itself; the local harness already passes when run with:

```bash
uv run --with tree-sitter-language-pack python scripts/ast_harness.py fixtures/mini_repo
```

The gap is invocation behavior. The skill currently says to prefer repo/user runtime choices and treats `uv` as optional. That is correct, but in a dependency-missing environment it means an agent may try ambient `python` first and fail instead of using available `uv`.

## Recommendation

Keep the permissive runtime language, but make `references/ast-helper.md` slightly more operational:

- First check repo/user runtime preferences.
- Then check whether `tree_sitter_language_pack` imports in that runtime.
- If not, and `uv` or `uvx` exists, use a dependency-isolated invocation for the helper rather than failing.
- Still avoid saying `uv` is required.

This would preserve the user's preference for non-prescriptive docs while improving dogfood success.

## Bottom Line

For this question, both agents answered correctly. The skill-guided agent produced a better safety/risk analysis but used more exploration and did not successfully leverage the bundled AST helper. The next improvement should be better runtime fallback guidance for the helper, not more AST code.

## Run 2: After Execution Tactics Update

Skill commit tested: `04f9699` (`Add AST workflow execution tactics`)

Simulated question was the same:

> How does Dirac's `replace_symbol` flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Agents:

- **Baseline agent**: normal exploration, no skill.
- **Skill-guided agent**: explicitly told to use local `skills/ast-code-workflow` at commit `04f9699`.

### Quantitative Findings

| Metric | Baseline agent | Skill-guided agent |
|---|---:|---:|
| Files inspected, self-reported | ~15 | 15 |
| Key files used | 8 | 6 |
| Estimated shell/tool calls | ~21 | ~31 |
| Search/listing commands | 3 `rg` searches | 8 search/listing commands |
| AST helper attempted | no | yes |
| AST helper succeeded | n/a | yes, 5 uses via `uv run --with tree-sitter-language-pack` |
| Final answer correctness | good | good |
| Limitation coverage | good | slightly stronger |

Shared key files:

- `src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts`
- `src/utils/ASTAnchorBridge.ts`
- `src/core/prompts/system-prompt/tools/replace_symbol.ts`
- `src/services/tree-sitter/languageParser.ts`
- `src/services/tree-sitter/queries/typescript.ts`
- `src/integrations/editor/DiffViewProvider.ts`

### Qualitative Differences

The baseline agent was more efficient than in the first run and produced a strong answer. It covered the core control flow, wrapper extension, overlap rejection, bottom-up application, save path, diagnostics, and cross-language tests.

The skill-guided agent successfully used the bundled AST helper this time. It reported five successful `ast_tool.py` uses for skeleton and symbol-body inspection of the handler and AST bridge. That is the main improvement versus Run 1, where the helper failed because the agent used ambient Python without the dependency.

Skill-guided strengths:

- Used AST-first inspection rather than only `rg` and manual file reads.
- Isolated the central flow around handler `execute`, bridge `getSymbolRange`, and `getExtendedRange`.
- Called out a specific testing gap: cross-language fixture coverage exists for ordinary success/failure paths, but no dedicated overlapping-range test was found.
- Preserved the distinction between structural matching and semantic language-server behavior.

Skill-guided weaknesses:

- Still used more tool calls than baseline.
- Still needed ordinary search to find tests, prompts, and surrounding infrastructure.
- The local helper provided useful structure but did not eliminate the need to inspect source files directly.

### What Changed Since Run 1

Run 1 showed the skill-guided agent had better safety framing but failed to run the helper. After updating runtime fallback guidance and adding execution tactics, Run 2 shows the agent successfully used the helper with:

```bash
uv run --with tree-sitter-language-pack ...
```

That suggests the skill text is now operational enough to make the optional helper usable while still not requiring `uv` as the only path.

### Updated Bottom Line

At commit `04f9699`, the skill improves qualitative framing and can successfully activate its bundled AST helper. It still costs more exploration than the baseline on this narrow question, but it produces a more tool-shaped investigation path and better surfaces structural risks. The helper is useful for orientation and symbol-body targeting; it does not replace source inspection, tests, or semantic language-server analysis.
