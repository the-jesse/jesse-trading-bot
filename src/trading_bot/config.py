from pydantic_settings import BaseSettings
 
class Settings(BaseSettings):
    exchange: str = "binance"
    api_key: str | None = None
    api_secret: str | None = None
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    paper_trading: bool = True
    dry_run: bool = True
    
    # Risk parameters
    max_position_pct: float = 0.02
    risk_per_trade_pct: float = 0.01
    daily_loss_limit_pct: float = 0.05
    
    # Strategy params
    sma_fast: int = 9
    sma_slow: int = 21
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()