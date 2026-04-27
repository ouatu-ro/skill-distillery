#!/usr/bin/env python3
"""Smoke harness for scripts/ast_tool.py.

The goal is not exhaustive parser testing. It demonstrates that AST extraction
can separate structure and identifier nodes from noisy text matches that `rg`
still usefully reports.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
AST_TOOL = SCRIPT_DIR / "ast_tool.py"


def run_json(args: list[str]) -> dict:
    proc = subprocess.run([sys.executable, str(AST_TOOL), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise AssertionError(f"{' '.join(args)} failed:\n{proc.stderr}")
    return json.loads(proc.stdout)


def assert_contains(symbols: list[dict], qualname: str) -> None:
    if not any(s["qualname"] == qualname for s in symbols):
        got = ", ".join(s["qualname"] for s in symbols)
        raise AssertionError(f"Expected symbol {qualname!r}; got: {got}")


def key(record: dict) -> tuple[str, int, str]:
    return (record["path"], record["line"], record["line_text"])


def check_fixture(
    root: Path,
    name: str,
    source_file: str,
    symbol_query: str,
    ref_query: str,
    expected_ast_lines: set[tuple[str, int, str]],
    expected_rg_only: set[tuple[str, int, str]],
) -> str:
    path = root / name / source_file
    skeleton = run_json(["skeleton", str(path)])
    assert skeleton["parse_error"] is False
    assert_contains(skeleton["symbols"], symbol_query)

    symbol = run_json(["symbol", str(path), symbol_query])
    assert symbol["match"]["qualname"] == symbol_query
    assert ref_query in symbol["source"]
    if name == "ts_basic":
        lexical = run_json(["symbol", str(path), "buildTask"])
        if not lexical["source"].startswith("export const buildTask"):
            raise AssertionError("ts_basic: lexical function extraction should include export const declaration context")

    refs = run_json(["refs", str(root / name), ref_query])
    ast_lines = {key(r) for r in refs["ast_occurrences"]}
    rg_only = {key(r) for r in refs["rg_only"]}
    if not expected_ast_lines.issubset(ast_lines):
        raise AssertionError(f"{name}: missing expected AST lines: {sorted(expected_ast_lines - ast_lines)}")
    if rg_only != expected_rg_only:
        raise AssertionError(f"{name}: rg_only mismatch. expected={sorted(expected_rg_only)} got={sorted(rg_only)}")
    if refs["ast_only"]:
        raise AssertionError(f"{name}: expected no ast_only lines, got {refs['ast_only']}")
    return f"{name}: skeleton ok, symbol ok, refs ok (ast={refs['ast_count']} rg={refs['rg_count']} rg_only={len(refs['rg_only'])})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run AST helper smoke checks against mini fixtures.")
    parser.add_argument("fixtures_root", nargs="?", default=str(Path(__file__).resolve().parents[1] / "fixtures" / "mini_repo"))
    args = parser.parse_args(argv)
    root = Path(args.fixtures_root)

    checks = [
        (
            "python_basic",
            "main.py",
            "Greeter.greet",
            "helper",
            {
                ("helper.py", 1, "def helper(value: str) -> str:"),
                ("main.py", 1, "from helper import helper"),
                ("main.py", 10, "return helper(name)"),
                ("main.py", 14, "value = helper(name)"),
            },
            {
                ("main.py", 4, "# helper is mentioned here as documentation noise."),
                ("main.py", 5, 'NOISE = "helper appears in a string but is not a reference"'),
            },
        ),
        (
            "ts_basic",
            "main.ts",
            "TaskRunner.run",
            "helper",
            {
                ("helper.ts", 1, "export function helper(value: string): string {"),
                ("main.ts", 1, 'import { helper } from "./helper"'),
                ("main.ts", 8, "return helper(task.id)"),
                ("main.ts", 12, "export const buildTask = (id: string): string => helper(id)"),
            },
            {
                ("main.ts", 3, "// helper is mentioned here as documentation noise."),
                ("main.ts", 4, 'const noise = "helper appears in a string but is not a reference"'),
            },
        ),
    ]
    for check in checks:
        print(check_fixture(root, *check))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
