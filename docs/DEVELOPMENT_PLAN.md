# Jesse Trading Bot — Development Plan

**Repo**: the-jesse/jesse-trading-bot | **Status**: Phase 0 complete → Phase 1 in progress

> ⚠️ **CRITICAL DISCLAIMER** ⚠️
> Cryptocurrency trading involves **substantial risk of loss**. This is **educational / paper-trading only**. Never use real funds without months of verified paper trading, full audits, and explicit approval. Authors accept zero liability.

## Phase 0 Summary (Complete)

**What works**:
- Excellent risk disclaimers in README
- Pluggable `BaseStrategy` + `SMACrossoverStrategy` (pandas-ta)
- Pydantic config with risk params
- Demo: `PYTHONPATH=src python -m trading_bot.main --paper` → generates synthetic data, emits signal (HOLD on seed), prints risk summary

**Verified**: Demo runs cleanly (tested 2026-05-17).

**Gaps**:
- No CCXT usage, no data provider
- No RiskManager / PositionSizer / pre-trade gates
- No PaperExecutor (virtual balance, fills, slippage, fees)
- No continuous loop or state
- Import path fragility (src layout vs top-level imports)
- No .gitignore, no tests, no docs beyond README
- Live mode stubbed with zero guards

**Push confirmed**: Yes (owner `the-jesse` via gh + MCP tools).

## Guiding Principles
1. Paper-first, fail-closed, auditable decisions
2. Small testable commits; run demo after every change
3. Type hints + Pydantic models for all trading objects
4. Hard safety limits that config cannot override
5. Clear separation: Data → Strategy → Risk → Execution → Orchestrator

## Target Architecture

```
Orchestrator (main loop / CLI)
  ↓ DataProvider (CCXT testnet + cache)
  ↓ Strategy (pluggable, returns Signal)
  ↓ RiskManager (sizing + gate + breakers)
  ↓ Executor (Paper | Live guarded)
  ↓ State + Logger (structlog)
```

Domain models: Position, OrderIntent, Trade, RiskReport (Pydantic).

Safety: DRY_RUN, KILL_SWITCH, max exposure, daily loss circuit breaker, realistic paper slippage/fees.

## Proposed Structure

```
src/trading_bot/
  data/ccxt_provider.py
  risk/risk_manager.py
  execution/paper_executor.py (and base)
  strategies/ (keep + registry)
  models.py, config.py (enhanced), main.py (refactored)
  backtest/engine.py
  utils/logging.py
  state/paper_state.py
```

docs/ (this + RISK_MANAGEMENT.md, ADDING_STRATEGY.md)
tests/, .gitignore, pyproject.toml, Makefile

## Phased Plan (Incremental, Paper Priority)

**Phase 1 (Now)**: This plan doc + .gitignore + package fixes + README update

**Phase 2 (Core)**:
1. CCXT DataProvider (public + testnet, rate limits, errors)
2. RiskManager (fractional sizing, pre-trade checks, stops)
3. PaperExecutor (virtual book, realistic fills)
4. Main loop (one-shot + continuous modes, logging)
5. Basic backtester

Each step: commit, push, run demo, update status.

**Phase 3**: Multi-symbol/strategy config, pluggable registry, bridges to crypto-monitor / polymarket-bot

**Phase 4**: Tests (risk math critical), expanded docs, .env hardening, lint/CI, Docker foundation

## Testing After Changes
- `PYTHONPATH=src python -m trading_bot.main --paper` still succeeds
- New unit tests pass (`pytest`)
- Risk calculations match hand-verified examples
- Paper fills produce correct P&L and fee deduction

## Open Questions
- Primary exchange/testnet preference (Binance vs Bybit)?
- First strategies beyond SMA?
- Persistence (SQLite) timing?
- Integration priority with your other repos?

**All development is paper-only until further explicit approval. Safety > features.**

*Updated after each milestone. Trade responsibly.*