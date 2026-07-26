import unittest
from datetime import datetime, timedelta, timezone

from antifragile.cftc import parse_disaggregated_gold
from antifragile.decision import (
    BollEvidence,
    ResearchEvidence,
    boll_position_wording,
    decide,
)
from antifragile.flows import aggregate_flows, classify_stock_flow
from antifragile.freshness import evaluate_scan_coverage, is_fresh_event
from antifragile.market_context import _weekly_metric, parse_fred_series
from unittest.mock import patch

from run_weekly_report import (
    eastmoney_secid,
    fetch_us_snapshot,
    parse_watch_tickers,
)


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

    def test_us_snapshot_keeps_requested_symbol_key(self):
        fields = ["0"] * 33
        fields[1] = "SPY ETF"
        fields[3] = "600.12"
        fields[30] = "2026-07-17 16:00:01"
        fields[32] = "-1.25"
        payload = f'v_usSPY="{"~".join(fields)}";'
        with patch("run_weekly_report.http_get", return_value=payload):
            result = fetch_us_snapshot(("usSPY",))
        self.assertEqual(result["usSPY"][:3], ("SPY ETF", "600.12", -1.25))
        self.assertEqual(result["usSPY"][3], datetime(2026, 7, 17, 16, 0, 1))

    def test_flow_windows_keep_exact_dates(self):
        rows = [
            {"date": f"2026-07-{day:02d}", "net_amount": day}
            for day in range(1, 21)
        ]
        result = aggregate_flows(rows)
        self.assertEqual(result[5].start.isoformat(), "2026-07-16")
        self.assertEqual(result[5].end.isoformat(), "2026-07-20")
        self.assertEqual(result[5].net_amount, 90)
        self.assertEqual(result[20].net_amount, 210)

    def test_flow_windows_reject_duplicate_dates(self):
        with self.assertRaises(ValueError):
            aggregate_flows(
                [
                    {"date": "2026-07-17", "net_amount": 1},
                    {"date": "2026-07-17", "net_amount": 2},
                ]
            )

    def test_flow_classification_uses_liquidity_tiers(self):
        self.assertEqual(
            classify_stock_flow(200_000_000, 20_000_000_000),
            "persistent_inflow",
        )
        self.assertEqual(
            classify_stock_flow(200_000_000, 200_000_000_000),
            "range_bound",
        )

    def test_event_freshness_gate_is_168_hours(self):
        now = datetime(2026, 7, 19, tzinfo=timezone.utc)
        self.assertTrue(is_fresh_event(now - timedelta(hours=168), now))
        self.assertFalse(is_fresh_event(now - timedelta(hours=169), now))
        self.assertFalse(is_fresh_event(now + timedelta(minutes=1), now))

    def test_no_event_requires_complete_scan(self):
        coverage = evaluate_scan_coverage(
            ("trade", "strait", "europe"),
            ("trade", "strait"),
        )
        self.assertFalse(coverage.is_complete)
        self.assertEqual(coverage.missing, ("europe",))

    def test_price_volume_gate_blocks_directional_action(self):
        result = decide(
            ResearchEvidence(
                price_verified=True,
                volume_verified=False,
                boll=BollEvidence("buy", 8, 0.75, 0.4, True),
            )
        )
        self.assertEqual(result.label, "observe")
        self.assertEqual(result.confidence, "low")

    def test_actionable_boll_has_priority(self):
        result = decide(
            ResearchEvidence(
                price_verified=True,
                volume_verified=True,
                boll=BollEvidence("sell", 6, 0.67, 0.2, True),
                flow_5d=2,
                flow_20d=9,
                flow_verified=True,
            )
        )
        self.assertEqual(result.label, "reduce")

    def test_low_sample_boll_is_not_a_hard_trade(self):
        result = decide(
            ResearchEvidence(
                price_verified=True,
                volume_verified=True,
                boll=BollEvidence("buy", 2, 1.0, 0.9, True),
                flow_verified=False,
            )
        )
        self.assertEqual(result.label, "observe")

    def test_conflicting_verified_risk_constrains_boll_buy(self):
        result = decide(
            ResearchEvidence(
                price_verified=True,
                volume_verified=True,
                boll=BollEvidence("buy", 5, 0.8, 0.3, True),
                flow_5d=-1,
                flow_20d=-4,
                flow_verified=True,
            )
        )
        self.assertEqual(result.label, "observe")

    def test_survival_risk_blocks_new_exposure(self):
        result = decide(
            ResearchEvidence(
                price_verified=True,
                volume_verified=True,
                boll=BollEvidence("buy", 9, 0.8, 0.4, True),
                survival_risk=True,
            )
        )
        self.assertEqual(result.label, "observe")

    def test_boll_wording_matches_band_position(self):
        self.assertEqual(
            boll_position_wording(101), "above_upper_band_sell_region"
        )
        self.assertEqual(
            boll_position_wording(-1), "below_lower_band_buy_region"
        )
        self.assertEqual(boll_position_wording(5), "near_lower_band")

    def test_fred_weekly_window_uses_latest_five_valid_values(self):
        points = parse_fred_series(
            "observation_date,DCOILBRENTEU\n"
            "2026-07-13,70\n"
            "2026-07-14,.\n"
            "2026-07-15,72\n"
            "2026-07-16,73\n"
            "2026-07-17,74\n"
            "2026-07-20,75\n",
            "DCOILBRENTEU",
        )
        metric = _weekly_metric("Brent", points, "FRED")
        self.assertEqual(metric.start.isoformat(), "2026-07-13")
        self.assertEqual(metric.end.isoformat(), "2026-07-20")
        self.assertAlmostEqual(metric.change_pct, (75 / 70 - 1) * 100)

    def test_parses_cftc_gold_and_prior_week(self):
        row = ["0"] * 64
        row[2] = "2026-07-14"
        row[3] = "088691"
        row[13] = "120000"
        row[14] = "40000"
        row[62] = "5000"
        row[63] = "-2000"
        item = parse_disaggregated_gold(",".join(row))
        self.assertEqual(item.managed_money_net, 80000)
        self.assertEqual(item.weekly_net_change, 7000)
        self.assertEqual(item.prior_week_net, 73000)


if __name__ == "__main__":
    unittest.main()
