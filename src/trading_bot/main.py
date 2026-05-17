"""Main entrypoint for Jesse Trading Bot.

Run with: python -m src.trading_bot.main --paper
For demo, it uses sample data if no exchange connection.
"""

import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trading_bot.config import settings
from trading_bot.strategies.sma_crossover import SMACrossoverStrategy


def generate_sample_ohlcv(n: int = 100) -> pd.DataFrame:
    """Generate synthetic price data for demo/paper testing."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=n, freq='h')
    price = 60000 + np.cumsum(np.random.randn(n) * 50)
    df = pd.DataFrame({
        'timestamp': dates,
        'open': price + np.random.randn(n) * 10,
        'high': price + np.abs(np.random.randn(n)) * 20,
        'low': price - np.abs(np.random.randn(n)) * 20,
        'close': price,
        'volume': np.random.uniform(100, 1000, n)
    })
    df.set_index('timestamp', inplace=True)
    return df


def run_paper_demo(strategy_name: str = "sma"):
    print("=== Jesse Trading Bot - Paper Trading Demo ===")
    print(f"Settings: symbol={settings.symbol}, paper={settings.paper_trading}")
    
    # Load or generate data
    ohlcv = generate_sample_ohlcv(200)
    print(f"Generated {len(ohlcv)} bars of sample data.")
    
    if strategy_name == "sma":
        strategy = SMACrossoverStrategy(config={
            'sma_fast': settings.sma_fast,
            'sma_slow': settings.sma_slow
        })
    else:
        print("Strategy not implemented yet, using SMA.")
        strategy = SMACrossoverStrategy()
    
    signal = strategy.generate_signal(ohlcv)
    print(f"\nLatest signal from {strategy.name()}: {signal.upper()}")
    
    # Simple risk example
    print(f"\nRisk params: max pos {settings.max_position_pct*100}%, daily loss limit {settings.daily_loss_limit_pct*100}%")
    
    print("\n[DEMO] In full version: fetch real data via CCXT, check risk, execute paper trade, log position.")
    print("[NEXT] I can expand this to full loop, CCXT integration, persistent state, etc.")
    print("\nRun this script or ask me to enhance!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jesse Trading Bot")
    parser.add_argument("--paper", action="store_true", help="Run in paper/demo mode")
    parser.add_argument("--strategy", default="sma", help="Strategy to use")
    args = parser.parse_args()
    
    if args.paper or settings.paper_trading:
        run_paper_demo(args.strategy)
    else:
        print("Live mode not fully implemented yet. Use --paper or ask for live executor.")
