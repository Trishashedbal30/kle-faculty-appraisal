#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Follow START_HERE.md to create the Python 3.12 virtual environment first."
  exit 1
fi
exec .venv/bin/python manage.py run
