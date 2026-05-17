from abc import ABC, abstractmethod
import pandas as pd
from typing import Literal

Signal = Literal['buy', 'sell', 'hold']

class BaseStrategy(ABC):
    """Abstract base for trading strategies. Implement generate_signal."""
    
    def __init__(self, config: dict | None = None):
        self.config = config or {}
    
    @abstractmethod
    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        """Return 'buy', 'sell', or 'hold' based on latest data."""
        raise NotImplementedError
    
    def name(self) -> str:
        return self.__class__.__name__