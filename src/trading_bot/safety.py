"""Paper-only execution gate.

Live order routing is intentionally not implemented. Callers must pass a paper
flag and must not rely on an override to reach an exchange.
"""


class LiveTradingDisabled(RuntimeError):
    """Raised when a caller tries to leave paper/demo mode."""


def ensure_paper_mode(paper_trading: bool, explicit_live_override: bool = False) -> None:
    """Allow only paper mode. The override argument is rejected on purpose.

    A future live executor needs its own reviewed module, credentials outside
    git, and a human merge. This function must not grow a bypass.
    """
    if explicit_live_override:
        raise LiveTradingDisabled(
            "Live override is not implemented. This build is paper/demo only."
        )
    if not paper_trading:
        raise LiveTradingDisabled(
            "paper_trading must stay true. Refusing to continue without a paper flag."
        )
