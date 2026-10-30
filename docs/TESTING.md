# Verification gates and evidence boundaries

1. Host serializer assertions: `python3 scripts/test_host.py` executes a native C binary.
2. Cross-language contract: host C generates 3 SYNTHETIC JSON lines; Python validates and parses them.
3. Receiver tests: Python unittest covers valid/invalid JSON, fields, units, status, intervals.
4. Real Zephyr compilation: `bash scripts/build.sh` in a Zephyr 4.x environment; archive actual command/log into `evidence/build.log`. This build needs no board.
5. Physical flash: `west flash`, then capture 10 real JSON records with `python scripts/uart_receiver.py --port COM5 --count 10 --out evidence/uart_capture.jsonl`.
6. Physical verification: record board identification, wiring photo, serial port, 10 live records, error test (disconnect DHT11 DATA), sequence, 3s intervals (tolerance 3000 to 3500ms under low load). Preserve logs.

A host test PASS does not establish #4–#6. Until #4–#6 are carried out, do not claim the board and firmware were verified.

Possible board-specific issues: Zephyr/ESP-IDF version differences, GPIO pulse timing, USB UART auto-reset via DTR/RTS. Adjust only on observed evidence.

## 本轮结果与 Windows 云端路径

2026-10-30：C 断言、18 个 Python 测试、3 条合成回放、Codex 云环境 ESP32 构建均通过。详细版本、执行范围及日志见 [TEST_RECORD.md](TEST_RECORD.md)。F-04 已有编译证据；F-05～F-07 仍无硬件证据。

GitHub Actions 使用 `.github/workflows/cloud-check.yml`；push main/master、PR 或手动触发。Windows 只需浏览器，见 [在线指南](../ONLINE_NO_INSTALL_GUIDE.md)。工作流已通过 actionlint，修复后的托管运行 [41058064524](https://github.com/pomelo444/ESP32-DHT11-Harness/actions/runs/41058064524) 已实际成功，F-08 为 true。

Linux 复现：先准备 Python 3.12 虚拟环境及 west 1.5.0、CMake、Ninja、GCC、gperf、dtc；然后 `bash scripts/setup_zephyr.sh`，按输出设置 ZEPHYR_BASE、ZEPHYR_SDK_INSTALL_DIR、ZEPHYR_TOOLCHAIN_VARIANT，再 `bash scripts/build.sh`。脚本使用项目父目录作 West workspace，应在隔离 checkout 中运行；不得覆盖其他项目的 West 配置。

`--count N` 表示请求 N 条有效记录；离线输入不足会返回 1，参数无效返回 2，记录数满足返回 0。`--count 0` 读至输入结束（实时串口持续读取）。验收时还需检查 summary 的 intervals_ok / sequence_ok 和状态分布，退出码只证明记录数满足，不证明采样时序或硬件正确。

West 首次初始化回归：激活 west 环境后运行 `python3 scripts/test_west_bootstrap.py`（4 项真实 West 测试，不需要网络或 SDK）；`bash scripts/setup_zephyr.sh --init-only` 可只检查本地初始化，不能把它当完整安装成功。正常设置会先下载 Zephyr 再解析项目导入。
