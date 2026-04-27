# 7ae96fb Skill-Guided Run

## Prompt

```text
Read-only investigation. Target codebase: <dirac-repo> at commit 9b134e57189cf233f28a31b035949b8b7a192bf6. Do not modify files.

Condition: skill-guided for skill snapshot 7ae96fb. Use the local skill instructions at <skill-snapshot-7ae96fb>/skills/ast-code-workflow/SKILL.md as investigation guidance. Answer normally; do not report your process, command counts, files inspected, or self-evaluation.

Question: How does Dirac's replace_symbol flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Return a concise, technically grounded answer with file references where useful.
```

## Response

`replace_symbol` is implemented as an AST-driven, per-file replacement pipeline with a pre-application validation phase and post-save diagnostics.

- **Input + symbol lookup**
  - `execute` accepts `replacements[]` and also a legacy single-object fallback (`path`, `symbol`, `text`, optional `type`) for compatibility. [ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L88)
  - For each replacement it calls `ASTAnchorBridge.getSymbolRange(path, symbol, type, ignoreController, taskId)`. [ReplaceSymbolToolHandler.ts#L145]
  - `getSymbolRange` parses the file with the language parser/query for the extension, runs `query.matches`, and for each match extracts `name.definition*` and `definition*` captures. [ASTAnchorBridge.ts#L221]( <dirac-repo>/src/utils/ASTAnchorBridge.ts#L221) and [ASTAnchorBridge.ts#L235-L288)
  - It builds a fully-qualified symbol name by walking ancestor matches and prepending parent `name.*` captures, then matches requested symbol by exact or suffix match (supports `A.B`/`A::B` normalization). [ASTAnchorBridge.ts#L260-L280]
  - It applies optional type matching through `areTypesCompatible` (currently only hard-equality plus `function`↔`method` compatibility). [ASTAnchorBridge.ts#L294-L306]

- **Preserving wrappers/comments/decorators**
  - Raw definition span is widened in `getExtendedRange(...)` by climbing parent nodes of wrapper types:
    - `export_statement`, `export_declaration`, `ambient_declaration`, `decorated_definition`, `internal_module`. [ASTAnchorBridge.ts#L317-L330]
  - Then it pulls in immediately-adjacent preceding named siblings if they are `comment`, `decorator`, `attribute`, or have `"comment"` in type, which is how it keeps adjacent metadata/decorators in the replacement range. [ASTAnchorBridge.ts#L332-L346]
  - The tool contract also explicitly requires replacement text to include associated JSDoc/comments/decorators/export keywords. [replace_symbol tool spec](file://<dirac-repo>/src/core/prompts/system-prompt/tools/replace_symbol.ts#L10-L33)

- **Preventing overlapping replacements**
  - After resolving ranges, replacements are sorted by `startIndex`.
  - If `prev.endIndex > next.startIndex`, the tool rejects the call with an `Overlapping replacements detected` error before applying anything. [ReplaceSymbolToolHandler.ts#L159-L166]
  - Non-overlapping order is then re-sorted descending so edits are applied bottom-up to keep index math stable. [ReplaceSymbolToolHandler.ts#L174-L177]

- **Apply + verify**
  - For each file batch:
    - Replacements are applied via string slicing from `startIndex` to `endIndex`, with hash markers stripped and optional leading indentation adjustment. [ReplaceSymbolToolHandler.ts#L178-L189]
    - Diff blocks are computed for approval, and tool-level approval is requested unless auto-approved. [ReplaceSymbolToolHandler.ts#L190-L259]
    - Edits are applied through `DiffViewProvider.update(...); saveChanges({ skipDiagnostics: true })`, then final content is read back (captures editor-formatting changes). [ReplaceSymbolToolHandler.ts#L280-L291; DiffViewProvider.ts#L353-L419]
  - Verification:
    - Pre-edit diagnostics state is captured.
    - After save, all providers run `getDiagnosticsFeedbackForFiles(...)` in parallel and new error-level findings are attached to the summary if present. [ReplaceSymbolToolHandler.ts#L262-L314]  
    - Providers are syntax + linter unless configured to syntax-only. [getDiagnosticsProviders.ts#L5-L14]

### Main limitations / risks

- **Ambiguous symbol resolution**: it returns the first matching candidate in query iteration order; same-named symbols can resolve unexpectedly in complex files or deep nesting. [ASTAnchorBridge.ts#L250-L288]
- **Query/parser dependent**: unsupported language or incomplete Tree-sitter queries mean symbols are “not found” and the whole tool fails for that symbol. [ASTAnchorBridge.ts#L221-L227]
- **Heuristic range widening**: wrapper/comment/decorator preservation is structural/adjacent only; trailing comments or non-recognized metadata may be excluded. [ASTAnchorBridge.ts#L317-L346]
- **Strict non-overlap rule**: any intersecting ranges are rejected, so nested/overlapping intent is not supported. [ReplaceSymbolToolHandler.ts#L159-L166]
- **No semantic equivalence check**: tool trusts `text` as a complete replacement; it does not validate that content belongs to the chosen symbol. It only runs lint/syntax afterward. [ReplaceSymbolToolHandler.ts#L88-L97; ReplaceSymbolToolHandler.ts#L339-L344]
- **Async/post-save verification**: diagnostics are run after save and do not prevent write; they are advisory (reported as messages). [DiffViewProvider.ts#L353-L419; ReplaceSymbolToolHandler.ts#L270-L325]
- **Diff preview vs final save mismatch risk**: diff blocks are generated from unindented-adjusted `newText` while application may normalize leading whitespace; and editor auto-formatting can further mutate final content. [ReplaceSymbolToolHandler.ts#L178-L186; ReplaceSymbolToolHandler.ts#L190-L199; DiffViewProvider.ts#L371-L402]
