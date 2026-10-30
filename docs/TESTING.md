# Verification gates and evidence boundaries

1. Host serializer assertions: `python3 scripts/test_host.py` executes a native C binary.
2. Cross-language contract: host C generates 3 SYNTHETIC JSON lines; Python validates and parses them.
3. Receiver tests: Python unittest covers valid/invalid JSON, fields, units, status, intervals.
4. Real Zephyr compilation: `bash scripts/build.sh` in a Zephyr 4.x environment; archive actual command/log into `evidence/build.log`.
5. Physical flash: `west flash`, then capture 10 real JSON records with `python scripts/uart_receiver.py --port COM5 --count 10 --out evidence/uart_capture.jsonl`.
6. Physical verification: record board identification, wiring photo, serial port, 10 live records, error test (disconnect DHT11 DATA), sequence, 3s intervals (tolerance 3000 to 3500ms under low load). Preserve logs.

A host test PASS does not establish #4–#6. Until #4–#6 are carried out, do not claim the board and firmware were verified.

Possible board-specific issues: Zephyr/ESP-IDF version differences, GPIO pulse timing, USB UART auto-reset via DTR/RTS. Adjust only on observed evidence.
