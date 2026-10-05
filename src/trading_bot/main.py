"""Main entrypoint for Jesse Trading Bot.

Run with: PYTHONPATH=src python -m trading_bot.main --paper
Demo uses synthetic data. Live order routing is disabled.
"""

import argparse
import pandas as pd
import numpy as np
from datetime import datetime

from trading_bot.config import settings
from trading_bot.safety import ensure_paper_mode
from trading_bot.strategies.sma_crossover import SMACrossoverStrategy
from trading_bot.risk.risk_manager import RiskManager


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


def run_paper_demo(strategy_name: str = "sma"):
    ensure_paper_mode(settings.paper_trading)
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

    gate = RiskManager(
        max_position_pct=settings.max_position_pct,
        risk_per_trade_pct=settings.risk_per_trade_pct,
        daily_loss_limit_pct=settings.daily_loss_limit_pct,
    )
    last_close = float(ohlcv["close"].iloc[-1])
    size = gate.calculate_size(equity=10_000, entry_price=last_close)
    report = gate.check_trade(
        symbol=settings.symbol,
        side="buy" if signal == "buy" else "sell",
        size=max(size, 0.00000001),
        entry_price=last_close,
        equity=10_000,
    )
    print(
        f"\nRisk params: max pos {settings.max_position_pct * 100}%, "
        f"daily loss limit {settings.daily_loss_limit_pct * 100}%"
    )
    print(
        f"Paper risk check: approved={report.approved} size={size} reason={report.reason}"
    )
    print("\n[DEMO] No exchange orders are sent. CCXT provider exists but is not wired here.")
    print("[NEXT] Paper executor + persistent state. Do not enable live keys.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jesse Trading Bot")
    parser.add_argument("--paper", action="store_true", help="Run in paper/demo mode")
    parser.add_argument("--strategy", default="sma", help="Strategy to use")
    args = parser.parse_args()

    if not (args.paper or settings.paper_trading):
        print("Live mode is disabled. Use --paper. This build will not place orders.")
        raise SystemExit(2)
    run_paper_demo(args.strategy)
