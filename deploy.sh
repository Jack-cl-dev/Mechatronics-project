#!/usr/bin/env bash
# Copy the project onto the micro:bit and run it.
#
# The micro:bit only auto-runs a file called main.py, so whichever entry script
# you pick is copied to the device AS main.py. The other entry script is left
# behind so it can't shadow it.
#
#   ./deploy.sh                       deploy Code/main.py       as main.py
#   ./deploy.sh test_avoidance.py     deploy Code/test_avoidance.py as main.py
#   ./deploy.sh test_avoidance.py --no-run   copy only, don't attach to serial
#
# Works on Linux and on Windows under Git Bash / MSYS2 / Cygwin. On Windows it
# will install mpremote for you if it's missing; on Linux it expects mpremote to
# already be there (it is, on all of our machines).

set -euo pipefail

cd "$(dirname "$0")"

# Scripts that are entry points rather than importable modules. Exactly one of
# these is deployed, renamed to main.py.
ENTRY_CANDIDATES="main.py test_avoidance.py"
DEFAULT_ENTRY="main.py"

entry="$DEFAULT_ENTRY"
run_after=1
for arg in "$@"; do
    case "$arg" in
        --no-run) run_after=0 ;;
        -h|--help)
            sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
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

# mpremote may be a bare command or only reachable as `<python> -m mpremote`,
# which is the common case on Windows where the Scripts dir isn't on PATH.
MPREMOTE=()
find_mpremote() {
    if command -v mpremote >/dev/null 2>&1; then
        MPREMOTE=(mpremote)
        return 0
    fi
    for py in python py python3; do
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

if ! find_mpremote; then
    if is_windows; then
        if ! install_mpremote || ! find_mpremote; then
            echo "Could not install mpremote automatically." >&2
            echo "Install Python from python.org (tick 'Add python.exe to PATH')," >&2
            echo "then run:  python -m pip install --user mpremote" >&2
            exit 1
        fi
    else
        echo "mpremote not found. Install it with: pipx install mpremote" >&2
        exit 1
    fi
fi

echo "Using mpremote: ${MPREMOTE[*]}"

# Everything that gets imported. robot_*.py are the vendor demo scripts -- they
# have top-level while loops and nothing imports them, so they stay off the
# device to save filesystem space.
echo "Copying modules..."
for module in Code/*.py; do
    name="$(basename "$module")"
    case " $ENTRY_CANDIDATES " in *" $name "*) continue ;; esac
    case "$name" in robot_*.py) continue ;; esac
    echo "  $name"
    "${MPREMOTE[@]}" connect auto fs cp "$module" ":$name"
done

echo "Copying Code/$entry as main.py (so the board runs it on reset)..."
"${MPREMOTE[@]}" connect auto fs cp "Code/$entry" ":main.py"

if [ "$run_after" -eq 1 ]; then
    echo "Running (Ctrl-C to stop, Ctrl-D then Ctrl-] to detach)..."
    "${MPREMOTE[@]}" connect auto run "Code/$entry"
else
    echo "Done. Reset the board to run it."
fi
