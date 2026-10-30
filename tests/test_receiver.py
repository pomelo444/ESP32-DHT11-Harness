import json
import sys
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


if __name__ == "__main__":
    unittest.main()
