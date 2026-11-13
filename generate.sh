#!/usr/bin/env bash
# Antigravity Unlimited Video Engine Runner
# Automatically runs python within the project's dedicated virtualenv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
  VENV_PYTHON="python3"
fi

exec "$VENV_PYTHON" "$SCRIPT_DIR/automate_reel.py" "$@"
