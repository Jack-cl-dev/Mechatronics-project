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


def lexical_minify(source):
    """Aggressively remove comments and unnecessary whitespace.

    tokenize protects strings, so spaces inside string literals are preserved.
    """
    import io
    import tokenize

    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    out = []
    prev = None

    for tok in tokens:
        typ, text = tok.type, tok.string

        if typ in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NL):
            continue
        if typ == tokenize.COMMENT:
            continue
        if typ == tokenize.INDENT:
            # MicroPython accepts tabs and they are smaller than 4 spaces.
            out.append("\t" * max(1, len(text) // 4))
            prev = tok
            continue
        if typ == tokenize.DEDENT:
            prev = tok
            continue
        if typ == tokenize.NEWLINE:
            out.append("\n")
            prev = tok
            continue

        # Python requires separation between adjacent names/numbers, but
        # almost everything else can touch.
        if prev is not None:
            if ((prev.type in (tokenize.NAME, tokenize.NUMBER)
                 and typ in (tokenize.NAME, tokenize.NUMBER))
                    or (prev.string in ("+", "-", "~")
                        and text in ("+", "-", "~"))
                    or (prev.string == "/" and text == "/")
                    or (prev.string == "*" and text == "*")):
                out.append(" ")

        out.append(text)
        prev = tok

    return "".join(out).rstrip() + "\n"


def minify(path: Path) -> str:
    src = path.read_text(encoding="utf-8")
    tree = strip_docstrings(ast.parse(src, filename=str(path)))

    # ast.unparse() removes comments/docstrings and normalizes source.
    # tokenize then removes the remaining unnecessary whitespace.
    normalized = ast.unparse(tree)
    result = lexical_minify(normalized)

    # Safety check: never emit code that no longer parses.
    ast.parse(result, filename=str(path))
    return result


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
