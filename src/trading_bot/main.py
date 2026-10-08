"""Main entrypoint for Jesse Trading Bot.

Run with: PYTHONPATH=src python -m trading_bot.main --paper
Demo uses synthetic data. Live money execution is refused.
"""

import argparse
import sys
from datetime import datetime

import numpy as np
import pandas as pd

from trading_bot.config import settings
from trading_bot.safety import PaperOnlyError, assert_paper_execution, resolve_mode
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


def run_paper_demo(strategy_name: str = "sma") -> None:
    mode = resolve_mode(
        paper_trading=settings.paper_trading,
        dry_run=settings.dry_run,
        allow_live=False,
    )
    assert_paper_execution(mode)
    print("=== Jesse Trading Bot - Paper Trading Demo ===")
    print(f"Settings: symbol={settings.symbol}, mode={mode}, paper={settings.paper_trading}")

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
    print(
        f"\nRisk params: max pos {settings.max_position_pct * 100}%, "
        f"daily loss limit {settings.daily_loss_limit_pct * 100}%"
    )
    print("\n[DEMO] Paper only. No live orders are placed from this entrypoint.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jesse Trading Bot")
    parser.add_argument("--paper", action="store_true", help="Run in paper/demo mode")
    parser.add_argument("--live", action="store_true", help="Refused. Live money is disabled.")
    parser.add_argument("--strategy", default="sma", help="Strategy to use")
    args = parser.parse_args(argv)

    if args.live:
        print(
            "Refusing --live. Paper trading only until a separate reviewed executor exists.",
            file=sys.stderr,
        )
        return 2

    try:
        mode = resolve_mode(
            paper_trading=bool(args.paper or settings.paper_trading),
            dry_run=settings.dry_run,
            allow_live=False,
        )
        assert_paper_execution(mode)
    except PaperOnlyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    run_paper_demo(args.strategy)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
