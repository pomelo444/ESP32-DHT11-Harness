> **零本地 Zephyr 安装方案**：打开 [ONLINE_NO_INSTALL_GUIDE.md](ONLINE_NO_INSTALL_GUIDE.md)，把本仓库上传 GitHub 后使用 Actions 云端构建。仅主机测试已运行，在线构建尚未运行，硬件测试未运行。

# ESP32 + Zephyr RTOS + DHT11 — Anthropic-style Harness Coursework

This is a **real source-code project plus host-verified tests**, not proof of physical deployment. Work aligns with the handout's final-page exercise. All group member names must be filled by the submitting group.

## 1. Design

Hardware: original **ESP32 DevKitC** (`esp32_devkitc/esp32/procpu`) + DHT11, DATA at GPIO18, 3.3V, GND. Connect a pullup 4.7–10 kOhm between DATA and 3.3V if not built into the sensor board. Use a level-safe 3.3 V signal. This is planned wiring, **not checked in person**.

Zephyr: two independent threads `sensor_thread` and `output_thread`. Producer samples every approximately 3s, pushes structured records through `k_msgq` (8 slots) and consumer emits JSON Lines at UART0 115200 baud. Error paths emit null numeric values and a nonzero error code.

## 2. Folder structure

- `src/main.c`: Zephyr sensor read, two threads, queue and UART.
- `src/json_report.[ch]`: portable, bounded JSON serializer, no printf/sprintf.
- `app.overlay`, `prj.conf`, `CMakeLists.txt`: board application configuration.
- `scripts/uart_receiver.py`: host receiver / offline replay / schema validation.
- `scripts/test_host.py`, `tests/*`: actual host tests and synthetic fixture.
- `AGENTS.md`, `features.json`, `PROGRESS.md`, `HANDOFF.md`, `init.sh`: Anthropic-style Harness control artifacts.
- `agent_prompts/*`, `docs/*`: repeatable agent workflow and decisions.

## 3. Host tests (can run without hardware)

Install Python 3.9+ and GCC or Clang, then from the project directory:

```sh
python scripts/test_host.py
```

The script compiles the native serializer, runs C assertions, generates 3 clearly **SYNTHETIC** records, executes Python parser tests, saves `evidence/host_synthetic_samples.jsonl`. This is genuine host-only verification. The script does not require pyserial.

## 4. Zephyr build / physical verification (group must execute)

Set up a working Zephyr 4.x environment (including Zephyr SDK, ESP32 tool dependencies) and connect the target board:

```sh
west update
west blobs fetch hal_espressif
west build -b esp32_devkitc/esp32/procpu -p always .
west flash
```

If you prefer a script in Linux/WSL, `bash scripts/build.sh` runs the build. Use an activated Zephyr environment on Windows/WSL. For local UART capture on Windows (replace COM5):

```powershell
py -m pip install -r requirements-host.txt
py scripts/uart_receiver.py --port COM5 --baud 115200 --count 10 --out evidence/uart_capture.jsonl
```

For Linux replace port with `/dev/ttyUSB0` or actual device. Stop any competing serial monitor. Zephyr boot messages are ignored as non-JSON. Some USB-UART adapters toggle RTS/DTR at open and may reset ESP32; inspect evidence before changing controls.

To replay *existing* JSONL without a board:

```sh
python scripts/uart_receiver.py --input evidence/host_synthetic_samples.jsonl --count 3
```

**Replay is not a hardware test**. Actual board testing should collect at least 10 rows, inspect seq, status, 3s intervals, and a controlled sensor disconnect failure.

## 5. Output format (synthetic illustration)

```json
{"device":"ESP32-DHT11","seq":1,"uptime_ms":100,"temperature":25.60,"temperature_unit":"C","humidity":62.00,"humidity_unit":"%RH","status":"OK","error_code":0}
```

On a sensor error, `temperature` and `humidity` become `null`, `status` is `ERROR`, and `error_code` carries a nonzero negative errno.

## 6. Acceptance and handoff

- Read `AGENTS.md` -> `PROGRESS.md` -> `features.json` before a new agent session.
- Do not mark a hardware-related feature as passed on source review alone.
- Run host tests after every change; run real Zephyr build and capture only on an available board.
- Save build evidence and UART logs, then update `features.json`, `PROGRESS.md`, `HANDOFF.md` truthfully. Commit with Git after checking results.

## 7. Scope boundary

No real ESP32/Zephyr toolchain or DHT11 hardware was connected in the preparation environment. Hardware-related features stay `passes=false`. Do not submit synthetic UART fixture as photographed/real device evidence.

## 8. References

1. Anthropic. *Effective harnesses for long-running agents*. https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
2. OpenAI. *Harness engineering: leveraging Codex in an agent-first world*. https://openai.com/index/harness-engineering/
3. DeepSeek. *DeepSeek Harness*. https://www.deepseek.com/en/harness/
4. Zephyr Project. *ESP32-DevKitC*. https://docs.zephyrproject.org/latest/boards/espressif/esp32_devkitc/doc/index.html
5. Zephyr Project. *aosong,dht binding*. https://docs.zephyrproject.org/latest/build/dts/api/bindings/sensor/aosong%2Cdht.html
6. Zephyr Project. *Message Queues*. https://docs.zephyrproject.org/latest/kernel/services/data_passing/message_queues.html
