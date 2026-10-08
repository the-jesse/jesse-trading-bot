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

Built upon review of existing repos (crypto-monitor for Solana monitoring/signals, polymarket-bot for prediction markets, solomon-trader) which demonstrate solid foundational work in market data and interaction.

### Key Features (Current & Planned)
- **Modular Architecture**: Data, Strategy, Risk, Execution layers (execution is paper-only).
- **Paper Trading**: Demo loop on synthetic bars. Virtual fills are not implemented yet.
- **Risk Management**: Position sizing, pre-trade gates, daily loss limits.
- **Pluggable Strategies**: Subclass `BaseStrategy`; SMA crossover is the demo strategy.
- **CCXT Powered**: provider module exists; demo path does not call the network.
- **Config Driven**: `.env` for symbols and risk percents. Never commit secrets.
- **Logging & Audit**: planned (structlog).
- **Backtesting Foundation**: not started.

## Quick Start (Paper Demo)

```bash
git clone https://github.com/the-jesse/jesse-trading-bot.git
cd jesse-trading-bot

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Leave API keys blank. PAPER_TRADING and DRY_RUN stay true.

PYTHONPATH=src python -m trading_bot.main --paper
python -m unittest tests/test_paper_gate.py
```

`--live` exits 2. `resolve_mode()` never selects a live executor.

See `docs/DEVELOPMENT_PLAN.md` for the phased roadmap. That plan is ahead of the code; trust this status section if they disagree.

## Current Status (2026-10-08)

**In tree on main (2026-05-17) plus this branch:**
- Package layout, SMA demo, CCXT provider module, `RiskManager` / `PositionSizer`.
- Paper-only gate in `src/trading_bot/safety.py`. Live money is refused even if `PAPER_TRADING=false` and an allow-live flag is set.
- `check_trade` rejects non-positive size, price, or equity before notional math.
- Stdlib tests in `tests/test_paper_gate.py` (no exchange, no keys).

**Not done (do not treat README marketing as shipped):**
- Paper executor (virtual positions, fees, slippage).
- Continuous loop and persistent state.
- Backtester, structlog, pyproject editable install.
- Any live order path. Do not add one in this repo without a separate reviewed design.

## Safety
- Paper trading correctness is the priority.
- Do not commit `.env`, API keys, or exchange secrets.
- Do not point this bot at live funds. solomon-trader Phase 7 stays gated separately.

## Development Approach
- Incremental: one focused module per change, with tests.
- Safety first: sizing and the risk gate have known-case tests.
- Never live without an explicit human review, and not from this agent loop.

See [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).
