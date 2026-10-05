# Jesse Trading Bot

**Professional, Modular Cryptocurrency Trading Bot**

> ⚠️ **IMPORTANT DISCLAIMER** ⚠️
>
> This software is provided **for educational, research, and demonstration purposes only**.
>
> - Cryptocurrency and prediction market trading involves **substantial risk of loss** and is not suitable for everyone.
> - Past performance does not guarantee future results.
> - You can lose **all your capital**.
> - This is **NOT financial advice**.
> - The authors and contributors are **not responsible** for any financial losses, damages, or issues arising from the use of this software.
> - **Always start with paper trading or testnets**. Test thoroughly before any live use.
> - Understand every line of code before using with real funds.
> - Comply with all applicable laws, regulations, and tax requirements in your jurisdiction (Maine, US).
> - Trading bots may be subject to specific regulations; consult professionals.
> - Use at your own risk.

## Overview

A senior-engineer level, production-minded crypto trading bot built in Python. Designed with clean architecture, strong risk management, pluggable strategies, paper trading simulation, and extensibility.

Built upon review of existing repos (crypto-monitor, polymarket-bot, solomon-trader). This repo is the Python framework. It does **not** place live orders.

### Key Features (Current & Planned)
- **Modular Architecture**: Data, Strategy, Risk, Execution layers (execution still paper-only).
- **Paper Trading**: Demo path uses synthetic OHLCV. A paper executor with fees/slippage is not wired yet.
- **Risk Management**: Position sizing, pre-trade gates, daily loss limits, exposure cap (`risk/risk_manager.py`).
- **Pluggable Strategies**: Subclass `BaseStrategy`; SMA crossover is the only strategy.
- **CCXT provider**: `data/ccxt_provider.py` exists but the demo loop does not call it.
- **Config Driven**: `.env` via pydantic-settings. Defaults keep `paper_trading=true`.
- **Logging & Audit**: structlog is a dependency; demo still prints.
- **Backtesting Foundation**: not implemented.
- Best practices: type hints, small testable commits. No live credentials in git.

## Quick Start (Paper Demo)

```bash
git clone https://github.com/the-jesse/jesse-trading-bot.git
cd jesse-trading-bot

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Leave API keys blank. paper_trading must stay true.

PYTHONPATH=src python -m trading_bot.main --paper
PYTHONPATH=src python -m unittest tests.test_risk_and_safety
```

**Note**: The `src/` layout requires `PYTHONPATH=src` until `pyproject.toml` lands.

See `docs/DEVELOPMENT_PLAN.md` for the phased roadmap. Treat that plan as intent, not current status.

## Current Status (2026-10-05)

**In tree**:
- Package layout under `src/trading_bot/` (config, SMA strategy, CCXT provider, risk manager).
- Paper-only gate in `safety.py`. Flipping `paper_trading` off exits; there is no live override.
- Stdlib tests for sizing, circuit breaker, exposure cap, and the paper gate.

**Not done**:
- Paper executor (virtual fills, fees, slippage, positions).
- Demo loop still uses synthetic data, not CCXT.
- No CI workflow yet.
- No live executor. Do not add one in this repo without a separate reviewed design.

**Run**:
```
PYTHONPATH=src python -m trading_bot.main --paper
PYTHONPATH=src python -m unittest tests.test_risk_and_safety
```

## Development Approach
- **Incremental**: one focused module per commit + test.
- **Safety first**: sizing, risk gate, and the paper lock have tests.
- **Never live without a separate review**: this build refuses live mode.

See [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).

**Trade responsibly. Paper only.**
