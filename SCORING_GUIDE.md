# Scoring System Guide

Complete reference for the 100-point scoring system used to evaluate established uptrends.

## Overview

The scoring system evaluates stocks across 6 categories, with each category contributing to a total score out of 100 points. Stocks are then binned into 4 tiers based on their total score.

## Total Score = 100 Points

| Category | Points | Purpose |
|----------|--------|---------|
| Trend Strength | 20 | How strong and sustainable is the trend? |
| Momentum Quality | 18 | Is momentum healthy or overextended? |
| Volume Profile | 17 | Is volume confirming the move? |
| Price Structure | 17 | Is support solid? How deep are pullbacks? |
| Risk/Reward Setup | 13 | Is this a good entry point? |
| **Trend Quality** | **15** | **How smooth vs choppy is the trend?** |

## 1. Trend Strength (20 Points)

Evaluates the strength and sustainability of the uptrend.

### ADX Level (8 points)

**What it measures**: Trend strength (not direction)

| ADX Value | Points | Interpretation |
|-----------|--------|----------------|
| > 40 | 8 pts | Very strong trend |
| 30-40 | 6 pts | Strong trend |
| 25-30 | 4 pts | Moderate trend |
| < 25 | 2 pts | Weak trend |

**Why it matters**: ADX > 40 indicates a powerful trend that's likely to continue. ADX < 25 suggests a weak or choppy trend that could reverse easily.

**Example**:
- Stock A: ADX = 45 → 8 points (very strong trend)
- Stock B: ADX = 28 → 4 points (moderate trend)

### MA20 Slope (8 points)

**What it measures**: Rate of trend acceleration (weekly % gain of MA20)

| Weekly % Gain | Points | Interpretation |
|---------------|--------|----------------|
| > 3% | 8 pts | Very steep uptrend |
| 1.5-3% | 6 pts | Moderate uptrend |
| 0.5-1.5% | 3 pts | Mild uptrend |
| < 0.5% | 0 pts | Flat/stalling |

**Calculation**:
```
MA20_slope = ((MA20_today - MA20_5_days_ago) / MA20_5_days_ago) * 100
```

**Why it matters**: A steep MA20 slope shows strong buying pressure. A flattening slope suggests momentum is fading.

**Example**:
- Stock A: MA20 up 4% in 5 days → 8 points (accelerating)
- Stock B: MA20 up 0.8% in 5 days → 3 points (slow)

### Days in Uptrend (4 points)

**What it measures**: How long the stock has been above MA20

| Days Above MA20 | Points | Interpretation |
|-----------------|--------|----------------|
| 20-60 days | 4 pts | Sweet spot - established but not late |
| 60-120 days | 2 pts | Mature trend - be cautious |
| > 120 days | 1 pt | Aging trend - nearing exhaustion |
| < 20 days | 0 pts | Too early for "established" |

**Why it matters**: The 20-60 day range balances between "established enough to trust" and "not so extended that it's about to reverse."

**Example**:
- Stock A: 35 days above MA20 → 4 points (perfect timing)
- Stock B: 150 days above MA20 → 1 point (late entry risk)

---

## 2. Momentum Quality (18 Points)

Evaluates whether momentum is healthy or overextended.

### RSI Position (9 points)

**What it measures**: Momentum strength and overbought/oversold levels

| RSI Range | Points | Interpretation |
|-----------|--------|----------------|
| 55-65 | 9 pts | Healthy momentum |
| 50-55 or 65-70 | 6 pts | Acceptable |
| 70-80 | 3 pts | Getting overbought |
| > 80 | 1 pt | Extremely overbought - high reversal risk |
| < 50 | 0 pts | Weak/negative momentum |

**Why it matters**: RSI 55-65 shows strong momentum without being overextended. RSI > 70 often precedes pullbacks.

**Example**:
- Stock A: RSI = 60 → 9 points (healthy)
- Stock B: RSI = 75 → 3 points (overbought, risky)

### MACD Histogram (9 points)

**What it measures**: Momentum trend (expanding, steady, or weakening)

| Histogram Behavior | Points | Interpretation |
|-------------------|--------|----------------|
| Expanding bullish (growing) | 9 pts | Accelerating momentum |
| Steady bullish (flat but positive) | 6 pts | Sustained momentum |
| Weakening but positive | 3 pts | Fading momentum |
| Negative | 0 pts | Bearish momentum |

