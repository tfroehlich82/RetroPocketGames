#!/usr/bin/env python3
"""Generate Markdown developer documentation from docstrings and comments."""

from __future__ import annotations

import argparse
import ast
import io
import tokenize
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE_DIR = DOCS_DIR.parent
DEFAULT_OUTPUT_DIR = DOCS_DIR / "api"
EXCLUDED_DIRS = {"__pycache__"}
DEFINITION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def collect_comments(source: str) -> dict[int, str]:
    """Map line numbers to the text of standalone comment lines."""
    comments = {}
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT and tok.line.strip().startswith("#"):
            comments[tok.start[0]] = tok.string.lstrip("#").strip()
    return comments


def leading_comment(node: ast.AST, comments: dict[int, str]) -> str:
    """Collect the comment block directly above a definition (and its decorators)."""
    start = node.lineno
    if getattr(node, "decorator_list", None):
        start = min(d.lineno for d in node.decorator_list)
    lines = []
    line = start - 1
    while line in comments:
        lines.insert(0, comments[line])
        line -= 1
    return "\n".join(lines)


def is_public(name: str) -> bool:
    """Return True for names that belong in the developer documentation."""
    return not name.startswith("_") or name == "__init__"


def render_signature(node: ast.AST) -> str:
    """Build a one-line signature for a class or function."""
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(b) for b in node.bases)
        return f"class {node.name}({bases})" if bases else f"class {node.name}"
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    signature = f"{prefix} {node.name}({ast.unparse(node.args)})"
    if node.returns is not None:
        signature += f" -> {ast.unparse(node.returns)}"
    return signature


def render_definition(node: ast.AST, comments: dict[int, str], depth: int) -> list[str]:
    """Render a class or function, followed by its nested members."""
    lines = [f"{'#' * min(depth, 6)} {node.name}", "", f"`{render_signature(node)}`", ""]

    comment = leading_comment(node, comments)
    if comment:
        lines += [f"> {line}".rstrip() if line else ">" for line in comment.splitlines()]
        lines.append("")

    doc = ast.get_docstring(node)
    if doc:
        lines += [doc, ""]

    if isinstance(node, ast.ClassDef):
        lines += render_body(node.body, comments, depth + 1)
    return lines


def render_body(body: list[ast.stmt], comments: dict[int, str], depth: int) -> list[str]:
    """Render all public definitions in a block."""
    lines: list[str] = []
    for node in body:
        if isinstance(node, DEFINITION_NODES) and is_public(node.name):
            lines += render_definition(node, comments, depth)
    return lines


def render_module(path: Path, source_dir: Path) -> str:
    """Render the Markdown page for a single Python module."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    comments = collect_comments(source)

    rel = path.relative_to(source_dir).as_posix()
    lines = [f"# {rel}", ""]

    module_doc = ast.get_docstring(tree)
    if module_doc:
        lines += [module_doc, ""]

    lines += render_body(tree.body, comments, depth=2)
    return "\n".join(lines).rstrip() + "\n"


def generate(source_dir: Path, output_dir: Path) -> list[tuple[str, str]]:
    """Write one Markdown page per module plus an index. Returns (source, page) pairs."""
    source_dir = source_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pages: list[tuple[str, str]] = []
    for path in sorted(source_dir.rglob("*.py")):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        rel = path.relative_to(source_dir)
        page_name = ".".join(rel.with_suffix("").parts) + ".md"
        try:
            content = render_module(path, source_dir)
        except (SyntaxError, UnicodeDecodeError) as exc:
            print(f"Skipping {rel.as_posix()}: {exc}")
            continue
        (output_dir / page_name).write_text(content, encoding="utf-8")
        pages.append((rel.as_posix(), page_name))

    index = ["# Developer Documentation", "", f"{len(pages)} module(s) documented.", ""]
    index += [f"- [{source}]({page})" for source, page in pages]
    (output_dir / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    return pages


def main() -> None:
    """Parse arguments and generate the developer documentation."""
    parser = argparse.ArgumentParser(
        description="Generate Markdown developer documentation from docstrings and comments"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Package directory to document (default: pocket_games)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated Markdown (default: pocket_games/docs/api)",
    )
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        raise SystemExit(f"Source directory does not exist: {args.source_dir}")

    pages = generate(args.source_dir, args.output_dir)
    print(f"Generated {len(pages)} page(s) in {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
