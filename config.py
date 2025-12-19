"""
Configuration file for Uptrend Momentum Scanner
"""

# Variables defined in this config file are used by the example scripts as default
# values, unless overridden by strategy-specific parameters defined below.

# ==============================================================================
# API Configuration
# ==============================================================================

# Polygon.io (Massive.com) API Key
# Get your key at: https://polygon.io/dashboard/api-keys
POLYGON_API_KEY = "rOkOTaxTpvpscYpFv4noWecL2hyljcS6"  # Replace with your actual API key

# API Rate Limiting
# Free tier: 5 requests/minute
# Starter ($29/mo): ~400K requests/day
# Advanced/Developer: Unlimited REST + WebSocket
MAX_REQUESTS_PER_MINUTE = None  # None = Unlimited (for Advanced membership)


# ==============================================================================
# Market Filters
# ==============================================================================

# Exchanges to scan
# XNAS = NASDAQ, XNYS = NYSE
# None = all exchanges
EXCHANGES = ['XNAS', 'XNYS']  # or None for all

# Stock Filters
MIN_PRICE = 5.0  # Minimum stock price (avoid penny stocks)
MAX_PRICE = None  # Maximum price (None = no limit)
MIN_VOLUME = 500000  # Minimum average daily volume (liquidity filter)
MIN_MARKET_CAP = None  # Minimum market cap (None = no filter)
MAX_MARKET_CAP = None  # Maximum market cap (None = no limit)

# Liquidity / Free Float Filters (NEW)
MIN_FREE_FLOAT_SHARES = None  # Minimum free float shares (None = no filter)
                               # Example: 10_000_000 = 10M shares minimum
MAX_FREE_FLOAT_SHARES = None   # Maximum free float shares (None = no filter)
                               # Example: 200_000_000 = 200M shares maximum
                               # Use for small/mid-cap focus strategies
MIN_FREE_FLOAT_PCT = None      # Minimum free float percentage (None = no filter)
                               # Example: 50.0 = 50% minimum free float
                               # Typical ranges: Large cap >80%, Mid cap >70%, Small cap >50%
MAX_EFFECTIVE_VOLUME_PCT = None  # Maximum effective volume as % of float (None = no limit)
                                 # Example: 10.0 = Filter out if daily vol > 10% of float
                                 # High values may indicate manipulation or thin float

# ==============================================================================
# Volatility-Based Scoring & Filtering (3 OPTIONS - Use individually or together)
# ==============================================================================

# OPTION 1: Volatility Tier Modifier (Recommended for Position Trading)
# Adjusts tier based on volatility after initial scoring
# Example: Tier 1 stock with high volatility → downgraded to Tier 2
ENABLE_VOLATILITY_TIER_MODIFIER = False  # Set to True to enable tier adjustments
VOLATILITY_TIER_THRESHOLDS = {
    'low': 25,       # < 25% volatility = low (smooth trends)
    'moderate': 40,  # 25-40% volatility = moderate
    'high': 40       # > 40% volatility = high (choppy/risky)
}
# Tier adjustment rules (applied if ENABLE_VOLATILITY_TIER_MODIFIER = True):
# - Tier 1 + Low Vol = Tier 1 (no change)
# - Tier 1 + High Vol = Tier 2 (downgrade)
# - Tier 2 + Low Vol = Tier 1 (upgrade)
# - Tier 2 + High Vol = Tier 2 (no change)
# - Tier 3 + Low Vol = Tier 2 (upgrade)
# - Tier 3 + High Vol = Tier 3 (no change)

# OPTION 2: Volatility in Risk/Reward Scoring
# Adds volatility as a component within the Risk/Reward category
ENABLE_VOLATILITY_IN_SCORING = False  # Set to True to add 5pts volatility to Risk/Reward
# If enabled:
# - Risk/Reward category expands from 15 to 20 points
# - Entry timing: 10 pts (unchanged)
# - Room to resistance: 5 pts (unchanged)
# - Volatility quality: 5 pts (NEW)
#   - Low vol (15-25%): 5 pts
#   - Moderate vol (25-40%): 3 pts
#   - High vol (>40%): 0 pts

