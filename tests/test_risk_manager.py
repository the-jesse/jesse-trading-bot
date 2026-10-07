"""Stdlib tests for pre-trade risk gates. No market data."""

import unittest

from trading_bot.risk.risk_manager import PositionSizer, RiskManager


class PositionSizerTests(unittest.TestCase):
    def test_fixed_fractional_caps_by_notional(self):
        size = PositionSizer.fixed_fractional(
            equity=10_000,
            risk_per_trade_pct=0.01,
            entry_price=100,
            stop_price=99,
            max_position_pct=0.02,
        )
        # risk $100 / $1 stop = 100 units, notional cap is $200 -> 2 units
        self.assertAlmostEqual(size, 2.0)

    def test_zero_stop_distance_is_zero_size(self):
        self.assertEqual(
            PositionSizer.fixed_fractional(10_000, 0.01, 100, 100),
            0.0,
        )


class RiskManagerTests(unittest.TestCase):
    def test_invalid_params_fail_before_notional(self):
        rm = RiskManager(max_position_pct=0.02)
        report = rm.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=0,
            entry_price=100,
            equity=10_000,
        )
        self.assertFalse(report.approved)
        self.assertIn("invalid_order_params", report.checks_failed)
        self.assertNotIn("position_size_ok", report.checks_passed)

    def test_daily_loss_circuit_breaker(self):
        rm = RiskManager(daily_loss_limit_pct=0.05)
        rm.record_fill(-600, realized=True)
        report = rm.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=0.01,
            entry_price=100,
            equity=10_000,
        )
        self.assertFalse(report.approved)
        self.assertIn("daily_loss_limit", report.checks_failed)

    def test_approves_small_order(self):
        rm = RiskManager(max_position_pct=0.02, hard_max_exposure_pct=0.10)
        report = rm.check_trade(
            symbol="BTC/USDT",
            side="buy",
            size=1,
            entry_price=100,
            equity=10_000,
        )
        self.assertTrue(report.approved)
        self.assertEqual(report.checks_failed, [])


if __name__ == "__main__":
    unittest.main()
