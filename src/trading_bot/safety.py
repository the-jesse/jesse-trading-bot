"""Hard gates. This package must not place live orders."""


class LiveTradingDisabled(RuntimeError):
    """Raised when a caller tries to leave paper mode."""


def assert_paper_only(*, paper_flag: bool, settings_paper: bool) -> None:
    """Refuse any path that is not explicitly paper.

    Both the CLI flag and settings.paper_trading must be true. A blank or
    false PAPER_TRADING value is a stop, not a live switch.
    """
    if not paper_flag or not settings_paper:
        raise LiveTradingDisabled(
            "Live trading is disabled in jesse-trading-bot. "
            "Pass --paper and keep PAPER_TRADING=true. No exchange order path."
        )
