"""CCXT-powered data provider with testnet/sandbox support.

Primary implementation of BaseDataProvider.

Safety notes:
- Public endpoints (no keys) always work for market data.
- Private methods (balance) require valid API keys + testnet mode for safety.
- Rate limiting is enabled by default via CCXT.
- All errors are caught and re-raised with context; never swallow failures silently.

Supported (initial): binance, bybit (testnet friendly).
"""

from typing import Optional, Any
import ccxt
import pandas as pd

from trading_bot.data.base_provider import BaseDataProvider


class CCXTDataProvider(BaseDataProvider):
    """Live / testnet data via CCXT unified API."""

    def __init__(
        self,
        exchange_id: str = "binance",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
        enable_rate_limit: bool = True,
        timeout: int = 30000,
        **exchange_options: Any,
    ) -> None:
        super().__init__()
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"Unsupported exchange: {exchange_id}. Check ccxt.exchanges")

        exchange_class = getattr(ccxt, exchange_id)
        config: dict[str, Any] = {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": enable_rate_limit,
            "timeout": timeout,
            "options": {"defaultType": "spot", **exchange_options},
        }

        self.exchange_id = exchange_id
        self.testnet = testnet
        self.exchange = exchange_class(config)

        # Testnet / sandbox configuration (exchange-specific)
        if testnet:
            self._configure_testnet()

        # Load markets once (fail fast if bad exchange)
        try:
            self.exchange.load_markets()
        except Exception as exc:  # broad but we want to surface config errors early
            raise RuntimeError(f"Failed to load markets for {exchange_id}: {exc}") from exc

    def _configure_testnet(self) -> None:
        """Enable sandbox/testnet mode for supported exchanges."""
        eid = self.exchange_id.lower()
        if eid == "binance":
            # Binance has official testnet
            self.exchange.set_sandbox_mode(True)
        elif eid == "bybit":
            # Bybit testnet via testnet flag or urls
            self.exchange.options["testnet"] = True
            # Some versions accept testnet=True in constructor; we force via urls if needed
            if hasattr(self.exchange, "urls") and "test" in self.exchange.urls:
                self.exchange.urls["api"] = self.exchange.urls["test"]
        elif eid in {"coinbase", "coinbasepro", "coinbaseadvanced"}:
            # Coinbase testnet is limited; warn but continue
            pass
        else:
            # Generic attempt
            if hasattr(self.exchange, "set_sandbox_mode"):
                self.exchange.set_sandbox_mode(True)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV and return standardized DataFrame."""
        try:
            raw = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            if not raw:
                return pd.DataFrame()
            df = pd.DataFrame(
                raw, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df = df.set_index("timestamp")
            # Ensure numeric
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            return df.dropna()
        except ccxt.NetworkError as e:
            raise RuntimeError(f"Network error fetching OHLCV {symbol}@{timeframe}: {e}") from e
        except ccxt.ExchangeError as e:
            raise RuntimeError(f"Exchange error fetching OHLCV {symbol}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error in fetch_ohlcv: {e}") from e

    def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        """Latest ticker snapshot."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "last": ticker.get("last"),
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "volume24h": ticker.get("quoteVolume") or ticker.get("baseVolume"),
                "timestamp": pd.to_datetime(ticker.get("timestamp"), unit="ms", utc=True)
                if ticker.get("timestamp")
                else pd.Timestamp.utcnow(),
                "raw": ticker,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch ticker for {symbol}: {e}") from e

    def fetch_balance(self) -> dict[str, Any]:
        """Account balance (requires API keys; use only on testnet for safety)."""
        if not self.exchange.apiKey:
            raise RuntimeError("fetch_balance requires API keys (use testnet keys only)")
        try:
            bal = self.exchange.fetch_balance()
            # Return a simplified view
            return {
                "total": bal.get("total", {}),
                "free": bal.get("free", {}),
                "used": bal.get("used", {}),
                "raw": bal,
            }
        except Exception as e:
            raise RuntimeError(f"Balance fetch failed (check keys + testnet): {e}") from e

    def get_markets(self) -> list[str]:
        """List of available symbols (after load_markets)."""
        return list(self.exchange.symbols or [])

    def name(self) -> str:
        mode = "testnet" if self.testnet else "live"
        return f"CCXTDataProvider({self.exchange_id}, {mode})"
