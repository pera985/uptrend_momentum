# Uptrend Momentum Scanner

A comprehensive Python-based stock scanner that identifies uptrending stocks using technical analysis and scores them on a 100-point scale.

## Overview

This scanner helps position traders find high-quality stock uptrends by:

1. **Classifying** stocks into two categories:
   - **Early Uptrends**: Stocks just starting to break out (see detailed criteria below)
   - **Established Uptrends**: Stocks in sustained trends

2. **Scoring** established uptrends (0-100 points) across 6 categories:
   - Trend Strength (20 pts) - ADX, MA slope, trend duration
   - Momentum Quality (18 pts) - RSI, MACD
   - Volume Profile (17 pts) - Volume trends, relative volume
   - Price Structure (17 pts) - Support quality, pullback behavior
   - Risk/Reward Setup (13 pts) - Entry timing, room to resistance
   - Trend Quality (15 pts) - Choppiness Index, efficiency ratio, price smoothness

3. **Binning** stocks into 4 tiers:
   - **Tier 1**: Prime Movers (80-100) - Strongest uptrends
   - **Tier 2**: Solid Performers (60-79) - Good uptrends
   - **Tier 3**: Momentum Plays (40-59) - Decent but higher risk
   - **Tier 4**: Watch List (<40) - Questionable

4. **Dual-Output System** (NEW!):
   - **ALL scanned stocks** saved to `./output/all_scanned/` with scores/tiers
   - **Uptrend stocks only** saved to `./output/uptrends/`
   - Charts generated for both categories
   - Never miss insights - even stocks that don't meet uptrend criteria get scored

## Features

- ✅ Scans entire NYSE + NASDAQ markets
- ✅ 100-point scoring system with detailed breakdown
- ✅ Early breakout detection
- ✅ Customizable scoring weights
- ✅ Multiple pre-built scanning strategies
- ✅ Dual-output system - exports ALL scanned stocks + uptrends separately
- ✅ CSV export with full score breakdown
- ✅ Automatic chart generation for top stocks
- ✅ Position trading optimized (REST API only)
- ✅ Configurable filters (price, volume, market cap)
- ✅ **Free float tracking** - shares outstanding, float shares, liquidity metrics (NEW!)
- ✅ **Effective volume calculation** - volume as % of float for liquidity analysis (NEW!)
- ✅ **Liquidity filtering** - filter by minimum free float or max effective volume (NEW!)
- ✅ Daily/weekly scanning capability

## Early Uptrend Detection Criteria

The scanner identifies stocks in the **early stage of a breakout** using a scoring system with 6 key indicators. A stock needs **at least 5 out of 8 points** to qualify as an early uptrend.

### The 6 Indicators (8 points total):

1. **MA20 Cross (2 points)**
   - Price crosses above the 20-day moving average within the last 5 days
   - Indicates recent bullish momentum shift

2. **Volume Spike (2 points)**
   - Current volume is at least 1.5x the 50-day average volume
   - Confirms institutional interest and breakout conviction

3. **RSI Healthy Range (1 point)**
   - RSI between 50-70
   - Not overbought (avoiding late entries), but showing strength

4. **ADX Rising (1 point)**
   - ADX > 20 AND higher than it was 5 days ago
   - Trend strength is building (not yet established, but growing)

5. **MACD Bullish Crossover (1 point)**
   - MACD line crosses above signal line within the last 10 days
   - Momentum indicator turning bullish

6. **Breakout Above Recent High (1 point)**
   - Current price is above the highest high of the previous 20 days
   - Breaking through resistance

### What This Means:

Early uptrend stocks are in the **breakout stage** - just starting a new uptrend with:
- Recent bullish signals (MA cross, MACD cross)
- Strong volume confirmation
- Not yet overbought
- Building trend strength (ADX rising but not necessarily strong yet)

This helps catch stocks at the **beginning of a trend** rather than jumping in late.

### Contrast with Established Uptrends:

Established uptrends require:
- MAs properly stacked (close > MA20 > MA50 > MA200)
- At least 20 days above MA20
- ADX > 25 (strong trend)
- Making higher highs and higher lows

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. API Setup

