#!/usr/bin/env python3
"""Conservative MicroPython source minifier.

The optimiser is deliberately lexical: it does not parse or regenerate Python
with CPython's AST, so it cannot introduce syntax from a newer Python version.
It only removes things that are safe to remove without changing execution:
comments, blank lines, standalone docstrings, and unnecessary whitespace.

It does NOT rename identifiers, rewrite expressions, fold constants, merge
statements, or otherwise alter program behaviour. Those transformations can
save more bytes but are substantially less appropriate for a fragile
micro:bit/MicroPython target.

USAGE
    python minify_microbit.py <src_dir> <out_dir>
    python minify_microbit.py <src_dir> <out_dir> file1.py file2.py ...
"""

import io
import sys
import tokenize
from pathlib import Path


def _is_docstring(tokens, i):
    """Return True when tokens[i] is a standalone first-statement string.

    We recognise only the unambiguous cases:
      * module start
      * immediately after INDENT
      * immediately after a NEWLINE which follows a suite-opening ':'

    This intentionally avoids trying to understand arbitrary Python syntax.
    """
    if tokens[i].type != tokenize.STRING:
        return False

    j = i - 1

    # Ignore an INDENT immediately before the string.
    if j >= 0 and tokens[j].type == tokenize.INDENT:
        j -= 1

    # A module/function/class docstring is the first real token of its suite.
    if j < 0:
        return True

    if tokens[j].type == tokenize.NEWLINE:
        # Walk backwards over harmless structural tokens to find the ':' that
        # opened this suite. This is deliberately conservative.
        k = j - 1
        depth = 0
        while k >= 0:
            t = tokens[k]
            if t.type == tokenize.OP:
                if t.string in (")", "]", "}"):
                    depth += 1
                elif t.string in ("(", "[", "{"):
                    if depth:
                        depth -= 1
                    else:
                        break
                elif t.string == ":" and depth == 0:
                    return True
                elif t.string == ";":
                    break
            elif t.type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
                if t.type == tokenize.NEWLINE:
                    break
            k -= 1

    return False


def lexical_minify(source):
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))

    out = []
    prev = None
    skip_docstring = False

    for i, tok in enumerate(tokens):
        typ, text = tok.type, tok.string

        # These tokens have no runtime meaning in the source file.
        if typ in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NL):
            continue

        # Comments, including shebangs and encoding declarations, are safe.
        if typ == tokenize.COMMENT:
            continue

        # Standalone module/function/class docstrings are not needed for
        # execution. Only remove an unambiguously first string statement.
        if typ == tokenize.STRING and _is_docstring(tokens, i):
            skip_docstring = True
            continue

        if typ == tokenize.INDENT:
            # Preserve indentation levels but use one tab per source nesting
            # level. This is safe for normal 4-space Python source and also
            # handles 2/8-space indentation without silently dropping a level.
            spaces = len(text.expandtabs(8))
            out.append("\t" * max(1, spaces // 4))
            prev = tok
            continue

        if typ == tokenize.DEDENT:
            prev = tok
            continue

        if typ == tokenize.NEWLINE:
            # A removed docstring may leave an empty suite line; preserve the
            # newline because it may terminate the surrounding statement.
            out.append("\n")
            prev = tok
            skip_docstring = False
            continue

        # Whitespace between tokens is needed only where removing it would
        # change tokenisation. In particular, keep NAME/NUMBER boundaries and
        # operator pairs such as + +, - -, ** and //.
        if prev is not None:
            need_space = (
                (prev.type in (tokenize.NAME, tokenize.NUMBER)
                 and typ in (tokenize.NAME, tokenize.NUMBER))
                or (prev.string in ("+", "-", "~") and
                    text in ("+", "-", "~"))
                or (prev.string == "/" and text == "/")
                or (prev.string == "*" and text == "*")
            )
            if need_space:
                out.append(" ")

        out.append(text)
        prev = tok

    # A final newline is not required by Python/MicroPython and costs a byte.
    return "".join(out).rstrip()


def minify(path):
    return lexical_minify(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) < 3:
        print("usage: python minify_microbit.py <src_dir> <out_dir> [files...]")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sys.argv[3:] or sorted(p.name for p in src_dir.glob("*.py"))

    total_before = 0
    total_after = 0

    for name in files:
        src_path = src_dir / name
        if not src_path.exists():
            print(f"  skip (missing): {name}")
            continue

        before = src_path.stat().st_size

        try:
            new_src = minify(src_path)
        except (SyntaxError, tokenize.TokenError) as e:
            print(f"  skip (tokenise error): {name}: {e}")
            continue

        out_path = out_dir / name
        out_path.write_text(new_src, encoding="utf-8", newline="")

        after = out_path.stat().st_size
        total_before += before
        total_after += after

        pct = round(100 * after / before) if before else 0
        print(f"  {name}: {before} -> {after} bytes ({pct}%)")

    print()
    saved = total_before - total_after
    pct = round(100 * total_after / total_before) if total_before else 0
    print(f"TOTAL: {total_before} -> {total_after} bytes "
          f"(saved {saved} bytes, {pct}% of original)")


if __name__ == "__main__":
    main()
