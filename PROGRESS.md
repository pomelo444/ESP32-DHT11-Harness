# PROGRESS — 2026-10-30

## Current status
- Completed locally: F-01 (Harness artifacts), F-02 (portable C JSON), F-03 (Python receiver + host contract).
- Evidence: `evidence/host_test_run.log` (10 Python tests, C assertions), `evidence/host_synthetic_samples.jsonl` (3 synthetic messages), and offline replay.
- NOT run: `west build`, `west flash`, physical DHT11 readings, actual UART serial capture. West/Zephyr SDK and board are absent in preparation environment.
- F-04 through F-07 remain `passes=false` until genuinely verified.

## Next action (on real equipment)
1. Identify the actual ESP32 module, verify power/ground/DATA GPIO18 and sensor pullup.
2. Activate Zephyr environment and run `west blobs fetch hal_espressif`, `bash scripts/build.sh`.
3. Save full build output to `evidence/build.log`, record Zephyr version.
4. Obtain consent before firmware flashing. Execute `west flash`.
5. Run Python UART receiver, save 10 real readings to `evidence/uart_capture.jsonl`.
6. Disconnect sensor signal in a controlled test, save ERROR evidence and update feature status.

## Caveats
- Synthetic host data is **not** hardware evidence. Hardware execution and timing are not assumed successful.
- Commit to Git after review; zip package is a portable project snapshot, not a Git history.
