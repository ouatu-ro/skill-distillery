---
name: ast-code-workflow
description: "Use when a coding task depends on structural code understanding: architecture summaries, symbol inspection, caller or reference analysis, renames, whole-symbol rewrites, or multi-file refactors where symbol-aware tools materially reduce risk. Prefer outline-first inspection, targeted symbol reads, reference mapping, minimal safe edits, and scoped verification."
---

# AST Code Workflow

Use this skill to work like a structure-aware coding agent: inspect architecture before logic, prefer symbol-aware operations over raw text changes, and keep context and edits scoped.

## Core Directives

- Finish the user's task, not just the investigation.
- Minimize round trips by batching independent reads, searches, and non-overlapping edits.
- Load only the context needed for the next decision.
- Prefer structural inspection over full-file reads when structure is enough.
- Prefer symbol-level edits over regex or line-level churn for semantic changes.
- End with a concise summary of changed scope, validation, and residual risks.

## Workflow

1. Identify candidate files with file listing, search, imports, tests, or user-provided paths.
2. Check user and repo instructions first, including the prompt, `AGENTS.md`, local skill guidance, package scripts, and preferred runtime/tooling.
3. Read structure first with an outline/skeleton tool, LSP document symbols, ctags, tree-sitter, the bundled AST helper, or equivalent.
4. Pull exact symbol bodies only after relevant functions, methods, classes, or interfaces are known.
5. Map definitions, callers, exports, and references before renames, signature changes, or behavior changes.
6. Choose the smallest safe edit unit: symbol-aware rename, whole-symbol replacement, anchored line edit, or codemod.
7. Verify with the narrowest useful check first, then broader tests/typecheck/lint when the changed surface warrants it.

## Optional AST Helper

Use the bundled [scripts/ast_tool.py](scripts/ast_tool.py) when native AST, LSP, or symbol tools are unavailable or weaker than a local parse. It provides best-effort `skeleton`, `symbol`, and `refs` subcommands for Python, TypeScript, and JavaScript.

Before running it:

- Prefer the user's stated runtime preference and repo-native workflow.
- Check for available runners such as `python`, `python3`, `uv`, `uvx`, project virtualenvs, or package scripts.
- Install or provide dependencies only in the active environment the user/repo expects.
- If the helper cannot run, fall back to LSP, ctags, tree-sitter tooling, targeted reads, and `rg`.

Read [references/ast-helper.md](references/ast-helper.md) for commands, limitations, and the harness.

## Execution Tactics

- Batch independent reads, searches, and non-overlapping edits whenever the active tools support batching.
- Use small throwaway shell, Python, Perl, or repo-native scripts when mechanical analysis or transforms are cheaper and safer than repeated manual tool calls.
- Fetch the next obvious context proactively when confidence is high, such as a symbol body after a skeleton reveals the target, or callers after a public signature change.
- Prefer anchored, range-aware, or symbol-aware edits when available; do not claim hash-anchor behavior unless the active environment actually provides it.
- Keep generated context focused: include outlines, exact bodies, references, diffs, and validation output that directly affect the next decision.
- Stop and disambiguate when the next context is not obvious, when public contracts are involved, or when tool results disagree.

## Safety Rules

- Do not edit generated, vendored, third-party, lockfile-like, or externally owned outputs unless the user asked for that exact surface.
- Before renaming or rewriting exported/public symbols, check whether they cross API, CLI, schema, config, persistence, plugin, or documentation boundaries.
- If a symbol match is ambiguous across overloads, aliases, re-exports, duplicate names, nested scopes, or generated declarations, disambiguate before editing.
- Preserve existing structure, wrappers, formatting conventions, imports, decorators, attributes, comments, JSDoc, visibility, and export keywords unless changing them is required.
- Replace whole symbols when changing a symbol body; do not splice large bodies with unrelated line edits.
- Re-emit complete symbol text when using symbol replacement.
- Use exact current anchors or line ranges for text edits; never edit from stale reads.
- Ensure multi-edit batches in one file do not overlap.
- Treat anchors, offsets, and symbol ranges as stale after edits, formatting, diagnostics, or user changes.
- Avoid broad search/replace for identifiers unless symbol-aware rename is unavailable and references have been checked.

## Failure Modes

- AST tools can fail on unsupported languages, parse errors, macros, mixed syntax, or generated code.
- Symbol indexes can be stale or less semantic than a language-server rename.
- Exact-name lookup can miss aliases, exports, dynamic references, overload-like constructs, or public contract usage.
- Regex search can hit comments, strings, unrelated identifiers, generated files, or vendored code.
- Whole-symbol replacement can accidentally drop metadata if decorators, comments, wrappers, visibility, or exports are not included.
- Formatter or editor save hooks can change code and invalidate future edit coordinates.
- A single search hit is not proof of exclusivity; verify definitions and representative references.

If symbol-aware tools are missing or incomplete, emulate the same flow with targeted reads, `rg`, LSP/compiler search, and narrower validation before broader tests.

## References

- Read [references/dirac-tool-map.md](references/dirac-tool-map.md) when mapping Dirac tool concepts to generic tools or deciding which operation to prefer.
- Read [references/examples.md](references/examples.md) when choosing a workflow for common task shapes.
- Read [references/ast-helper.md](references/ast-helper.md) before using the bundled Python helper or harness.

## Exclusions

- Do not recreate Dirac's symbol-index database, parser loading, runtime persistence, telemetry, approval UI, provider schema conversion, or tool handlers.
- Do not promise perfect semantic rename unless the available tool actually provides language-server-grade rename.
- Do not add broad documentation files to a skill; keep procedural content in `SKILL.md` and optional one-level references.
