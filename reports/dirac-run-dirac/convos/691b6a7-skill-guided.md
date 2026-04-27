# 691b6a7 Skill-Guided Run

## Prompt

```text
Read-only investigation. Target codebase: <dirac-repo> at commit 9b134e57189cf233f28a31b035949b8b7a192bf6. Do not modify files.

Condition: skill-guided for skill snapshot 691b6a7. Use the local skill instructions at <skill-snapshot-691b6a7>/skills/ast-code-workflow/SKILL.md as investigation guidance. Answer normally; do not report your process, command counts, files inspected, or self-evaluation.

Question: How does Dirac's replace_symbol flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Return a concise, technically grounded answer with file references where useful.
```

## Response

Dirac’s `replace_symbol` flow is AST-driven, symbol-granular, and staged into **resolve → validate → apply → verify**.

1. How it finds symbol ranges  
- `ReplaceSymbolToolHandler.execute` parses replacements, resolves each file path, reads the file, and calls `ASTAnchorBridge.getSymbolRange(...)` per symbol [`ReplaceSymbolToolHandler.ts#L111`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L111), [`#L145`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L145).  
- `getSymbolRange` loads the language parser/query, walks all query matches, finds `name.definition.*` + corresponding definition capture, and builds a full dotted name by walking parent matches (`Class.method` style nesting). It matches `::`-style names by normalizing to dots and accepts exact or suffix matches (e.g., `Outer.inner`) [`ASTAnchorBridge.ts#L248`](.../src/utils/ASTAnchorBridge.ts#L248), [`#L276`](.../src/utils/ASTAnchorBridge.ts#L276).  
- It filters by optional `type` using a compatibility check (not strict class/type matching beyond simple compatibility; `function`/`method` are treated as synonyms) and returns `startIndex/endIndex/startLine` for the matched symbol range [`ASTAnchorBridge.ts#L294`](.../src/utils/ASTAnchorBridge.ts#L294), [`#L282`](.../src/utils/ASTAnchorBridge.ts#L282).

2. How it preserves wrappers/comments/decorators  
- `getExtendedRange` starts from the definition node and expands upward while parent node types are in a wrapper allow-list (`export_statement`, `export_declaration`, `ambient_declaration`, `decorated_definition`, `internal_module`) [`ASTAnchorBridge.ts#L317`](.../src/utils/ASTAnchorBridge.ts#L317).  
- It then walks previous named siblings and extends the range backward when siblings are comment/decorator/attribute-style nodes, so doc comments or decorator metadata immediately attached to the symbol can be included in the replacement span [`ASTAnchorBridge.ts#L332`](.../src/utils/ASTAnchorBridge.ts#L332).  
- The tool spec also explicitly requires callers to pass complete replacement text including associated JSDoc/comments/decorators/export keywords, since range replacement is whole-symbol text replacement [`replace_symbol.ts#L10`](.../src/core/prompts/system-prompt/tools/replace_symbol.ts#L10).

3. How it prevents overlapping replacements  
- For each batch/file, all resolved ranges are sorted by start index, and if any `range[i].endIndex > range[i+1].startIndex`, the tool returns an overlap error before editing anything in that file [`ReplaceSymbolToolHandler.ts#L160`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L160).  
- The actual write pass applies replacements in **descending start index** order to avoid index drift (`currentContent` string replacement does not get invalidated by earlier edits) [`ReplaceSymbolToolHandler.ts#L175`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L175).

4. How edits are applied and verified  
- It builds a diff summary (with anchored line context) and asks/records approval unless auto-approval applies [`ReplaceSymbolToolHandler.ts#L214`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L214), [`#L239`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L239).  
- On apply, it uses `diffViewProvider` (`editType = "modify"`), `open(...)`, `update(finalContent, true)`, tiny wait (200ms), then `saveChanges({ skipDiagnostics: true })` [`ReplaceSymbolToolHandler.ts#L280`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L280), [`#L288`](.../src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts#L288).  
- `saveChanges` collects post-save content (including editor auto-formatting), computes whether user edits/auto-formatting changed text, and can run diagnostics feedback after save if not skipped [`DiffViewProvider.ts#L353`](.../src/integrations/editor/DiffViewProvider.ts#L353), [`DiffViewProvider.ts#L405`](.../src/integrations/editor/DiffViewProvider.ts#L405).  
- Handlers used for verification are syntax + (by default) linter providers; pre-save state is captured before open, then compared against post-save diagnostics with diff filtering [`getDiagnosticsProviders.ts#L5`](.../src/integrations/diagnostics/getDiagnosticsProviders.ts#L5), [`LinterFeedbackProvider.ts#L14`](.../src/integrations/diagnostics/LinterFeedbackProvider.ts#L14), [`SyntaxFeedbackProvider.ts#L10`](.../src/integrations/diagnostics/SyntaxFeedbackProvider.ts#L10).

Main limitations / risks
1. Ambiguous symbol resolution risk: suffix matching and first-match return semantics can target the wrong declaration when duplicate/same-named symbols exist in AST scope; there’s no explicit conflict/error for non-unique matches [`ASTAnchorBridge.ts#L156`](.../src/utils/ASTAnchorBridge.ts#L156), [`#L278`](.../src/utils/ASTAnchorBridge.ts#L278).  
2. Parser/query coverage risk: only languages with loaded tree-sitter queries/correct node types are supported; unsupported/parse-failing files return null/not found [`ASTAnchorBridge.ts#L225`](.../src/utils/ASTAnchorBridge.ts#L225), [`#L231`](.../src/utils/ASTAnchorBridge.ts#L231).  
3. Wrapper/comment preservation is best-effort, limited to specific node kinds and immediate previous named siblings; custom wrappers or non-adjacent metadata may be missed [`ASTAnchorBridge.ts#L317`](.../src/utils/ASTAnchorBridge.ts#L317), [`#L332`](.../src/utils/ASTAnchorBridge.ts#L332).  
4. No rollback orchestration: multi-file batches apply sequentially; if a later step fails, earlier files may already be modified.  
5. Verification is asynchronous/polling-based and may miss issues that appear late or in tools/time windows (`diagnostic` polling + timeout), so “no new problems” doesn’t prove perfect health [`LinterFeedbackProvider.ts#L24`](.../src/integrations/diagnostics/LinterFeedbackProvider.ts#L24), [`pollForNewDiagnostics` loop](.../src/integrations/diagnostics/index.ts#L123).
