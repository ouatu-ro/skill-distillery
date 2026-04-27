---
name: ast-code-workflow
description: Use when working in codebases where structural understanding matters: repo orientation, architecture summaries, function or method inspection, caller impact analysis, refactors, symbol renames, whole-symbol rewrites, safe multi-file edits, or tasks where AST, LSP, symbol, or anchored edit tools are available. Guides Codex to inspect skeletons first, fetch exact symbol bodies, map references, edit the smallest safe unit, and verify changes without cloning Dirac's runtime.
---

# AST Code Workflow

Use this skill to work like a structure-aware coding agent: inspect architecture before logic, prefer symbol-aware operations over raw text changes, and keep context and edits scoped.

## Core Directives

- Finish the user's task, not just the investigation.
- Minimize round trips by batching independent reads, searches, and non-overlapping edits.
- Load only the context needed for the next decision.
- Prefer structural tools over full-file reads when they are available.
- Prefer symbol-level edits over regex or line-level churn for semantic changes.
- End with a concise completion summary covering changed scope, validation, and residual risks.

## Workflow

1. Identify candidate files with file listing, search, imports, tests, or user-provided paths.
2. Read structure first with `get_file_skeleton`, LSP outline, ctags, tree-sitter, or an equivalent symbol outline.
3. Pull exact symbol bodies with `get_function`, LSP symbol lookup, or targeted line ranges only after the relevant symbols are known.
4. Map references before refactors with `find_symbol_references`, LSP references, compiler usages, or targeted search.
5. Choose the smallest safe edit unit: rename, whole-symbol replacement, anchored line edit, or codemod.
6. Verify with the narrowest useful check first, then broader tests/typecheck/lint when the changed surface warrants it.

## Decision Tree

- Need repo orientation: list top-level files, manifests, and relevant directories.
- Need architecture in known files: inspect file skeletons before reading full files.
- Need implementation details: fetch the exact function, method, class, or neighboring range.
- Need impact analysis: find symbol definitions and references before editing.
- Need a rename: prefer AST/LSP `rename_symbol`; fall back to reference mapping plus targeted edits.
- Need a function, method, or class rewrite: prefer `replace_symbol` or whole-symbol replacement.
- Need local syntax or import adjustment: use fresh anchored line edits.
- Need broad mechanical updates: use a script or codemod, then inspect representative diffs and run validation.
- Need text, comments, config, or unsupported language changes: use targeted search and careful text edits.

## Editing Rules

- Preserve existing structure, wrappers, formatting conventions, imports, decorators, attributes, comments, JSDoc, and export keywords unless changing them is required.
- Replace whole symbols when changing a symbol body; do not splice large bodies with unrelated line edits.
- Re-emit complete symbol text when using symbol replacement.
- Use exact current anchors or line ranges for text edits; never edit from stale reads.
- Ensure multi-edit batches in one file do not overlap.
- Apply bottom-up or tool-managed edits when raw offsets could shift.
- Treat anchors, offsets, and symbol ranges as stale after edits, formatting, or user changes.
- Re-read before follow-up edits when autoformatting or diagnostics changed the file.
- Avoid broad search/replace for identifiers unless symbol-aware rename is unavailable and references have been checked.

## Failure Modes

- AST tools can fail on unsupported languages, parse errors, generated files, macros, or mixed syntax.
- Symbol indexes can be stale or less semantic than a language-server rename.
- Exact-name lookup can miss aliases, exports, dynamic references, or overload-like constructs.
- Regex search can hit comments, strings, unrelated identifiers, generated files, or vendored code.
- Whole-symbol replacement can accidentally drop metadata if decorators, comments, or wrappers are not included.
- Formatter or editor save hooks can change code and invalidate future edit coordinates.
- A single search hit is not proof of exclusivity; verify definitions and representative references.

## Fallbacks

- If AST tools exist, use them first for source code structure and symbols.
- If AST tools are absent, emulate the workflow with LSP, compiler tooling, `rg`, ctags, targeted reads, and focused tests.
- If reference results look incomplete, cross-check with textual search, exports, tests, and call sites.
- If a rename is risky, stage it as references first, edit second, verify third.

## References

- Read [references/dirac-tool-map.md](references/dirac-tool-map.md) when mapping Dirac tool concepts to generic tools or deciding which operation to prefer.
- Read [references/examples.md](references/examples.md) when choosing a workflow for common task shapes.

## Exclusions

- Do not recreate Dirac's symbol-index database, parser loading, runtime persistence, telemetry, approval UI, provider schema conversion, or tool handlers.
- Do not promise perfect semantic rename unless the available tool actually provides language-server-grade rename.
- Do not add broad documentation files to a skill; keep procedural content in `SKILL.md` and optional one-level references.
