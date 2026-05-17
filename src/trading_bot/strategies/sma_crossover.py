import pandas as pd
import pandas_ta as ta
from trading_bot.strategies.base_strategy import BaseStrategy, Signal

class SMACrossoverStrategy(BaseStrategy):
    """Dual SMA Crossover Strategy.
    
    Generates buy signal on bullish crossover (fast > slow),
    sell on bearish crossover.
    Simple trend following example.
    """
    
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.fast_period = self.config.get('sma_fast', 9)
        self.slow_period = self.config.get('sma_slow', 21)
    
    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        if len(ohlcv) < max(self.fast_period, self.slow_period) + 2:
            return 'hold'
        
        df = ohlcv.copy()
        df['sma_fast'] = ta.sma(df['close'], length=self.fast_period)
        df['sma_slow'] = ta.sma(df['close'], length=self.slow_period)
        
        # Use latest two candles for crossover
        fast = df['sma_fast'].iloc[-1]
        slow = df['sma_slow'].iloc[-1]
        fast_prev = df['sma_fast'].iloc[-2]
        slow_prev = df['sma_slow'].iloc[-2]
        
        if pd.isna(fast) or pd.isna(slow):
            return 'hold'
        
        if fast_prev <= slow_prev and fast > slow:
            return 'buy'
        if fast_prev >= slow_prev and fast < slow:
            return 'sell'
        
        return 'hold'