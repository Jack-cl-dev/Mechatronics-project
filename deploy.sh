#!/usr/bin/env bash
# Copy the project onto the micro:bit and run it.
#
# Deployment flow:
#   Code/*.py -> minify.py -> .minified/*.py -> micro:bit
#
# mpremote is always given one concrete filename at a time. No shell
# wildcards are passed to mpremote.
#
# Usage:
#   ./deploy.sh
#   ./deploy.sh test_avoidance.py
#   ./deploy.sh test_avoidance.py --no-run

set -euo pipefail

cd "$(dirname "$0")"

ENTRY_CANDIDATES="main.py test_avoidance.py"
DEFAULT_ENTRY="main.py"
MINIFIED_DIR=".minified"

entry="$DEFAULT_ENTRY"
run_after=1

for arg in "$@"; do
    case "$arg" in
        --no-run) run_after=0 ;;
        -h|--help)
            sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *) entry="$arg" ;;
    esac
done

if [ ! -f "Code/$entry" ]; then
    echo "No such entry script: Code/$entry" >&2
    echo "Available:$(for e in $ENTRY_CANDIDATES; do [ -f "Code/$e" ] && printf ' %s' "$e"; done)" >&2
    exit 1
fi

is_windows() {
    case "$(uname -s 2>/dev/null || echo unknown)" in
        MINGW*|MSYS*|CYGWIN*|Windows_NT) return 0 ;;
        *) return 1 ;;
    esac
}

MPREMOTE=()
find_mpremote() {
    if command -v mpremote >/dev/null 2>&1; then
        MPREMOTE=(mpremote)
        return 0
    fi

    for py in python python3 py; do
        if command -v "$py" >/dev/null 2>&1 \
           && "$py" -c "import mpremote" >/dev/null 2>&1; then
            MPREMOTE=("$py" -m mpremote)
            return 0
        fi
    done
    return 1
}

install_mpremote() {
    for py in python py python3; do
        if command -v "$py" >/dev/null 2>&1; then
            echo "Installing mpremote with $py..."
            if "$py" -m pip install --user --upgrade mpremote; then
                return 0
            fi
        fi
    done
    return 1
}

# Find Python for the minifier.
PYTHON=""
for py in python3 python py; do
    if command -v "$py" >/dev/null 2>&1; then
        PYTHON="$py"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python is required to run minify.py." >&2
    exit 1
fi

if [ ! -f "minify.py" ]; then
    echo "minify.py not found next to deploy.sh." >&2
    exit 1
fi

echo "Minifying Code/ into $MINIFIED_DIR..."
rm -rf "$MINIFIED_DIR"
mkdir -p "$MINIFIED_DIR"
"$PYTHON" minify.py Code "$MINIFIED_DIR"

# The minifier skips files it cannot parse. Make sure the selected entry
# actually made it into the deployment directory.
if [ ! -f "$MINIFIED_DIR/$entry" ]; then
    echo "Minification did not produce $MINIFIED_DIR/$entry." >&2
    exit 1
fi

if ! find_mpremote; then
    if is_windows; then
        if ! install_mpremote || ! find_mpremote; then
            echo "Could not install mpremote automatically." >&2
            echo "Install it with: python -m pip install --user mpremote" >&2
            exit 1
        fi
    else
        echo "mpremote not found. Install it with: pipx install mpremote" >&2
        exit 1
    fi
fi

echo "Using mpremote: ${MPREMOTE[*]}"

echo "Copying minified modules..."
copied=0
while IFS= read -r -d '' module; do
    name="$(basename "$module")"

    # Entry scripts are handled separately below. The selected entry becomes
    # main.py; the other entry point is not copied at all.
    case " $ENTRY_CANDIDATES " in *" $name "*) continue ;; esac

    echo "  $name"
    "${MPREMOTE[@]}" connect auto fs cp "$module" ":$name"
    copied=$((copied + 1))
done < <(find "$MINIFIED_DIR" -maxdepth 1 -type f -name '*.py' -print0 | sort -z)

echo "Copying $MINIFIED_DIR/$entry as main.py..."
"${MPREMOTE[@]}" connect auto fs cp "$MINIFIED_DIR/$entry" ":main.py"

if [ "$run_after" -eq 1 ]; then
    echo "Running minified $entry (Ctrl-C to stop, Ctrl-D then Ctrl-] to detach)..."
    "${MPREMOTE[@]}" connect auto run "$MINIFIED_DIR/$entry"
else
    echo "Done. Reset the board to run it."
fi
