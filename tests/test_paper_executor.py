"""Stdlib tests for the paper executor. No network, no exchange keys."""

import unittest

from trading_bot.execution.paper import (
    InsufficientCash,
    InsufficientPosition,
    PaperExecutor,
)
from trading_bot.safety import LiveTradingDisabled, assert_paper_only


class PaperExecutorTests(unittest.TestCase):
    def test_buy_applies_fee_and_slippage(self):
        ex = PaperExecutor(starting_cash=10_000, fee_bps=10, slippage_bps=5)
        fill = ex.fill("BTC/USDT", "buy", size=0.1, mid_price=60_000)
        self.assertTrue(fill.paper)
        self.assertAlmostEqual(fill.fill_price, 60_030.0)
        expected_fee = 60_030.0 * 0.1 * 0.001
        self.assertAlmostEqual(fill.fee, expected_fee)
        self.assertAlmostEqual(ex.cash, 10_000 - (60_030.0 * 0.1) - expected_fee)
        self.assertAlmostEqual(ex.position("BTC/USDT"), 0.1)

    def test_sell_rejects_short_and_credits_cash(self):
        ex = PaperExecutor(starting_cash=10_000, fee_bps=0, slippage_bps=0)
        ex.fill("BTC/USDT", "buy", size=0.2, mid_price=50_000)
        cash_after_buy = ex.cash
        with self.assertRaises(InsufficientPosition):
            ex.fill("BTC/USDT", "sell", size=0.3, mid_price=50_000)
        fill = ex.fill("BTC/USDT", "sell", size=0.2, mid_price=51_000)
        self.assertEqual(fill.side, "sell")
        self.assertAlmostEqual(ex.position("BTC/USDT"), 0.0)
        self.assertAlmostEqual(ex.cash, cash_after_buy + 51_000 * 0.2)

    def test_buy_rejects_when_cash_short(self):
        ex = PaperExecutor(starting_cash=100, fee_bps=0, slippage_bps=0)
        with self.assertRaises(InsufficientCash):
            ex.fill("BTC/USDT", "buy", size=1, mid_price=101)
        self.assertEqual(ex.fills, [])
        self.assertEqual(ex.cash, 100)


class SafetyGateTests(unittest.TestCase):
    def test_requires_both_flags(self):
        assert_paper_only(paper_flag=True, settings_paper=True)
        with self.assertRaises(LiveTradingDisabled):
            assert_paper_only(paper_flag=False, settings_paper=True)
        with self.assertRaises(LiveTradingDisabled):
            assert_paper_only(paper_flag=True, settings_paper=False)


if __name__ == "__main__":
    unittest.main()
