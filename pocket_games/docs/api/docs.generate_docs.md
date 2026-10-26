# docs/generate_docs.py

Generate Markdown developer documentation from docstrings and comments.

## collect_comments

`def collect_comments(source: str) -> dict[int, str]`

Map line numbers to the text of standalone comment lines.

## leading_comment

`def leading_comment(node: ast.AST, comments: dict[int, str]) -> str`

Collect the comment block directly above a definition (and its decorators).

## is_public

`def is_public(name: str) -> bool`

Return True for names that belong in the developer documentation.

## render_signature

`def render_signature(node: ast.AST) -> str`

Build a one-line signature for a class or function.

## render_definition

`def render_definition(node: ast.AST, comments: dict[int, str], depth: int) -> list[str]`

Render a class or function, followed by its nested members.

## render_body

`def render_body(body: list[ast.stmt], comments: dict[int, str], depth: int) -> list[str]`

Render all public definitions in a block.

## render_module

`def render_module(path: Path, source_dir: Path) -> str`

Render the Markdown page for a single Python module.

## generate

`def generate(source_dir: Path, output_dir: Path) -> list[tuple[str, str]]`

Write one Markdown page per module plus an index. Returns (source, page) pairs.

## main

`def main() -> None`

Parse arguments and generate the developer documentation.
