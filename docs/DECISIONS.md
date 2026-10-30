# Decisions

- D-001 | 2026-10-30 | Approach: Anthropic initializer + coding-agent feature list/progress/checkpoints. OpenAI-style mechanical tests are added as quality gates. Reason: the assignment allows Anthropic or DeepSeek, and this works without a hosted runtime.
- D-002 | 2026-10-30 | Target: ESP32 DevKitC original ESP32, Zephyr board `esp32_devkitc/esp32/procpu`, UART0 at 115200. Board-specific validation pending.
- D-003 | 2026-10-30 | DHT11 DATA planned on GPIO18; 3.3V and a 4.7–10 kOhm pullup if module lacks one. Physical wiring not observed.
- D-004 | 2026-10-30 | Two statically defined threads; nonblocking producer -> eight-slot k_msgq -> UART consumer. New records may be dropped under persistent queue overload.
- D-005 | 2026-10-30 | JSON Lines single record per sample; errors output `null` measurements and nonzero error_code; units `C` and `%RH`; seq and uptime_ms included.
- D-006 | 2026-10-30 | Separate pure-C serializer from Zephyr hardware layer to enable real host-unit testing without a board. No printf/sprintf for embedded JSON formatting.
- D-007 | 2026-10-30 | Documentation must distinguish host synthetic fixture and physically captured UART evidence. No unobserved PASS claims.
