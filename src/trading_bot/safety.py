"""Paper-only execution gate.

This module has no third-party imports so tests can run without the trading stack.
Live money is intentionally unreachable: a live flag never selects an executor.
"""

from __future__ import annotations


class PaperOnlyError(RuntimeError):
    """Raised when a caller asks for live-money execution."""


def resolve_mode(
    *,
    paper_trading: bool = True,
    dry_run: bool = True,
    allow_live: bool = False,
) -> str:
    """Return the only supported execution mode.

    ``allow_live`` is accepted so mis-set env vars are visible in logs, but it
    cannot unlock a live executor. Paper or dry-run always wins; otherwise the
    mode is ``blocked-live`` and :func:`assert_paper_execution` raises.
    """
    if paper_trading or dry_run or not allow_live:
        return "paper"
    return "blocked-live"


def assert_paper_execution(mode: str) -> None:
    """Fail closed unless mode is paper."""
    if mode != "paper":
        raise PaperOnlyError(
            "Live money execution is disabled. Keep PAPER_TRADING=true and "
            "DRY_RUN=true. This repo will not place live orders."
        )
