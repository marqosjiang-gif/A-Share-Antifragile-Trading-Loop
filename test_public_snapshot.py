import unittest

from run_weekly_report import eastmoney_secid, parse_watch_tickers


class PublicSnapshotTests(unittest.TestCase):
    def test_empty_watchlist_is_valid(self):
        self.assertEqual(parse_watch_tickers(""), [])

    def test_normalizes_and_deduplicates_symbols(self):
        self.assertEqual(
            parse_watch_tickers("600000.SH, 000001.SZ, 600000.SS"),
            ["600000.SS", "000001.SZ"],
        )

    def test_rejects_invalid_symbols(self):
        with self.assertRaises(ValueError):
            parse_watch_tickers("AAPL")

    def test_converts_market_suffix(self):
        self.assertEqual(eastmoney_secid("600000.SS"), "1.600000")
        self.assertEqual(eastmoney_secid("000001.SZ"), "0.000001")


if __name__ == "__main__":
    unittest.main()
