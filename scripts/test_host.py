#!/usr/bin/env python3
"""Compile and execute genuine HOST-only tests (no ESP32 board needed)."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
TEST_BUILD = ROOT / ".host-build"
TEST_BUILD.mkdir(exist_ok=True)
compiler = os.environ.get("CC") or shutil.which("gcc") or shutil.which("clang")
if compiler is None:
    raise SystemExit("C compiler (gcc or clang) required for host test")


def compile_run(source, output):
    args = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
            "-I", str(ROOT / "src"),
            str(ROOT / "src" / "json_report.c"), str(ROOT / "tests" / source),
            "-o", str(TEST_BUILD / output)]
    subprocess.run(args, check=True)
    return subprocess.run([str(TEST_BUILD / output)], check=True,
                          capture_output=True, text=True).stdout


compile_run("test_json_report.c", "test_json_report")
print("PASS C serializer unit assertions")
result = compile_run("generate_host_samples.c", "generate_host_samples")
records = [json.loads(line) for line in result.splitlines()]
assert len(records) == 3
assert [record["status"] for record in records] == ["OK", "OK", "ERROR"]

sys.path.insert(0, str(ROOT / "scripts"))
from uart_receiver import parse_record, summarize  # noqa: E402
for line in result.splitlines():
    parse_record(line)
assert summarize(records)["intervals_ok"]
print("PASS C-to-Python JSON Lines integration (3 SYNTHETIC rows)")

unittest_args = [sys.executable, "-m", "unittest", "discover", "-s",
                 str(ROOT / "tests"), "-p", "test_receiver.py", "-v"]
subprocess.run(unittest_args, check=True)

fixture = ROOT / "evidence" / "host_synthetic_samples.jsonl"
fixture.write_text(result, encoding="utf-8")
print("PASS host tests; synthetic fixture saved:", fixture)
print("NOT RUN: Zephyr west build, ESP32 flash, live DHT11, live UART")
