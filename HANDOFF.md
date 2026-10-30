# HANDOFF — 2026-10-30

先读 `AGENTS.md` → `PROGRESS.md` → `features.json` → `docs/TESTING.md`。

本轮已完成 F-04：Codex 云端 ESP32 固件实际构建成功（Zephyr v4.4.2 / SDK 1.0.1）。C 断言、18 个 Python 测试、3 条模拟数据回放与工作流静态检查均通过；日志见 `evidence/`。主机测试输出的 NOT RUN 只描述主机测试脚本自身范围，固件结果以独立 `build.log` 为准。

新增工作流 `.github/workflows/cloud-check.yml`：push main/master、PR、手动运行；主机证据与固件分开上传。`scripts/setup_zephyr.sh` 只同步目标相关模块，按 SDK_VERSION 获取 SDK，并校验官方 SHA-256；`scripts/build.sh` 支持 BUILD_DIR/BUILD_JOBS。Windows 用户走 `ONLINE_NO_INSTALL_GUIDE.md`，无需本地 Zephyr。

下一项是 F-08 的真实 GitHub Actions 执行：推送审查后的修改，保存运行 URL、SHA 和 artifacts。当前未推送、没有远程运行结果；不要仅凭静态检查标记通过。

F-05～F-07 仍需真实板与传感器。GPIO18、3.3V、上拉和 UART0 115200 是设计配置而非现场验证；未烧录，必须先取得批准。采样是读取后休眠 3 秒，不能声称严格实时。不要把 synthetic fixture 当硬件证据。

当前云环境复验：`source /workspace/.setup/activate.sh`，从项目目录运行 `python3 scripts/test_host.py`；`BUILD_DIR=/workspace/.build/esp32-dht11 bash scripts/build.sh`。新任务先检查环境，不假定该机器的绝对路径总存在。
