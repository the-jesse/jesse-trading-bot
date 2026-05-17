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

Built upon review of your existing repos (crypto-monitor for Solana monitoring/signals, polymarket-bot for prediction markets, solomon-trader) which demonstrate solid foundational work in market data and interaction. Great starting points — this new bot provides a robust framework you can extend or integrate with.

### Key Features (Current & Planned)
- **Modular Architecture**: Data, Strategy, Risk, Execution layers (in progress).
- **Paper Trading**: Realistic simulation (fees, slippage, virtual fills).
- **Risk Management**: Position sizing, pre-trade gates, daily loss limits, circuit breakers.
- **Pluggable Strategies**: Subclass `BaseStrategy` easily; registry for multi-strat configs.
- **CCXT Powered**: 100+ exchanges, first-class testnet support.
- **Config Driven**: .env + future YAML for symbols/strategies.
- **Logging & Audit**: structlog for every decision and trade event.
- **Backtesting Foundation**: Event-driven + vectorized paths.
- Best practices: type hints, Pydantic models, small testable commits.

## Quick Start (Paper Demo)

```bash
git clone https://github.com/the-jesse/jesse-trading-bot.git
cd jesse-trading-bot

# Recommended: use venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — leave API keys blank for public data / paper mode

# Run the current demo (synthetic data + SMA signal)
PYTHONPATH=src python -m trading_bot.main --paper
```

**Note**: The `src/` layout requires `PYTHONPATH=src` until we add `pyproject.toml` + editable install (coming in Phase 1/4).

See `docs/DEVELOPMENT_PLAN.md` for the full phased roadmap, architecture, and safety rules.

## Current Status (Phase 1 Foundations — 2026-05-17)

**Completed**:
- Phase 0 deep assessment: full exploration via GitHub tools, demo verified, gaps documented.
- `docs/DEVELOPMENT_PLAN.md`: comprehensive plan with target architecture, safety layers, module specs, testing rules, and open questions.
- `.gitignore`: protects `.env`, API secrets, state snapshots, logs, caches, test outputs.
- `src/trading_bot/__init__.py` + `strategies/__init__.py`: proper package, version, clean exports.
- All changes via small, auditable commits with clear messages.

**Demo still works** (verified post-changes):
```
PYTHONPATH=src python -m trading_bot.main --paper
# Outputs: signal (buy/sell/hold), risk params, demo notice
```

**Next Immediate Work** (Phase 2 — incremental, paper-first):
1. CCXT Data Provider (`data/ccxt_provider.py`) — real OHLCV + testnet
2. Risk Manager — sizing + pre-trade validation
3. Paper Executor — virtual positions, realistic fills
4. Main loop refactor — continuous mode + logging

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
- **Never live without approval**: the live executor will be heavily guarded and disabled by default.

See the full plan in [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).

**Trade responsibly. Questions? Let's discuss in the next iteration.**
