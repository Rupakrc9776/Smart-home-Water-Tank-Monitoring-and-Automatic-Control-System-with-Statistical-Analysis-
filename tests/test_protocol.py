import unittest

from dashboard import parse_reading


class ParseReadingTests(unittest.TestCase):
    def test_accepts_three_field_payload(self):
        self.assertEqual(parse_reading("15,25,ON"), (15.0, 25.0, "ON"))

    def test_accepts_legacy_four_field_payload(self):
        self.assertEqual(parse_reading("millis,15,25,OFF"), (15.0, 25.0, "OFF"))

    def test_clamps_numeric_ranges(self):
        self.assertEqual(parse_reading("-2,125,ON"), (0.0, 100.0, "ON"))

    def test_rejects_invalid_payload(self):
        self.assertIsNone(parse_reading("15,25,UNKNOWN"))
        self.assertIsNone(parse_reading("15,25"))
        self.assertIsNone(parse_reading("distance,level,ON"))


if __name__ == "__main__":
    unittest.main()
