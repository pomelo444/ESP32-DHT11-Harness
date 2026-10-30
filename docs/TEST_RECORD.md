# 中文测试记录 — 2026-10-30

执行地点：Codex Linux x86_64 云环境，Python 3.12.14、主机 GCC 14.2.0、west 1.5.0、CMake 4.4.4、Ninja 1.13.2、Zephyr v4.4.2、SDK 1.0.1、Xtensa GCC 14.3.0、esptool 5.6.0。

| 检查 | 实际结果 | 证据 |
|---|---|---|
| `python3 scripts/test_host.py` | 通过：C 断言、3 条 C→Python 模拟 JSON 集成、18 个 Python 测试 | `evidence/host_test_run.log` |
| `python3 scripts/uart_receiver.py --input evidence/host_synthetic_samples.jsonl --count 3` | 通过：3 条、2 OK/1 ERROR、intervals_ok 与 sequence_ok 均为 true | `evidence/offline_replay.log` |
| `bash scripts/setup_zephyr.sh` | 通过：同步固定模块，当前已安装 SDK 可复用，依赖检查通过 | `evidence/setup.log` |
| `BUILD_DIR=/workspace/.build/esp32-dht11 bash scripts/build.sh` | 通过：目标 `esp32_devkitc/esp32/procpu`，生成非空 ELF/BIN；SHA-256 见日志末尾 | `evidence/build.log` |
| actionlint v1.7.7 | 通过：Actions YAML/表达式检查，无报告错误 | `evidence/workflow_validation.log` |
| `bash -n scripts/build.sh scripts/setup_zephyr.sh init.sh` | 通过：Bash 语法检查 | `evidence/workflow_validation.log` |
| GitHub Actions 托管执行 | 未执行，无远程运行 URL，不能标记成功 | F-08 保持 false |
| 固件烧录、真实温湿度、真实 UART、断线与队列满 | 均未执行，无硬件证据 | F-05～F-07 保持 false |

Python 新增回归覆盖：空/不足/足量输入的 CLI 退出码、负 count、重复键、整数范围、非有限/巨大读数、uint32 回绕、序号缺口和重启。日志中的 `SKIP: invalid JSON` 是接收器故意跳过启动文本的输出；18 个 unittest 全部执行，没有跳过测试。

C 测试使用 `-std=c11 -Wall -Wextra -Werror -pedantic`；新增精确容量、短一字节的越界哨兵以及 INT32_MIN/INT32_MAX/UINT32_MAX 断言。合成数据文件含 ERROR 记录是刻意的协议测试，不是实际 DHT11 故障。

固件本轮使用当前云环境有效缓存并重新配置、链接和生成镜像，未声称是全新 GitHub runner 的全量构建。上一轮设置已下载并验证官方 SDK 与工具链 SHA-256；本轮 bootstrap 复用它们，未再次执行 SDK 首次下载分支。Actions 的全新 Ubuntu 安装、制品上传与 GitHub 权限仍需首次实际运行验证。

主机脚本打印的 `NOT RUN: Zephyr west build...` 描述其自身不执行的范围；独立固件构建已执行，以 `build.log` 为准。没有把该行改为虚构的固件或硬件 PASS。

复现方法见 `TESTING.md` 和 `../ONLINE_NO_INSTALL_GUIDE.md`。在 GitHub 首次运行通过后追加运行 URL、提交 SHA、目标、下载产物校验值；硬件日志须单独存储，不覆盖 `host_synthetic_samples.jsonl`。
