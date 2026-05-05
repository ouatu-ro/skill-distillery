# Skill Distillery

Distilled agent workflows, structural tooling, and reusable agent skills.

This repository includes distilled workflow skills:

- [Dirac Workflow](skills/dirac-workflow/SKILL.md) distills structural-code habits inspired by [Dirac](https://github.com/dirac-run/dirac) into an installable skill.
- [Meta-Harness Workflow](skills/meta-harness-workflow/SKILL.md), inspired by [Islo's Meta-Harness workflow](https://zozo123.github.io/meta-harness-on-islo-page/), models prompt and harness iteration as explicit before/after state transitions with auditable deltas.

These skills are independent distillations of ideas I found interesting, paired with small reports that make limited, falsifiable claims about how the distilled workflows performed. They are not official implementations of, or affiliated with, the projects that inspired them.

Human-facing notes and reports are in [`reports/`](reports/), and installable skills are in [`skills/`](skills/). Reports are drafted with agent assistance and reviewed/edited by me before publication.

Suggested entry points:

- [`reports/dirac-run-dirac/limitations.md`](reports/dirac-run-dirac/limitations.md) for a short scan of the Dirac workflow skill.
- [`reports/meta-harness-workflow/report.md`](reports/meta-harness-workflow/report.md) for the meta-harness workflow report.

Each skill/report pair is a small distillation and evaluation pass, roughly a couple of hours of work per skill. The claims are directional, not benchmark-grade.

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
