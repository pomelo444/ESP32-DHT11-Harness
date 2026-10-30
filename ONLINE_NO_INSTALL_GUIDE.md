# 免在本机安装 Zephyr 的在线完成方式

## 一句话说明

本项目**仍然使用 Zephyr RTOS**，只是通过 GitHub Actions 的 Linux 云端运行器下载 Zephyr 源码、SDK 和工具链，进行 ESP32 固件交叉编译。用户本机不需要安装 Zephyr、west、CMake、SDK 或 Python。

该流程**不是**真实 ESP32 + DHT11 板上测试。编译成功证明固件生成，并不能证明 DHT11 能够读取温湿度、GPIO18 接线正确、串口数据来自真实设备。

## 纯浏览器操作

1. 注册/登录 https://github.com/ ，点击 New 建立一个仓库，例如 `esp32-dht11-harness`。建议使用私人仓库，避免公开个人作业或组员信息（Actions 用量与可用权限以账户为准）。
2. 解压本 ZIP，把压缩包内本目录中的**所有文件和隐藏的 `.github` 目录**上传到 GitHub 仓库根目录。必须保证根目录包含 `west.yml`，以及 `.github/workflows/cloud-check.yml`。
3. 打开仓库的 **Actions** 标签页。如果 GitHub 提示启用 Workflows，按提示启用。
4. 选择 `ESP32 Zephyr cloud verification` -> `Run workflow`。`push` 到 `main` / `master` 时也会自动触发。
5. 等待页面里的 `Host JSON / Python tests` 和 `ESP32 Zephyr cross compilation` 执行。**只有看到对应步骤绿色通过后**，才可在报告里写明云端编译通过。
6. 打开对应的 Job 查看日志。若成功，可从页面的 Artifacts 下载 `host-test-evidence` 和 `esp32-zephyr-firmware`，截图包含运行日期、构建目标和成功信息的页面作为**云端构建**证据。
7. 若 Zephyr 构建失败，请保留日志，交给 AI 分析修改，不要把失败改写为成功。

## 两类验证的区别

| 验证类型 | 无本地 Zephyr | 无实物 ESP32 | 能证明什么 |
|---|---|---|---|
| 主机 C/Python 测试 | 可以 | 可以 | JSON 格式化、解析、边界与合成数据路径 |
| GitHub Actions Zephyr 构建 | 可以 | 可以 | 若真正成功，证明 Zephyr 固件可交叉编译 |
| 真实 DHT11 采样 / 串口 / Queue 时序 | 可以用云端编译固件并交由有板同学测试 | 不可以 | 真实传感器与串口通信是否按要求工作 |

## 提交前怎么写

- 当前已经有的本机主机验证：C JSON 格式化测试、10 项 Python 解析单元测试、3 条**模拟**数据集成测试。
- 云端编译：**本文件只提供工作流，尚未在你的 GitHub 仓库运行**。成功后才可追加测试截图/日志和“已通过”。
- 硬件验证：没有板子、没有真实传感器数据时填“未验证”。
- 请补充你们小组的所有成员姓名。

## 注意事项

- `west.yml` 固定 Zephyr `v4.4.2`，避免示例依赖不稳定的每日开发主分支。
- GitHub Actions 的 Zephyr 安装运行在远程 Linux 服务器上，你不需要在 Windows 装 Zephyr。
- 云端流程受 GitHub 服务可用性、免费额度、网络与官方 Action 兼容性影响；本文件不是事先完成的云构建证明。
- 编译目标 `esp32_devkitc/esp32/procpu` 适用于**原版 ESP32 DevKitC**，与 ESP32-C3/S3 不同；若硬件不是原版 ESP32，需改目标和引脚。
- 如果老师严格要求实物效果，仍要有组员使用硬件验证，不能拿模拟串口数据充当实测。
