"""
Uptrend Momentum Extensions

Provides integration with shared_modules for:
- Walk-forward backtesting
- Performance monitoring
- Parameter versioning
- Market regime detection
"""

from .backtest_adapter import UptrendMomentumAdapter

__all__ = ['UptrendMomentumAdapter']
