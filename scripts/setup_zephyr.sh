#!/usr/bin/env bash
# Linux CI bootstrap. Run with Python 3.12+, west 1.5.0, CMake, Ninja,
# GCC, gperf, dtc, curl and xz installed. No hardware or flashing is used.
set -euo pipefail
if [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "$1" != --init-only ]; }; then
  echo 'Usage: bash scripts/setup_zephyr.sh [--init-only]' >&2
  exit 2
fi
APP=$(cd "$(dirname "$0")/.." && pwd)
WORKSPACE=$(dirname "$APP")
cd "$APP"
if [ ! -f "$WORKSPACE/.west/config" ]; then
  west init -l "$APP"
fi
if [ "$(west topdir)" != "$WORKSPACE" ]; then
  echo 'ERROR: expected an isolated West workspace in the parent directory' >&2
  exit 2
fi
# Do NOT resolve project imports yet: a cold workspace has no Zephyr checkout.
# These config commands only read .west/config and do not load the manifest.
manifest_path=$(west config --local manifest.path)
manifest_file=$(west config --local manifest.file || echo west.yml)
if [ "$(realpath -m "$WORKSPACE/$manifest_path/$manifest_file")" != "$APP/west.yml" ]; then
  echo 'ERROR: existing West workspace belongs to another manifest' >&2
  exit 2
fi
if [ "${1:-}" = --init-only ]; then
  echo 'West workspace initialized and local manifest ownership checked (no imports resolved).'
  exit 0
fi
west config manifest.project-filter -- '-.*,+zephyr,+hal_espressif,+hal_xtensa,+picolibc,+mbedtls'
west update zephyr --fetch-opt=--depth=1 --fetch-opt=--no-tags
# Zephyr's west.yml is available now; full imported-manifest validation is safe.
resolved_manifest=$(west manifest --path)
if [ "$(realpath "$resolved_manifest")" != "$APP/west.yml" ]; then
  echo 'ERROR: resolved manifest does not match this application' >&2
  exit 2
fi
# Exact SHAs matter: fetching only shallow branch tips can omit pinned commits.
python3 - <<'PY'
from pathlib import Path
import subprocess
from west.manifest import Manifest
for p in Manifest.from_topdir().get_projects(['hal_espressif', 'hal_xtensa', 'picolibc', 'mbedtls']):
    if not (Path(p.abspath) / '.git').exists():
        Path(p.abspath).mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', p.abspath], check=True)
    found = subprocess.run(['git', '-C', p.abspath, 'cat-file', '-e',
                            p.revision + '^{commit}'], capture_output=True)
    if found.returncode:
        subprocess.run(['git', '-C', p.abspath, 'fetch', '--depth=1',
                        '--no-tags', p.url, p.revision], check=True)
PY
west update --fetch-opt=--depth=1 --fetch-opt=--no-tags
python3 -m pip install -r "$WORKSPACE/zephyr/scripts/requirements-base.txt" \
  -r "$WORKSPACE/modules/hal/espressif/zephyr/requirements.txt"
sdk_version=$(cat "$WORKSPACE/zephyr/SDK_VERSION")
sdk_dir=${ZEPHYR_SDK_INSTALL_DIR:-$WORKSPACE/.zephyr-sdk/zephyr-sdk-$sdk_version}
if [ "$(uname -s)-$(uname -m)" != Linux-x86_64 ]; then
  echo 'ERROR: this bootstrap supports Linux x86_64 runners only' >&2
  exit 2
fi
if [ ! -x "$sdk_dir/gnu/xtensa-espressif_esp32_zephyr-elf/bin/xtensa-espressif_esp32_zephyr-elf-gcc" ]; then
  mkdir -p "$(dirname "$sdk_dir")"
  download_dir=$(mktemp -d)
  trap 'rm -rf "$download_dir"' EXIT
  sdk_url="https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v$sdk_version"
  sdk_archive="zephyr-sdk-${sdk_version}_linux-x86_64_minimal.tar.xz"
  tc_archive=toolchain_gnu_linux-x86_64_xtensa-espressif_esp32_zephyr-elf.tar.xz
  (
    cd "$download_dir"
    curl -fsSL "$sdk_url/sha256.sum" -o sha256.sum
    for archive in "$sdk_archive" "$tc_archive"; do
      curl -fsSL "$sdk_url/$archive" -o "$archive"
      awk -v file="$archive" '$2 == file {print}' sha256.sum | sha256sum -c -
    done
    tar -xf "$sdk_archive"
    mkdir -p "zephyr-sdk-$sdk_version/gnu"
    tar -xf "$tc_archive" -C "zephyr-sdk-$sdk_version/gnu"
    mv "zephyr-sdk-$sdk_version" "$sdk_dir"
  )
fi
if [ "$(cat "$sdk_dir/sdk_version")" != "$sdk_version" ]; then
  echo 'ERROR: SDK version does not match Zephyr SDK_VERSION' >&2
  exit 2
fi
export ZEPHYR_BASE="$WORKSPACE/zephyr"
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export ZEPHYR_SDK_INSTALL_DIR="$sdk_dir"
west blobs fetch hal_espressif
python3 -m pip check
printf 'Zephyr: '; git -C "$ZEPHYR_BASE" describe --tags --always
echo "SDK: $sdk_version"
echo "ZEPHYR_BASE=$ZEPHYR_BASE"
echo "ZEPHYR_TOOLCHAIN_VARIANT=$ZEPHYR_TOOLCHAIN_VARIANT"
echo "ZEPHYR_SDK_INSTALL_DIR=$ZEPHYR_SDK_INSTALL_DIR"
if [ -n "${GITHUB_ENV:-}" ]; then
  {
    echo "ZEPHYR_BASE=$ZEPHYR_BASE"
    echo "ZEPHYR_TOOLCHAIN_VARIANT=$ZEPHYR_TOOLCHAIN_VARIANT"
    echo "ZEPHYR_SDK_INSTALL_DIR=$ZEPHYR_SDK_INSTALL_DIR"
  } >> "$GITHUB_ENV"
fi