**Calculation**: Compare current histogram to 5 days ago
- Growing: Current > 5-days-ago
- Steady: Roughly the same
- Weakening: Current < 5-days-ago but still positive

**Why it matters**: Expanding histogram shows increasing buying pressure. Weakening histogram suggests the trend may be losing steam.

**Example**:
- Stock A: Histogram = 0.50 (was 0.30) → 9 points (expanding)
- Stock B: Histogram = 0.20 (was 0.40) → 3 points (weakening)

---

## 3. Volume Profile (17 Points)

Evaluates whether volume is confirming the price movement.

### Volume Trend (9 points)

**What it measures**: Whether volume is higher on up days vs down days

| Behavior | Points | Interpretation |
|----------|--------|----------------|
| Up-day volume > down-day volume (by 20%+) | 9 pts | Strong confirmation |
| Up-day volume > down-day volume | 5 pts | Moderate confirmation |
| Down-day volume > up-day volume | 2 pts | Weak/distribution |

**Calculation**:
```
avg_up_day_volume = mean of volume on days when price rose
avg_down_day_volume = mean of volume on days when price fell

if avg_up_day_volume > avg_down_day_volume * 1.2:
    score = 9
```

**Why it matters**: Higher volume on up days confirms institutional buying. Higher volume on down days suggests distribution.

**Example**:
- Stock A: Up days avg 2M volume, Down days avg 1.5M → 9 points
- Stock B: Up days avg 1M volume, Down days avg 1.2M → 2 points

### Relative Volume (8 points)

**What it measures**: Current volume vs 50-day average

| Relative Volume | Points | Interpretation |
|-----------------|--------|----------------|
| > 1.5x average | 8 pts | Very high interest |
| 1.2-1.5x average | 6 pts | Above average |
| 0.8-1.2x average | 4 pts | Normal |
| < 0.8x average | 2 pts | Low interest |

**Calculation**:
```
relative_volume = current_volume / volume_MA_50
```

**Why it matters**: High relative volume indicates strong interest and liquidity.

**Example**:
- Stock A: Today's volume = 3M, MA50 = 2M → 1.5x → 8 points
- Stock B: Today's volume = 800K, MA50 = 1M → 0.8x → 2 points

---

## 4. Price Structure (17 Points)

Evaluates support quality and pullback behavior.

### Support Quality (9 points)

**What it measures**: How well MA20 acts as support

| Support Touches | Points | Interpretation |
|-----------------|--------|----------------|
| 3+ touches | 9 pts | Strong, tested support |
| 2 touches | 5 pts | Some support |
| 0-1 touches | 2 pts | Weak/untested support |

**Definition of "touch"**: Low comes within 2% of MA20

**Why it matters**: Multiple successful tests of MA20 support increase confidence for entries on pullbacks.

**Example**:
- Stock A: Touched MA20 4 times in 60 days, bounced each time → 9 points
- Stock B: Never pulled back to MA20 → 2 points (untested)

### Pullback Behavior (8 points)

**What it measures**: Average depth of pullbacks

| Average Pullback | Points | Interpretation |
|------------------|--------|----------------|
| < 10% | 8 pts | Shallow, controlled pullbacks |
| 10-15% | 5 pts | Moderate pullbacks |
| > 15% | 3 pts | Deep, volatile pullbacks |

**Calculation**:
```
For each local high in last 60 days:
    Find subsequent low
    pullback_pct = (high - low) / high * 100

average_pullback = mean of all pullbacks
```

**Why it matters**: Shallow pullbacks indicate strong buying support. Deep pullbacks increase risk.

**Example**:
- Stock A: Average pullback = 7% → 8 points (controlled)
- Stock B: Average pullback = 18% → 3 points (volatile)

---

## 5. Risk/Reward Setup (13 Points)

Evaluates whether this is a good entry point.

### Distance from MA20 (7 points)

**What it measures**: How far price is from MA20 support

| Distance | Points | Interpretation |
|----------|--------|----------------|
| Within 5% | 7 pts | Good entry - close to support |
| 5-10% | 4 pts | Acceptable |
| > 10% | 2 pts | Extended - poor risk/reward |

**Calculation**:
```
distance_pct = ((price - MA20) / MA20) * 100
```

**Why it matters**: Buying close to MA20 offers:
- Better risk/reward (tight stop loss)
- Higher probability of success (support nearby)

**Example**:
- Stock A: Price = $102, MA20 = $100 → 2% away → 7 points
- Stock B: Price = $115, MA20 = $100 → 15% away → 2 points

