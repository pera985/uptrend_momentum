#!/usr/bin/env python3
"""
Test script to show raw data fetching from Polygon.io

This script demonstrates what the data looks like when fetched from the API.
It will show both the raw JSON response and the converted DataFrame.
"""

import logging
from uptrend_scanner import PolygonAPI
import config

# Set up DEBUG logging to see the raw data
logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s'  # Simplified format for cleaner output
)

# IMPORTANT: Set the uptrend_scanner module logger to DEBUG
# (it defaults to INFO which won't show debug messages)
scanner_logger = logging.getLogger('uptrend_scanner')
scanner_logger.setLevel(logging.DEBUG)

def main():
    """Fetch and display raw data for a sample ticker"""

    print("\n" + "="*70)
    print("POLYGON.IO DATA FETCH TEST")
    print("="*70)
    print("\nThis will show you exactly what data is fetched from Polygon.io")
    print("and how it's converted into a DataFrame.\n")

    # Initialize API
    api = PolygonAPI(config.POLYGON_API_KEY)

    # Test with a well-known ticker
    ticker = "AAPL"

    print(f"Fetching 365 days of data for {ticker}...")
    print(f"(This will show first 3 bars and last 3 bars of raw data)\n")

    # Fetch data (will trigger debug output)
    df = api.get_aggregates(ticker, days=365)

    if df is not None:
        print(f"\n{'='*70}")
        print("SUMMARY")
        print("="*70)
        print(f"✓ Successfully fetched {len(df)} trading days for {ticker}")
        print(f"✓ Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"✓ Columns: {list(df.columns)}")
        print(f"\nLatest close price: ${df['close'].iloc[-1]:.2f}")
        print(f"{'='*70}\n")
    else:
        print(f"✗ Failed to fetch data for {ticker}")

    # Test with another ticker for comparison
    print(f"\n{'='*70}")
    ticker2 = "MSFT"
    print(f"Fetching data for {ticker2} (second example)...")
    print(f"{'='*70}\n")

    df2 = api.get_aggregates(ticker2, days=365)

    if df2 is not None:
        print(f"\n{'='*70}")
        print("SUMMARY")
        print("="*70)
        print(f"✓ Successfully fetched {len(df2)} trading days for {ticker2}")
        print(f"✓ Date range: {df2.index[0].strftime('%Y-%m-%d')} to {df2.index[-1].strftime('%Y-%m-%d')}")
        print(f"\nLatest close price: ${df2['close'].iloc[-1]:.2f}")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
