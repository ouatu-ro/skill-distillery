#!/usr/bin/env python3
"""Small AST helper for outline-first code inspection.

This is intentionally best-effort: it extracts structural symbols and
identifier-name occurrences, but it does not perform semantic resolution.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

try:
    from tree_sitter_language_pack import get_parser
except ModuleNotFoundError:
    print(
        "Missing dependency: tree_sitter_language_pack. Install it into the Python environment you are using for this repo, then re-run.",
        file=sys.stderr,
    )
    raise SystemExit(2)


LANG_BY_EXT = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}

SKIP_DIRS = {".git", "node_modules", "dist", "build", "out", "__pycache__"}
IDENTIFIER_TYPES = {
    "identifier",
    "property_identifier",
    "shorthand_property_identifier",
    "type_identifier",
}


@dataclass
class Symbol:
    name: str
    qualname: str
    kind: str
    language: str
    path: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    parent: str | None = None
    exported: bool = False
    async_: bool = False


@dataclass
class Occurrence:
    path: str
    line: int
    column: int
    text: str
    node_type: str
    line_text: str


def point_line(point) -> int:
    return point.row + 1


def point_col(point) -> int:
    return point.column + 1


def node_text(source: bytes, node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def line_at(source: bytes, line_one_based: int) -> str:
    lines = source.decode("utf-8", errors="replace").splitlines()
    if 1 <= line_one_based <= len(lines):
        return lines[line_one_based - 1]
    return ""


def detect_language(path: Path, override: str = "auto") -> str:
    if override != "auto":
        return override
    try:
        return LANG_BY_EXT[path.suffix]
    except KeyError as exc:
        raise ValueError(f"Unsupported file extension for {path}") from exc


def parse_file(path: Path, language: str):
    source = path.read_bytes()
    parser = get_parser(language)
    tree = parser.parse(source)
    return source, tree.root_node, tree.root_node.has_error


def child_name(source: bytes, node) -> str | None:
    name = node.child_by_field_name("name")
    if name is not None:
        return node_text(source, name)
    for child in node.named_children:
        if child.type in IDENTIFIER_TYPES:
            return node_text(source, child)
    return None


def exported_wrapper(node):
    parent = node.parent
    if parent is not None and parent.type == "export_statement":
        return parent
    return node


def symbol_from_node(
    source: bytes,
    path: Path,
    language: str,
    node,
    name: str,
    kind: str,
    parent: str | None = None,
    exported: bool = False,
    async_: bool = False,
):
    range_node = exported_wrapper(node)
    qualname = f"{parent}.{name}" if parent else name
    return Symbol(
        name=name,
        qualname=qualname,
        kind=kind,
        language=language,
        path=str(path),
        start_line=point_line(range_node.start_point),
        start_col=point_col(range_node.start_point),
        end_line=point_line(range_node.end_point),
        end_col=point_col(range_node.end_point),
        parent=parent,
        exported=exported or range_node is not node,
        async_=async_,
    )


def unwrap_decorated(node):
    if node.type != "decorated_definition":
        return node, node
    for child in node.named_children:
        if child.type in {"function_definition", "class_definition"}:
            return child, node
    return node, node


def iter_python_symbols(source: bytes, path: Path, root) -> list[Symbol]:
    symbols: list[Symbol] = []

    def add_top(node):
        actual, wrapper = unwrap_decorated(node)
        if actual.type == "class_definition":
            name = child_name(source, actual)
            if name:
                sym = symbol_from_node(source, path, "python", wrapper, name, "class")
                symbols.append(sym)
                body = actual.child_by_field_name("body")
                if body is not None:
                    for member in body.named_children:
                        member_actual, member_wrapper = unwrap_decorated(member)
                        if member_actual.type == "function_definition":
                            method_name = child_name(source, member_actual)
                            if method_name:
                                symbols.append(
                                    symbol_from_node(
                                        source,
                                        path,
                                        "python",
                                        member_wrapper,
                                        method_name,
                                        "method",
                                        parent=name,
                                        async_=b"async " in source[member_wrapper.start_byte : member_actual.start_byte + 10],
                                    )
                                )
        elif actual.type == "function_definition":
            name = child_name(source, actual)
            if name:
                symbols.append(symbol_from_node(source, path, "python", wrapper, name, "function"))

    for node in root.named_children:
        add_top(node)
    return symbols


def iter_ts_symbols(source: bytes, path: Path, language: str, root) -> list[Symbol]:
    symbols: list[Symbol] = []

    def declaration_from_top(node):
        exported = node.type == "export_statement"
        if exported:
            for child in node.named_children:
                if child.type in {"class_declaration", "function_declaration", "lexical_declaration"}:
                    return child, exported
        return node, exported

    def add_class(node, exported: bool):
        name = child_name(source, node)
        if not name:
            return
        symbols.append(symbol_from_node(source, path, language, node, name, "class", exported=exported))
        body = node.child_by_field_name("body")
        if body is None:
            return
        for member in body.named_children:
            if member.type == "method_definition":
                method_name = child_name(source, member)
                if method_name:
                    symbols.append(
                        symbol_from_node(
                            source,
                            path,
                            language,
                            member,
                            method_name,
                            "method",
                            parent=name,
                            async_=member.children and member.children[0].type == "async",
                        )
                    )

    def add_lexical(node, exported: bool):
        for child in node.named_children:
            if child.type != "variable_declarator":
                continue
            value = child.child_by_field_name("value")
            name_node = child.child_by_field_name("name")
            if value is None or name_node is None:
                continue
            if value.type in {"arrow_function", "function", "function_expression"}:
                symbols.append(
                    symbol_from_node(
                        source,
                        path,
                        language,
                        child,
                        node_text(source, name_node),
                        "function",
                        exported=exported,
                    )
                )

    for top in root.named_children:
        node, exported = declaration_from_top(top)
        if node.type == "class_declaration":
            add_class(node, exported)
        elif node.type == "function_declaration":
            name = child_name(source, node)
            if name:
                symbols.append(symbol_from_node(source, path, language, node, name, "function", exported=exported))
        elif node.type == "lexical_declaration":
            add_lexical(node, exported)
    return symbols


def iter_symbols(source: bytes, path: Path, language: str, root) -> list[Symbol]:
    if language == "python":
        return iter_python_symbols(source, path, root)
    if language in {"typescript", "javascript"}:
        return iter_ts_symbols(source, path, language, root)
    return []


def find_symbol(symbols: list[Symbol], query: str) -> Symbol:
    matches = [s for s in symbols if s.qualname == query or s.name == query]
    if not matches:
        raise ValueError(f"No symbol found for query: {query}")
    exact = [s for s in matches if s.qualname == query]
    if len(exact) == 1:
        return exact[0]
    if len(matches) == 1:
        return matches[0]
    choices = ", ".join(s.qualname for s in matches)
    raise ValueError(f"Ambiguous symbol query {query!r}; choose one of: {choices}")


def source_slice(source: bytes, symbol: Symbol) -> str:
    lines = source.decode("utf-8", errors="replace").splitlines()
    return "\n".join(lines[symbol.start_line - 1 : symbol.end_line])


def walk(node) -> Iterable:
    yield node
    for child in node.named_children:
        yield from walk(child)


def identifier_occurrences(source: bytes, path: Path, language: str, root, query: str) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    for node in walk(root):
        if node.type not in IDENTIFIER_TYPES:
            continue
        text = node_text(source, node)
        if text != query:
            continue
        line = point_line(node.start_point)
        occurrences.append(
            Occurrence(
                path=str(path),
                line=line,
                column=point_col(node.start_point),
                text=text,
                node_type=node.type,
                line_text=line_at(source, line).strip(),
            )
        )
    return occurrences


def candidate_files(root: Path, lang: str) -> list[Path]:
    exts = {ext for ext, mapped in LANG_BY_EXT.items() if lang == "auto" or mapped == lang}
    if root.is_file():
        return [root] if root.suffix in exts else []
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in exts:
            files.append(path)
    return sorted(files)


def rg_occurrences(root: Path, query: str) -> list[dict]:
    try:
        proc = subprocess.run(
            ["rg", "-n", "-w", "--no-heading", query, str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:
        return []
    out: list[dict] = []
    for line in proc.stdout.splitlines():
        match = re.match(r"^(.*?):(\d+):(.*)$", line)
        if not match:
            continue
        path, lineno, text = match.groups()
        out.append({"path": path, "line": int(lineno), "line_text": text.strip()})
    return out


def relative_records(records: list[dict], root: Path) -> list[dict]:
    normalized = []
    for record in records:
        item = dict(record)
        try:
            item["path"] = str(Path(item["path"]).resolve().relative_to(root.resolve()))
        except ValueError:
            item["path"] = str(Path(item["path"]))
        normalized.append(item)
    return normalized


def command_skeleton(args) -> dict:
    path = Path(args.path)
    language = detect_language(path, args.lang)
    source, root, parse_error = parse_file(path, language)
    symbols = iter_symbols(source, path, language, root)
    return {
        "path": str(path),
        "language": language,
        "parse_error": parse_error,
        "symbols": [asdict(s) for s in symbols],
    }


def command_symbol(args) -> dict:
    path = Path(args.path)
    language = detect_language(path, args.lang)
    source, root, parse_error = parse_file(path, language)
    symbols = iter_symbols(source, path, language, root)
    match = find_symbol(symbols, args.query)
    return {
        "path": str(path),
        "language": language,
        "parse_error": parse_error,
        "query": args.query,
        "match": asdict(match),
        "source": source_slice(source, match),
    }


def command_refs(args) -> dict:
    root_path = Path(args.root)
    requested_lang = args.lang
    ast_occurrences: list[dict] = []
    parse_errors: list[str] = []
    for file_path in candidate_files(root_path, requested_lang):
        language = detect_language(file_path, "auto" if requested_lang == "auto" else requested_lang)
        source, root, parse_error = parse_file(file_path, language)
        if parse_error:
            parse_errors.append(str(file_path))
        ast_occurrences.extend(asdict(o) for o in identifier_occurrences(source, file_path, language, root, args.query))

    rg_records = rg_occurrences(root_path, args.query)
    ast_norm = relative_records(ast_occurrences, root_path)
    rg_norm = relative_records(rg_records, root_path)
    ast_keys = {(r["path"], r["line"]) for r in ast_norm}
    rg_keys = {(r["path"], r["line"]) for r in rg_norm}
    return {
        "root": str(root_path),
        "query": args.query,
        "mode": "identifier-name",
        "parse_errors": parse_errors,
        "ast_occurrences": ast_norm,
        "rg_occurrences": rg_norm,
        "ast_count": len(ast_norm),
        "rg_count": len(rg_norm),
        "rg_only": [r for r in rg_norm if (r["path"], r["line"]) not in ast_keys],
        "ast_only": [r for r in ast_norm if (r["path"], r["line"]) not in rg_keys],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Best-effort AST helper for code inspection.")
    sub = parser.add_subparsers(dest="command", required=True)

    skeleton = sub.add_parser("skeleton", help="Extract a file outline.")
    skeleton.add_argument("path")
    skeleton.add_argument("--lang", default="auto", choices=["auto", "python", "typescript", "javascript"])
    skeleton.set_defaults(func=command_skeleton)

    symbol = sub.add_parser("symbol", help="Extract one symbol body.")
    symbol.add_argument("path")
    symbol.add_argument("query")
    symbol.add_argument("--lang", default="auto", choices=["auto", "python", "typescript", "javascript"])
    symbol.set_defaults(func=command_symbol)

    refs = sub.add_parser("refs", help="Compare AST identifier-name occurrences with rg.")
    refs.add_argument("root")
    refs.add_argument("query")
    refs.add_argument("--lang", default="auto", choices=["auto", "python", "typescript", "javascript"])
    refs.set_defaults(func=command_refs)

    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except Exception as exc:
        print(f"ast_tool error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
