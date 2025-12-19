# Quick Start Guide

Get up and running with the Uptrend Momentum Scanner in 5 minutes.

## Step 1: Install Dependencies (1 minute)

```bash
cd uptrend_momentum
pip install -r requirements.txt
```

This installs:
- pandas (data manipulation)
- numpy (numerical computing)
- requests (API calls)

## Step 2: Get API Key (2 minutes)

1. Go to https://polygon.io
2. Sign up for free account
3. Navigate to dashboard → API Keys
4. Copy your API key

## Step 3: Configure (1 minute)

Edit `config.py`:

```python
# Line 11: Replace with your actual API key
POLYGON_API_KEY = "your_actual_api_key_here"
```

Save the file.

## Step 4: Run First Scan (1 minute)

```bash
# Test with 50 stocks
python example_usage.py 1
```

You should see:
```
======================================================================
STRATEGY 1: Quick Test Scan (50 stocks)
======================================================================
Fetched 50 tickers
Scanning 50 stocks...
Progress: 50/50

Results:
Early uptrends: X
Established uptrends: Y

Top 5 Established Uptrends:
  AAPL: Score 85.5 - Tier 1: Prime Movers
  MSFT: Score 82.3 - Tier 1: Prime Movers
  ...
```

## Step 5: Check Results

Results are in `./output/` directory:

```bash
ls output/
```

You should see:
- `early_uptrends_TIMESTAMP.csv`
- `established_uptrends_TIMESTAMP.csv`

Open the CSV files in Excel or any spreadsheet app.

## Next Steps

### Try Other Strategies

```bash
# Full market scan (takes 1-2 hours)
python example_usage.py 2

# Large cap quality focus
python example_usage.py 3

# Early breakouts
python example_usage.py 5

# Generate curated watchlist
python example_usage.py 9
```

### Customize Configuration

Edit `config.py` to adjust:
- Minimum price (`MIN_PRICE = 10.0`)
- Minimum volume (`MIN_VOLUME = 1000000`)
- Scoring weights (`SCORING_WEIGHTS`)
- Entry/exit rules (`ENTRY_RULES`, `EXIT_RULES`)

### Programmatic Usage

```python
from uptrend_scanner import UptrendScanner
import config

scanner = UptrendScanner(config.POLYGON_API_KEY)
results = scanner.scan_market(
    exchanges=['XNAS', 'XNYS'],
    ticker_type='CS',  # Common stock only (default). Use None for all types.
    min_price=10.0,
    max_stocks=100
)

# Access results
for stock in results['established_uptrends'][:10]:
    print(f"{stock['ticker']}: {stock['score']:.1f}")
```

### Set Up Daily Scans

For position trading, run this daily after market close (6 PM):

```bash
# Linux/Mac: Add to crontab
0 18 * * 1-5 cd /path/to/uptrend_momentum && python example_usage.py 9

# Windows: Use Task Scheduler
# Schedule python example_usage.py 9 at 6:00 PM weekdays
```

## Common Issues

### API Key Error
```
⚠️  ERROR: Please set your Polygon.io API key in config.py
```
**Fix**: Edit `config.py` and add your actual API key.

### Import Error
```
ModuleNotFoundError: No module named 'pandas'
```
**Fix**: Run `pip install -r requirements.txt`

### No Results
```
Found 0 uptrends
```
**Possible causes**:
- Bearish market (fewer uptrends)
- Filters too strict (lower MIN_PRICE or MIN_VOLUME)
- Test limit too small (increase max_stocks)

## Understanding the Output

### Score Interpretation
- **80-100**: Tier 1 (Prime Movers) - Best opportunities
- **60-79**: Tier 2 (Solid Performers) - Good trades
- **40-59**: Tier 3 (Momentum Plays) - Higher risk
- **<40**: Tier 4 (Watch List) - Avoid

### Scoring Categories (100 Points Total)
The scanner uses 6 categories to evaluate stocks:
- **Trend Strength** (20 pts) - ADX, MA slope, days in uptrend
- **Momentum Quality** (18 pts) - RSI position, MACD histogram
- **Volume Profile** (17 pts) - Volume trends, relative volume
- **Price Structure** (17 pts) - Support quality, pullback behavior
- **Risk/Reward** (13 pts) - Distance from MA20, room to resistance
- **Trend Quality** (15 pts) - Choppiness Index, efficiency ratio, price smoothness

### Position Trading Entry Checklist
For each stock in your watchlist:
- ✅ Score ≥ 80 (Tier 1)
- ✅ Within 5% of MA20 (good entry point)
- ✅ ADX > 30 (strong trend)
- ✅ RSI 50-65 (healthy, not overbought)
- ✅ 20-60 days in uptrend (sweet spot)

### Exit Signals
Monitor your positions daily. Exit when:
- ❌ Score drops below 60
- ❌ Price closes below MA20
- ❌ ADX drops below 25
- ❌ RSI drops below 40

## Recommended Daily Workflow

**Evening (6:00 PM)** - After market close:
```bash
# 1. Run curated watchlist generator
python example_usage.py 9

# 2. Review top 15 stocks in output/watchlist_tickers.txt

# 3. Check existing positions (manually or via script)

# 4. Prepare limit orders for tomorrow
```

**Morning (Before Open)**:
- Review watchlist from previous evening
- Place limit orders for new entries
- Set stop losses for existing positions

## Tips for Success

1. **Start Small**: Use Strategy 1 to test before full market scans
2. **Position Size**: Full position for score 85-100, half for 80-84
3. **Diversify**: Hold 5-10 positions, not all in one sector
4. **Be Patient**: Wait for high-quality setups (Tier 1 near MA20)
5. **Respect Exits**: Follow the exit rules strictly

## Learning the System

1. **Day 1**: Run test scan, understand the output
2. **Day 2**: Try different strategies (1-9)
3. **Day 3**: Customize config.py for your style
4. **Day 4**: Paper trade for 2 weeks
5. **Day 5+**: Go live with small position sizes

## Resources

- **README.md**: Full documentation
- **SCORING_GUIDE.md**: Detailed scoring explanation
- **config.py**: All configuration options
- **example_usage.py**: 9 strategy examples

## What's Next?

Once comfortable with the basics:

1. **Backtest**: Export historical results and validate
2. **Optimize**: Adjust scoring weights for your style
3. **Automate**: Set up daily cron jobs
4. **Monitor**: Track performance of Tier 1 picks
5. **Refine**: Iterate based on results

Good luck with your trading! 🚀
