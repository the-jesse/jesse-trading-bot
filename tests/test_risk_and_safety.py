"""Stdlib tests for position sizing, the risk gate, and the paper-only lock.

Run from repo root:
    PYTHONPATH=src python -m unittest tests.test_risk_and_safety
"""

import unittest

from trading_bot.risk.risk_manager import PositionSizer, RiskManager
from trading_bot.safety import LiveTradingDisabled, ensure_paper_mode


class PositionSizerTests(unittest.TestCase):
    def test_fixed_fractional_caps_by_notional(self):
        size = PositionSizer.fixed_fractional(
            equity=10_000,
            risk_per_trade_pct=0.01,
            entry_price=100,
            stop_price=90,
            max_position_pct=0.02,
        )
        # Raw risk size is 10 units; 2% notional cap is 2 units.
        self.assertEqual(size, 2.0)

    def test_zero_stop_distance_returns_zero(self):
        size = PositionSizer.fixed_fractional(
            equity=10_000,
            risk_per_trade_pct=0.01,
            entry_price=100,
            stop_price=100,
        )
        self.assertEqual(size, 0.0)

    def test_non_positive_entry_returns_zero(self):
        size = PositionSizer.fixed_fractional(
            equity=10_000,
            risk_per_trade_pct=0.01,
            entry_price=0,
            stop_price=1,
        )
        self.assertEqual(size, 0.0)


class RiskManagerTests(unittest.TestCase):
    def test_rejects_invalid_params_before_notional_math(self):
        gate = RiskManager()
        report = gate.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=-1,
            entry_price=100,
            equity=10_000,
        )
        self.assertFalse(report.approved)
        self.assertIn("invalid_order_params", report.checks_failed)

    def test_rejects_non_positive_equity(self):
        gate = RiskManager()
        report = gate.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=0.01,
            entry_price=100,
            equity=0,
        )
        self.assertFalse(report.approved)
        self.assertIn("invalid_equity", report.checks_failed)

    def test_daily_loss_circuit_breaker(self):
        gate = RiskManager(daily_loss_limit_pct=0.05)
        gate.record_fill(-600, realized=True)
        report = gate.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=0.01,
            entry_price=100,
            equity=10_000,
        )
        self.assertFalse(report.approved)
        self.assertIn("daily_loss_limit", report.checks_failed)

    def test_approves_small_paper_order(self):
        gate = RiskManager(max_position_pct=0.02, hard_max_exposure_pct=0.10)
        report = gate.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=1,
            entry_price=100,
            equity=10_000,
            current_exposure_notional=0,
        )
        self.assertTrue(report.approved)
        self.assertEqual(report.checks_failed, [])

    def test_blocks_exposure_cap(self):
        gate = RiskManager(max_position_pct=0.05, hard_max_exposure_pct=0.10)
        report = gate.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=4,
            entry_price=100,
            equity=10_000,
            current_exposure_notional=700,
        )
        self.assertFalse(report.approved)
        self.assertIn("total_exposure_cap", report.checks_failed)


class PaperGateTests(unittest.TestCase):
    def test_paper_mode_allowed(self):
        ensure_paper_mode(True)

    def test_live_flag_rejected(self):
        with self.assertRaises(LiveTradingDisabled):
            ensure_paper_mode(False)

    def test_override_rejected(self):
        with self.assertRaises(LiveTradingDisabled):
            ensure_paper_mode(True, explicit_live_override=True)


if __name__ == "__main__":
    unittest.main()