# OPTION 3: Hard Volatility Filters by Tier
# Filters out stocks that exceed volatility thresholds for their tier
# More aggressive than Option 1 (removes vs downgrades)
ENABLE_VOLATILITY_FILTERS = False  # Set to True to enable hard filters
MAX_VOLATILITY_FOR_TIER_1 = 35   # Tier 1 stocks must have <35% volatility
MAX_VOLATILITY_FOR_TIER_2 = 50   # Tier 2 stocks must have <50% volatility
# Note: Tier 3 and Tier 4 have no volatility limits

# ==============================================================================
# Testing / Scanning Limits
MAX_STOCKS_TO_SCAN = None   # Default max stocks for strategies 1,3-8 (None = scan all)
                          # Strategy 2 always scans all stocks
MAX_STOCKS_STRATEGY_9 = None  # Max stocks to scan for Strategy 9 (None = scan all)
NUM_CHARTS_TO_PLOT = 200   # Number of charts to generate (applies to all strategies 1-9)

# Chart Generation Control for All Scanned Stocks
# LEGACY VARIABLE - kept for backward compatibility
# With the new sector-based chart organization (plot_watchlist_by_sector), this is no longer used.
# The new system uses:
#   - NUM_CHARTS_TO_PLOT: Controls charts in the 'all/' folder
#   - CHARTS_PER_SECTOR_ALL_SCANNED (ZZ): Controls charts per sector folder
USE_NUM_CHARTS_FOR_ALL_SCANNED = True  # Legacy - not used in new sector-based chart generation

# Charts per sector configuration (for sector-based chart organization)
CHARTS_PER_SECTOR_ALL_SCANNED = 20    # ZZ - top stocks per sector in all_scanned folders
CHARTS_PER_SECTOR_EARLY = 10          # YY - top stocks per sector in early uptrend folders
CHARTS_PER_SECTOR_ESTABLISHED = 10    # XX - top stocks per sector in established uptrend folders

# FULL MARKET SCAN NOTE:
# ----------------------
# By setting MAX_STOCKS_TO_SCAN = None and MAX_STOCKS_STRATEGY_9 = None (as above),
# ALL strategies will process through the entire NYSE + NASDAQ market (~3,000-5,000 stocks).
# This is the same behavior as Strategy 2.
#
# Time implications when running multiple strategies with None:
#   - Each strategy: ~1-2 hours
#   - run_multiple_strategies.py 4 5 8: ~3-6 hours total
#   - All 12 strategies: ~12-24 hours
#
# To limit scanning (faster runs), set these to a number:
#   MAX_STOCKS_TO_SCAN = 50      # Strategies 1, 3-8, 10-12 scan only 50 stocks
#   MAX_STOCKS_STRATEGY_9 = 500  # Strategy 9 scans 500 stocks


# ==============================================================================
# Strategy-Specific Parameters
# ==============================================================================
#
# PRIORITY HIERARCHY:
# -------------------
# 1. Strategy-specific parameters (HIGHEST PRIORITY) - Override global defaults
#    - Defined in STRATEGY_X dictionaries below
#    - Example: STRATEGY_3['min_price'] = 50.0 overrides MIN_PRICE = 5.0
#
# 2. Global Stock Filters (FALLBACK) - Used when strategy doesn't specify value
#    - Defined in "Stock Filters" section above
#    - Example: Strategy 2 uses MIN_PRICE and MIN_VOLUME as defaults
#
# This design allows reasonable global defaults while letting individual
# strategies customize their filtering criteria.

# Strategy 1: Quick Test Scan (limited to 50 stocks for fast testing)
STRATEGY_1 = {
    'min_price': 5.0,
    'min_volume': 500000,
    'max_stocks': 50,  # Limit for quick testing
}

# Strategy 3: Large Cap Quality
STRATEGY_3 = {
    'min_price': 50.0,
    'min_volume': 2000000,
}

# Strategy 4: Aggressive Momentum
STRATEGY_4 = {
    'min_price': 10.0,
    'min_volume': 1000000,
}

# Strategy 5: Early Breakouts
STRATEGY_5 = {
    'min_price': 10.0,
    'min_volume': 1000000,
}

