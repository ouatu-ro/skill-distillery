# 691b6a7 Baseline Rerun

## Prompt

```text
Read-only investigation. Target codebase: <dirac-repo> at commit 9b134e57189cf233f28a31b035949b8b7a192bf6. Do not modify files.

Condition: baseline for skill snapshot 691b6a7. Do not use any local skill instructions. Answer normally; do not report your process, command counts, files inspected, or self-evaluation.

Question: How does Dirac's replace_symbol flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Return a concise, technically grounded answer with file references where useful.
```

## Response

Here is how `replace_symbol` works in that revision:

- **Input and batching**: `ReplaceSymbolToolHandler.execute` accepts either `replacements[]` or legacy single `{path,symbol,text}` format, then groups replacements by absolute file path before processing. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L88-L123), [L133-L135))

- **Symbol range lookup**: For each requested symbol, it calls `ASTAnchorBridge.getSymbolRange(path, symbol, type, ...)`; if that returns null, the tool errors with “not found.” ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L144-L156), [ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L210-L216))

- **AST-based resolution details**:  
  - Loads parser/query for file extension (unsupported extension ⇒ null). ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L221-L227), [languageParser.ts](file://<dirac-repo>/src/services/tree-sitter/languageParser.ts:L91-L160))  
  - Walks Tree-sitter captures (`name.definition*`, `definition.*`) and checks requested symbol against full dotted name (or suffix match). ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L250-L281))  
  - Optional type disambiguation: exact type match or `function`/`method` synonym treatment. ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L294-L305))

- **Wrapper/comments/decorators preservation**:  
  - `getExtendedRange` can expand the symbol range outward through specific wrapper parent node types (`export_statement`, `decorated_definition`, etc.). ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L317-L330))  
  - It also walks previous named siblings and includes preceding nodes typed as `comment`, `decorator`, `attribute`, or `*comment*`. ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L332-L346))  
  - Tool spec also explicitly tells callers to provide the full replacement including JSDoc/comments/decorators/export keywords. ([replace_symbol.ts](file://<dirac-repo>/src/core/prompts/system-prompt/tools/replace_symbol.ts:L9-L10), [replace_symbol.ts](file://<dirac-repo>/src/core/prompts/system-prompt/tools/replace_symbol.ts:L30-L33))  
  - Before inserting, `stripHashes` removes line-anchor tokens from provided text. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L178-L186), [line-hashing.ts](file://<dirac-repo>/src/shared/utils/line-hashing.ts:L32-L40))

- **Preventing overlap**:  
  - Resolved replacements are sorted by `startIndex` and checked pairwise; any `endIndex > next.startIndex` aborts with overlap error. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L159-L167))  
  - Successful edits are then applied in descending `startIndex` order so earlier string index math does not shift later ranges. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L169-L176))

- **Apply + verify**:  
  - After approval, files are opened via `DiffViewProvider`, updated with final content, then saved with `skipDiagnostics: true`. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L262-L290), [DiffViewProvider.ts](file://<dirac-repo>/src/integrations/editor/DiffViewProvider.ts:L32-L69), [DiffViewProvider.ts](file://<dirac-repo>/src/integrations/editor/DiffViewProvider.ts:L353-L419))  
  - Pre-edit diagnostics state is captured, then after edits all files are checked through providers (`SyntaxFeedbackProvider` + `LinterFeedbackProvider`) with `getDiagnosticsFeedbackForFiles`, and first non-empty `newProblemsMessage` is attached per file. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L262-L325), [getDiagnosticsProviders.ts](file://<dirac-repo>/src/integrations/diagnostics/getDiagnosticsProviders.ts:L5-L14), [LinterFeedbackProvider.ts](file://<dirac-repo>/src/integrations/diagnostics/LinterFeedbackProvider.ts:L24-L56), [SyntaxFeedbackProvider.ts](file://<dirac-repo>/src/integrations/diagnostics/SyntaxFeedbackProvider.ts:L15-L62))

**Main limitations / risks**

1. **AST/query fragility**: unsupported file extensions fail fast, and missing grammar/query captures in supported languages can still return wrong or no symbol match. ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L221-L233), [languageParser.ts](file://<dirac-repo>/src/services/tree-sitter/languageParser.ts:L91-L160))

2. **Ambiguous name matching**: suffix matching (`endsWith`) and limited type compatibility can match unintended symbols in nested contexts. ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L276-L281), [ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L294-L305))

3. **Wrapper/comment preservation is heuristic**: only specific wrapper node types and immediate preceding comment/decorator siblings are included; other metadata placement patterns can be dropped. ([ASTAnchorBridge.ts](file://<dirac-repo>/src/utils/ASTAnchorBridge.ts:L317-L349))

4. **Partial failure risk across files**: files are edited and saved sequentially; there is no transactional rollback if a later file fails or diagnostics reject afterward. ([ReplaceSymbolToolHandler.ts](file://<dirac-repo>/src/core/task/tools/handlers/ReplaceSymbolToolHandler.ts:L277-L303))

5. **Diagnostics blind spots**: verification focuses on post-edit delta (mostly errors) with provider timeouts/limits, so some issues may be delayed, truncated, or not captured. ([getDiagnosticsProviders.ts](file://<dirac-repo>/src/integrations/diagnostics/getDiagnosticsProviders.ts:L5-L14), [LinterFeedbackProvider.ts](file://<dirac-repo>/src/integrations/diagnostics/LinterFeedbackProvider.ts:L24-L56), [SyntaxFeedbackProvider.ts](file://<dirac-repo>/src/integrations/diagnostics/SyntaxFeedbackProvider.ts:L15-L62))

6. **Hash stripping edge case**: `stripHashes` strips `\b[A-Z][a-zA-Z]*§` patterns, so real code tokens matching that pattern format could be altered unexpectedly in replacement text. ([line-hashing.ts](file://<dirac-repo>/src/shared/utils/line-hashing.ts:L37-L41))
