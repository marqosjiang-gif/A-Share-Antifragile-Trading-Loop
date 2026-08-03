import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from quant_loop import build_report, load_watchlist


class QuantLoopTests(unittest.TestCase):
    def test_local_watchlist_rejects_position_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "watchlist.local.json"
            path.write_text(json.dumps({"universe": [{
                "code": "000001", "exchange": "SZ", "name": "Example", "shares": 100
            }]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_watchlist(path)

    def test_report_records_time_boundaries(self):
        report = build_report(date(2026, 8, 2), [{
            "code": "000001", "exchange": "SZ", "name": "Example"
        }], Path("watchlist.local.json"))
        self.assertIn("evidence_cutoff:", report)
        self.assertIn("validation_window: 2026-08-03 open", report)
        self.assertIn("decision_status: research_only", report)


if __name__ == "__main__":
    unittest.main()
