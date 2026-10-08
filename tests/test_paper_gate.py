"""Stdlib tests for the paper gate and risk checks. No network, no keys."""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from trading_bot.risk.risk_manager import PositionSizer, RiskManager  # noqa: E402
from trading_bot.safety import PaperOnlyError, assert_paper_execution, resolve_mode  # noqa: E402


class PaperGateTests(unittest.TestCase):
    def test_defaults_are_paper(self):
        self.assertEqual(resolve_mode(), "paper")

    def test_allow_live_alone_does_not_unlock(self):
        self.assertEqual(
            resolve_mode(paper_trading=True, dry_run=True, allow_live=True),
            "paper",
        )

    def test_both_flags_off_is_blocked_even_if_allow_live(self):
        mode = resolve_mode(paper_trading=False, dry_run=False, allow_live=True)
        self.assertEqual(mode, "blocked-live")
        with self.assertRaises(PaperOnlyError):
            assert_paper_execution(mode)

    def test_dry_run_keeps_paper_when_paper_flag_off(self):
        self.assertEqual(
            resolve_mode(paper_trading=False, dry_run=True, allow_live=True),
            "paper",
        )


class RiskManagerTests(unittest.TestCase):
    def test_fixed_fractional_caps_by_notional(self):
        size = PositionSizer.fixed_fractional(
            equity=10_000,
            risk_per_trade_pct=0.01,
            entry_price=100,
            stop_price=99,
            max_position_pct=0.02,
        )
        self.assertAlmostEqual(size, 2.0)

    def test_zero_stop_distance_is_zero_size(self):
        self.assertEqual(
            PositionSizer.fixed_fractional(10_000, 0.01, 100, 100),
            0.0,
        )

    def test_invalid_params_rejected_before_notional(self):
        report = RiskManager().check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=-1,
            entry_price=-50,
            equity=10_000,
        )
        self.assertFalse(report.approved)
        self.assertIn("invalid_order_params", report.checks_failed)
        self.assertNotIn("position_size_ok", report.checks_passed)

    def test_daily_loss_breaker(self):
        rm = RiskManager(daily_loss_limit_pct=0.05)
        rm.record_fill(-600)
        report = rm.check_trade("BTC/USDT", "buy", 0.01, 100, 10_000)
        self.assertFalse(report.approved)
        self.assertIn("daily_loss_limit", report.checks_failed)

    def test_approves_small_paper_order(self):
        report = RiskManager().check_trade(
            "BTC/USDT", "buy", 0.01, 100, 10_000, current_exposure_notional=0
        )
        self.assertTrue(report.approved)
        self.assertEqual(
            report.checks_passed,
            ["params_sane", "daily_loss_ok", "position_size_ok", "exposure_ok"],
        )


if __name__ == "__main__":
    unittest.main()
