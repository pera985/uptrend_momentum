"""
Plot a Single Stock Chart
=========================

Utility script to generate a detailed chart for a single stock.

Usage:
    python plot_single_stock.py AAPL
    python plot_single_stock.py TSLA NVDA MSFT  # Multiple stocks
"""

import sys
from uptrend_scanner import UptrendScanner
import config


def main():
    if len(sys.argv) < 2:
        print("\nPlot Single Stock - Generate detailed technical analysis chart")
        print("=" * 70)
        print("\nUsage: python plot_single_stock.py <TICKER> [TICKER2] [TICKER3] ...")
        print("\nExamples:")
        print("  python plot_single_stock.py AAPL")
        print("  python plot_single_stock.py TSLA NVDA MSFT")
        sys.exit(1)

    # Check API key
    if config.POLYGON_API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  ERROR: Please set your Polygon.io API key in config.py")
        print("Get your key at: https://polygon.io/dashboard/api-keys")
        sys.exit(1)

    tickers = sys.argv[1:]

    print("=" * 70)
    print(f"Generating charts for {len(tickers)} stock(s)")
    print("=" * 70)

    # Initialize scanner
    scanner = UptrendScanner(config.POLYGON_API_KEY,
                            max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE)

    # Generate charts
    for ticker in tickers:
        print(f"\nGenerating chart for {ticker}...")
        chart_file = scanner.plot_stock_chart(ticker.upper())

        if chart_file:
            print(f"✓ Chart saved: {chart_file}")
        else:
            print(f"✗ Failed to generate chart for {ticker}")

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == '__main__':
    main()