# Strategy 6: Custom Scoring
STRATEGY_6 = {
    'min_price': 15.0,
    'min_volume': 500000,
}

# Strategy 7: Swing Trade Setups
STRATEGY_7 = {
    'min_price': 10.0,
    'min_volume': 1000000,
    'max_distance_from_ma20': 3.0,  # Percentage (%) distance from MA20 for filtering near support
}

# Strategy 8: Multi-Timeframe Concept
STRATEGY_8 = {
    'min_price': 20.0,
    'min_volume': 1000000,
}

# Strategy 9: Curated Watchlist
STRATEGY_9 = {
    'min_price': 15.0,
    'min_volume': 1000000,
}

# Strategy 10: Small Cap Focus
STRATEGY_10 = {
    'min_price': 5.0,
    'min_volume': 500000,
    'min_market_cap': 300_000_000,    # $300M minimum
    'max_market_cap': 2_000_000_000,  # $2B maximum
}

# Strategy 11: Medium Cap Focus
STRATEGY_11 = {
    'min_price': 10.0,
    'min_volume': 1000000,
    'min_market_cap': 2_000_000_000,   # $2B minimum
    'max_market_cap': 10_000_000_000,  # $10B maximum
}

# Strategy 12: Micro Cap Momentum
STRATEGY_12 = {
    'min_price': 3.0,
    'min_volume': 250000,              # Lower volume requirement for micro caps
    'min_market_cap': 50_000_000,      # $50M minimum
    'max_market_cap': 300_000_000,     # $300M maximum
    'min_free_float_shares': 5_000_000,   # 5M shares minimum (ensure some liquidity)
    'max_free_float_shares': 100_000_000, # 100M shares maximum (tight float focus)
}


# ==============================================================================
# Scoring System Weights
# ==============================================================================

# Custom weights for scoring (default: out of 100 points)
SCORING_WEIGHTS = {
    'trend_strength': 25,     # ADX, MA slope, days in uptrend
    'momentum_quality': 20,   # RSI, MACD
    'volume_profile': 20,     # Volume trend, relative volume
    'price_structure': 20,    # Support quality, pullback behavior
    'risk_reward': 15         # Distance from MA20, room to resistance
}

# Tier Thresholds
TIER_THRESHOLDS = {
    'tier_1': 80,  # Prime Movers
    'tier_2': 60,  # Solid Performers
    'tier_3': 40,  # Momentum Plays
    # < 40 = Watch List
}


# ==============================================================================
# Early Uptrend Detection
# ==============================================================================

# Minimum score for early uptrend classification (out of 8)
EARLY_UPTREND_MIN_SCORE = 5

# Lookback periods for early detection
EARLY_MA_CROSS_DAYS = 5      # MA20 cross within this many days
EARLY_MACD_CROSS_DAYS = 10   # MACD cross within this many days
EARLY_VOLUME_MULTIPLIER = 1.5  # Volume spike threshold (1.5x = 150%)


# ==============================================================================
# Established Uptrend Detection
# ==============================================================================

# Minimum days above MA20 for established uptrend
ESTABLISHED_MIN_DAYS = 20

# ADX threshold for strong trend
ESTABLISHED_ADX_THRESHOLD = 25


# ==============================================================================
# Technical Indicator Parameters
# ==============================================================================

# Moving Averages
MA_PERIODS = {
    'short': 20,
    'medium': 50,
    'long': 200
}

# RSI
RSI_PERIOD = 14
RSI_HEALTHY_RANGE = (50, 70)  # Ideal RSI range for uptrends

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# ADX
ADX_PERIOD = 14
ADX_STRONG_THRESHOLD = 25
ADX_VERY_STRONG_THRESHOLD = 40

# Bollinger Bands
BB_PERIOD = 20
BB_STD_DEV = 2.0

# Volume
VOLUME_MA_PERIOD = 50


# ==============================================================================
# Position Trading Rules
# ==============================================================================