Get a free API key from [Polygon.io](https://polygon.io/):

1. Sign up at https://polygon.io
2. Get your API key from dashboard
3. Add to `config.py`:

```python
POLYGON_API_KEY = "your_actual_api_key_here"
```

### 3. Run Your First Scan

```bash
# Quick test with 50 stocks
python example_usage.py 1
```

Results will be in `./output/` directory with CSV files, charts, and detailed breakdowns.

**Output includes:**
- All scanned stocks (with scores, even if not in uptrends)
- Uptrend-only stocks (meeting criteria)
- Technical analysis charts for both categories

## Example Strategies

The `example_usage.py` file includes 9 pre-built strategies:

```bash
python example_usage.py <number>
```

1. **Quick Test Scan** - Test with 50 stocks
2. **Full Market Scan** - Scan entire NYSE + NASDAQ
3. **Large Cap Quality** - High-quality large caps
4. **Aggressive Momentum** - High-momentum plays
5. **Early Breakouts** - Stocks just starting to trend
6. **Custom Scoring** - Custom weight example
7. **Swing Trade Setups** - Stocks near MA20 support
8. **Multi-Timeframe** - Concept demo
9. **Curated Watchlist** - Top 15 opportunities
10. **Small Cap Focus** - Market cap $300M-$2B
11. **Medium Cap Focus** - Market cap $2B-$10B
12. **Micro Cap Momentum** - Market cap $50M-$300M with tight float

### Strategy 2 vs Other Strategies: Scan Coverage Comparison

**Strategy 2 ("Full Market Scan")** is the **most comprehensive** strategy, while others are intentionally limited for speed:

| Aspect | Strategy 2 (Full Market) | Other Strategies (1, 3-12) |
|--------|-------------------------|---------------------------|
| **Stocks Scanned** | ~3,000-5,000 (ALL NYSE + NASDAQ) | ~50 (limited sample) |
| **Time Required** | 1-2 hours | 5-15 minutes |
| **`max_stocks` Parameter** | `None` (no limit) | `MAX_STOCKS_TO_SCAN = 50` |
| **API Calls** | ~6,000-10,000 | ~100-150 |
| **Best For** | Weekend deep-dive, comprehensive analysis | Daily quick checks, targeted scans |
| **Opportunities Found** | Complete market picture | Representative sample |

**Key Insight**: Strategy 2 is **NOT limiting** - it's the opposite. It provides **exhaustive market coverage** while other strategies sacrifice comprehensiveness for speed.

**From config.py:**
```python
MAX_STOCKS_TO_SCAN = 50   # Default max stocks for strategies 1,3-12
                          # Strategy 2 always scans all stocks
```

**When to Use Each:**
- **Strategy 2**: Weekend analysis, finding all opportunities across entire market
- **Other Strategies**: Daily monitoring with specific focus (large cap, momentum, swing setups, etc.)

## Scoring System Details

### Trend Strength (20 points)
- **ADX Level** (8 pts): Measures trend strength
  - ADX > 40: 8 pts (very strong)
  - ADX 30-40: 6 pts
  - ADX 25-30: 4 pts

- **MA20 Slope** (8 pts): Rate of trend acceleration
  - > 3% weekly gain: 8 pts
  - 1.5-3%: 6 pts
  - 0.5-1.5%: 3 pts

- **Days in Uptrend** (4 pts):
  - 20-60 days: 4 pts (sweet spot)
  - 60-120 days: 2 pts
  - > 120 days: 1 pt (aging trend)

### Momentum Quality (18 points)
- **RSI Position** (9 pts):
  - 55-65: 9 pts (healthy momentum)
  - 50-55 or 65-70: 6 pts
  - 70-80: 3 pts (getting extended)

- **MACD Histogram** (9 pts):
  - Expanding bullish: 9 pts
  - Steady bullish: 6 pts
  - Weakening but positive: 3 pts

### Volume Profile (17 points)
- **Volume Trend** (9 pts):
  - Higher volume on up days: 9 pts
  - Stable: 5 pts
  - Lower: 2 pts

- **Relative Volume** (8 pts):
  - > 1.5x average: 8 pts
  - 1.2-1.5x: 6 pts
  - 0.8-1.2x: 4 pts

### Price Structure (17 points)
- **Support Quality** (9 pts):
  - 3+ MA20 touches: 9 pts
  - 2 touches: 5 pts
  - Weak support: 2 pts

- **Pullback Behavior** (8 pts):
  - Shallow pullbacks (<10%): 8 pts
  - Moderate (10-15%): 5 pts
  - Deep (>15%): 3 pts

### Risk/Reward Setup (13 points)
- **Distance from MA20** (7 pts):
  - Within 5%: 7 pts (good entry)
  - 5-10%: 4 pts
  - > 10%: 2 pts (extended)

- **Room to Resistance** (6 pts):
  - > 10% room: 6 pts
  - 5-10%: 3 pts
  - < 5%: 1 pt

### Trend Quality (15 points) - NEW
- **Choppiness Index** (6 pts): Measures trend smoothness vs choppiness
  - CI < 40: 6 pts (very smooth trend)
  - CI 40-50: 4 pts (moderate)
  - CI 50-62: 2 pts (choppy)

- **Efficiency Ratio** (5 pts): Kaufman's directional efficiency
  - ER > 0.5: 5 pts (highly efficient)
  - ER 0.3-0.5: 3 pts (moderate)
  - ER < 0.3: 1 pt (inefficient)

- **Price Deviation** (4 pts): Smoothness around trend line
  - < 2% deviation: 4 pts (very smooth)
  - 2-4% deviation: 3 pts (moderate)
  - > 4% deviation: 1 pt (volatile)

## How Scoring Correlates with Strategies

**Every stock gets scored 0-100** using the same 6 categories, but **strategies differ in how they USE and WEIGHT the scores**.

### Three Key Differences Between Strategies:

1. **Custom Scoring Weights** - Changes what matters most (trend vs momentum vs structure)
2. **Filtering Criteria** - Pre-scan filters (price, volume, market cap)
3. **Post-Scan Filtering** - Additional selection criteria (tier, distance from MA20, etc.)

### How Strategies Customize Scoring:

| Strategy | Weight Customization | Key Focus |
|----------|---------------------|-----------|
| **S1, S2, S5, S7-S12** | Default (balanced) | General purpose |
| **S3: Large Cap** | Trend 30, Structure 25 (↑) | Quality & sustainability |
| **S4: Aggressive** | Momentum 35, Volume 25 (↑) | Strong moves, high risk |
| **S6: Custom** | Structure 25, Risk/Reward 20 (↑) | Entry timing & support |

### Example: Same Stock, Different Results

**Stock with score 72 (Tier 2):**
- **Strategy 2 (Full Market)**: ✅ INCLUDED (shows all tiers)
- **Strategy 3 (Large Cap)**: ❌ REJECTED (wants Tier 1 only)
- **Strategy 4 (Momentum)**: ✅ ACCEPTED (high momentum component)
- **Strategy 7 (Swing)**: ❌ REJECTED (8% from MA20, wants <3%)

### Default Weights (Most Strategies):
```python
SCORING_WEIGHTS = {
    'trend_strength': 20,      # Balanced
    'momentum_quality': 18,
    'volume_profile': 17,
    'price_structure': 17,
    'risk_reward': 13,
    'trend_quality': 15        # NEW - Choppiness Index & smoothness
}
```

### Strategy 3 Weights (Conservative):
```python
'trend_strength': 25,      # ↑ More weight on sustainability
'price_structure': 20,     # ↑ More weight on support
'trend_quality': 20,       # ↑ Prioritize smooth trends
'momentum_quality': 15     # ↓ Less weight (avoids chasing)
```

### Strategy 4 Weights (Aggressive):
```python
'momentum_quality': 30,    # ↑ Heavy emphasis on momentum
'volume_profile': 22,      # ↑ Volume confirmation critical
'trend_quality': 10,       # ↓ Less concerned with smoothness
'price_structure': 10      # ↓ Less concerned with support
```

**Key Insight**: The scoring system is the **universal language**, but each strategy **speaks it differently** based on trading objectives.

**See [SCORING_GUIDE.md](SCORING_GUIDE.md) for detailed correlation analysis and examples.**

## Configuration

Edit `config.py` to customize:

### Market Filters
```python
EXCHANGES = ['XNAS', 'XNYS']  # NYSE + NASDAQ
TICKER_TYPE = 'CS'            # Ticker type filter (see table below)
MIN_PRICE = 5.0               # Minimum stock price
MIN_VOLUME = 500000           # Minimum daily volume
MIN_MARKET_CAP = None         # Minimum market cap (None = no filter)
```

### Ticker Type Filter

The `ticker_type` parameter controls which types of securities are included in market scans.

| Type | Description | Included by Default |
|------|-------------|---------------------|
| `CS` | Common Stock | ✓ Yes |
| `ADRC` | American Depositary Receipt (ADR) - Foreign stocks | No |
| `ETF` | Exchange-Traded Fund | No |
| `ETN` | Exchange-Traded Note | No |
| `PFD` | Preferred Stock | No |
| `WARRANT` | Warrants | No |
| `UNIT` | Units (stock + warrant combo) | No |
| `RIGHT` | Rights | No |

**Why filter to `CS` only (recommended):**
- **Cleaner signals**: ETFs, preferred shares, and warrants don't behave like individual stocks
- **Faster scans**: ~5,000 tickers vs ~8,000+ without filter
- **More actionable**: Uptrend detection designed for company stocks, not derivatives

**To include ADRs** (foreign stocks like BABA, TSM):
```python
# In scan_market() call
results = scanner.scan_market(exchanges=['XNAS', 'XNYS'], ticker_type='CS')  # default
results = scanner.scan_market(exchanges=['XNAS', 'XNYS'], ticker_type=None)  # all types
```

**To include all types** (not recommended):
```python
ticker_type=None  # Fetches ETFs, ADRs, preferred shares, warrants, etc.
```

### Free Float & Liquidity Filters (NEW!)
```python
MIN_FREE_FLOAT_SHARES = None  # Minimum free float shares (None = no filter)
                               # Example: 10_000_000 = 10M shares minimum
MAX_FREE_FLOAT_SHARES = None   # Maximum free float shares (None = no filter)
                               # Example: 200_000_000 = 200M shares maximum
                               # Use for small/mid-cap focus strategies
MIN_FREE_FLOAT_PCT = None      # Minimum free float percentage (None = no filter)
                               # Example: 50.0 = 50% minimum free float
                               # Typical: Large cap >80%, Mid cap >70%, Small cap >50%
MAX_EFFECTIVE_VOLUME_PCT = None  # Max effective volume as % of float (None = no limit)
                                 # Example: 10.0 = Filter out if daily vol > 10% of float
```

**Free Float Explained:**
- **Shares Outstanding**: Total shares issued by the company
- **Float Shares**: Shares available for public trading (excludes insider/restricted shares)
- **Free Float %**: Percentage of shares in the float (estimated ~80% for most stocks)
- **Effective Volume**: Average daily volume as % of float (liquidity metric)
  - **Formula**: Effective Volume % = (Average Daily Volume / Float Shares) × 100
  - **Low values (0.5-2%)**: Normal, healthy liquidity - plenty of shares available
  - **Moderate values (2-5%)**: Active trading, good liquidity
  - **High values (5-10%)**: Very active trading, may indicate strong interest
  - **Very high values (>10%)**: Potential red flag - could indicate manipulation, pump & dump schemes, or extremely tight float with excessive turnover
  - **Example**: Stock with 50M float trading 2M shares/day = (2M / 50M) × 100 = 4.0% effective volume

**Typical Free Float by Market Cap:**
- **Large Cap (>$10B)**: 80-95% free float, 400M-2B+ shares
- **Mid Cap ($2B-$10B)**: 70-90% free float, 100M-400M shares
- **Small Cap ($300M-$2B)**: 50-80% free float, 20M-100M shares

**Why It Matters:**
- Higher free float = better liquidity, easier entry/exit
- Low free float + high volume = potential manipulation or squeeze setups
- Position sizing: avoid taking >1-2% of average daily volume
- Effective Volume helps assess if there's enough liquidity to enter/exit positions without moving the market

**Use Cases for MAX_FREE_FLOAT_SHARES:**

1. **Small-Cap Momentum Strategy**
   ```python
   MAX_FREE_FLOAT_SHARES = 100_000_000  # 100M shares max
   MIN_FREE_FLOAT_SHARES = 20_000_000   # 20M shares min
   # Focus: Small-cap stocks with 20M-100M float
   # Benefit: Higher volatility, momentum potential, avoid mega-caps
   ```

2. **Mid-Cap Quality Focus**
   ```python
   MAX_FREE_FLOAT_SHARES = 400_000_000  # 400M shares max
   MIN_FREE_FLOAT_SHARES = 100_000_000  # 100M shares min
   # Focus: Mid-cap range (typically $2B-$10B market cap)
   # Benefit: Balance of liquidity and growth potential
   ```

3. **Exclude Large Caps**
   ```python
   MAX_FREE_FLOAT_SHARES = 300_000_000  # 300M shares max
   # Focus: All stocks below large-cap threshold
   # Benefit: Filter out slow-moving mega-caps, focus on nimble companies
   ```

4. **Tight Float Momentum Plays**
   ```python
   MAX_FREE_FLOAT_SHARES = 50_000_000   # 50M shares max
   MIN_FREE_FLOAT_SHARES = 10_000_000   # 10M shares min
   # Focus: Low float stocks with momentum potential
   # Benefit: Potential for explosive moves, but requires careful position sizing
   # Warning: Higher risk due to lower liquidity
   ```

5. **Combined with Market Cap Filters**
   ```python
   MIN_MARKET_CAP = 500_000_000         # $500M minimum
   MAX_MARKET_CAP = 5_000_000_000       # $5B maximum
   MAX_FREE_FLOAT_SHARES = 200_000_000  # 200M shares max
   # Focus: Small to mid-cap range with specific float characteristics
   # Benefit: Precise market cap targeting
   ```

### Chart Generation Control
```python
NUM_CHARTS_TO_PLOT = 15                    # Charts for uptrends (early + established)
USE_NUM_CHARTS_FOR_ALL_SCANNED = False     # Chart limit for all_scanned stocks
                                           # False: Generate charts for ALL scanned stocks
                                           # True: Limit to NUM_CHARTS_TO_PLOT
```

**Behavior:**
- **Uptrend charts** (early + established): Always limited to `NUM_CHARTS_TO_PLOT` (default: 15)
- **All scanned charts**: Controlled by `USE_NUM_CHARTS_FOR_ALL_SCANNED`
  - `False` (default): Generates charts for **all** scanned stocks (respects `MAX_STOCKS_TO_SCAN`)
  - `True`: Limits to `NUM_CHARTS_TO_PLOT` (same as uptrends)

### Scoring Weights
```python
SCORING_WEIGHTS = {
    'trend_strength': 20,
    'momentum_quality': 18,
    'volume_profile': 17,
    'price_structure': 17,
    'risk_reward': 13,
    'trend_quality': 15        # NEW - Choppiness Index & smoothness
}
```

### Position Trading Rules
```python
ENTRY_RULES = {
    'min_tier': 1,                    # Only Tier 1
    'max_distance_from_ma20': 5.0,    # Within 5% of MA20
    'min_adx': 30,                    # Strong trend
    'rsi_range': (50, 65),            # Healthy RSI
}
```

## Usage Examples

### Basic Programmatic Usage

```python
from uptrend_scanner import UptrendScanner
import config

# Initialize scanner
scanner = UptrendScanner(config.POLYGON_API_KEY)

# Scan market
results = scanner.scan_market(
    exchanges=['XNAS', 'XNYS'],
    min_price=10.0,
    min_volume=500000,
    max_stocks=100  # Limit for testing
)

# Access results
print(f"Early uptrends: {len(results['early_uptrends'])}")
print(f"Established uptrends: {len(results['established_uptrends'])}")

# Filter Tier 1 stocks
tier_1 = [s for s in results['established_uptrends']
          if s['tier'] == 'Tier 1: Prime Movers']

# Export to CSV
scanner.export_to_csv(results)
```

### Custom Scoring Weights

```python
# Emphasize momentum over structure
custom_config = {
    'weights': {
        'trend_strength': 18,
        'momentum_quality': 28,  # Increased
        'volume_profile': 22,    # Increased
        'price_structure': 10,   # Decreased
        'risk_reward': 10,
        'trend_quality': 12      # Slightly reduced
    }
}

scanner = UptrendScanner(config.POLYGON_API_KEY, config=custom_config)
results = scanner.scan_market(exchanges=['XNAS'])
```

### Scan Single Stock

```python
# Analyze a specific ticker
result = scanner.scan_stock('AAPL')

if result:
    print(f"Ticker: {result['ticker']}")
    print(f"Price: ${result['current_price']:.2f}")

    if result['is_established_uptrend']:
        print(f"Score: {result['score']:.1f}/100")
        print(f"Tier: {result['tier']}")

        # Access detailed breakdown
        breakdown = result['score_breakdown']
        print(f"Trend Strength: {breakdown['trend_strength']:.1f}/20")
        print(f"Momentum: {breakdown['momentum_quality']:.1f}/18")
        print(f"Trend Quality: {breakdown['trend_quality']:.1f}/15")
```

## Output Files

Results are saved to `./output/` directory with the following structure:

```
output/
├── uptrends/                              # Uptrend-only results
│   ├── csv/                               # CSV files
│   │   ├── early/                         # Early uptrend CSVs (no timestamp in folder)
│   │   │   └── early_uptrends_Sx_TIMESTAMP.csv
│   │   └── established/                   # Established uptrend CSVs (no timestamp in folder)
│   │       └── established_uptrends_Sx_TIMESTAMP.csv
│   └── charts/                            # Technical charts for uptrends
│       ├── early/                         # Early uptrend charts (no timestamp in folder)
│       │   └── early_Sx_TIMESTAMP/        # Timestamped subfolder with strategy ID
│       │       └── TICKER_Sx_TIMESTAMP.png
│       └── established/                   # Established uptrend charts (no timestamp in folder)
│           └── established_Sx_TIMESTAMP/  # Timestamped subfolder with strategy ID
│               └── TICKER_Sx_TIMESTAMP.png
└── all_scanned/                           # All scanned stocks
    ├── csv/                               # CSV files (directly here, no subdirectory)
    │   └── all_scanned_Sx_TIMESTAMP.csv
    └── charts/                            # Charts for all scanned stocks
        └── charts_Sx_TIMESTAMP/           # Timestamped chart folder with strategy ID
            └── TICKER_Sx_TIMESTAMP.png
```

**Strategy Identifier Convention:**
- `Sx` = Strategy number (e.g., S1, S3, S12)
- `Sx-y-z` = Multiple combined strategies (e.g., S1-3-5)
- All outputs include strategy identifier for easy organization

### CSV Columns

**All CSV files now have identical 31-column structure:**

**Basic Information (14 columns):**
- `ticker` - Stock symbol
- `exchange` - Market exchange (NASDAQ or NYSE)
- `score` - Total score (0-100)
- `tier` - Assigned tier (Tier 1-4)
- `current_price` - Latest price
- `volatility_20` - 20-day annualized volatility (%)
- `volatility_50` - 50-day annualized volatility (%)
- `shares_outstanding` - Total outstanding shares
- `float_shares` - Free float shares (shares available for public trading)
- `free_float_pct` - Free float percentage (estimated ~80% for most stocks)
- `market_cap` - Market capitalization
- `effective_volume_pct` - Average volume as % of float (liquidity metric)
- `is_early_uptrend` - True/False
- `is_established_uptrend` - True/False

**Score Breakdown (6 columns):**
- `trend_strength` - Trend score component (0-20)
- `momentum_quality` - Momentum score component (0-18)
- `volume_profile` - Volume score component (0-17)
- `price_structure` - Structure score component (0-17)
- `risk_reward` - Risk/reward score component (0-13)
- `trend_quality` - Trend quality score component (0-15) - NEW

**Trend Quality Metrics (2 columns):**
- `choppiness_index` - Choppiness Index (38-62 range, lower = smoother trend)
- `efficiency_ratio` - Kaufman Efficiency Ratio (0-1, higher = more directional)

**Technical Indicators (9 columns):**
- `early_score` - Early uptrend score (0-8 points)
- `ma20_cross_recent` - MA20 cross within last 5 days (True/False)
- `volume_spike` - Volume > 1.5x average (True/False)
- `rsi_healthy` - RSI in 50-70 range (True/False)
- `rsi` - RSI indicator value
- `adx_rising` - ADX > 20 and increasing (True/False)
- `adx` - ADX indicator value
- `macd_cross_recent` - MACD bullish cross within 10 days (True/False)
- `breakout` - Breakout above 20-day high (True/False)

**Note:** All three CSV files (early_uptrends, established_uptrends, all_scanned) use this same structure for consistency.

### Chart Output

**Enhanced Vertical Layout** - Each chart includes:

1. **Price Chart** - Main price action with:
   - Line chart with MA20, MA50, MA200
   - Bollinger Bands (filled area)
   - Dual y-axis (price on both left and right)
   - Earnings markers ('E' in yellow circles on earnings report dates)
   - 4 minor ticks on x-axis
   - Timestamp (generation date/time) in lower right corner
   - Larger, more visible grid (alpha=0.6)
   - Major/minor ticks pointing inside

2. **Volume Chart** - Directly below price with:
   - Color-coded bars (green=up day, red=down day)
   - 50-day volume moving average
   - EMA5 and EMA20 of close price (on secondary y-axis)
   - Combined legend showing all indicators
   - Enhanced grid visibility
   - No date labels (cleaner layout)

3. **Volatility Chart** (NEW) - Historical volatility:
   - 20-day annualized volatility line (darkred)
   - Reference lines at 30% (moderate) and 50% (high)
   - Compact layout with smaller y-axis labels
   - Enhanced grid visibility

4. **RSI Chart** - Relative Strength Index:
   - Overbought (70) and Oversold (30) levels
   - Compact layout with smaller y-axis labels
   - Enhanced grid visibility

5. **MACD Chart** - Momentum indicator:
   - MACD line, Signal line, and Histogram
   - Zero line reference
   - Compact layout with smaller y-axis labels
   - Enhanced grid visibility

6. **ADX Chart** - Trend strength indicator:
   - Strong trend (25) and Very Strong (40) levels
   - **Only chart showing date labels** (bottom of layout)
   - 3 minor ticks on x-axis
   - Smaller y-axis labels, rotated date labels
   - Major/minor ticks crossing the x-axis (inout direction)

7. **Analysis Summary Panel** - Multi-column score display:
   - **Row 1:** Price, Score/100, Tier, RSI, ADX, Volatility(20d), Float (millions)
   - **Row 2:** Trend Strength/20, Momentum Quality/18, Volume Profile/17
   - **Row 3:** Price Structure/17, Risk/Reward/13, Trend Quality/15
   - **Row 4:** Days Above SMA20, Effective Volume %, Choppiness Index, Efficiency Ratio
   - Wider panel layout (170 chars) to accommodate all metrics
   - Easy-to-read score breakdown with max values shown
   - Free float and liquidity metrics for position sizing
   - Trend quality metrics (Choppiness Index, Efficiency Ratio) for trend smoothness evaluation

**Chart Features:**
- Vertical stack layout with 7 panels (no spacing, hspace=0.0)
- All charts share synchronized x-axis (time alignment)
- Enhanced grid visibility (alpha=0.6) on all panels
- Adjusted height ratios to fit all panels: Price (2.5), Volume (0.7), Volatility (0.7), RSI (0.7), MACD (0.7), ADX (0.7), Summary (1.0)
- Professional wheat-colored summary panel background
- 16x14 inch figure size for optimal detail
- 150 DPI for crisp output

## Position Trading Workflow

Based on the original chat discussion, here's the recommended workflow for position trading:

### Daily Routine

**Morning (Pre-Market)**
```bash
# Review results from previous evening scan
# Check watchlist for entry opportunities
# Set limit orders for new positions
```

**Evening (After Close - 6:00 PM)**
```bash
# Run daily scan
python example_usage.py 9  # Curated watchlist

# Review top 15 stocks
# Update positions (check if scores dropped)
# Prepare for tomorrow
```

### Entry Criteria
- ✅ Tier 1 only (score ≥ 80)
- ✅ Within 5% of MA20 (good risk/reward)
- ✅ ADX > 30 (strong trend)
- ✅ RSI 50-65 (not overbought)
- ✅ In uptrend 20-60 days (sweet spot)

### Exit Criteria
- ❌ Score drops below 60 (Tier 2 → Tier 3)
- ❌ Price closes below MA20
- ❌ ADX drops below 25
- ❌ RSI drops below 40
- ✅ Profit target hit (+20%, +30%, +50%)

## Why REST (Not WebSocket)?

For position trading:
- ✅ Daily timeframe analysis - trends don't change intraday
- ✅ Simpler implementation - already working
- ✅ Lower costs - $29/month vs $79/month
- ✅ Sufficient for EOD decisions - no need for real-time

WebSocket is only needed for:
- Day trading
- Real-time alerts during market hours
- Sub-minute analysis

## API Costs

### Free Tier
- 5 requests/minute
- Good for: Testing, small watchlists

### Starter ($29/month)
- ~400K requests/day
- Good for: Full market scans, position trading

### Developer ($79/month)
- Unlimited REST + WebSocket
- Good for: Real-time monitoring, day trading

## Technical Requirements

- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.23.0
- requests >= 2.28.0

## Project Structure

```
uptrend_momentum/
├── uptrend_scanner.py           # Main scanner engine
├── config.py                    # Configuration
├── example_usage.py             # 9 strategy examples
├── run_multiple_strategies.py   # Run multiple strategies in sequence
├── backtest_integration.py      # Walk-forward backtesting
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── QUICK_START.md              # 5-minute guide
├── SCORING_GUIDE.md            # Detailed scoring docs
├── input_files/                 # Input ticker lists for backtesting
│   └── watchlist.txt            # Sample watchlist
└── output/                      # Results directory (auto-created)
    ├── uptrends/                # Uptrend-only results
    │   ├── csv/                # Early/established uptrend CSVs
    │   └── charts/             # Charts for uptrend stocks
    │       ├── established_TIMESTAMP/  # Established uptrend charts
    │       └── early_TIMESTAMP/        # Early uptrend charts
    └── all_scanned/            # All scanned stocks
        ├── csv/                # Complete scan results
        └── charts/             # Charts for all stocks
            └── charts_TIMESTAMP/  # Timestamped chart folder
```

## Limitations

- Requires Polygon.io API key (free tier available)
- Rate limits based on API tier
- Daily data only (intraday requires WebSocket upgrade)
- US markets only (NYSE, NASDAQ)

## Future Enhancements

See `PROJECT_ROADMAP.md` for planned features:
- Multi-timeframe analysis
- Weekly trend confirmation
- Sector rotation analysis
- Earnings calendar integration
- Real-time WebSocket monitoring
- Java port for HFT systems

## Troubleshooting

### API Key Error
```
⚠️  ERROR: Please set your Polygon.io API key in config.py
```
**Solution**: Edit `config.py` and replace `YOUR_API_KEY_HERE` with your actual key.

### Rate Limit Errors
```
Error 429: Too Many Requests
```
**Solution**: Adjust `MAX_REQUESTS_PER_MINUTE` in `config.py` or upgrade API tier.

### No Results
```
Found 0 early uptrends, 0 established uptrends
```
**Solution**:
- Check market conditions (bearish markets = fewer uptrends)
- Lower `min_price` or `min_volume` filters
- Increase `max_stocks` limit
- Verify API key is working

## Support

For issues or questions:
1. Check the documentation files (QUICK_START.md, SCORING_GUIDE.md)
2. Review example strategies in `example_usage.py`
3. Check Polygon.io API status: https://polygon.io/status

## License

This project is for personal use. Polygon.io API usage subject to their terms of service.

## Credits

Based on the Claude chat discussion for position trading uptrend identification.
Uses Polygon.io (Massive.com) for stock market data.
