"""Trading strategies package. All strategies subclass BaseStrategy.

See docs/ADDING_A_STRATEGY.md (future) for extension guide.
"""

from .base_strategy import BaseStrategy, Signal
from .sma_crossover import SMACrossoverStrategy

__all__ = ["BaseStrategy", "Signal", "SMACrossoverStrategy"]
