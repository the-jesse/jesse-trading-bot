"""Risk management package.

RiskManager enforces position sizing, pre-trade gates, daily loss limits,
and other safety rules. All trades must pass through here.

Paper trading uses the same rules as live.
"""

from .risk_manager import RiskManager, RiskReport, PositionSizer

__all__ = ["RiskManager", "RiskReport", "PositionSizer"]
