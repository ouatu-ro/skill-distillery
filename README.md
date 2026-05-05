# Skill Distillery

Distilled agent workflows, structural tooling, and reusable agent skills.

This repository includes distilled workflow skills:

- [Dirac Workflow](skills/dirac-workflow/SKILL.md), based on [Dirac](https://github.com/dirac-run/dirac), extracts structural-code habits into an installable skill. It is not meant to match the original project one to one.
- [Meta-Harness Workflow](skills/meta-harness-workflow/SKILL.md) models prompt and harness iteration as explicit before/after state transitions with auditable deltas.

This project is independent and is not affiliated with Dirac.

Human-facing notes and reports live in [`reports/`](reports/). Start with [`reports/dirac-run-dirac/limitations.md`](reports/dirac-run-dirac/limitations.md) for a short scan of the Dirac workflow skill, or [`reports/meta-harness-workflow/report.md`](reports/meta-harness-workflow/report.md) for the meta-harness workflow report. Installable skills live in [`skills/`](skills/).

## Install

In Codex, use `$skill-installer` with this repo and the skill path under `skills/`.

Manual fallback:

```bash
cp -R skills/<skill-name> ~/.codex/skills/
```

## Smoke Test

```bash
uv run --with tree-sitter-language-pack \
  python skills/dirac-workflow/scripts/ast_harness.py \
  skills/dirac-workflow/fixtures/mini_repo
```

## License

Licensed under Apache-2.0.

SPDX-License-Identifier: Apache-2.0
