import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from uart_receiver import RecordError, parse_record, receive, summarize


GOOD = {
    "device": "ESP32-DHT11", "seq": 1, "uptime_ms": 100,
    "temperature": 25.6, "temperature_unit": "C",
    "humidity": 62.0, "humidity_unit": "%RH",
    "status": "OK", "error_code": 0
}


class ReceiverTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(parse_record(json.dumps(GOOD)), GOOD)

    def test_bad_json(self):
        with self.assertRaises(RecordError):
            parse_record("broken}")

    def test_bad_field(self):
        row = dict(GOOD)
        del row["humidity_unit"]
        with self.assertRaises(RecordError):
            parse_record(json.dumps(row))

    def test_wrong_unit(self):
        row = dict(GOOD, humidity_unit="percentage")
        with self.assertRaises(RecordError):
            parse_record(json.dumps(row))

    def test_invalid_bool_seq(self):
        row = dict(GOOD, seq=True)
        with self.assertRaises(RecordError):
            parse_record(json.dumps(row))

    def test_bad_status_pair(self):
        row = dict(GOOD, status="ERROR")
        with self.assertRaises(RecordError):
            parse_record(json.dumps(row))

    def test_error_contract(self):
        row = dict(GOOD, status="ERROR", temperature=None,
                   humidity=None, error_code=-5)
        self.assertEqual(parse_record(json.dumps(row)), row)

    def test_long_record(self):
        with self.assertRaises(RecordError):
            parse_record(" " * 513)

    def test_summary_intervals(self):
        records = [dict(GOOD, seq=n, uptime_ms=100 + (n-1)*3000)
                   for n in (1, 2, 3)]
        self.assertTrue(summarize(records)["intervals_ok"])
        records[2]["uptime_ms"] = 7900
        self.assertFalse(summarize(records)["intervals_ok"])

    def test_replay_skips_invalid_lines(self):
        lines = ["boot banner\n", json.dumps(GOOD) + "\n", "not json\n"]
        with self.subTest("replay"):
            records = receive(lines, limit=1)
            self.assertEqual(len(records), 1)

    def test_integer_limits(self):
        for field, value in (("seq", -1), ("seq", 2**32),
                             ("uptime_ms", 2**32), ("error_code", -(2**31)-1)):
            with self.subTest(field=field, value=value), self.assertRaises(RecordError):
                parse_record(json.dumps(dict(GOOD, **{field: value})))

    def test_nonfinite_and_huge_readings(self):
        for value in (float("nan"), float("inf"), True, 10**400):
            with self.subTest(value=value), self.assertRaises(RecordError):
                parse_record(json.dumps(dict(GOOD, temperature=value)))

    def test_duplicate_fields(self):
        line = json.dumps(GOOD)[:-1] + ', "seq": 2}'
        with self.assertRaises(RecordError):
            parse_record(line)

    def test_uint32_wrap(self):
        rows = [dict(GOOD, seq=0xFFFFFFFF, uptime_ms=0xFFFFFFFF-999),
                dict(GOOD, seq=0, uptime_ms=2000)]
        for row in rows:
            parse_record(json.dumps(row))
        self.assertTrue(summarize(rows)["intervals_ok"])
        self.assertTrue(summarize(rows)["sequence_ok"])

    def test_sequence_gap_and_reboot(self):
        rows = [dict(GOOD, seq=9, uptime_ms=9000),
                dict(GOOD, seq=11, uptime_ms=12000)]
        self.assertFalse(summarize(rows)["sequence_ok"])
        rows[1] = dict(GOOD, seq=1, uptime_ms=100)
        self.assertFalse(summarize(rows)["intervals_ok"])
        self.assertFalse(summarize(rows)["sequence_ok"])

    def test_empty_summary(self):
        self.assertIsNone(summarize([])["intervals_ok"])
        self.assertIsNone(summarize([])["sequence_ok"])

    def test_cli_record_count(self):
        receiver = Path(__file__).resolve().parents[1] / "scripts/uart_receiver.py"
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "rows.jsonl"
            for content, count, expected in (("boot banner\n", 1, 1),
                                             (json.dumps(GOOD)+"\n", 2, 1),
                                             (json.dumps(GOOD)+"\n", 1, 0)):
                fixture.write_text(content, encoding="utf-8")
                result = subprocess.run([sys.executable, str(receiver), "--input",
                                         str(fixture), "--count", str(count)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_cli_negative_count(self):
        receiver = Path(__file__).resolve().parents[1] / "scripts/uart_receiver.py"
        result = subprocess.run([sys.executable, str(receiver), "--input", "unused",
                                 "--count", "-1"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
