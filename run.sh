#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
export PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1

case "${1:-}" in
    assemble)
        shift
        exec python3 -m src.assembler "$@"
        ;;
    interpret)
        shift
        exec python3 -m src.interpreter "$@"
        ;;
    test)
        shift
        exec python3 -m unittest discover -s "$PROJECT_DIR/tests" -v "$@"
        ;;
    *)
        printf 'Usage: %s {assemble|interpret|test} [args...]\n' "$0" >&2
        exit 2
        ;;
esac
