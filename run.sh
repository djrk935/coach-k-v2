#!/usr/bin/env bash
# Start the Coach K v2 backend. Sets the Homebrew lib path WeasyPrint needs on
# macOS (libgobject/pango) — without it the server crashes on import.
set -euo pipefail
cd "$(dirname "$0")"
export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib"
exec .venv/bin/uvicorn app.main:app --port 8000 "$@"
