#!/bin/sh

# Pokud existuje python3, použij ho
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Python interpreter not found." >&2
    exit 1
fi

exec "$PYTHON" "$@"
