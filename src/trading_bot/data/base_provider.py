"""Abstract base class for all data providers.

Defines the contract used by strategies, risk, execution, and backtester.
All implementations must be safe for paper trading and handle errors gracefully.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class BaseDataProvider(ABC):
    """Interface for market data access."""

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV candles as DataFrame with datetime index.

        Columns: open, high, low, close, volume (float)
        Index: timestamp (pd.DatetimeIndex, UTC or local)
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_ticker(self, symbol: str) -> dict:
        """Return latest ticker: last, bid, ask, volume24h, etc."""
        raise NotImplementedError

    def fetch_balance(self) -> dict:
        """Optional: return account balance (only meaningful with API keys).

        Paper trading should use virtual balances from PaperState instead.
        """
        raise NotImplementedError("fetch_balance not supported by this provider")

    def name(self) -> str:
        return self.__class__.__name__
