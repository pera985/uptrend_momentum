"""
Test different exchange filtering approaches
"""
import requests
import config

url = "https://api.polygon.io/v3/reference/tickers"

# Test different parameter combinations
tests = [
    {"name": "No exchange filter", "params": {'market': 'stocks', 'active': True, 'limit': 5, 'apiKey': config.POLYGON_API_KEY}},
    {"name": "Exchange = XNAS", "params": {'market': 'stocks', 'active': True, 'limit': 5, 'exchange': 'XNAS', 'apiKey': config.POLYGON_API_KEY}},
    {"name": "Exchange = XNYS", "params": {'market': 'stocks', 'active': True, 'limit': 5, 'exchange': 'XNYS', 'apiKey': config.POLYGON_API_KEY}},
    {"name": "Exchange = XNAS,XNYS", "params": {'market': 'stocks', 'active': True, 'limit': 5, 'exchange': 'XNAS,XNYS', 'apiKey': config.POLYGON_API_KEY}},
    {"name": "primary_exchange = XNAS", "params": {'market': 'stocks', 'active': True, 'limit': 5, 'primary_exchange': 'XNAS', 'apiKey': config.POLYGON_API_KEY}},
]

for test in tests:
    print(f"\n{'='*70}")
    print(f"TEST: {test['name']}")
    print(f"{'='*70}")

    try:
        response = requests.get(url, params=test['params'])

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Results: {len(results)}")

            if results:
                for ticker in results[:2]:
                    print(f"  {ticker.get('ticker')} - Exchange: {ticker.get('primary_exchange', 'N/A')}")
        else:
            print(f"ERROR: Status {response.status_code}")
            print(response.text[:200])

    except Exception as e:
        print(f"ERROR: {e}")
