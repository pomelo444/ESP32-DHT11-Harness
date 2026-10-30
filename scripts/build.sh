#!/usr/bin/env bash
set -euo pipefail
if ! command -v west >/dev/null 2>&1; then
  echo 'ERROR: west not installed or Zephyr environment not activated' >&2
  exit 2
fi
cd "$(dirname "$0")/.."
west build --cmake -b esp32_devkitc/esp32/procpu \
  -d "${BUILD_DIR:-build}" . -o=-j"${BUILD_JOBS:-4}"
