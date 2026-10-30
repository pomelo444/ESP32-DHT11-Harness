# HANDOFF — 2026-10-30

先读 `AGENTS.md` → `PROGRESS.md` → `features.json` → `docs/TESTING.md`。

本轮已完成 F-04：Codex 云端 ESP32 固件实际构建成功（Zephyr v4.4.2 / SDK 1.0.1）。C 断言、18 个 Python 测试、3 条模拟数据回放与工作流静态检查均通过；日志见 `evidence/`。主机测试输出的 NOT RUN 只描述主机测试脚本自身范围，固件结果以独立 `build.log` 为准。

新增工作流 `.github/workflows/cloud-check.yml`：push main/master、PR、手动运行；主机证据与固件分开上传。`scripts/setup_zephyr.sh` 只同步目标相关模块，按 SDK_VERSION 获取 SDK，并校验官方 SHA-256；`scripts/build.sh` 支持 BUILD_DIR/BUILD_JOBS。Windows 用户走 `ONLINE_NO_INSTALL_GUIDE.md`，无需本地 Zephyr。

PR #1 的首次远程运行 41056844083 初始化失败，已由修复提交 `8e51c0f3f03fa6367645551c3a942048aa4ab9cd` 解决。[运行 41058064524](https://github.com/pomelo444/ESP32-DHT11-Harness/actions/runs/41058064524) 的主机与固件两个 Job 均成功，F-08 已通过，公开步骤状态与三个产物 SHA-256 摘要见 `evidence/github_actions.json`。

F-05～F-07 仍需真实板与传感器。GPIO18、3.3V、上拉和 UART0 115200 是设计配置而非现场验证；未烧录，必须先取得批准。采样是读取后休眠 3 秒，不能声称严格实时。不要把 synthetic fixture 当硬件证据。

当前云环境复验：`source /workspace/.setup/activate.sh`，从项目目录运行 `python3 scripts/test_host.py`；`BUILD_DIR=/workspace/.build/esp32-dht11 bash scripts/build.sh`。新任务先检查环境，不假定该机器的绝对路径总存在。

## 本次修复交接

`scripts/setup_zephyr.sh --init-only` 只初始化与检查本地配置，不加载导入；正常调用会在 `west update zephyr` 后解析 manifest。`scripts/test_west_bootstrap.py` 使用本地 Git fixture 与真实 west，不需要网络或 SDK，4 项通过，已接入固件 Job。真实全新 West/SDK 下载与全量 ESP32 构建也已在 Codex 云环境通过，见 cold_setup/cold_build 日志。修复已推送原分支，实际重跑已成功；API 当前返回 Forbidden，采用公开 GitHub 运行/Job 网页核验步骤和产物元数据，未声称下载了需登录的完整远程日志。接下来审查 PR #1，不自动合并；硬件 F-05～F-07 不变。
