# Dogfood Method

Human-facing method note for the Dirac workflow reports. Not part of the installable skill payload.

## Question Template

Use the same target repo, target commit, question, and answer constraints for every agent.

```text
Read-only investigation. Target codebase: <target-repo> at commit <target-commit>. Do not modify files.

Condition: <baseline-or-skill-guided> for skill snapshot <skill-commit>.
<For baseline: Do not use any local skill instructions.>
<For skill-guided: Use the local skill instructions at <skill-path> as investigation guidance.>

Answer normally; do not report your process, command counts, files inspected, or self-evaluation.

Question: How does Dirac's replace_symbol flow find the symbol range, preserve wrappers/comments/decorators, prevent overlapping replacements, and apply/verify edits? What are the main limitations or risks?

Return a concise, technically grounded answer with file references where useful.
```

## Reviewer Assessment Template

The reviewer compares only the returned answers.

Assess:

- Core flow correctness
- Citation specificity
- Wrapper/comment/decorator nuance
- Overlap prevention and edit application explanation
- Verification-limit clarity
- Risk framing
- Any unsupported or overstated claims

## Reporting Policy

- "Do not use process metrics supplied by answering agents."
- "Do not report shell command counts, file counts, or timing unless independently measured outside the answering agents."

## Matrix Used For This Report

Skill snapshots are commits in this repository, not Dirac commits.

| Skill snapshot | Condition |
|---|---|
| `691b6a7` | baseline, no skill guidance |
| `691b6a7` | skill-guided, using that snapshot's skill instructions |
| `7ae96fb` | baseline, no skill guidance |
| `7ae96fb` | skill-guided, using that snapshot's skill instructions |

The target Dirac commit was `9b134e57189cf233f28a31b035949b8b7a192bf6`.
