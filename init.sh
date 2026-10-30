#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo 'Harness initializer / project status:'
cat PROGRESS.md
python3 scripts/test_host.py
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git log --oneline -5
else
  echo 'Git repository not initialized. Run: git init && git add . && git commit -m "Initial project"'
fi
