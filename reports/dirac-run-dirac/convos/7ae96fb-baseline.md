# 7ae96fb Baseline Rerun

## Prompt

```text
Read-only investigation. Target codebase: <dirac-repo> at commit 9b134e57189cf233f28a31b035949b8b7a192bf6. Do not modify files.

Condition: baseline for skill snapshot 7ae96fb. Do not use any local skill instructions. Answer normally; do not report your process, command counts, files inspected, or self-evaluation.

Question: How does Dirac's replace_symbol flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Return a concise, technically grounded answer with file references where useful.
```

## Response

`replace_symbol` is handled by `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L87)` and the AST lookup lives in `[ASTAnchorBridge.ts](<dirac-repo>/src/utils/ASTAnchorBridge.ts#L210)`.

1. How it finds symbol range  
- The handler normalizes input into an array of `replacements` (supports legacy single-object form too), groups by file, reads each file, then resolves every symbol via `ASTAnchorBridge.getSymbolRange(...)`.  
- `getSymbolRange` loads the language parser from extension-based registration in `[languageParser.ts](<dirac-repo>/src/services/tree-sitter/languageParser.ts#L91)` and runs tree-sitter query matches.  
- For each match it extracts `name.definition*` and definition node, builds a dot-notation qualified name by walking ancestor matches, normalizes `::` → `.`, then matches if either exact or suffix match, and checks symbol type compatibility (`function`/`method` treated as aliases for compatibility).  
- On a match it returns `{ startIndex, endIndex, startLine }` from `getExtendedRange` for the definition node.

2. How wrappers/comments/decorators are preserved  
- Range expansion is done in `getExtendedRange`: it first bubbles up through parent nodes of types  
  `export_statement`, `export_declaration`, `ambient_declaration`, `decorated_definition`, `internal_module`.  
  That keeps wrapper syntax around the symbol.  
- Then it repeatedly absorbs preceding named siblings if they are `comment`, `decorator`, `attribute`, or names containing `"comment"`.  
- This is how decorators/doc comments right before the symbol get included in the replaced span.  
- The tool then replaces exactly that expanded span, so the output slice is expected to include metadata/comments as part of the replaced block. Tool contract reinforces this: callers are required to provide full replacement text including docs/decorators/exports.  
  - `[replace_symbol tool spec](<dirac-repo>/src/core/prompts/system-prompt/tools/replace_symbol.ts#L9)`.

3. How overlap is prevented  
- After resolving ranges for a file, ranges are sorted by `startIndex` and checked pairwise with `endIndex > next.startIndex`; any overlap returns an error and aborts before applying any write for that file.  
  - `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L159)`.  
- Actual replacement is done in descending `startIndex` order so prior replacements don’t invalidate later offsets.

4. How edits are applied  
- Replacements are applied directly to the in-memory file string (`currentContent = currentContent.slice(0, start) + adjustedNewText + currentContent.slice(end)`).  
- Before inserting, `stripHashes()` is called on user text to remove line-anchor markers.  
  - `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L178)`  
  - `stripHashes` implementation: `[line-hashing.ts](<dirac-repo>/src/shared/utils/line-hashing.ts#L32)`.  
- Leading indentation at replacement start is normalized by removing matching leading spaces/tabs from the user text.  
  - `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L181)`.  
- If tool call isn’t auto-approved, a diff+replacement payload is shown and user approval is requested; otherwise it proceeds automatically for approved settings.  
  - `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L225)`.  
- Actual file write goes through `diffViewProvider` (`open` → `update` → `saveChanges({skipDiagnostics: true})`).  
  - `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L280)`  
  - Diff view save behavior is in `[DiffViewProvider.ts](<dirac-repo>/src/integrations/editor/DiffViewProvider.ts#L353)`.

5. How verification happens  
- The handler captures pre-save diagnostics once, then after all files are applied it runs provider checks in parallel for all modified files.  
  - Providers are syntax + linter by default (or syntax-only flag).  
  - `[getDiagnosticsProviders.ts](<dirac-repo>/src/integrations/diagnostics/getDiagnosticsProviders.ts#L5)`.  
- `LinterFeedbackProvider` polls host diagnostics and compares new vs pre state; `SyntaxFeedbackProvider` parses with tree-sitter and reports parse errors.  
  - `[LinterFeedbackProvider.ts](<dirac-repo>/src/integrations/diagnostics/LinterFeedbackProvider.ts#L24)`  
  - `[SyntaxFeedbackProvider.ts](<dirac-repo>/src/integrations/diagnostics/SyntaxFeedbackProvider.ts#L37)`.  
- The first non-empty problem message is returned in the final summary; summary explicitly notes stale anchors after edit.  
  - `[ReplaceSymbolToolHandler.ts](<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L341)`.

Main limitations / risks  
- AST coverage is parser/query-limited: unsupported extensions throw in parser loading and parsing can fail to find symbols.  
  - `[languageParser.ts](<dirac-repo>/src/services/tree-sitter/languageParser.ts#L158)`.  
- Ambiguity handling is weak: full/qualified-name suffix matching can target only the first matching AST hit, so duplicate/shadowed names can be mis-selected.  
  - `[ASTAnchorBridge.ts](<dirac-repo>/src/utils/ASTAnchorBridge.ts#L277)`.  
- Wrapper/comment preservation is intentionally narrow (`comment/decorator/attribute` siblings + fixed wrapper type list), so trailing comments, non-standard decorator/comment node shapes, or language constructs outside that set may be dropped.  
  - `[ASTAnchorBridge.ts](<dirac-repo>/src/utils/ASTAnchorBridge.ts#L317)`.  
- Overlap prevention is all-or-nothing; overlapping/nested replacements in one file are rejected.  
- No transactional rollback: on partial failures, earlier files may already be written before the error path returns.  
- Verification is mostly “new errors only” (severity error, not warnings), and depends on diagnostics polling timing; non-error regressions can be missed.  
- `stripHashes` applies a generic regex and can strip unintended sequences that resemble hash anchors inside code if they match the pattern.  
  - `[line-hashing.ts](<dirac-repo>/src/shared/utils/line-hashing.ts#L37)`
