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


def check_fixture(root: Path, name: str, source_file: str, symbol_query: str, ref_query: str) -> str:
    path = root / name / source_file
    skeleton = run_json(["skeleton", str(path)])
    assert skeleton["parse_error"] is False
    assert_contains(skeleton["symbols"], symbol_query)

    symbol = run_json(["symbol", str(path), symbol_query])
    assert symbol["match"]["qualname"] == symbol_query
    assert ref_query in symbol["source"]

    refs = run_json(["refs", str(root / name), ref_query])
    if refs["ast_count"] <= 0:
        raise AssertionError(f"{name}: expected AST refs for {ref_query}")
    if refs["rg_count"] <= refs["ast_count"]:
        raise AssertionError(f"{name}: expected rg to include noisy extra hits for {ref_query}")
    if not refs["rg_only"]:
        raise AssertionError(f"{name}: expected rg_only false-positive lines")
    return f"{name}: skeleton ok, symbol ok, refs ok (ast={refs['ast_count']} rg={refs['rg_count']} rg_only={len(refs['rg_only'])})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run AST helper smoke checks against mini fixtures.")
    parser.add_argument("fixtures_root", nargs="?", default=str(Path(__file__).resolve().parents[1] / "fixtures" / "mini_repo"))
    args = parser.parse_args(argv)
    root = Path(args.fixtures_root)

    checks = [
        ("python_basic", "main.py", "Greeter.greet", "helper"),
        ("ts_basic", "main.ts", "TaskRunner.run", "helper"),
    ]
    for check in checks:
        print(check_fixture(root, *check))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
