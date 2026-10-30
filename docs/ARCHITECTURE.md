# Architecture

Design source: course handout section on ESP32 + Zephyr + DHT11, including 2 threads / Queue and JSON Lines.

```text
 DHT11 (3.3V, GND, DATA=GPIO18)
        |
 Zephyr DHT driver + Sensor API
        |
 sensor_thread (approximately every 3000 ms)
        | sensor_reading {seq,uptime_ms,value,status,error_code}
        v
 k_msgq (capacity=8 messages)
        |
 output_thread (K_FOREVER receive)
        |
 pure-C json_report_format() -> JSON Lines
        |
 UART0 (115200, CRLF) -> USB-UART -> Host Python receiver -> JSONL file
```

Producer deliberately never blocks on a full queue: `k_msgq_put(..., K_NO_WAIT)` drops newest messages and increments `dropped_messages`. Gaps in `seq` let the receiver detect missing records (but not distinguish queue overflow from serial loss). Sequence starts at 1 after each reboot; uptime wraps at uint32 milliseconds.

`status=ERROR` uses null sensor values with nonzero error_code so downstream parsing can remain deterministic. Sensor values are stored as signed integer milli-units and serialized to two decimals without floating point formatting.

Periodic delay is measured after each sensor fetch, so actual sample-to-sample interval is 3000ms plus execution/scheduling overhead; not a hard real-time 3s guarantee.

Hardware wiring must be checked by the group. GPIO18 is a project design choice, not an observed board fact.

The receiver now reports `sequence_ok` separately from timing and handles uint32 uptime/sequence wrap. An empty or incomplete requested replay exits nonzero; a successful replay still does not establish hardware acceptance.
