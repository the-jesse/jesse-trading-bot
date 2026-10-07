"""Paper executor: virtual cash, fees, and slippage. Never talks to an exchange."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


class PaperExecutionError(Exception):
    """Base error for simulated fills."""


class InsufficientCash(PaperExecutionError):
    """Buy cost including fees exceeds paper cash."""


class InsufficientPosition(PaperExecutionError):
    """Sell size exceeds the simulated position."""


@dataclass
class PaperFill:
    symbol: str
    side: str
    size: float
    mid_price: float
    fill_price: float
    fee: float
    paper: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PaperExecutor:
    """In-memory paper account. Safe to unit-test without network or keys."""

    def __init__(
        self,
        starting_cash: float = 10_000.0,
        fee_bps: float = 10.0,
        slippage_bps: float = 5.0,
    ) -> None:
        if starting_cash < 0:
            raise ValueError("starting_cash must be >= 0")
        if fee_bps < 0 or slippage_bps < 0:
            raise ValueError("fee_bps and slippage_bps must be >= 0")
        self.cash = float(starting_cash)
        self.fee_bps = float(fee_bps)
        self.slippage_bps = float(slippage_bps)
        self.positions: dict[str, float] = {}
        self.fills: list[PaperFill] = []

    def position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)

    def fill(self, symbol: str, side: str, size: float, mid_price: float) -> PaperFill:
        side = side.lower()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        if size <= 0 or mid_price <= 0:
            raise ValueError("size and mid_price must be positive")

        slip = mid_price * (self.slippage_bps / 10_000.0)
        fill_price = mid_price + slip if side == "buy" else mid_price - slip
        if fill_price <= 0:
            raise ValueError("slippage drove fill price to non-positive")

        notional = fill_price * size
        fee = notional * (self.fee_bps / 10_000.0)

        if side == "buy":
            cost = notional + fee
            if cost > self.cash + 1e-9:
                raise InsufficientCash(
                    f"need {cost:.4f} paper cash, have {self.cash:.4f}"
                )
            self.cash -= cost
            self.positions[symbol] = self.position(symbol) + size
        else:
            held = self.position(symbol)
            if size > held + 1e-12:
                raise InsufficientPosition(
                    f"sell {size} exceeds paper position {held}"
                )
            self.positions[symbol] = held - size
            self.cash += notional - fee

        record = PaperFill(
            symbol=symbol,
            side=side,
            size=size,
            mid_price=mid_price,
            fill_price=fill_price,
            fee=fee,
        )
        self.fills.append(record)
        return record
