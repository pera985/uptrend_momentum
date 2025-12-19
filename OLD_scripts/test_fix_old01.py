"""
Test the fixed ticker fetching
"""
from uptrend_scanner import UptrendScanner
import config

print("=" * 70)
print("Testing Fixed Ticker Fetching")
print("=" * 70)

scanner = UptrendScanner(config.POLYGON_API_KEY, max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE)

# Test fetching from both exchanges
print("\nFetching tickers from XNAS and XNYS...")
tickers = scanner.api.get_all_tickers(exchange=['XNAS', 'XNYS'], limit=100)

print(f"\nTotal tickers fetched: {len(tickers)}")

if len(tickers) > 0:
    print(f"\nFirst 10 tickers:")
    for i, ticker in enumerate(tickers[:10], 1):
        print(f"  {i}. {ticker.get('ticker')} - {ticker.get('name', 'N/A')[:40]} - Exchange: {ticker.get('primary_exchange', 'N/A')}")

    print("\n✓ SUCCESS: Ticker fetching is working correctly!")
else:
    print("\n✗ ERROR: No tickers fetched")

print("\n" + "=" * 70)
