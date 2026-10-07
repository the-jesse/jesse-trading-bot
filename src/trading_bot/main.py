"""Main entrypoint for Jesse Trading Bot.

Paper only. Live exchange orders are not implemented and are refused.
Run with: PYTHONPATH=src python -m trading_bot.main --paper
"""

import argparse
import sys
from datetime import datetime

import numpy as np
import pandas as pd

from trading_bot.config import settings
from trading_bot.execution.paper import PaperExecutor
from trading_bot.risk.risk_manager import RiskManager
from trading_bot.safety import LiveTradingDisabled, assert_paper_only
from trading_bot.strategies.sma_crossover import SMACrossoverStrategy


def generate_sample_ohlcv(n: int = 100) -> pd.DataFrame:
    """Generate synthetic price data for demo/paper testing."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=n, freq="h")
    price = 60000 + np.cumsum(np.random.randn(n) * 50)
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "open": price + np.random.randn(n) * 10,
            "high": price + np.abs(np.random.randn(n)) * 20,
            "low": price - np.abs(np.random.randn(n)) * 20,
            "close": price,
            "volume": np.random.uniform(100, 1000, n),
        }
    )
    df.set_index("timestamp", inplace=True)
    return df


def run_paper_demo(strategy_name: str = "sma") -> int:
    print("=== Jesse Trading Bot - Paper Trading Demo ===")
    print(f"Settings: symbol={settings.symbol}, paper={settings.paper_trading}")

    ohlcv = generate_sample_ohlcv(200)
    print(f"Generated {len(ohlcv)} bars of sample data.")

    if strategy_name == "sma":
        strategy = SMACrossoverStrategy(
            config={"sma_fast": settings.sma_fast, "sma_slow": settings.sma_slow}
        )
    else:
        print("Strategy not implemented yet, using SMA.")
        strategy = SMACrossoverStrategy()

    signal = strategy.generate_signal(ohlcv)
    print(f"\nLatest signal from {strategy.name()}: {signal.upper()}")

    risk = RiskManager(
        max_position_pct=settings.max_position_pct,
        risk_per_trade_pct=settings.risk_per_trade_pct,
        daily_loss_limit_pct=settings.daily_loss_limit_pct,
    )
    executor = PaperExecutor(starting_cash=10_000.0)
    last_price = float(ohlcv["close"].iloc[-1])
    print(
        f"\nRisk params: max pos {settings.max_position_pct * 100}%, "
        f"daily loss limit {settings.daily_loss_limit_pct * 100}%"
    )

    if signal == "hold":
        print("[PAPER] Hold. No virtual fill.")
        return 0

    size = risk.calculate_size(equity=executor.cash, entry_price=last_price)
    report = risk.check_trade(
        symbol=settings.symbol,
        side=signal,
        size=size,
        entry_price=last_price,
        equity=executor.cash,
        current_exposure_notional=executor.position(settings.symbol) * last_price,
    )
    print(f"[PAPER] Risk: approved={report.approved} reason={report.reason}")
    if not report.approved or size <= 0:
        print("[PAPER] Order blocked. No exchange call.")
        return 0
    if signal == "sell" and executor.position(settings.symbol) <= 0:
        print("[PAPER] Sell signal ignored: no virtual position to reduce.")
        return 0

    fill = executor.fill(settings.symbol, signal, size, last_price)
    print(
        f"[PAPER] Fill {fill.side} {fill.size} @ {fill.fill_price:.2f} "
        f"fee={fill.fee:.4f} cash={executor.cash:.2f}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jesse Trading Bot (paper only)")
    parser.add_argument("--paper", action="store_true", help="Run in paper/demo mode")
    parser.add_argument("--strategy", default="sma", help="Strategy to use")
    args = parser.parse_args(argv)

    try:
        assert_paper_only(
            paper_flag=args.paper,
            settings_paper=bool(settings.paper_trading),
        )
    except LiveTradingDisabled as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return run_paper_demo(args.strategy)


if __name__ == "__main__":
    raise SystemExit(main())