### Room to Resistance (6 points)

**What it measures**: Distance to recent high (resistance)

| Room to Resistance | Points | Interpretation |
|--------------------|--------|----------------|
| > 10% | 6 pts | Plenty of room to run |
| 5-10% | 4 pts | Some room |
| < 5% | 1 pt | Near resistance - likely stall |

**Calculation**:
```
recent_high = max(high of last 60 days)
room_pct = ((recent_high - current_price) / current_price) * 100
```

**Why it matters**: More room to resistance means better upside potential before hitting overhead supply.

**Example**:
- Stock A: Price = $100, Recent high = $115 → 15% room → 6 points
- Stock B: Price = $112, Recent high = $115 → 2.7% room → 1 point

---

## 6. Trend Quality (15 Points) - NEW

Evaluates how smooth vs choppy the trend is using three complementary metrics.

### Choppiness Index Score (6 points)

**What it measures**: Whether market is trending or consolidating

| Choppiness Index | Points | Interpretation |
|------------------|--------|----------------|
| < 40 | 6 pts | Very smooth, strong trending |
| 40-47 | 5 pts | Smooth trend |
| 47-53 | 3 pts | Neutral/mixed |
| 53-58 | 2 pts | Somewhat choppy |
| > 58 | 0 pts | Very choppy, ranging |

**Calculation**: Uses ATR sum divided by high-low range over 60 days
```
CI = 100 * log10(ATR_sum / high_low_range) / log10(n)
```

**Why it matters**: Lower CI indicates price is moving directionally (trending). Higher CI indicates price is oscillating (choppy/ranging). Smooth trends are easier to trade.

**Example**:
- Stock A: CI = 38 → 6 points (very smooth trend)
- Stock B: CI = 62 → 0 points (very choppy)

### Efficiency Ratio Score (5 points)

**What it measures**: How direct is the price movement (Kaufman Efficiency Ratio)

| Efficiency Ratio | Points | Interpretation |
|------------------|--------|----------------|
| > 0.50 | 5 pts | Very efficient/directional |
| 0.35-0.50 | 4 pts | Good efficiency |
| 0.20-0.35 | 2 pts | Moderate |
| < 0.20 | 0 pts | Choppy/inefficient |

**Calculation**:
```
direction = abs(close_today - close_60_days_ago)
volatility = sum of all daily |close - prev_close| moves
efficiency_ratio = direction / volatility
```

**Why it matters**: ER of 0.5 means 50% of daily moves contributed to the net change. Higher ER = less wasted movement.

**Example**:
- Stock A: ER = 0.55 → 5 points (directional)
- Stock B: ER = 0.15 → 0 points (choppy)

### Price Deviation Score (4 points)

**What it measures**: How closely price follows a smoothed trend line

| Average Deviation | Points | Interpretation |
|-------------------|--------|----------------|
| < 1% | 4 pts | Very tight to trend |
| 1-2% | 3 pts | Good adherence |
| 2-3% | 2 pts | Moderate deviation |
| > 3% | 0 pts | High deviation/choppy |

**Calculation**: Uses Gaussian-smoothed price line
```
smoothed = gaussian_filter(close_prices, sigma=5)
deviation_pct = avg(|price - smoothed| / smoothed * 100)
```

**Why it matters**: Lower deviation means price follows the trend smoothly without excessive whipsaws.

**Example**:
- Stock A: 0.8% average deviation → 4 points (smooth)
- Stock B: 3.5% average deviation → 0 points (choppy)

---

## Tier Classification

Total scores are binned into 4 tiers:

### Tier 1: Prime Movers (80-100 points)
**Characteristics**:
- All signals aligned
- Strong trend (ADX > 35)
- Healthy momentum (RSI 55-65)
- Volume confirming
- Solid support structure
- Good entry point
- **Smooth, non-choppy trend**

**Action**: Full position size, high confidence trades

**Example**: Score 85
- Trend: 18/20 (ADX=42, steep slope, 45 days in uptrend)
- Momentum: 15/18 (RSI=60, MACD expanding)
- Volume: 15/17 (strong confirmation)
- Structure: 14/17 (3 support touches, 8% avg pullback)
- Risk/Reward: 10/13 (3% from MA20, 12% to resistance)
- **Trend Quality: 13/15 (CI=42, ER=0.45, low deviation)**

### Tier 2: Solid Performers (60-79 points)
**Characteristics**:
- Good overall setup
- One or two minor weaknesses
- Still tradeable but less ideal

