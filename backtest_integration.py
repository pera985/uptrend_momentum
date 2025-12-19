#!/usr/bin/env python3
"""
Walk-Forward Backtesting Integration for Uptrend Momentum Scanner

This script connects the Uptrend Momentum Scanner's 100-point scoring system
with walk-forward backtesting to evaluate historical performance and optimize
scoring weights.

Usage:
    python3 backtest_integration.py --tickers AAPL,MSFT,GOOGL --years 3
    python3 backtest_integration.py --file watchlist.txt --years 5

Note: Input files are automatically read from the input_files/ directory.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from uptrend_momentum.uptrend_scanner import UptrendScanner
import uptrend_momentum.config as config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UptrendMomentumBacktester:
    """
    Walk-forward backtesting integration for Uptrend Momentum Scanner.

    Tests different score thresholds (60, 70, 80, 90) to find optimal
    entry criteria over historical data.
    """

    def __init__(self, api_key, initial_capital=100000):
        """
        Initialize backtester.

        Args:
            api_key: Polygon.io API key
            initial_capital: Starting capital for backtest
        """
        self.api_key = api_key
        self.initial_capital = initial_capital
        self.scanner = UptrendScanner(api_key)

    def fetch_historical_data(self, tickers, years=5):
        """
        Fetch historical daily data for backtesting.

        Args:
            tickers: List of ticker symbols
            years: Number of years of historical data

        Returns:
            dict: {ticker: DataFrame} with OHLCV data
        """
        logger.info(f"Fetching {years} years of data for {len(tickers)} tickers...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)

        historical_data = {}

        for ticker in tickers:
            try:
                logger.info(f"Fetching data for {ticker}...")
                df = self.scanner.get_aggregates(ticker, days=years*365)

                if df is not None and len(df) > 0:
                    historical_data[ticker] = df
                    logger.info(f"  ✓ {ticker}: {len(df)} days of data")
                else:
                    logger.warning(f"  ✗ {ticker}: No data available")

            except Exception as e:
                logger.error(f"  ✗ {ticker}: Error fetching data - {e}")

        logger.info(f"Successfully fetched data for {len(historical_data)} tickers")
        return historical_data

    def optimize_score_threshold(self, train_data, thresholds=[60, 70, 80, 90]):
        """
        Optimize score threshold on training data.

        Tests different minimum score values for entry signals.

        Args:
            train_data: dict of {ticker: DataFrame} for training period
            thresholds: List of score thresholds to test

        Returns:
            int: Best score threshold
        """
        best_threshold = 80
        best_score = -float('inf')

        logger.info(f"Testing score thresholds: {thresholds}")

        for threshold in thresholds:
            # Simulate strategy with this threshold
            total_return = 0
            num_signals = 0

            for ticker, df in train_data.items():
                try:
                    # Score each day
                    scores = self._calculate_scores(df)

                    # Generate signals where score >= threshold
                    signals = []
                    for i in range(len(scores)):
                        if scores[i] >= threshold:
                            signals.append((df.index[i], df.iloc[i]['close'], scores[i]))

                    # Calculate returns
                    if len(signals) > 0:
                        returns = self._calculate_returns(df, signals)
                        total_return += returns
                        num_signals += len(signals)

                except Exception as e:
                    logger.warning(f"Error processing {ticker}: {e}")
                    continue

            # Score = average return per signal
            avg_return = total_return / max(num_signals, 1)

            logger.info(f"  Threshold {threshold}: Avg Return {avg_return:.2%}, Signals: {num_signals}")

            if avg_return > best_score:
                best_score = avg_return
                best_threshold = threshold

        logger.info(f"✓ Best threshold: {best_threshold} (Avg Return: {best_score:.2%})")
        return best_threshold

    def _calculate_scores(self, df):
        """
        Calculate uptrend momentum scores for each day.

        Simplified scoring based on:
        - Trend Strength (25 pts): ADX, MA slope
        - Momentum Quality (20 pts): RSI
        - Volume Profile (20 pts): Volume trend
        - Price Structure (20 pts): Support quality
        - Risk/Reward (15 pts): Distance from MA20

        Args:
            df: DataFrame with OHLCV data

        Returns:
            list: Scores (0-100) for each day
        """
        scores = []

        # Calculate moving averages
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()

        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate ADX (simplified)
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ADX'] = tr.rolling(window=14).mean()  # Simplified ADX

        # Calculate volume MA
        df['vol_ma'] = df['volume'].rolling(window=50).mean()

        for i in range(50, len(df)):  # Start after 50 days
            score = 0

            # Trend Strength (25 pts)
            if not pd.isna(df.iloc[i]['ADX']):
                if df.iloc[i]['ADX'] > 30:
                    score += 15
                elif df.iloc[i]['ADX'] > 25:
                    score += 10

            # MA slope
            if not pd.isna(df.iloc[i]['MA20']) and not pd.isna(df.iloc[i-5]['MA20']):
                ma_slope = (df.iloc[i]['MA20'] - df.iloc[i-5]['MA20']) / df.iloc[i-5]['MA20']
                if ma_slope > 0.015:  # 1.5% weekly gain
                    score += 10

            # Momentum Quality (20 pts)
            if not pd.isna(df.iloc[i]['RSI']):
                if 55 <= df.iloc[i]['RSI'] <= 65:
                    score += 20
                elif 50 <= df.iloc[i]['RSI'] <= 70:
                    score += 15

            # Volume Profile (20 pts)
            if not pd.isna(df.iloc[i]['vol_ma']):
                if df.iloc[i]['volume'] > df.iloc[i]['vol_ma'] * 1.5:
                    score += 20
                elif df.iloc[i]['volume'] > df.iloc[i]['vol_ma']:
                    score += 10

            # Price Structure (20 pts)
            if not pd.isna(df.iloc[i]['MA20']) and not pd.isna(df.iloc[i]['MA50']):
                if df.iloc[i]['close'] > df.iloc[i]['MA20'] > df.iloc[i]['MA50']:
                    score += 20

            # Risk/Reward (15 pts)
            if not pd.isna(df.iloc[i]['MA20']):
                distance_from_ma = abs(df.iloc[i]['close'] - df.iloc[i]['MA20']) / df.iloc[i]['MA20']
                if distance_from_ma < 0.05:  # Within 5%
                    score += 15
                elif distance_from_ma < 0.10:
                    score += 8

            scores.append(min(score, 100))  # Cap at 100

        # Pad with zeros for first 50 days
        return [0] * 50 + scores

    def _calculate_returns(self, df, signals, holding_period=21):
        """
        Calculate returns for given signals.

        Args:
            df: DataFrame with OHLCV data
            signals: List of (date, price, score) tuples
            holding_period: Days to hold position (default: 21 = 1 month)

        Returns:
            float: Total return percentage
        """
        total_return = 0

        for signal_date, entry_price, score in signals:
            try:
                signal_idx = df.index.get_loc(signal_date)
                exit_idx = min(signal_idx + holding_period, len(df) - 1)
                exit_price = df.iloc[exit_idx]['close']

                trade_return = (exit_price - entry_price) / entry_price
                total_return += trade_return

            except Exception as e:
                continue

        return total_return

    def test_strategy(self, test_data, threshold):
        """
        Test strategy on out-of-sample test data.

        Args:
            test_data: dict of {ticker: DataFrame} for test period
            threshold: Score threshold to use

        Returns:
            dict: Test results with metrics
        """
        trades = []

        for ticker, df in test_data.items():
            try:
                # Calculate scores
                scores = self._calculate_scores(df)

                # Generate signals
                for i in range(len(scores)):
                    if scores[i] >= threshold:
                        entry_date = df.index[i]
                        entry_price = df.iloc[i]['close']
                        entry_score = scores[i]

                        # Calculate exit
                        exit_idx = min(i + 21, len(df) - 1)
                        exit_date = df.index[exit_idx]
                        exit_price = df.iloc[exit_idx]['close']

                        trade_return = (exit_price - entry_price) / entry_price

                        trades.append({
                            'ticker': ticker,
                            'entry_date': entry_date,
                            'exit_date': exit_date,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'entry_score': entry_score,
                            'return': trade_return,
                            'outcome': 'win' if trade_return > 0 else 'loss'
                        })

            except Exception as e:
                logger.warning(f"Error testing {ticker}: {e}")
                continue

        # Calculate metrics
        if len(trades) == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'total_return': 0
            }

        trades_df = pd.DataFrame(trades)

        # Score-based analysis
        tier1_trades = trades_df[trades_df['entry_score'] >= 80]
        tier2_trades = trades_df[(trades_df['entry_score'] >= 70) & (trades_df['entry_score'] < 80)]

        results = {
            'total_trades': len(trades),
            'win_rate': len(trades_df[trades_df['outcome'] == 'win']) / len(trades),
            'avg_return': trades_df['return'].mean(),
            'total_return': trades_df['return'].sum(),
            'tier1_win_rate': len(tier1_trades[tier1_trades['outcome'] == 'win']) / len(tier1_trades) if len(tier1_trades) > 0 else 0,
            'tier2_win_rate': len(tier2_trades[tier2_trades['outcome'] == 'win']) / len(tier2_trades) if len(tier2_trades) > 0 else 0,
            'trades': trades_df
        }

        return results

    def run_walkforward_backtest(self, historical_data, train_window=252, test_window=63):
        """
        Run walk-forward backtesting.

        Args:
            historical_data: dict of {ticker: DataFrame}
            train_window: Training period in days (default: 252 = 1 year)
            test_window: Test period in days (default: 63 = 3 months)

        Returns:
            dict: Backtest results
        """
        logger.info("Starting walk-forward backtesting...")
        logger.info(f"Train window: {train_window} days, Test window: {test_window} days")

        # Find common date range
        all_dates = []
        for df in historical_data.values():
            all_dates.extend(df.index.tolist())

        min_date = min(all_dates)
        max_date = max(all_dates)

        logger.info(f"Data range: {min_date.date()} to {max_date.date()}")

        # Create walk-forward windows
        windows = []
        current_start = min_date

        while current_start + timedelta(days=train_window + test_window) <= max_date:
            train_end = current_start + timedelta(days=train_window)
            test_end = train_end + timedelta(days=test_window)

            windows.append({
                'train_start': current_start,
                'train_end': train_end,
                'test_start': train_end,
                'test_end': test_end
            })

            current_start = train_end

        logger.info(f"Created {len(windows)} walk-forward windows")

        # Run backtest for each window
        all_results = []

        for i, window in enumerate(windows, 1):
            logger.info(f"\n=== Window {i}/{len(windows)} ===")
            logger.info(f"Train: {window['train_start'].date()} to {window['train_end'].date()}")
            logger.info(f"Test:  {window['test_start'].date()} to {window['test_end'].date()}")

            # Split data
            train_data = {}
            test_data = {}

            for ticker, df in historical_data.items():
                train_df = df[(df.index >= window['train_start']) & (df.index < window['train_end'])]
                test_df = df[(df.index >= window['test_start']) & (df.index < window['test_end'])]

                if len(train_df) > 0:
                    train_data[ticker] = train_df
                if len(test_df) > 0:
                    test_data[ticker] = test_df

            # Optimize
            best_threshold = self.optimize_score_threshold(train_data)

            # Test
            test_results = self.test_strategy(test_data, best_threshold)

            logger.info(f"Test Results: {test_results['total_trades']} trades, "
                       f"Win Rate: {test_results['win_rate']:.1%}, "
                       f"Avg Return: {test_results['avg_return']:.2%}")

            all_results.append({
                'window': i,
                **window,
                'best_threshold': best_threshold,
                **test_results
            })

        # Aggregate
        summary = self._aggregate_results(all_results)

        return {
            'windows': all_results,
            'summary': summary
        }

    def _aggregate_results(self, all_results):
        """Aggregate results across all windows."""
        total_trades = sum(r['total_trades'] for r in all_results)
        total_wins = sum(r['total_trades'] * r['win_rate'] for r in all_results)
        total_return = sum(r['total_return'] for r in all_results)

        summary = {
            'total_windows': len(all_results),
            'total_trades': total_trades,
            'overall_win_rate': total_wins / total_trades if total_trades > 0 else 0,
            'total_return': total_return,
            'avg_return_per_trade': total_return / total_trades if total_trades > 0 else 0
        }

        logger.info("\n" + "="*70)
        logger.info("BACKTEST SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Windows:        {summary['total_windows']}")
        logger.info(f"Total Trades:         {summary['total_trades']}")
        logger.info(f"Overall Win Rate:     {summary['overall_win_rate']:.1%}")
        logger.info(f"Total Return:         {summary['total_return']:.2%}")
        logger.info(f"Avg Return/Trade:     {summary['avg_return_per_trade']:.2%}")
        logger.info("="*70)

        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Uptrend Momentum Scanner Walk-Forward Backtest')
    parser.add_argument('--tickers', help='Comma-separated list of tickers')
    parser.add_argument('--file', help='Filename in input_files/ directory with tickers (one per line). E.g., --file watchlist.txt')
    parser.add_argument('--years', type=int, default=3, help='Years of historical data (default: 3)')
    parser.add_argument('--capital', type=float, default=100000, help='Initial capital (default: 100000)')
    parser.add_argument('--api-key', help='Polygon.io API key (or set POLYGON_API_KEY env var)')

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('POLYGON_API_KEY') or config.POLYGON_API_KEY
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        logger.error("API key required. Use --api-key or set POLYGON_API_KEY environment variable")
        sys.exit(1)

    # Get tickers
    tickers = []
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
    elif args.file:
        # Build full path to input file (auto-prepend input_files/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_file_path = os.path.join(script_dir, 'input_files', args.file)
        with open(input_file_path, 'r') as f:
            tickers = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
    else:
        logger.error("Must provide --tickers or --file")
        sys.exit(1)

    logger.info(f"Starting backtest for {len(tickers)} tickers: {', '.join(tickers)}")

    # Run backtest
    backtester = UptrendMomentumBacktester(api_key, initial_capital=args.capital)
    historical_data = backtester.fetch_historical_data(tickers, years=args.years)

    if len(historical_data) == 0:
        logger.error("No historical data available. Exiting.")
        sys.exit(1)

    results = backtester.run_walkforward_backtest(historical_data)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = 'backtest_results'
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f'uptrend_momentum_backtest_{timestamp}.csv')

    all_trades = []
    for window_result in results['windows']:
        if 'trades' in window_result and window_result['trades'] is not None:
            trades_df = window_result['trades'].copy()
            trades_df['window'] = window_result['window']
            all_trades.append(trades_df)

    if all_trades:
        all_trades_df = pd.concat(all_trades, ignore_index=True)
        all_trades_df.to_csv(output_file, index=False)
        logger.info(f"\nDetailed results saved to: {output_file}")

    logger.info("\nBacktest complete!")


if __name__ == '__main__':
    main()
