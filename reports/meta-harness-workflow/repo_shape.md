
# Repo Shape: Spark Exact-Output Benchmark

This file records the benchmark fixture contents used by the final meta-harness comparison. It is a static snapshot, not an active repository.


# File: README.md
# Spark Exact-Output Benchmark

This repo contains a small exact-output benchmark for Spark subagents.

The workload has three tasks under `tasks/`. Each task has a `prompt.md` and an executable `grade.sh`.

The starting Spark prompt is `harness/v000/prompt.md`.



# File: experiment.md
# Benchmark Contract

This repo contains a small exact-output task suite.

Goal: improve `harness/v000/prompt.md` so Spark subagents (`gpt-5.3-codex-spark`) pass the tasks in `tasks/`.

Rules:

- Use the prompt in `harness/v000/prompt.md` as the starting prompt.
- Do not edit files under `tasks/`.
- Run real Spark subagents; do not simulate their answers.
- For each task, give the subagent only the current harness prompt and that task's `prompt.md`.
- Grade each answer with the matching `grade.sh`.
- Stop when all tasks pass or after three total prompt versions.
- If Spark subagents cannot be spawned, stop and report that blocker.



# File: harness/v000/prompt.md
# Spark Subagent Prompt v000

Solve the task and include a brief explanation before the answer.

For structured outputs, prefer readable formatting over compact formatting.
Escape special characters so they are clear in markdown.



# File: tasks/json-ledger/grade.sh
#!/usr/bin/env bash
set -euo pipefail

actual_file="${1:?usage: grade.sh OUTPUT_FILE}"
expected="$(mktemp)"
trap 'rm -f "$expected"' EXIT

printf '{"account":"checking","start_cents":1250,"transactions":[{"type":"deposit","cents":775},{"type":"withdrawal","cents":430},{"type":"fee","cents":35},{"type":"deposit","cents":100}],"final_cents":1660,"status":"ok"}\n' > "$expected"
diff -u "$expected" "$actual_file"



# File: tasks/json-ledger/prompt.md
# Task: JSON Ledger

Compute the final checking-account balance after these transactions, starting from 1250 cents:

- deposit 775 cents
- withdrawal 430 cents
- fee 35 cents
- deposit 100 cents

Output strict compact JSON on one line:

```json
{"account":"checking","start_cents":1250,"transactions":[{"type":"deposit","cents":775},{"type":"withdrawal","cents":430},{"type":"fee","cents":35},{"type":"deposit","cents":100}],"final_cents":N,"status":"ok"}
```

Replace only `N`. Preserve key order, punctuation, quotes, array/object nesting, and no spaces.



# File: tasks/manifest/grade.sh
#!/usr/bin/env bash
set -euo pipefail

actual_file="${1:?usage: grade.sh OUTPUT_FILE}"
expected="$(mktemp)"
trap 'rm -f "$expected"' EXIT

cat > "$expected" <<'EOT'
BEGIN_MANIFEST
file=src/app.ts;lines=7
file=README.md;lines=12
file=test/app.test.ts;lines=5
total_lines=24
END_MANIFEST
EOT

diff -u "$expected" "$actual_file"



# File: tasks/manifest/prompt.md
# Task: Manifest

Create a manifest for these files:

- `src/app.ts` has 7 lines
- `README.md` has 12 lines
- `test/app.test.ts` has 5 lines

Total the line count.

Output format is strict and multi-line:

```text
BEGIN_MANIFEST
file=src/app.ts;lines=7
file=README.md;lines=12
file=test/app.test.ts;lines=5
total_lines=N
END_MANIFEST
```

Replace only `N`. Preserve line order, casing, semicolons, and the exact `BEGIN_MANIFEST` / `END_MANIFEST` wrapper lines.



# File: tasks/pipe-escape/grade.sh
#!/usr/bin/env bash
set -euo pipefail

actual_file="${1:?usage: grade.sh OUTPUT_FILE}"
expected="$(mktemp)"
trap 'rm -f "$expected"' EXIT

printf 'USERS|count=3|records=lovelace\,ada;hopper\,grace;turing\,alan|checksum=35\n' > "$expected"
diff -u "$expected" "$actual_file"



# File: tasks/pipe-escape/prompt.md
# Task: Pipe Escape

Normalize these user names:

- Ada Lovelace
- Grace Hopper
- Alan Turing

For each name, produce lowercase `last,first`. Join the records with semicolons.

Output format is strict:

```text
USERS|count=3|records=lovelace\,ada;hopper\,grace;turing\,alan|checksum=NN
```

The checksum is the sum of the character counts of the three normalized names before comma escaping:

- `lovelace,ada`
- `hopper,grace`
- `turing,alan`

Replace only `NN`. Preserve the literal backslashes before commas, pipe separators, semicolons, and lowercase text.
