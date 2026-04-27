# Skill Distillery

Distilled agent workflows, structural tooling, and reusable agent skills.

This repository includes a skill based on [Dirac](https://github.com/dirac-run/dirac). It extracts the workflow and structural-code ideas into an installable skill so they are easy to explore; it is not meant to match the original project one to one.

This project is independent and is not affiliated with Dirac.

Human-facing notes and dogfood reports live in [`reports/`](reports/). Start with [`reports/ast-code-workflow-limitations.md`](reports/ast-code-workflow-limitations.md) for a short scan. Installable skills live in [`skills/`](skills/).

## Smoke Test

```bash
uv run --with tree-sitter-language-pack \
  python skills/ast-code-workflow/scripts/ast_harness.py \
  skills/ast-code-workflow/fixtures/mini_repo
```

## License

Licensed under Apache-2.0.
