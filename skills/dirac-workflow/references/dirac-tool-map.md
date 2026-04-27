# Dirac Tool Map

Use this reference to translate Dirac's tool discipline into whatever tools are available in the current agent environment.

## Structural Inspection

- `list_files`: Locate candidate files and understand directory shape. Prefer excluding generated, vendored, third-party, build, and lockfile-like outputs unless explicitly in scope.
- `get_file_skeleton`: Read classes, functions, methods, signatures, line counts, and sometimes local calls without loading implementation bodies.
- Generic equivalents: LSP document symbols, tree-sitter outline, ctags, language-specific analyzers, focused grep for definitions, or the bundled `scripts/ast_tool.py skeleton` helper when appropriate.

## Targeted Reads

- `get_function`: Fetch exact function or method bodies after skeleton inspection identifies the relevant symbol.
- `read_file`: Use only when full-file context or a precise line range is needed.
- Generic equivalents: LSP symbol lookup, tree-sitter node extraction, targeted `sed` ranges, editor symbol navigation, or `scripts/ast_tool.py symbol`.

## Impact Analysis

- `find_symbol_references`: Find definitions/references for exact symbols before refactors.
- Generic equivalents: LSP references, compiler usages, `scripts/ast_tool.py refs`, `rg` cross-checks, import/export search, tests that exercise callers.
- Treat index-backed results as a strong first pass, not a guarantee of full semantic coverage.

## Edits

- `rename_symbol`: Prefer for symbol renames. It is safer than raw text replacement but can still miss stale-index or unsupported-language cases.
- `replace_symbol`: Prefer for replacing complete functions, methods, or classes. Provide the full replacement, including metadata attached to the symbol.
- `edit_file`: Use for localized anchored line edits after a fresh read. Batch non-overlapping edits.
- Hash-anchored edits: Prefer them when the active environment provides them. This skill does not implement Dirac's hash-anchor/Myers-diff editing engine.
- Shell scripts/codemods: Use for broad mechanical updates when a deterministic transform is cheaper and easier to verify.
- Public contract edits: Before changing exported APIs, CLI flags, schemas, config keys, persistence fields, or plugin interfaces, inspect external boundaries and compatibility expectations.

## Context Curation

- Dirac's original runtime aggressively batches operations, uses AST structure to avoid full-file reads, and opportunistically adds context it predicts the model will need next.
- In this skill, mirror that behavior as a workflow preference: fetch high-confidence next context, but keep context scoped and stop before ambiguous or risky expansion.

## Completion

- `attempt_completion`: End with a brief result summary, validation performed, and relevant risks or skipped checks.

## What Not To Import Into A Skill

- Approval mechanics, partial UI messages, telemetry, task-state counters, diff-view internals, previous-result hash lookup, parser cache details, database schema, and provider-specific tool serialization.