**Action**: Consider swing trades, half position size

**Example**: Score 68
- May have aging trend (100+ days)
- Or slightly overbought RSI (68)
- Or lower volume confirmation
- Or somewhat choppy trend quality

### Tier 3: Momentum Plays (40-59 points)
**Characteristics**:
- Mixed signals
- Higher risk
- Some uptrend qualities but questionable

**Action**: Short-term only, small positions, watch closely

**Example**: Score 52
- Weak ADX (26)
- Or poor risk/reward (12% from MA20)
- Or volume not confirming
- Or choppy trend (high CI)

### Tier 4: Watch List (< 40 points)
**Characteristics**:
- Failing most criteria
- Weak trend or losing momentum
- Questionable uptrend
- Very choppy price action

**Action**: Avoid or paper trade only

---

## Customizing Weights

You can adjust category weights in `config.py` to match your trading style:

### Conservative Trader (Value Structure, Risk/Reward & Smoothness)
```python
SCORING_WEIGHTS = {
    'trend_strength': 18,
    'momentum_quality': 10,    # Lower
    'volume_profile': 12,      # Lower
    'price_structure': 25,     # Higher
    'risk_reward': 15,         # Higher
    'trend_quality': 20        # Higher - prioritize smooth trends
}
```

### Aggressive Trader (Value Momentum)
```python
SCORING_WEIGHTS = {
    'trend_strength': 18,
    'momentum_quality': 30,    # Higher
    'volume_profile': 22,      # Higher
    'price_structure': 10,     # Lower
    'risk_reward': 10,         # Lower
    'trend_quality': 10        # Lower - accept choppier setups
}
```

### Balanced (Default)
```python
SCORING_WEIGHTS = {
    'trend_strength': 20,
    'momentum_quality': 18,
    'volume_profile': 17,
    'price_structure': 17,
    'risk_reward': 13,
    'trend_quality': 15
}
```

---

## Real-World Example

Let's score a fictional stock "XYZ":

### Data
- Price: $105
- MA20: $102 (slope: +2.5%/week)
- MA50: $95
- MA200: $80
- ADX: 38
- RSI: 62
- MACD Histogram: +0.45 (was +0.35 5 days ago)
- Days above MA20: 42
- Volume today: 2.1M (MA50: 1.4M)
- Up-day avg volume: 1.8M
- Down-day avg volume: 1.3M
- Support touches: 3 (in last 60 days)
- Average pullback: 9%
- Recent high: $118
- **Choppiness Index: 44**
- **Efficiency Ratio: 0.42**
- **Avg Deviation: 1.5%**

### Scoring

**1. Trend Strength: 16/20**
- ADX (38) → 6 pts (30-40 range)
- MA20 slope (2.5%) → 6 pts (1.5-3% range)
- Days (42) → 4 pts (20-60 range)
- **Total: 16 pts**

**2. Momentum Quality: 18/18**
- RSI (62) → 9 pts (55-65 range)
- MACD (expanding: 0.45 > 0.35) → 9 pts
- **Total: 18 pts**

**3. Volume Profile: 17/17**
- Volume trend (1.8M up / 1.3M down = 1.38x) → 9 pts
- Relative volume (2.1M / 1.4M = 1.5x) → 8 pts
- **Total: 17 pts**

**4. Price Structure: 14/17**
- Support (3 touches) → 9 pts
- Pullbacks (9% average) → 5 pts (< 10%)
- **Total: 14 pts**

**5. Risk/Reward: 11/13**
- Distance from MA20: (105-102)/102 = 2.9% → 7 pts
- Room to resistance: (118-105)/105 = 12.4% → 4 pts (>10%)
- **Total: 11 pts**

**6. Trend Quality: 12/15**
- Choppiness Index (44) → 5 pts (40-47 range, smooth)
- Efficiency Ratio (0.42) → 4 pts (0.35-0.50 range)
- Price Deviation (1.5%) → 3 pts (1-2% range)
- **Total: 12 pts**

### Final Score: 16 + 18 + 17 + 14 + 11 + 12 = **88/100**

**Tier: Tier 1 - Prime Mover**

**Interpretation**: Excellent setup
- Strong trend that's not aging
- Perfect momentum (RSI in sweet spot, MACD accelerating)
- Volume confirming
- Tested support
- Great entry point (close to MA20, plenty of room)
- **Smooth trend (low choppiness, good efficiency)**

