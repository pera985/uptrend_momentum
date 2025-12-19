"""
Uptrend Momentum Backtest Adapter

Connects uptrend_momentum to shared_modules functionality.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared_modules.base_adapter import BaseAnalyzerAdapter


class UptrendMomentumAdapter(BaseAnalyzerAdapter):
    """
    Adapter for uptrend_momentum integration with shared_modules.

    Usage:
        from extensions import UptrendMomentumAdapter

        adapter = UptrendMomentumAdapter(
            api_key="your_polygon_api_key",
            storage_path="./output/backtest_data"
        )

        results = adapter.run_backtest(
            tickers=['AAPL', 'MSFT'],
            start_date='2022-01-01',
            end_date='2024-12-31'
        )
    """

    def __init__(self, api_key: str, storage_path: str = "./output/backtest_data"):
        super().__init__(
            analyzer_name="uptrend_momentum",
            storage_path=storage_path,
            api_key=api_key
        )

        # Import scanner
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from uptrend_scanner import UptrendScanner
            self.scanner = UptrendScanner(api_key=api_key)
        except ImportError as e:
            raise ImportError(f"Could not import UptrendScanner: {e}")

        self._parameters = self._load_default_parameters()

        if not self.parameter_versioning.versions:
            self.parameter_versioning.initialize(
                self._parameters, "Initial uptrend_momentum parameters"
            )

    def _load_default_parameters(self) -> Dict[str, Any]:
        """Load default parameters."""
        return {
            'early_uptrend_threshold': 5,  # Points needed (out of 8)
            'established_days_above_ma20': 20,
            'adx_strong_threshold': 25,
            'rsi_healthy_min': 50,
            'rsi_healthy_max': 70,
            'volume_spike_threshold': 1.5,
            'score_tier1_min': 80,
            'score_tier2_min': 60,
            'score_tier3_min': 40
        }

    def generate_signal(
        self, ticker: str, date: datetime, price_data: pd.DataFrame
    ) -> Optional[Dict[str, Any]]:
        try:
            result = self.scanner.scan_stock(ticker)
            if result is None:
                return None

            is_early = result.get('is_early_uptrend', False)
            is_established = result.get('is_established_uptrend', False)
            score = result.get('score', 0)

            signal = 'HOLD'
            if is_early or is_established:
                signal = 'BUY'

            return {
                'signal': signal,
                'score': score,
                'is_early_uptrend': is_early,
                'is_established_uptrend': is_established,
                'tier': result.get('tier', 4)
            }
        except Exception as e:
            print(f"Signal generation failed for {ticker}: {e}")
            return None

    def get_parameters(self) -> Dict[str, Any]:
        return self._parameters.copy()

    def set_parameters(self, params: Dict[str, Any]) -> None:
        self._parameters.update(params)

    def optimize_parameters(
        self, tickers: List[str], price_data: Dict[str, pd.DataFrame],
        start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        # Simple optimization placeholder
        return self._parameters.copy()

    def fetch_price_data(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        try:
            df = self.scanner.api.get_aggregates(ticker, days=365)
            if df is not None and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")
            return pd.DataFrame()


def create_adapter(api_key: str, storage_path: str = "./output/backtest_data"):
    return UptrendMomentumAdapter(api_key=api_key, storage_path=storage_path)