# Entry Rules
ENTRY_RULES = {
    'min_tier': 1,                    # Only enter Tier 1 stocks
    'max_distance_from_ma20': 5.0,    # Max % away from MA20 (risk/reward)
    'min_adx': 30,                    # Minimum ADX for entry
    'rsi_range': (50, 65),           # RSI must be in this range
    'min_days_in_uptrend': 20,       # Minimum days in uptrend
    'max_days_in_uptrend': 60,       # Maximum days (avoid late entries)
}

# Exit Rules
EXIT_RULES = {
    'score_drop_threshold': 60,       # Exit if score drops below this
    'stop_loss_below_ma20': True,     # Exit if price closes below MA20
    'adx_drop_threshold': 25,         # Exit if ADX drops below this
    'rsi_drop_threshold': 40,         # Exit if RSI drops below this
    'profit_targets': [20, 30, 50],   # Profit target levels (%)
}

# Position Sizing (based on score)
POSITION_SIZING = {
    'score_85_to_100': 1.0,  # Full position
    'score_80_to_84': 0.5,   # Half position
    'score_below_80': 0.0,   # No position
}


# ==============================================================================
# Output Configuration
# ==============================================================================

# Output directory
OUTPUT_DIR = './output'

# CSV Export
EXPORT_CSV = True
EXPORT_DETAILED_BREAKDOWN = True  # Include full score breakdown in CSV

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = './uptrend_scanner.log'


# ==============================================================================
# Scanning Schedule (for automation)
# ==============================================================================

# Time to run daily scan (after market close)
# Format: "HH:MM" in 24-hour format
DAILY_SCAN_TIME = "18:00"  # 6:00 PM (after market close at 4:00 PM + 2hr buffer)

# Days to run scan
SCAN_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # Weekdays only


# ==============================================================================
# Strategy Presets
# ==============================================================================

# Different strategy configurations for different trading styles

STRATEGY_AGGRESSIVE = {
    'name': 'Aggressive Momentum',
    'min_tier': 2,
    'max_distance_from_ma20': 10.0,
    'min_adx': 25,
    'rsi_range': (55, 75),
    'weight_momentum': 30,  # Increase momentum weight
    'weight_trend': 20,
}

STRATEGY_CONSERVATIVE = {
    'name': 'Conservative Quality',
    'min_tier': 1,
    'max_distance_from_ma20': 3.0,
    'min_adx': 35,
    'rsi_range': (50, 60),
    'min_days_in_uptrend': 30,
    'max_days_in_uptrend': 90,
}

STRATEGY_SWING_TRADE = {
    'name': 'Swing Trade Setups',
    'min_tier': 2,
    'max_distance_from_ma20': 2.0,  # Close to MA20 for entry
    'min_adx': 25,
    'rsi_range': (45, 60),  # Allow slightly lower RSI for pullbacks
}

STRATEGY_BREAKOUT = {
    'name': 'Early Breakout',
    'focus': 'early_uptrends',  # Focus on early uptrends instead of established
    'min_early_score': 6,  # Out of 8
    'volume_multiplier': 2.0,  # Require strong volume
}


# ==============================================================================
# Watchlist Management
# ==============================================================================

# Existing positions to monitor
MY_POSITIONS = [
    # Add your current positions here for daily monitoring
    # Example: {'ticker': 'AAPL', 'entry': 175.00, 'shares': 100}
]

# Custom watchlist (high-priority stocks to always check)
CUSTOM_WATCHLIST = [
    # Add specific tickers you always want to monitor
    # Example: 'AAPL', 'MSFT', 'NVDA'
]


# ==============================================================================
# Advanced Features (Future)
# ==============================================================================

# Multi-timeframe analysis
ENABLE_MULTI_TIMEFRAME = False
TIMEFRAMES = ['daily', 'weekly']  # Confirm daily uptrend with weekly

# Sector rotation
ENABLE_SECTOR_ANALYSIS = False
PREFERRED_SECTORS = []  # Empty = all sectors

# Earnings filter
AVOID_EARNINGS_WINDOW = True
EARNINGS_BUFFER_DAYS = 2  # Avoid stocks within 2 days of earnings

# WebSocket (for future real-time monitoring)
ENABLE_WEBSOCKET = False
WEBSOCKET_WATCHLIST_SIZE = 20  # Monitor top 20 stocks in real-time
