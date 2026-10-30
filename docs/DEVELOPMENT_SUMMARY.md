# 中文开发总结

日期：2026-10-30。组员姓名、班级、学号：由提交小组填写。

## 作业实现与审查

工程使用 Zephyr RTOS，目标为原版 ESP32 DevKitC 的 PROCPU。`sensor_thread` 调用 DHT 驱动取得温湿度，形成固定大小的 `sensor_reading`；`output_thread` 阻塞等待消息并通过 UART0 发出每行一个 JSON 对象。两个工作线程各有 2048 字节栈、优先级 5，由 `K_THREAD_DEFINE` 启动；Zephyr 自身还会有系统线程。

`K_MSGQ_DEFINE` 分配 8 个固定槽位。生产者用 `K_NO_WAIT` 入队，满队列时丢弃最新记录并增加内部计数；序号缺口可提示丢失，但不能单凭缺口区分队列溢出与串口丢包。消费者用 `K_FOREVER` 等待。采集失败时保留序号和 uptime，输出 `null`、`ERROR` 及非零错误码。

当前循环在读取后休眠 3000ms，因此是约 3 秒采集，包含驱动与调度耗时。课程验收使用 3000～3500ms 容差；真实周期、线程运行与队列压力均未进行板上测量。

`prj.conf` 启用了 GPIO、传感器、DHT、串口及 UART console，关闭日志。`app.overlay` 将 DHT 绑定至 GPIO18，并启用内部上拉；外部 4.7～10kΩ 上拉和 3.3V 电气条件仍需现场核实。构建后的设备树确认 console 为 UART0、波特率 115200、DATA 为 GPIO18。已有嵌入式实现符合上述结构，本轮保留它，未改引脚或线程。

## 本轮修复与自动化

- 接收器原先对空回放、记录不足也返回成功；现返回非零退出码，并用 CLI 回归测试验证。
- 明确接收 uint32 序号和 uptime、int32 错误码；序号在回绕时允许 0。拒绝重复字段、非有限值、超出序列化表示范围的数值。
- 汇总新增 `sequence_ok`，间隔按 uint32 回绕计算；这些诊断不自动证明板上采样正常，调用者须检查汇总。
- C 测试补充精确缓冲区容量、越界哨兵与整数极值。Python 测试增至 18 项。
- 新增 GitHub Actions：主机测试通过后编译 ESP32，安装固定 Zephyr v4.4.2 与 SDK 1.0.1，只取目标相关模块；SDK/工具链使用官方 SHA-256 校验。第三方 Actions 固定提交 SHA，权限仅 contents:read。
- 上传主机合成数据、构建日志、ELF/BIN、设备树与配置。失败仍保留当次日志，构建前清除检入的旧日志，避免把历史成功冒充本次成功。
- 新增构建产物忽略规则；构建脚本支持目录与并发覆盖并保留有效增量产物。

## Harness 验收方法

沿用项目的 initializer/coding-agent 入口、`features.json`、进度与交接文件。先检查已有代码，聚焦 F-04，再按执行证据更新状态。F-04 由实际 Zephyr 构建证明；F-08 单独要求 GitHub 运行 URL；F-05～F-07 必须由硬件证据证明。测试详情和未执行事项见 `TEST_RECORD.md`。

本次完成的是可审查源码、自动化配置及云环境编译验证，不是完整硬件验收。Windows 无需安装 Zephyr：在浏览器运行 Actions、下载产物后由有设备的同学按实际 runner 配置烧录。后续修复已推送原分支并更新 PR #1，GitHub Actions [41058064524](https://github.com/pomelo444/ESP32-DHT11-Harness/actions/runs/41058064524) 主机测试与固件构建已通过；仍未连接或烧录开发板。

## West 首次初始化修复

原脚本在 `west update` 前解析包含 import:true 的 manifest，冷环境缺少 Zephyr 时失败。现先读取 `.west/config` 检查实际 checkout 归属，下载 Zephyr 后才解析导入；保留 self.path:app 的默认语义。4 项真实 West 回归与一次全新 West/SDK 下载、全量构建已在 Codex 执行通过，GitHub 托管重跑也已成功，详见测试记录。
