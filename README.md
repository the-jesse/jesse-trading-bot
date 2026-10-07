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
> - **This repo refuses live order placement.** `--paper` and `PAPER_TRADING=true` are both required. There is no live executor.

## Overview

A senior-engineer level, production-minded crypto trading bot built in Python. Designed with clean architecture, strong risk management, pluggable strategies, paper trading simulation, and extensibility.

Built upon review of your existing repos (crypto-monitor for Solana monitoring/signals, polymarket-bot for prediction markets, solomon-trader) which demonstrate solid foundational work in market data and interaction. Great starting points — this new bot provides a robust framework you can extend or integrate with.

### Key Features (Current & Planned)
- **Modular Architecture**: Data, Strategy, Risk, Execution layers (paper execution landed).
- **Paper Trading**: Virtual cash, fees, and slippage via `PaperExecutor`. No exchange orders.
- **Risk Management**: Position sizing, pre-trade gates, daily loss limits, circuit breakers.
- **Pluggable Strategies**: Subclass `BaseStrategy` easily; registry for multi-strat configs.
- **CCXT Powered**: Provider module exists; demo still uses synthetic bars.
- **Config Driven**: .env + future YAML for symbols/strategies.
- **Logging & Audit**: structlog planned; paper fills print a one-line audit for now.
- **Backtesting Foundation**: Not wired yet.
- Best practices: type hints, small testable commits. Risk and paper fills have stdlib tests.

## Quick Start (Paper Demo)

```bash
git clone https://github.com/the-jesse/jesse-trading-bot.git
cd jesse-trading-bot

# Recommended: use venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — leave API keys blank. PAPER_TRADING must stay true.

# Run the paper demo (synthetic data + SMA signal + virtual fill)
PYTHONPATH=src python -m trading_bot.main --paper

# Risk + paper executor tests (no pandas, no network)
PYTHONPATH=src python -m unittest tests.test_paper_executor tests.test_risk_manager
```

Omitting `--paper`, or setting `PAPER_TRADING=false`, exits 2. That is intentional.

**Note**: The `src/` layout requires `PYTHONPATH=src` until we add `pyproject.toml` + editable install.

See `docs/DEVELOPMENT_PLAN.md` for the full phased roadmap, architecture, and safety rules.

## Current Status (2026-10-07)

**Completed**:
- Phase 0 docs and package layout.
- Risk manager with fixed-fractional sizing and daily-loss gate.
- Paper executor (fees, slippage, cash, no shorts) plus live-mode refusal.
- Stdlib tests and a no-network GitHub workflow.

**Not done / do not do in an agent run**:
- Live exchange orders, API key use, or real capital.
- Continuous loop and persisted paper ledger.
- Wiring CCXT bars into the demo (still synthetic).

**Strong risk disclaimers remain in place. Paper trading correctness is the #1 priority.**

## Your Existing Repos Review
I reviewed your GitHub:
- **crypto-monitor**: Node.js/TypeScript Solana pool monitor with signals, docs, roadmap. Excellent for on-chain alpha.
- **polymarket-bot**: JS bot for Polymarket (prediction markets).
- **solomon-trader**: Alpaca stock/crypto trading (paper live).

These are good prototypes. The new Python bot offers stronger quant tools (pandas, indicators, backtesting) and structure for a full trading system. We can merge ideas, e.g., feed crypto-monitor signals into strategies or add Polymarket executor.

## Development Approach
- **Incremental**: one focused module per commit + test + push + update docs.
- **Safety first**: every financial primitive (sizing, risk gate, fill math) will have tests against known cases.
- **Never live without approval**: live execution stays disabled. Do not add an order path in this repo until a separate, explicit decision.

See the full plan in [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).

**Trade responsibly.**
