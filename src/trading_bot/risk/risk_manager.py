"""Risk Manager - the most critical safety component.

ALL proposed trades must pass through RiskManager.check_trade() before reaching
any executor. This is non-negotiable for both paper and live.

Current implementation (v0.2):
- Fixed-fractional position sizing with stop distance
- Hard max exposure and daily loss circuit breaker
- Per-trade risk cap + notional sanity
- Clear rejection reasons for audit logs

Future: ATR volatility sizing, correlation matrix, Kelly, portfolio heat.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime


@dataclass
class RiskReport:
    """Result of a pre-trade risk check."""
    approved: bool
    reason: str
    adjusted_size: Optional[float] = None
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PositionSizer:
    """Pure position sizing logic (testable in isolation)."""

    @staticmethod
    def fixed_fractional(
        equity: float,
        risk_per_trade_pct: float,
        entry_price: float,
        stop_price: float,
        max_position_pct: float = 0.10,
    ) -> float:
        """Return position size using fixed fractional risk."""
        risk_amount = equity * risk_per_trade_pct
        risk_per_unit = abs(entry_price - stop_price)
        if risk_per_unit <= 0:
            return 0.0
        raw_size = risk_amount / risk_per_unit
        max_notional = equity * max_position_pct
        max_size_by_notional = max_notional / entry_price if entry_price > 0 else 0
        size = min(raw_size, max_size_by_notional)
        return max(0.0, round(size, 8))


class RiskManager:
    """Gatekeeper for all trading decisions."""

    def __init__(
        self,
        max_position_pct: float = 0.02,
        risk_per_trade_pct: float = 0.01,
        daily_loss_limit_pct: float = 0.05,
        hard_max_exposure_pct: float = 0.10,
    ) -> None:
        self.max_position_pct = max_position_pct
        self.risk_per_trade_pct = risk_per_trade_pct
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.hard_max_exposure_pct = hard_max_exposure_pct
        self._daily_realized_pnl: float = 0.0
        self._daily_unrealized_pnl: float = 0.0
        self._last_reset: datetime = datetime.utcnow()

    def reset_daily_pnl(self) -> None:
        self._daily_realized_pnl = 0.0
        self._daily_unrealized_pnl = 0.0
        self._last_reset = datetime.utcnow()

    def update_daily_pnl(self, realized: float = 0.0, unrealized: float = 0.0) -> None:
        self._daily_realized_pnl += realized
        self._daily_unrealized_pnl += unrealized

    @property
    def current_daily_pnl(self) -> float:
        return self._daily_realized_pnl + self._daily_unrealized_pnl

    def check_daily_loss_limit(self, equity: float) -> bool:
        loss = -self.current_daily_pnl
        limit = equity * self.daily_loss_limit_pct
        return loss <= limit

    def calculate_size(
        self,
        equity: float,
        entry_price: float,
        stop_price: Optional[float] = None,
    ) -> float:
        """Recommended size for a new position using current risk settings."""
        if stop_price is None:
            stop_price = entry_price * (1 - 0.01)
        return PositionSizer.fixed_fractional(
            equity=equity,
            risk_per_trade_pct=self.risk_per_trade_pct,
            entry_price=entry_price,
            stop_price=stop_price,
            max_position_pct=min(self.max_position_pct, self.hard_max_exposure_pct),
        )

    def check_trade(
        self,
        symbol: str,
        side: Literal["buy", "sell"],
        size: float,
        entry_price: float,
        equity: float,
        current_exposure_notional: float = 0.0,
        stop_price: Optional[float] = None,
    ) -> RiskReport:
        """Main gate. Returns detailed report; only approved=True means proceed."""
        checks_passed: list[str] = []
        checks_failed: list[str] = []
        reason_parts: list[str] = []

        if not self.check_daily_loss_limit(equity):
            checks_failed.append("daily_loss_limit")
            reason_parts.append(
                f"Daily loss {abs(self.current_daily_pnl):.2f} exceeds limit "
                f"{equity * self.daily_loss_limit_pct:.2f}"
            )
            return RiskReport(
                approved=False,
                reason="; ".join(reason_parts),
                checks_failed=checks_failed,
                checks_passed=checks_passed,
            )
        checks_passed.append("daily_loss_ok")

        notional = size * entry_price
        max_allowed_notional = equity * self.max_position_pct
        if notional > max_allowed_notional * 1.05:
            checks_failed.append("max_position_exceeded")
            reason_parts.append(
                f"Notional {notional:.2f} > max allowed {max_allowed_notional:.2f}"
            )
            suggested = self.calculate_size(equity, entry_price, stop_price)
            return RiskReport(
                approved=False,
                reason="; ".join(reason_parts),
                adjusted_size=suggested,
                checks_failed=checks_failed,
                checks_passed=checks_passed,
            )
        checks_passed.append("position_size_ok")

        projected_exposure = current_exposure_notional + notional
        hard_cap = equity * self.hard_max_exposure_pct
        if projected_exposure > hard_cap:
            checks_failed.append("total_exposure_cap")
            reason_parts.append(
                f"Projected exposure {projected_exposure:.2f} would exceed hard cap {hard_cap:.2f}"
            )
            return RiskReport(
                approved=False,
                reason="; ".join(reason_parts),
                checks_failed=checks_failed,
                checks_passed=checks_passed,
            )
        checks_passed.append("exposure_ok")

        if size <= 0 or entry_price <= 0:
            checks_failed.append("invalid_order_params")
            reason_parts.append("Size and entry_price must be positive")
            return RiskReport(approved=False, reason="; ".join(reason_parts), checks_failed=checks_failed)
        checks_passed.append("params_sane")

        return RiskReport(
            approved=True,
            reason="All risk checks passed",
            checks_passed=checks_passed,
            checks_failed=checks_failed,
        )

    def record_fill(self, pnl: float, realized: bool = True) -> None:
        """Call after a fill to update daily profit and loss tracking."""
        if realized:
            self._daily_realized_pnl += pnl
        else:
            self._daily_unrealized_pnl += pnl
