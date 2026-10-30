"""Host-side JSON Lines receiver for ESP32; supports offline replay and live UART.

Offline tests never count as physical board verification.
"""
import argparse
import json
import math
import pathlib
import sys


class RecordError(ValueError):
    pass


def parse_record(line):
    if isinstance(line, bytes):
        line = line.decode("utf-8", errors="strict")
    if len(line) > 512:
        raise RecordError("line too long")
    try:
        data = json.loads(line)
    except (ValueError, TypeError) as exc:
        raise RecordError("invalid JSON") from exc
    if not isinstance(data, dict):
        raise RecordError("JSON record must be an object")
    required = {
        "device", "seq", "uptime_ms", "temperature", "temperature_unit",
        "humidity", "humidity_unit", "status", "error_code"
    }
    if set(data) != required:
        raise RecordError("field set mismatch")
    if data["device"] != "ESP32-DHT11":
        raise RecordError("unexpected device")
    if data["temperature_unit"] != "C" or data["humidity_unit"] != "%RH":
        raise RecordError("unit mismatch")
    for field, minimum in (("seq", 1), ("uptime_ms", 0)):
        value = data[field]
        if type(value) is not int or value < minimum:
            raise RecordError(field + " must be an unsigned integer")
    if type(data["error_code"]) is not int:
        raise RecordError("error_code must be integer")
    if data["status"] == "OK":
        if data["error_code"] != 0:
            raise RecordError("OK with error_code")
        for field in ("temperature", "humidity"):
            v = data[field]
            if type(v) not in (int, float) or not math.isfinite(v):
                raise RecordError("invalid " + field)
    elif data["status"] == "ERROR":
        if data["error_code"] == 0:
            raise RecordError("ERROR with zero error_code")
        if data["temperature"] is not None or data["humidity"] is not None:
            raise RecordError("ERROR must contain null readings")
    else:
        raise RecordError("invalid status")
    return data


def summarize(records):
    if not records:
        return {"total": 0, "ok": 0, "errors": 0, "intervals_ok": None}
    intervals = [b["uptime_ms"] - a["uptime_ms"]
                 for a, b in zip(records, records[1:])]
    # The application uses k_sleep(3000 ms) after sampling: the 500 ms
    # window is a *coursework acceptance tolerance*, not a hard timing guarantee.
    intervals_ok = all(3000 <= diff <= 3500 for diff in intervals) if intervals else None
    return {"total": len(records),
            "ok": sum(x["status"] == "OK" for x in records),
            "errors": sum(x["status"] == "ERROR" for x in records),
            "intervals_ok": intervals_ok}


def receive(lines, output_path=None, limit=0):
    accepted = []
    out = None
    try:
        if output_path:
            dest = pathlib.Path(output_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            out = dest.open("w", encoding="utf-8")
        for raw in lines:
            try:
                record = parse_record(raw)
            except (RecordError, UnicodeError) as exc:
                print("SKIP:", str(exc), file=sys.stderr)
                continue
            accepted.append(record)
            if out is not None:
                out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            print(json.dumps(record, ensure_ascii=False))
            if limit and len(accepted) >= limit:
                break
    finally:
        if out is not None:
            out.close()
    return accepted


def main():
    parser = argparse.ArgumentParser(description="ESP32 JSONL UART receiver")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--port", help="serial port like COM5 or /dev/ttyUSB0")
    src.add_argument("--input", help="offline JSONL path; does NOT prove UART works")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--out", help="write accepted JSONL to this path")
    args = parser.parse_args()

    if args.input:
        with open(args.input, encoding="utf-8") as stream:
            rows = receive(stream, args.out, args.count)
    else:
        try:
            import serial
        except ImportError as exc:
            raise SystemExit("pip install pyserial first") from exc
        # Avoid deliberate DTR/RTS reset, although some adapters can glitch
        # those lines when the OS first opens the device.
        ser = serial.Serial()
        ser.port = args.port
        ser.baudrate = args.baud
        ser.timeout = 1.0
        ser.rtscts = False
        ser.dsrdtr = False
        ser.rts = False
        ser.dtr = False
        ser.open()
        try:
            def serial_lines():
                while True:
                    chunk = ser.readline()
                    if chunk:
                        yield chunk
            rows = receive(serial_lines(), args.out, args.count)
        finally:
            ser.close()
    print("SUMMARY:", json.dumps(summarize(rows), ensure_ascii=False))


if __name__ == "__main__":
    main()
