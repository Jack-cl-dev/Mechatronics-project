#!/usr/bin/env python3
"""Shrinks .py files for micro:bit deployment.

Strips comments, docstrings, and blank lines, and switches 4-space indents to
single tabs. Output is still plain, valid .py source -- imported the normal
way -- so there's no bytecode/version compatibility risk like mpy-cross has,
because we can't have nice things.

USAGE
    python minify_for_microbit.py <src_dir> <out_dir>
    python minify_for_microbit.py <src_dir> <out_dir> file1.py file2.py ...

If no filenames are given, every *.py in src_dir is processed. Files that
fail to parse (syntax errors) are skipped and reported.

This can be run manually, though any sane person would run the script.
"""
import ast
import sys
from pathlib import Path


def strip_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
                if not node.body:
                    node.body.append(ast.Pass())
    return tree


def tabify(source):
    """ast.unparse() emits uniform 4-space indents, so this is a safe,
    mechanical swap: each level of 4 leading spaces becomes one tab."""
    out_lines = []
    for line in source.splitlines():
        stripped = line.lstrip(" ")
        n_spaces = len(line) - len(stripped)
        if n_spaces and stripped:
            level = n_spaces // 4
            out_lines.append("\t" * level + stripped)
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def minify(path: Path) -> str:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    tree = strip_docstrings(tree)
    return tabify(ast.unparse(tree))


def main():
    if len(sys.argv) < 3:
        print("usage: minify_for_microbit.py <src_dir> <out_dir> [files...]")
        sys.exit(1)
    src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sys.argv[3:] or sorted(p.name for p in src_dir.glob("*.py"))

    total_before = total_after = 0
    for name in files:
        src_path = src_dir / name
        if not src_path.exists():
            print(f"  skip (missing): {name}")
            continue
        before = src_path.stat().st_size
        try:
            new_src = minify(src_path)
        except SyntaxError as e:
            print(f"  skip (parse error): {name}: {e}")
            continue
        out_path = out_dir / name
        out_path.write_text(new_src, encoding="utf-8")
        after = out_path.stat().st_size
        total_before += before
        total_after += after
        pct = round(100 * after / before)
        print(f"  {name}: {before} -> {after} bytes ({pct}%)")

    print()
    print(f"TOTAL: {total_before} -> {total_after} bytes "
          f"(saved {total_before - total_after} bytes, "
          f"{round(100 * total_after / total_before)}% of original)")


if __name__ == "__main__":
    main()
