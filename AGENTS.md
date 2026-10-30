# Agent entry point — ESP32 / Zephyr / DHT11

Read these at session start (in order): `PROGRESS.md`, `features.json`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`.

Rules:
- Work on ONE incomplete feature per session. Inspect existing files before editing.
- Distinguish host-generated synthetic data from real ESP32 UART evidence.
- Never mark a feature `passes=true` without its own acceptance evidence.
- Do not edit verified pin connections or flash a physical device without owner approval.
- Preserve two threads, fixed-size queue, and the JSON Lines contract.
- Avoid `printf` and `sprintf` in embedded C. Keep JSON serialization host-testable.
- Run `python3 scripts/test_host.py` after changes; perform `west build` when Zephyr SDK exists.
- Commit only after review; document results and unresolved items in `PROGRESS.md` and `HANDOFF.md`.
