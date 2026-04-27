# AST Helper

The skill includes `scripts/ast_tool.py` as an optional best-effort structural helper. Use it when the current environment lacks stronger AST, LSP, or symbol tools.

## Runtime Selection

Prefer the runtime and dependency workflow already chosen by the user or repo:

- Read the prompt, `AGENTS.md`, package scripts, local docs, and virtualenv/tooling hints before choosing commands.
- Check what exists locally: `python`, `python3`, `uv`, `uvx`, project virtualenvs, or repo task runners.
- Check whether `tree_sitter_language_pack` imports in the selected runtime before assuming the helper is unavailable.
- If dependencies are missing, install them only into the active environment the user/repo expects.
- If there is no repo preference and `uv` or `uvx` is available, prefer a dependency-isolated invocation over failing on ambient Python.
- Do not assume `uv` is required; it is just one convenient option when available.

The helper needs `tree_sitter_language_pack`. It will print a short missing-dependency message if that package is unavailable.

## Commands

Use the repo-preferred Python runner. Examples below use plain `python` as a placeholder:

```bash
python scripts/ast_tool.py skeleton fixtures/mini_repo/python_basic/main.py
python scripts/ast_tool.py symbol fixtures/mini_repo/python_basic/main.py Greeter.greet
python scripts/ast_tool.py refs fixtures/mini_repo/ts_basic helper
```

If no repo preference exists and `uv` is available, this is a convenient dependency-isolated form:

```bash
uv run --with tree-sitter-language-pack python scripts/ast_harness.py fixtures/mini_repo
```

Use the same pattern for the helper itself when needed:

```bash
uv run --with tree-sitter-language-pack python scripts/ast_tool.py skeleton fixtures/mini_repo/ts_basic/main.ts
```

## Subcommands

- `skeleton <file>`: extract common classes, functions, methods, interfaces, type aliases, enums, namespaces, line ranges, and qualified names.
- `symbol <file> <query>`: extract one exact symbol body by name or qualified name.
- `refs <root> <query>`: compare raw AST identifier-name occurrences with literal `rg` word matches.

## Harness

Run the smoke harness against bundled fixtures:

```bash
python scripts/ast_harness.py fixtures/mini_repo
```

Expected behavior:

- Python and TypeScript skeleton extraction succeeds.
- Symbol extraction returns exact method bodies.
- `refs` shows fewer AST identifier occurrences than `rg` because `rg` also reports comments and strings.

## Limits

- This is not a semantic language server.
- `refs` is syntactic identifier-name matching and does not resolve imports, aliases, dynamic dispatch, overloads, or type information.
- Occurrence counts are raw AST nodes, not unique source lines.
- TypeScript/TSX support covers common declarations, but does not model overload signatures, re-export declarations, or every JSX grammar edge case.
- `.jsx` files are parsed through the TSX grammar because the current dependency does not expose a separate JSX parser; this is best-effort and reports `language: "tsx"`.
- `replace_symbol` and semantic rename are intentionally not implemented.
- Treat results as a structural first pass and cross-check with LSP, compiler output, tests, or `rg` when risk is high.
