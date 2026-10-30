# HANDOFF — Next Coding-Agent Session

Read in order: `AGENTS.md` -> `PROGRESS.md` -> `features.json` -> `docs/TESTING.md`.

Last genuinely executed command: `python scripts/test_host.py`.
Result: native C serializer assertions OK, native C -> Python JSONL integration (3 synthetic records) OK, 10 Python unittest cases OK. Offline replay OK. Logs in `evidence/`.

Outstanding: Feature F-04 (Zephyr board build) is next. Prepare an ESP32 + DHT11 setup and a Zephyr environment; do **not** mark hardware-related tasks PASS based on host results. Record errors if compilation or GPIO timing fails and iterate a single feature at a time.

Known assumptions: original ESP32 DevKitC board; DHT11 at GPIO18; 3.3V supply and pullup; UART0 at 115200. They are design choices to verify, not observed physical facts. Do not flash without approval.
