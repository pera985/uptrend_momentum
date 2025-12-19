"""
Quick API test to diagnose ticker fetching issue
"""
import requests
import config

# Test 1: Basic tickers endpoint
print("=" * 70)
print("TEST 1: Fetching tickers from Polygon API")
print("=" * 70)

url = "https://api.polygon.io/v3/reference/tickers"
params = {
    'market': 'stocks',
    'active': True,
    'limit': 10,
    'apiKey': config.POLYGON_API_KEY
}

print(f"\nRequest URL: {url}")
print(f"Parameters: {params}")

try:
    response = requests.get(url, params=params)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys()}")

        if 'results' in data:
            print(f"Number of results: {len(data['results'])}")
            print(f"\nFirst 3 tickers:")
            for ticker in data['results'][:3]:
                print(f"  {ticker.get('ticker', 'N/A')} - {ticker.get('name', 'N/A')}")
        else:
            print("ERROR: No 'results' key in response")
            print(f"Response: {data}")
    else:
        print(f"ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"ERROR: {e}")

# Test 2: With exchange filter
print("\n" + "=" * 70)
print("TEST 2: Fetching with exchange filter (XNAS, XNYS)")
print("=" * 70)

params_with_exchange = {
    'market': 'stocks',
    'active': True,
    'limit': 10,
    'exchange': 'XNAS,XNYS',
    'apiKey': config.POLYGON_API_KEY
}

print(f"\nParameters: {params_with_exchange}")

try:
    response = requests.get(url, params=params_with_exchange)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if 'results' in data:
            print(f"Number of results: {len(data['results'])}")
            print(f"\nFirst 3 tickers:")
            for ticker in data['results'][:3]:
                print(f"  {ticker.get('ticker', 'N/A')} - {ticker.get('name', 'N/A')} - Exchange: {ticker.get('primary_exchange', 'N/A')}")
        else:
            print("ERROR: No 'results' key in response")
            print(f"Response: {data}")
    else:
        print(f"ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 70)
print("API Test Complete")
print("=" * 70)