**Action**: This is a high-confidence trade. Full position size appropriate.

---

## Tips for Using Scores

1. **Don't chase high scores alone**: A score of 95 extended 15% above MA20 is worse than a score of 82 at MA20.

2. **Watch score changes**: If a position drops from 88 to 62, that's a red flag even if still Tier 2.

3. **Context matters**: In bear markets, a score of 70 might be exceptional. In bull markets, hold out for 80+.

4. **Use with chart review**: Scores guide you, but always look at the chart.

5. **Track performance**: After 20-30 trades, see which score ranges work best for you.

6. **Trend Quality matters**: Two stocks with score 75 can behave very differently - the one with higher trend quality (lower choppiness) will be easier to trade.

---

## Correlation Between Scoring System and Strategies

### Core Principle

**Every stock gets scored 0-100** using the same 6 categories, but **strategies differ in how they USE and WEIGHT the scores**.

Strategies have **3 key differences**:
1. **Custom Scoring Weights** (changes what matters most)
2. **Filtering Criteria** (who gets scanned)
3. **Post-Scan Filtering** (who gets selected from results)

---

### How Each Strategy Uses Scoring

| Strategy | Scoring Weights | Filtering Focus | Post-Scan Selection |
|----------|----------------|-----------------|---------------------|
| **S1: Quick Test** | Default (20/18/17/17/13/15) | None special | Top scores |
| **S2: Full Market** | Default (20/18/17/17/13/15) | None - scans ALL | All tiers shown |
| **S3: Large Cap** | **Custom**: Trend ↑, Structure ↑ | Price >$50, Vol >2M | **Tier 1 only** |
| **S4: Aggressive** | **Custom**: Momentum ↑, Volume ↑ | Price >$10 | Momentum score >15 |
| **S5: Early Breakouts** | Default | Price >$10 | **Early uptrend signals** |
| **S6: Custom** | **Custom**: Structure ↑, Risk/Reward ↑ | Price >$15 | Top custom scores |
| **S7: Swing Trade** | Default | Price >$10 | **Distance from MA20 <3%** |
| **S8: Multi-Timeframe** | Default | Price >$20 | Top scores |
| **S9: Curated** | Default | Specific tickers | Top scores |
| **S10: Small Cap** | Default | MarketCap: $300M-$2B | Top scores |
| **S11: Medium Cap** | Default | MarketCap: $2B-$10B | Top scores |
| **S12: Micro Cap** | Default | MarketCap: $50M-$300M | Top scores, float limits |

---

### Default Scoring Weights (Strategies 1, 2, 5, 7-12)

```python
SCORING_WEIGHTS = {
    'trend_strength': 20,      # ADX, MA slope, days in uptrend
    'momentum_quality': 18,    # RSI, MACD
    'volume_profile': 17,      # Volume trend, relative volume
    'price_structure': 17,     # Support quality, pullback behavior
    'risk_reward': 13,         # Distance from MA20, room to resistance
    'trend_quality': 15        # Choppiness, efficiency, deviation
}
```

**Result**: Balanced evaluation - all factors matter with trend quality rewarding smooth trends

---

### Key Insights

#### 1. Scoring is Universal, Weighting is Strategic
- Every stock gets the same **raw component scores**
- **Weights change** what components matter most
- **Final score** reflects strategy's priorities

#### 2. Two-Stage Filtering
- **Pre-scan**: Price, volume, market cap filters
- **Scoring**: 0-100 evaluation with custom weights
- **Post-scan**: Tier filtering, specific criteria (distance from MA20, etc.)

#### 3. Trend Quality as a Differentiator
- Two stocks can have identical traditional scores but different trend quality
- **Lower choppiness = easier to trade, clearer signals**
- Smooth trends allow tighter stops and better risk management

---

## CSV Output Columns

The CSV export includes the following trend quality columns:

| Column | Description |
|--------|-------------|
| `trend_quality` | Score component (0-15 points) |
| `choppiness_index` | Raw CI value (38-62 typical range, lower = smoother) |
| `efficiency_ratio` | Raw ER value (0-1, higher = more efficient) |

---

## Summary

The 100-point system provides an objective way to:
- Identify highest-quality uptrends
- Compare stocks apples-to-apples
- Make consistent entry/exit decisions
- Track what works for your style
- **Customize weighting** to match your strategy
- **Prioritize smooth, tradeable trends** using trend quality metrics

Use it as a starting point, then customize weights and thresholds based on your trading results.
