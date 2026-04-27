# Examples

## Summarize Architecture From Skeletons

Task: "Explain how task execution works."

Sequence:
1. List likely directories and manifests.
2. Read skeletons for entrypoints and coordinator files.
3. Pull exact bodies only for central dispatch or lifecycle functions.
4. Summarize modules, control flow, extension points, and open questions.

## Change A Function Signature

Task: "Add an options parameter to `runTask`."

Sequence:
1. Find the definition and exact function body.
2. Find symbol references and imports/exports.
3. Inspect representative callers before editing.
4. Replace the function signature/body as a whole if logic changes.
5. Update callers with targeted edits.
6. Run typecheck or focused tests.

## Rename A Class Or Function

Task: "Rename `TaskRunner` to `ExecutionRunner`."

Sequence:
1. Confirm definition and scope.
2. Use AST/LSP rename when available.
3. Cross-check references with textual search for exports, strings, docs, and tests.
4. Fix missed non-code references intentionally.
5. Run typecheck or test commands that cover the changed module.

## Replace A Method Safely

Task: "Rewrite `SessionStore.save` to debounce writes."

Sequence:
1. Read the file skeleton to locate the method and containing class.
2. Fetch the exact method body and nearby class context.
3. Find callers if behavior or contract changes.
4. Replace the whole method, preserving decorators, comments, visibility, and class indentation.
5. Re-read or inspect the diff after formatter hooks.
6. Run focused tests for the class or persistence layer.

## Multi-File Mechanical Edit

Task: "Replace deprecated helper imports across `src/core`."

Sequence:
1. Search imports and references under scoped directories.
2. Prefer a codemod or batched anchored edits if the transform is regular.
3. Avoid generated/vendor/build files.
4. Inspect representative diffs.
5. Run lint/typecheck and a targeted search proving the deprecated form is gone.
