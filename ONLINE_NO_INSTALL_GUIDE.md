# 免在本机安装 Zephyr 的在线完成方式

## 一句话说明

本项目**仍然使用 Zephyr RTOS**，只是通过 GitHub Actions 的 Linux 云端运行器下载 Zephyr 源码、SDK 和工具链，进行 ESP32 固件交叉编译。用户本机不需要安装 Zephyr、west、CMake、SDK 或 Python。

该流程**不是**真实 ESP32 + DHT11 板上测试。编译成功证明固件生成，并不能证明 DHT11 能够读取温湿度、GPIO18 接线正确、串口数据来自真实设备。

## 纯浏览器操作（现有仓库优先）

1. 登录现有仓库 `pomelo444/ESP32-DHT11-Harness`，审查并合入本轮修改。无需新建仓库；若使用 ZIP 副本，可上传至自己的仓库（Actions 权限与用量以账户为准）。
2. 使用 Git 时推送审查后的提交；若使用 ZIP 副本，解压并上传**包括隐藏 `.github` 目录在内的完整项目**。确认仓库根目录有 `west.yml` 和 `.github/workflows/cloud-check.yml`。
3. 打开仓库的 **Actions** 标签页。如果 GitHub 提示启用 Workflows，按提示启用。
4. 选择 `ESP32 Zephyr cloud verification` -> `Run workflow`。`push` 到 `main` / `master` 时也会自动触发。
5. 等待页面里的 `Host JSON / Python tests` 和 `ESP32 Zephyr cross compilation` 执行。PR 也会触发；手动入口须先让工作流存在于默认分支。**只有看到对应步骤绿色通过后**，才可在报告里写明云端编译通过。
6. 打开对应的 Job 查看日志。若成功，可从页面的 Artifacts 下载 `host-test-evidence`、`esp32-build-evidence` 和 `esp32-zephyr-firmware`，截图包含运行日期、构建目标和成功信息的页面作为**云端构建**证据。
7. 若 Zephyr 构建失败，请保留日志，交给 AI 分析修改，不要把失败改写为成功。

## 两类验证的区别

| 验证类型 | 无本地 Zephyr | 无实物 ESP32 | 能证明什么 |
|---|---|---|---|
| 主机 C/Python 测试 | 可以 | 可以 | JSON 格式化、解析、边界与合成数据路径 |
| GitHub Actions Zephyr 构建 | 可以 | 可以 | 若真正成功，证明 Zephyr 固件可交叉编译 |
| 真实 DHT11 采样 / 串口 / Queue 时序 | 可以用云端编译固件并交由有板同学测试 | 不可以 | 真实传感器与串口通信是否按要求工作 |

## 提交前怎么写

- 当前已经有的 Codex 云环境主机验证：C JSON 格式化测试、18 项 Python 解析单元测试、3 条**模拟**数据集成测试。
- 云端编译：Codex 云环境已成功编译 Zephyr v4.4.2 / SDK 1.0.1；**GitHub 托管 Actions 尚未运行**，两者不得混淆。成功后才可追加测试截图/日志和“已通过”。
- 硬件验证：没有板子、没有真实传感器数据时填“未验证”。
- 请补充你们小组的所有成员姓名。

## 注意事项

- `west.yml` 固定 Zephyr `v4.4.2`，避免示例依赖不稳定的每日开发主分支。
- GitHub Actions 的 Zephyr 安装运行在远程 Linux 服务器上，你不需要在 Windows 装 Zephyr。
- 云端流程受 GitHub 服务可用性、免费额度、网络与官方 Action 兼容性影响；本文件不是事先完成的云构建证明。
- 编译目标 `esp32_devkitc/esp32/procpu` 适用于**原版 ESP32 DevKitC**，与 ESP32-C3/S3 不同；若硬件不是原版 ESP32，需改目标和引脚。
- 如果老师严格要求实物效果，仍要有组员使用硬件验证，不能拿模拟串口数据充当实测。

## 下载后的硬件交接

产物提供 `zephyr.elf`、`zephyr.bin`、生成的 `zephyr.dts` 与 `.config`。这些是构建产物，不等于适用于任意模块的一键烧录包；烧录者应检查目标、flash offset 和设备型号，并按 Zephyr runner/实际板配置操作。不要猜偏移或未经批准烧录。本指南不要求 Windows 安装 Zephyr；真实烧录与串口实测可交给有设备的同学完成。
