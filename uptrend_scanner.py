"""
Uptrend Momentum Scanner
========================
Scans stocks for uptrend opportunities using Polygon.io (Massive.com) API.

Identifies two types of uptrends:
1. Early Uptrend: Stocks just breaking out
2. Established Uptrend: Stocks in sustained uptrends

Scores established uptrends (0-100 points) across 6 categories:
- Trend Strength (20 pts): ADX level, MA20 slope, days in uptrend
- Momentum Quality (18 pts): RSI position, MACD histogram
- Volume Profile (17 pts): Volume trend, relative volume
- Price Structure (17 pts): Support quality, pullback behavior
- Risk/Reward Setup (13 pts): Distance from MA20, proximity to resistance
- Trend Quality (15 pts): Choppiness Index, Efficiency Ratio, price deviation

Bins stocks into 4 tiers based on score.
"""

import pandas as pd
import numpy as np
import requests
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d

# Color scheme for RSI (same as stock_trend_analyzer)
RSI_COLOR_OVERSOLD = '#FFD700'  # Yellow (<30)
RSI_COLOR_BEARISH = '#F44336'   # Red (30-50)
RSI_COLOR_BULLISH = '#2196F3'   # Blue (50-70)
RSI_COLOR_OVERBOUGHT = '#FFD700' # Yellow (>70)

# Velocity/Acceleration colors (same as stock_trend_analyzer)
SMOOTHED_COLOR = 'blue'           # Blue for smoothed price line
VELOCITY_COLOR = 'blue'           # Blue for velocity line
ACCEL_COLOR = '#C49821'           # Gold/amber color for acceleration

# Quadrant colors for velocity/acceleration shading
COLOR_VEL_POS_ACC_POS = '#00C853'  # Bright green - rising & steepening
COLOR_VEL_POS_ACC_NEG = '#69F0AE'  # Medium green - rising but flattening
COLOR_VEL_NEG_ACC_POS = '#FF8A80'  # Medium red - falling but flattening
COLOR_VEL_NEG_ACC_NEG = '#D50000'  # Bright red - falling & steepening

# ==============================================================================
# SIC to GICS Sector Mapping
# ==============================================================================
# Maps Standard Industrial Classification (SIC) codes from Polygon.io
# to GICS (Global Industry Classification Standard) sectors
# ==============================================================================

# The 11 GICS Sectors
GICS_SECTORS = [
    'Communication Services',
    'Consumer Discretionary',
    'Consumer Staples',
    'Energy',
    'Financials',
    'Health Care',
    'Industrials',
    'Information Technology',
    'Materials',
    'Real Estate',
    'Utilities'
]

def get_gics_sector_from_sic(sic_code: str, sic_description: str = '') -> Tuple[str, str]:
    """
    Map SIC code to GICS sector and industry group.

    Args:
        sic_code: The SIC code string (e.g., '3571', '6022')
        sic_description: The SIC description from Polygon.io (optional, used for refinement)

    Returns:
        Tuple of (sector, industry_group)
    """
    if not sic_code:
        return 'Unknown', 'Unknown'

    try:
        sic = int(sic_code)
    except (ValueError, TypeError):
        return 'Unknown', 'Unknown'

    # SIC code ranges to GICS sector mapping
    # Based on Standard Industrial Classification structure

    # Agriculture, Forestry, Fishing (0100-0999) -> Materials
    if 100 <= sic <= 999:
        return 'Materials', 'Materials'

    # Mining (1000-1499) -> Energy or Materials
    elif 1000 <= sic <= 1499:
        if 1300 <= sic <= 1399:  # Oil & Gas Extraction
            return 'Energy', 'Energy Equipment & Services'
        else:  # Metal, coal, other mining
            return 'Materials', 'Materials'

    # Construction (1500-1799) -> Industrials
    elif 1500 <= sic <= 1799:
        return 'Industrials', 'Capital Goods'

    # Manufacturing (2000-3999)
    elif 2000 <= sic <= 3999:
        # Food & Kindred Products (2000-2099) -> Consumer Staples
        if 2000 <= sic <= 2099:
            return 'Consumer Staples', 'Food Beverage & Tobacco'
        # Tobacco (2100-2199) -> Consumer Staples
        elif 2100 <= sic <= 2199:
            return 'Consumer Staples', 'Food Beverage & Tobacco'
        # Textile Mill Products (2200-2299) -> Consumer Discretionary
        elif 2200 <= sic <= 2299:
            return 'Consumer Discretionary', 'Consumer Durables & Apparel'
        # Apparel (2300-2399) -> Consumer Discretionary
        elif 2300 <= sic <= 2399:
            return 'Consumer Discretionary', 'Consumer Durables & Apparel'
        # Lumber & Wood (2400-2499) -> Materials
        elif 2400 <= sic <= 2499:
            return 'Materials', 'Materials'
        # Furniture (2500-2599) -> Consumer Discretionary
        elif 2500 <= sic <= 2599:
            return 'Consumer Discretionary', 'Consumer Durables & Apparel'
        # Paper & Allied Products (2600-2699) -> Materials
        elif 2600 <= sic <= 2699:
            return 'Materials', 'Materials'
        # Printing & Publishing (2700-2799) -> Communication Services
        elif 2700 <= sic <= 2799:
            return 'Communication Services', 'Media & Entertainment'
        # Chemicals (2800-2899) -> Materials (except pharma)
        elif 2800 <= sic <= 2899:
            if 2830 <= sic <= 2836:  # Drugs/Pharmaceuticals
                return 'Health Care', 'Pharmaceuticals Biotechnology & Life Sciences'
            else:
                return 'Materials', 'Materials'
        # Petroleum Refining (2900-2999) -> Energy
        elif 2900 <= sic <= 2999:
            return 'Energy', 'Oil Gas & Consumable Fuels'
        # Rubber & Plastics (3000-3099) -> Materials
        elif 3000 <= sic <= 3099:
            return 'Materials', 'Materials'
        # Leather (3100-3199) -> Consumer Discretionary
        elif 3100 <= sic <= 3199:
            return 'Consumer Discretionary', 'Consumer Durables & Apparel'
        # Stone, Clay, Glass (3200-3299) -> Materials
        elif 3200 <= sic <= 3299:
            return 'Materials', 'Materials'
        # Primary Metal (3300-3399) -> Materials
        elif 3300 <= sic <= 3399:
            return 'Materials', 'Materials'
        # Fabricated Metal (3400-3499) -> Industrials
        elif 3400 <= sic <= 3499:
            return 'Industrials', 'Capital Goods'
        # Industrial Machinery & Equipment (3500-3599) -> Industrials
        elif 3500 <= sic <= 3599:
            if 3570 <= sic <= 3579:  # Computer Equipment
                return 'Information Technology', 'Technology Hardware & Equipment'
            else:
                return 'Industrials', 'Capital Goods'
        # Electronic Equipment (3600-3699) -> Information Technology
        elif 3600 <= sic <= 3699:
            if 3660 <= sic <= 3669:  # Communications Equipment
                return 'Communication Services', 'Telecommunication Services'
            elif 3674 <= sic <= 3679:  # Semiconductors
                return 'Information Technology', 'Semiconductors & Semiconductor Equipment'
            else:
                return 'Information Technology', 'Technology Hardware & Equipment'
        # Transportation Equipment (3700-3799) -> Industrials or Consumer Discretionary
        elif 3700 <= sic <= 3799:
            if 3711 <= sic <= 3716:  # Motor Vehicles
                return 'Consumer Discretionary', 'Automobiles & Components'
            else:
                return 'Industrials', 'Capital Goods'
        # Measuring Instruments (3800-3899) -> Health Care or Information Technology
        elif 3800 <= sic <= 3899:
            if 3841 <= sic <= 3851:  # Medical Instruments
                return 'Health Care', 'Health Care Equipment & Services'
            else:
                return 'Information Technology', 'Technology Hardware & Equipment'
        # Miscellaneous Manufacturing (3900-3999) -> Consumer Discretionary
        elif 3900 <= sic <= 3999:
            return 'Consumer Discretionary', 'Consumer Durables & Apparel'

    # Transportation, Communications, Utilities (4000-4999)
    elif 4000 <= sic <= 4999:
        # Railroads (4000-4099) -> Industrials
        if 4000 <= sic <= 4099:
            return 'Industrials', 'Transportation'
        # Trucking (4100-4199) -> Industrials
        elif 4100 <= sic <= 4199:
            return 'Industrials', 'Transportation'
        # Water Transportation (4400-4499) -> Industrials
        elif 4400 <= sic <= 4499:
            return 'Industrials', 'Transportation'
        # Transportation by Air (4500-4599) -> Industrials
        elif 4500 <= sic <= 4599:
            return 'Industrials', 'Transportation'
        # Pipelines (4600-4699) -> Energy
        elif 4600 <= sic <= 4699:
            return 'Energy', 'Oil Gas & Consumable Fuels'
        # Communications (4800-4899) -> Communication Services
        elif 4800 <= sic <= 4899:
            return 'Communication Services', 'Telecommunication Services'
        # Utilities (4900-4999) -> Utilities
        elif 4900 <= sic <= 4999:
            return 'Utilities', 'Utilities'
        else:
            return 'Industrials', 'Transportation'

    # Wholesale Trade (5000-5199) -> Consumer Discretionary
    elif 5000 <= sic <= 5199:
        return 'Consumer Discretionary', 'Consumer Discretionary Distribution & Retail'

    # Retail Trade (5200-5999)
    elif 5200 <= sic <= 5999:
        # Eating/Drinking Places (5800-5899) -> Consumer Discretionary
        if 5800 <= sic <= 5899:
            return 'Consumer Discretionary', 'Consumer Services'
        # Food Stores (5400-5499) -> Consumer Staples
        elif 5400 <= sic <= 5499:
            return 'Consumer Staples', 'Consumer Staples Distribution & Retail'
        else:
            return 'Consumer Discretionary', 'Consumer Discretionary Distribution & Retail'

    # Finance, Insurance, Real Estate (6000-6799)
    elif 6000 <= sic <= 6799:
        # Banks (6000-6099) -> Financials
        if 6000 <= sic <= 6099:
            return 'Financials', 'Banks'
        # Credit Agencies (6100-6199) -> Financials
        elif 6100 <= sic <= 6199:
            return 'Financials', 'Financial Services'
        # Securities (6200-6299) -> Financials
        elif 6200 <= sic <= 6299:
            return 'Financials', 'Financial Services'
        # Insurance (6300-6399) -> Financials
        elif 6300 <= sic <= 6399:
            return 'Financials', 'Insurance'
        # Insurance Agents (6400-6499) -> Financials
        elif 6400 <= sic <= 6499:
            return 'Financials', 'Insurance'
        # Real Estate (6500-6599) -> Real Estate
        elif 6500 <= sic <= 6599:
            return 'Real Estate', 'Real Estate Management & Development'
        # Holding & Investment Offices (6700-6799) -> Financials
        elif 6700 <= sic <= 6799:
            if 6798 == sic:  # REITs
                return 'Real Estate', 'Equity REITs'
            else:
                return 'Financials', 'Financial Services'

    # Services (7000-8999)
    elif 7000 <= sic <= 8999:
        # Hotels (7000-7099) -> Consumer Discretionary
        if 7000 <= sic <= 7099:
            return 'Consumer Discretionary', 'Consumer Services'
        # Personal Services (7200-7299) -> Consumer Discretionary
        elif 7200 <= sic <= 7299:
            return 'Consumer Discretionary', 'Consumer Services'
        # Business Services (7300-7399) -> Industrials or Info Tech
        elif 7300 <= sic <= 7399:
            if 7370 <= sic <= 7379:  # Computer Programming
                return 'Information Technology', 'Software & Services'
            else:
                return 'Industrials', 'Commercial & Professional Services'
        # Auto Services (7500-7599) -> Consumer Discretionary
        elif 7500 <= sic <= 7599:
            return 'Consumer Discretionary', 'Consumer Services'
        # Motion Pictures (7800-7899) -> Communication Services
        elif 7800 <= sic <= 7899:
            return 'Communication Services', 'Media & Entertainment'
        # Amusement & Recreation (7900-7999) -> Consumer Discretionary
        elif 7900 <= sic <= 7999:
            return 'Consumer Discretionary', 'Consumer Services'
        # Health Services (8000-8099) -> Health Care
        elif 8000 <= sic <= 8099:
            return 'Health Care', 'Health Care Equipment & Services'
        # Legal Services (8100-8199) -> Industrials
        elif 8100 <= sic <= 8199:
            return 'Industrials', 'Commercial & Professional Services'
        # Educational Services (8200-8299) -> Consumer Discretionary
        elif 8200 <= sic <= 8299:
            return 'Consumer Discretionary', 'Consumer Services'
        # Social Services (8300-8399) -> Health Care
        elif 8300 <= sic <= 8399:
            return 'Health Care', 'Health Care Equipment & Services'
        # Engineering & Accounting (8700-8799) -> Industrials
        elif 8700 <= sic <= 8799:
            return 'Industrials', 'Commercial & Professional Services'
        else:
            return 'Consumer Discretionary', 'Consumer Services'

    # Public Administration (9000-9999) -> Industrials (rare for public companies)
    elif 9000 <= sic <= 9999:
        return 'Industrials', 'Capital Goods'

    # Default fallback
    return 'Unknown', 'Unknown'

# Swing label colors (same as stock_trend_analyzer)
SWING_LABEL_COLORS = {
    'HH': 'darkgreen',   # Higher High - bullish
    'HL': 'green',       # Higher Low - bullish
    'LH': 'darkred',     # Lower High - bearish
    'LL': 'red'          # Lower Low - bearish
}


def calculate_smoothed_velocity_acceleration(df, sigma=3):
    """
    Calculate smoothed price, velocity (1st derivative), and acceleration (2nd derivative)
    using Gaussian smoothing - same approach as stock_trend_analyzer.

    Args:
        df: DataFrame with 'close' column
        sigma: Gaussian smoothing parameter (default: 3)

    Returns:
        Dict with 'smoothed', 'velocity', 'acceleration' Series
    """
    prices = df['close'].values.astype(float)

    # Smooth prices using Gaussian filter
    smoothed = gaussian_filter1d(prices, sigma=sigma)

    # Calculate derivatives
    velocity = np.gradient(smoothed)       # First derivative (rate of change)
    acceleration = np.gradient(velocity)   # Second derivative

    return {
        'smoothed': pd.Series(smoothed, index=df.index),
        'velocity': pd.Series(velocity, index=df.index),
        'acceleration': pd.Series(acceleration, index=df.index)
    }


def detect_swing_points(df, window=5):
    """
    Detect swing highs and lows and classify them as HH, HL, LH, LL.

    HH (Higher High): A swing high that is higher than the previous swing high
    LH (Lower High): A swing high that is lower than the previous swing high
    HL (Higher Low): A swing low that is higher than the previous swing low
    LL (Lower Low): A swing low that is lower than the previous swing low

    Args:
        df: DataFrame with 'high' and 'low' columns
        window: Lookback window for swing detection (bars on each side)

    Returns:
        DataFrame with swing point classifications added
    """
    df = df.copy()
    highs = df['high'].values
    lows = df['low'].values

    # Initialize columns
    df['swing_high'] = False
    df['swing_low'] = False
    df['swing_label'] = ''
    df['is_major_swing'] = False  # For distinguishing major vs minor

    swing_highs = []  # List of (index, price)
    swing_lows = []   # List of (index, price)

    # Detect swing highs and lows
    for i in range(window, len(df) - window):
        # Swing high: highest point in the window
        if highs[i] == max(highs[i-window:i+window+1]):
            df.iloc[i, df.columns.get_loc('swing_high')] = True
            swing_highs.append((i, highs[i]))

        # Swing low: lowest point in the window
        if lows[i] == min(lows[i-window:i+window+1]):
            df.iloc[i, df.columns.get_loc('swing_low')] = True
            swing_lows.append((i, lows[i]))

    # Classify swing highs as HH or LH
    prev_swing_high = None
    for idx, price in swing_highs:
        if prev_swing_high is not None:
            if price > prev_swing_high:
                df.iloc[idx, df.columns.get_loc('swing_label')] = 'HH'
            else:
                df.iloc[idx, df.columns.get_loc('swing_label')] = 'LH'
        prev_swing_high = price

    # Classify swing lows as HL or LL
    prev_swing_low = None
    for idx, price in swing_lows:
        if prev_swing_low is not None:
            if price > prev_swing_low:
                df.iloc[idx, df.columns.get_loc('swing_label')] = 'HL'
            else:
                df.iloc[idx, df.columns.get_loc('swing_label')] = 'LL'
        prev_swing_low = price

    # Mark major swings (larger window = more significant)
    major_window = window * 2
    for i in range(major_window, len(df) - major_window):
        if df.iloc[i]['swing_high']:
            if highs[i] == max(highs[i-major_window:i+major_window+1]):
                df.iloc[i, df.columns.get_loc('is_major_swing')] = True
        if df.iloc[i]['swing_low']:
            if lows[i] == min(lows[i-major_window:i+major_window+1]):
                df.iloc[i, df.columns.get_loc('is_major_swing')] = True

    return df


def get_rsi_color(rsi_value):
    """Get color based on RSI value (same thresholds as stock_trend_analyzer)"""
    if rsi_value < 30:
        return RSI_COLOR_OVERSOLD
    elif 30 <= rsi_value < 50:
        return RSI_COLOR_BEARISH
    elif 50 <= rsi_value <= 70:
        return RSI_COLOR_BULLISH
    else:  # > 70
        return RSI_COLOR_OVERBOUGHT


def calculate_trend_quality(df: pd.DataFrame, lookback: int = 60) -> Dict:
    """
    Calculate trend quality using three complementary methods.
    Adapted from inflection_detector.

    Combines:
    1. Efficiency Ratio (Kaufman) - How direct is the price movement?
    2. Choppiness Index - Is the market trending or consolidating?
    3. Smoothed Price Deviation - How closely does price follow the trend?

    Args:
        df: DataFrame with OHLCV data
        lookback: Period for calculations (default 60 days)

    Returns:
        Dict with efficiency_ratio, choppiness_index, avg_deviation_pct,
        trend_quality (0-1), and trend_quality_score (0-10)
    """
    import math

    # Use last 'lookback' days, or all available if less
    n = min(lookback, len(df))
    if n < 20:
        return {
            'efficiency_ratio': 0.0,
            'choppiness_index': 50.0,
            'avg_deviation_pct': 5.0,
            'trend_quality': 0.0,
            'trend_quality_score': 0
        }

    closes = df['close'].iloc[-n:].values
    highs = df['high'].iloc[-n:].values
    lows = df['low'].iloc[-n:].values

    # =================================================================
    # 1. EFFICIENCY RATIO (Kaufman) - How direct is the move?
    # =================================================================
    # Direction: net price change over period
    direction = abs(closes[-1] - closes[0])

    # Volatility: sum of all daily moves
    volatility = sum(abs(closes[i] - closes[i-1]) for i in range(1, len(closes)))

    efficiency_ratio = direction / volatility if volatility > 0 else 0
    # ER ranges 0-1: higher = smoother trend

    # =================================================================
    # 2. CHOPPINESS INDEX - Is the market trending or consolidating?
    # =================================================================
    # Calculate True Range for each bar
    atr_values = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        atr_values.append(tr)

    atr_sum = sum(atr_values)
    high_low_range = max(highs) - min(lows)

    if high_low_range > 0 and n > 1:
        choppiness = 100 * math.log10(atr_sum / high_low_range) / math.log10(n)
    else:
        choppiness = 50  # Neutral
    # CI ranges ~0-100: lower = smoother trend, higher = choppier

    # =================================================================
    # 3. SMOOTHED PRICE DEVIATION - How closely does price follow the trend?
    # =================================================================
    smoothed = gaussian_filter1d(closes, sigma=5)

    # Average % deviation from smoothed line
    deviations = [abs(closes[i] - smoothed[i]) / smoothed[i] * 100
                  for i in range(len(closes)) if smoothed[i] > 0]
    avg_deviation = sum(deviations) / len(deviations) if deviations else 5.0
    # Lower deviation = smoother trend

    # =================================================================
    # COMBINE INTO SINGLE SCORE
    # =================================================================
    # Normalize each metric to 0-1 scale (1 = smoothest)

    # ER already 0-1, higher is better
    er_score = efficiency_ratio

    # CI: 38 = very smooth, 62 = very choppy
    # Invert and normalize: (62 - CI) / (62 - 38)
    ci_score = max(0, min(1, (62 - choppiness) / 24))

    # Deviation: 0% = perfect, 3%+ = choppy
    # Invert: (3 - deviation) / 3
    dev_score = max(0, min(1, (3 - avg_deviation) / 3))

    # Weighted average (ER and CI are most established, deviation is complementary)
    combined = (er_score * 0.4) + (ci_score * 0.4) + (dev_score * 0.2)

    # Convert to 0-10 score with thresholds
    if combined >= 0.70:
        trend_quality_score = 10
    elif combined >= 0.55:
        trend_quality_score = 7
    elif combined >= 0.40:
        trend_quality_score = 4
    elif combined >= 0.25:
        trend_quality_score = 2
    else:
        trend_quality_score = 0

    return {
        'efficiency_ratio': round(efficiency_ratio, 3),
        'choppiness_index': round(choppiness, 1),
        'avg_deviation_pct': round(avg_deviation, 2),
        'trend_quality': round(combined, 3),
        'trend_quality_score': trend_quality_score
    }


# Configure logging to both file and console
import os

# Create output directory if it doesn't exist
os.makedirs('./output/logs', exist_ok=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler with timestamp (create new log file for each run)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'./output/logs/scan_{timestamp}.log'
file_handler = logging.FileHandler(log_filename, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Log the start of the session
logger.info(f"=" * 70)
logger.info(f"UPTREND SCANNER - NEW SESSION")
logger.info(f"Log file: {log_filename}")
logger.info(f"=" * 70)


class PolygonAPI:
    """Handler for Polygon.io (Massive.com) API interactions"""

    def __init__(self, api_key: str, max_requests_per_minute: Optional[int] = None):
        """
        Initialize Polygon API client

        Args:
            api_key: Polygon.io API key
            max_requests_per_minute: Rate limit (None for unlimited, 5 for free tier)
        """
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = []

    def _rate_limit_wait(self):
        """Wait if necessary to respect rate limits"""
        # Skip rate limiting if unlimited (None)
        if self.max_requests_per_minute is None:
            return

        now = time.time()
        # Remove timestamps older than 60 seconds
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.max_requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]) + 0.1
            if sleep_time > 0:
                logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)

        self.request_times.append(now)

    def get_all_tickers(self, market: str = 'stocks',
                       exchange: Optional[List[str]] = None,
                       active: bool = True,
                       limit: int = 1000,
                       ticker_type: str = 'CS') -> List[Dict]:
        """
        Get list of all tickers from specified exchanges

        Args:
            market: Type of asset (stocks, options, etc)
            exchange: List of exchanges ['XNAS', 'XNYS'] or None for all
            active: Only active tickers
            limit: Max results per request
            ticker_type: Type of ticker to filter ('CS' = common stock, None = all)

        Returns:
            List of ticker dictionaries
        """
        # If multiple exchanges specified, fetch each separately and combine
        # (Polygon API doesn't support comma-separated exchange values)
        if exchange and len(exchange) > 1:
            all_tickers = []
            seen_tickers = set()

            for exch in exchange:
                logger.info(f"Fetching tickers from {exch}...")
                tickers = self.get_all_tickers(market=market, exchange=[exch],
                                              active=active, limit=limit,
                                              ticker_type=ticker_type)
                # Remove duplicates
                for ticker in tickers:
                    ticker_symbol = ticker.get('ticker')
                    if ticker_symbol not in seen_tickers:
                        seen_tickers.add(ticker_symbol)
                        all_tickers.append(ticker)

            logger.info(f"Fetched {len(all_tickers)} unique tickers from {len(exchange)} exchanges")
            return all_tickers

        # Single exchange or no exchange filter
        self._rate_limit_wait()

        url = f"{self.base_url}/v3/reference/tickers"
        params = {
            'market': market,
            'active': active,
            'limit': limit,
            'apiKey': self.api_key
        }

        if exchange and len(exchange) == 1:
            params['exchange'] = exchange[0]

        if ticker_type:
            params['type'] = ticker_type

        all_tickers = []
        next_url = None

        try:
            while True:
                if next_url:
                    response = requests.get(next_url)
                else:
                    response = requests.get(url, params=params)

                response.raise_for_status()
                data = response.json()

                if 'results' in data:
                    all_tickers.extend(data['results'])

                # Check for pagination
                next_url = data.get('next_url')
                if next_url:
                    next_url += f"&apiKey={self.api_key}"
                    self._rate_limit_wait()
                else:
                    break

            logger.info(f"Fetched {len(all_tickers)} tickers")
            return all_tickers

        except Exception as e:
            logger.error(f"Error fetching tickers: {e}")
            return []

    def get_aggregates(self, ticker: str, days: int = 200,
                      timespan: str = 'day') -> Optional[pd.DataFrame]:
        """
        Get aggregate bars for a ticker

        Args:
            ticker: Stock symbol
            days: Number of days of historical data
            timespan: Bar size (day, week, month)

        Returns:
            DataFrame with OHLCV data or None
        """
        self._rate_limit_wait()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/{timespan}/" \
              f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"

        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'apiKey': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'results' not in data or not data['results']:
                return None

            # DEBUG: Print raw data sample for first ticker
            if logger.level <= logging.DEBUG:
                logger.debug(f"\n{'='*70}")
                logger.debug(f"RAW DATA SAMPLE for {ticker}")
                logger.debug(f"{'='*70}")
                logger.debug(f"Response metadata: status={data.get('status')}, "
                           f"resultsCount={data.get('resultsCount')}, "
                           f"ticker={data.get('ticker')}")
                logger.debug(f"\nFirst 3 bars (raw JSON):")
                for i, bar in enumerate(data['results'][:3]):
                    logger.debug(f"  Bar {i+1}: {bar}")
                logger.debug(f"\nLast 3 bars (raw JSON):")
                for i, bar in enumerate(data['results'][-3:]):
                    logger.debug(f"  Bar {len(data['results'])-2+i}: {bar}")
                logger.debug(f"{'='*70}\n")

            df = pd.DataFrame(data['results'])
            df['date'] = pd.to_datetime(df['t'], unit='ms')
            df = df.rename(columns={
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })

            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df.set_index('date', inplace=True)

            # DEBUG: Print DataFrame sample
            if logger.level <= logging.DEBUG:
                logger.debug(f"CONVERTED DATAFRAME for {ticker}")
                logger.debug(f"Shape: {df.shape} (rows, columns)")
                logger.debug(f"\nFirst 5 rows:")
                logger.debug(f"\n{df.head()}")
                logger.debug(f"\nLast 5 rows:")
                logger.debug(f"\n{df.tail()}")
                logger.debug(f"\nData types:")
                logger.debug(f"\n{df.dtypes}")
                logger.debug(f"{'='*70}\n")

            return df

        except Exception as e:
            logger.debug(f"Error fetching data for {ticker}: {e}")
            return None

    def get_earnings_dates(self, ticker: str, days: int = 365) -> List[str]:
        """
        Get earnings report dates for a ticker

        Args:
            ticker: Stock symbol
            days: Number of days back to search

        Returns:
            List of earnings dates (YYYY-MM-DD format)
        """
        self._rate_limit_wait()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Polygon v1 financials endpoint
        url = f"{self.base_url}/vX/reference/financials"

        params = {
            'ticker': ticker,
            'filing_date.gte': start_date.strftime('%Y-%m-%d'),
            'filing_date.lte': end_date.strftime('%Y-%m-%d'),
            'limit': 100,
            'apiKey': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            earnings_dates = []
            if 'results' in data:
                for result in data['results']:
                    # Get the filing date or report period
                    filing_date = result.get('filing_date')
                    if filing_date:
                        earnings_dates.append(filing_date)

            logger.debug(f"Found {len(earnings_dates)} earnings dates for {ticker}")
            return earnings_dates

        except Exception as e:
            logger.debug(f"Error fetching earnings dates for {ticker}: {e}")
            return []

    def get_ticker_details(self, ticker: str) -> Dict:
        """
        Get ticker details including shares outstanding, float data, and sector/industry

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with ticker details:
            - shares_outstanding: Total outstanding shares
            - float_shares: Shares available for trading (free float)
            - free_float_pct: Percentage of shares that are free float
            - market_cap: Market capitalization
            - sector: GICS sector (mapped from SIC code)
            - industry_group: GICS industry group (mapped from SIC code)
            - sic_code: Original SIC code from Polygon
            - sic_description: SIC description from Polygon
        """
        self._rate_limit_wait()

        url = f"{self.base_url}/v3/reference/tickers/{ticker}"

        params = {
            'apiKey': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'results' in data:
                results = data['results']

                # Get shares outstanding (weighted shares is most accurate)
                shares_outstanding = results.get('weighted_shares_outstanding',
                                               results.get('share_class_shares_outstanding', 0))

                # Market cap
                market_cap = results.get('market_cap', 0)

                # Calculate free float (Polygon doesn't provide this directly)
                # We'll use weighted_shares_outstanding as a proxy for free float
                # In reality, free float = outstanding - restricted shares
                # For now, we estimate float as 80% of outstanding (conservative estimate)
                # This can be improved with additional data sources
                float_shares = shares_outstanding * 0.80  # Conservative estimate

                free_float_pct = 80.0 if shares_outstanding > 0 else 0.0

                # Extract SIC code and description for sector mapping
                sic_code = results.get('sic_code', '')
                sic_description = results.get('sic_description', '')

                # Map SIC to GICS sector and industry group
                sector, industry_group = get_gics_sector_from_sic(sic_code, sic_description)

                logger.debug(f"{ticker}: Outstanding={shares_outstanding:,.0f}, Float={float_shares:,.0f}, Sector={sector}")

                return {
                    'shares_outstanding': shares_outstanding,
                    'float_shares': float_shares,
                    'free_float_pct': free_float_pct,
                    'market_cap': market_cap,
                    'sector': sector,
                    'industry_group': industry_group,
                    'sic_code': sic_code,
                    'sic_description': sic_description
                }

            return {
                'shares_outstanding': 0,
                'float_shares': 0,
                'free_float_pct': 0,
                'market_cap': 0,
                'sector': 'Unknown',
                'industry_group': 'Unknown',
                'sic_code': '',
                'sic_description': ''
            }

        except Exception as e:
            logger.debug(f"Error fetching ticker details for {ticker}: {e}")
            return {
                'shares_outstanding': 0,
                'float_shares': 0,
                'free_float_pct': 0,
                'market_cap': 0,
                'sector': 'Unknown',
                'industry_group': 'Unknown',
                'sic_code': '',
                'sic_description': ''
            }


class TechnicalAnalyzer:
    """Calculate technical indicators for stock analysis"""

    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """Calculate Simple Moving Average"""
        return df[column].rolling(window=period).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12,
                      slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD, Signal line, and Histogram"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line

        return macd, signal_line, histogram

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        high = df['high']
        low = df['low']
        close = df['close']

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

        # Smoothed values
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # ADX calculation
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20,
                                 num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return upper, middle, lower

    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate historical volatility (annualized)

        Args:
            df: DataFrame with OHLC data
            period: Lookback period (default 20 days)

        Returns:
            Annualized volatility as percentage
        """
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252) * 100
        return volatility

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators and add to DataFrame"""
        # Moving Averages
        df['ma_20'] = self.calculate_sma(df, 20)
        df['ma_50'] = self.calculate_sma(df, 50)
        df['ma_200'] = self.calculate_sma(df, 200)

        # RSI
        df['rsi'] = self.calculate_rsi(df, 14)

        # MACD
        df['macd'], df['macd_signal'], df['macd_histogram'] = self.calculate_macd(df)

        # ADX
        df['adx'] = self.calculate_adx(df, 14)

        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = \
            self.calculate_bollinger_bands(df, 20, 2.0)

        # Volatility
        df['volatility_20'] = self.calculate_volatility(df, 20)
        df['volatility_50'] = self.calculate_volatility(df, 50)

        # Volume MA
        df['volume_ma_50'] = self.calculate_sma(df, 50, 'volume')

        return df


class UptrendClassifier:
    """Classify stocks into early vs established uptrends"""

    @staticmethod
    def is_early_uptrend(df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Detect if stock is in early uptrend (breakout stage)

        Criteria:
        - Price breaking above resistance/consolidation
        - Volume spike on breakout
        - Recent MA20 cross (within 1-5 days)
        - RSI 50-70 (not overbought)
        - ADX starting to rise (>20, increasing)
        - MACD bullish crossover (within 1-10 days)

        Returns:
            (is_early, details_dict)
        """
        if len(df) < 60:
            return False, {}

        latest = df.iloc[-1]
        recent_5 = df.iloc[-5:]
        recent_10 = df.iloc[-10:]

        details = {}
        score = 0

        # 1. Price above MA20 recently (within last 5 days)
        ma20_cross = False
        for i in range(-5, 0):
            if df.iloc[i-1]['close'] <= df.iloc[i-1]['ma_20'] and \
               df.iloc[i]['close'] > df.iloc[i]['ma_20']:
                ma20_cross = True
                break
        details['ma20_cross_recent'] = ma20_cross
        if ma20_cross:
            score += 2

        # 2. Volume spike (1.5-2x average)
        volume_spike = latest['volume'] > (latest['volume_ma_50'] * 1.5)
        details['volume_spike'] = volume_spike
        if volume_spike:
            score += 2

        # 3. RSI in healthy range (50-70)
        rsi_healthy = 50 <= latest['rsi'] <= 70
        details['rsi_healthy'] = rsi_healthy
        details['rsi'] = latest['rsi']
        if rsi_healthy:
            score += 1

        # 4. ADX rising and > 20
        adx_rising = latest['adx'] > 20 and \
                    latest['adx'] > df.iloc[-5]['adx']
        details['adx_rising'] = adx_rising
        details['adx'] = latest['adx']
        if adx_rising:
            score += 1

        # 5. MACD bullish crossover (within 10 days)
        macd_cross = False
        for i in range(-10, 0):
            if df.iloc[i-1]['macd'] <= df.iloc[i-1]['macd_signal'] and \
               df.iloc[i]['macd'] > df.iloc[i]['macd_signal']:
                macd_cross = True
                break
        details['macd_cross_recent'] = macd_cross
        if macd_cross:
            score += 1

        # 6. Breakout above recent high
        high_20 = df.iloc[-20:-1]['high'].max()
        breakout = latest['close'] > high_20
        details['breakout'] = breakout
        if breakout:
            score += 1

        details['score'] = score

        # Require at least 5 out of 8 points
        is_early = score >= 5

        return is_early, details

    @staticmethod
    def is_established_uptrend(df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Detect if stock is in established uptrend (continuation stage)

        Criteria:
        - Price above MA20, MA50, MA200 (stacked properly)
        - Uptrend sustained for 20+ days
        - Making higher highs and higher lows
        - ADX > 25 (strong trend)

        Returns:
            (is_established, details_dict)
        """
        if len(df) < 200:
            return False, {}

        latest = df.iloc[-1]
        details = {}

        # 1. MAs properly stacked
        mas_stacked = (latest['close'] > latest['ma_20']) and \
                     (latest['ma_20'] > latest['ma_50']) and \
                     (latest['ma_50'] > latest['ma_200'])
        details['mas_stacked'] = mas_stacked

        # 2. Count days in uptrend (above MA20)
        days_in_uptrend = 0
        for i in range(len(df)-1, -1, -1):
            if df.iloc[i]['close'] > df.iloc[i]['ma_20']:
                days_in_uptrend += 1
            else:
                break
        details['days_in_uptrend'] = days_in_uptrend

        # 3. Higher highs and higher lows (last 30 days)
        recent_30 = df.iloc[-30:]
        highs = recent_30['high'].values
        lows = recent_30['low'].values

        higher_highs = all(highs[i] >= highs[i-1] or highs[i] >= highs[i-2]
                          for i in range(2, len(highs), 5))
        higher_lows = all(lows[i] >= lows[i-1] or lows[i] >= lows[i-2]
                         for i in range(2, len(lows), 5))

        details['higher_highs'] = higher_highs
        details['higher_lows'] = higher_lows

        # 4. ADX strong
        adx_strong = latest['adx'] > 25
        details['adx'] = latest['adx']
        details['adx_strong'] = adx_strong

        # All criteria must be met
        is_established = mas_stacked and days_in_uptrend >= 20 and adx_strong

        return is_established, details


class StockScorer:
    """Score stocks on 100-point scale across 6 categories"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize scorer with custom weights

        Args:
            config: Dict with custom weights and thresholds
        """
        self.config = config or {}

        # Default weights (can be overridden)
        # Total: 100 points across 6 categories
        self.weights = self.config.get('weights', {
            'trend_strength': 20,      # Was 25, reduced by 5
            'momentum_quality': 18,    # Was 20, reduced by 2
            'volume_profile': 17,      # Was 20, reduced by 3
            'price_structure': 17,     # Was 20, reduced by 3
            'risk_reward': 13,         # Was 15, reduced by 2
            'trend_quality': 15        # NEW: Choppiness/smoothness scoring
        })

    def score_trend_strength(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score trend strength (0-20 points)

        Components:
        - ADX level (0-8 pts)
        - MA20 slope (0-8 pts)
        - Days in uptrend (0-4 pts)
        """
        latest = df.iloc[-1]
        details = {}
        score = 0

        # ADX Level (0-8 points)
        adx = latest['adx']
        if adx > 40:
            adx_score = 8
        elif adx > 30:
            adx_score = 6
        elif adx > 25:
            adx_score = 4
        else:
            adx_score = 2

        details['adx'] = adx
        details['adx_score'] = adx_score
        score += adx_score

        # MA20 Slope (0-8 points)
        ma20_5d_ago = df.iloc[-5]['ma_20']
        ma20_slope = ((latest['ma_20'] - ma20_5d_ago) / ma20_5d_ago) * 100

        if ma20_slope > 3:  # >3% per week
            slope_score = 8
        elif ma20_slope > 1.5:
            slope_score = 6
        elif ma20_slope > 0.5:
            slope_score = 3
        else:
            slope_score = 0

        details['ma20_slope_pct'] = ma20_slope
        details['slope_score'] = slope_score
        score += slope_score

        # Days in uptrend (0-4 points)
        days_in_uptrend = 0
        for i in range(len(df)-1, -1, -1):
            if df.iloc[i]['close'] > df.iloc[i]['ma_20']:
                days_in_uptrend += 1
            else:
                break

        if 20 <= days_in_uptrend <= 60:  # Sweet spot
            days_score = 4
        elif 60 < days_in_uptrend <= 120:
            days_score = 2
        elif days_in_uptrend > 120:
            days_score = 1
        else:
            days_score = 0

        details['days_in_uptrend'] = days_in_uptrend
        details['days_score'] = days_score
        score += days_score

        return score, details

    def score_momentum_quality(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score momentum quality (0-18 points)

        Components:
        - RSI position (0-9 pts)
        - MACD histogram (0-9 pts)
        """
        latest = df.iloc[-1]
        details = {}
        score = 0

        # RSI Position (0-9 points)
        rsi = latest['rsi']
        if 55 <= rsi <= 65:  # Healthy momentum
            rsi_score = 9
        elif (50 <= rsi < 55) or (65 < rsi <= 70):
            rsi_score = 6
        elif 70 < rsi <= 80:
            rsi_score = 3
        else:  # > 80 overbought
            rsi_score = 1

        details['rsi'] = rsi
        details['rsi_score'] = rsi_score
        score += rsi_score

        # MACD Histogram (0-9 points)
        macd_hist = latest['macd_histogram']
        macd_hist_5d_ago = df.iloc[-5]['macd_histogram']

        if macd_hist > 0 and macd_hist > macd_hist_5d_ago:  # Expanding bullish
            macd_score = 9
        elif macd_hist > 0:  # Steady bullish
            macd_score = 6
        elif macd_hist > macd_hist_5d_ago:  # Weakening but positive
            macd_score = 3
        else:
            macd_score = 0

        details['macd_histogram'] = macd_hist
        details['macd_score'] = macd_score
        score += macd_score

        return score, details

    def score_volume_profile(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score volume profile (0-17 points)

        Components:
        - Volume trend (0-9 pts)
        - Relative volume (0-8 pts)
        """
        latest = df.iloc[-1]
        recent_5 = df.iloc[-5:]
        details = {}
        score = 0

        # Volume Trend (0-9 points)
        # Check if volume is higher on up days
        up_days_volume = []
        down_days_volume = []

        for i in range(-5, 0):
            if df.iloc[i]['close'] > df.iloc[i-1]['close']:
                up_days_volume.append(df.iloc[i]['volume'])
            else:
                down_days_volume.append(df.iloc[i]['volume'])

        if up_days_volume and down_days_volume:
            avg_up_vol = np.mean(up_days_volume)
            avg_down_vol = np.mean(down_days_volume)

            if avg_up_vol > avg_down_vol * 1.2:  # 20% more volume on up days
                volume_trend_score = 9
            elif avg_up_vol > avg_down_vol:
                volume_trend_score = 5
            else:
                volume_trend_score = 2
        else:
            volume_trend_score = 4

        details['volume_trend_score'] = volume_trend_score
        score += volume_trend_score

        # Relative Volume (0-8 points)
        rel_volume = latest['volume'] / latest['volume_ma_50']

        if rel_volume > 1.5:
            rel_vol_score = 8
        elif rel_volume > 1.2:
            rel_vol_score = 6
        elif rel_volume > 0.8:
            rel_vol_score = 4
        else:
            rel_vol_score = 2

        details['relative_volume'] = rel_volume
        details['rel_vol_score'] = rel_vol_score
        score += rel_vol_score

        return score, details

    def score_price_structure(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score price structure (0-17 points)

        Components:
        - Support quality (0-9 pts)
        - Pullback behavior (0-8 pts)
        """
        latest = df.iloc[-1]
        recent_60 = df.iloc[-60:]
        details = {}
        score = 0

        # Support Quality (0-9 points)
        # Look for MA20 acting as support
        touches = 0
        for i in range(-60, -1):
            low = df.iloc[i]['low']
            ma20 = df.iloc[i]['ma_20']

            # If low is within 2% of MA20, count as touch
            if abs(low - ma20) / ma20 < 0.02:
                touches += 1

        if touches >= 3:
            support_score = 9
        elif touches >= 2:
            support_score = 5
        else:
            support_score = 2

        details['support_touches'] = touches
        details['support_score'] = support_score
        score += support_score

        # Pullback Behavior (0-8 points)
        # Measure average pullback depth
        highs = recent_60['high'].values
        lows = recent_60['low'].values

        pullbacks = []
        for i in range(5, len(highs)):
            local_high = max(highs[i-5:i])
            subsequent_low = min(lows[i:min(i+5, len(lows))])
            pullback_pct = ((local_high - subsequent_low) / local_high) * 100
            if pullback_pct > 0:
                pullbacks.append(pullback_pct)

        if pullbacks:
            avg_pullback = np.mean(pullbacks)

            if avg_pullback < 10:  # Shallow pullbacks
                pullback_score = 8
            elif avg_pullback < 15:
                pullback_score = 5
            else:
                pullback_score = 3
        else:
            pullback_score = 4

        details['avg_pullback_pct'] = avg_pullback if pullbacks else 0
        details['pullback_score'] = pullback_score
        score += pullback_score

        return score, details

    def score_risk_reward(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score risk/reward setup (0-13 points)

        Components:
        - Distance from MA20 (0-7 pts)
        - Proximity to resistance (0-6 pts)
        """
        import config
        latest = df.iloc[-1]
        recent_60 = df.iloc[-60:]
        details = {}
        score = 0

        # Distance from MA20 (0-7 points)
        distance_from_ma20 = ((latest['close'] - latest['ma_20']) / latest['ma_20']) * 100

        if abs(distance_from_ma20) < 5:  # Within 5% (good entry)
            distance_score = 7
        elif abs(distance_from_ma20) < 10:
            distance_score = 4
        else:  # > 10% (extended)
            distance_score = 2

        details['distance_from_ma20_pct'] = distance_from_ma20
        details['distance_score'] = distance_score
        score += distance_score

        # Proximity to resistance (0-6 points)
        recent_high = recent_60['high'].max()
        room_to_resistance = ((recent_high - latest['close']) / latest['close']) * 100

        if room_to_resistance > 10:  # >10% room
            resistance_score = 6
        elif room_to_resistance > 5:
            resistance_score = 4
        else:  # <5% room
            resistance_score = 1

        details['room_to_resistance_pct'] = room_to_resistance
        details['resistance_score'] = resistance_score
        score += resistance_score

        return score, details

    def score_trend_quality(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score trend quality/smoothness (0-15 points)

        Uses Choppiness Index, Efficiency Ratio, and price deviation to measure
        how smooth vs choppy the trend is. Lower choppiness = smoother, better trend.

        Components:
        - Choppiness Index score (0-6 pts)
        - Efficiency Ratio score (0-5 pts)
        - Price Deviation score (0-4 pts)
        """
        # Calculate trend quality metrics
        tq_data = calculate_trend_quality(df)

        details = {
            'choppiness_index': tq_data['choppiness_index'],
            'efficiency_ratio': tq_data['efficiency_ratio'],
            'avg_deviation_pct': tq_data['avg_deviation_pct'],
            'trend_quality_combined': tq_data['trend_quality']
        }

        score = 0

        # Choppiness Index score (0-6 points)
        # CI: 38 = very smooth, 62 = very choppy
        ci = tq_data['choppiness_index']
        if ci < 40:  # Very smooth trend
            ci_score = 6
        elif ci < 47:  # Smooth trend
            ci_score = 5
        elif ci < 53:  # Neutral
            ci_score = 3
        elif ci < 58:  # Somewhat choppy
            ci_score = 2
        else:  # Very choppy
            ci_score = 0

        details['choppiness_score'] = ci_score
        score += ci_score

        # Efficiency Ratio score (0-5 points)
        # ER: 0-1, higher = more efficient/smooth
        er = tq_data['efficiency_ratio']
        if er > 0.5:  # Very efficient trend
            er_score = 5
        elif er > 0.35:  # Good efficiency
            er_score = 4
        elif er > 0.2:  # Moderate
            er_score = 2
        else:  # Choppy/inefficient
            er_score = 0

        details['efficiency_score'] = er_score
        score += er_score

        # Price Deviation score (0-4 points)
        # How closely price follows the smoothed line
        dev = tq_data['avg_deviation_pct']
        if dev < 1.0:  # Very tight to trend
            dev_score = 4
        elif dev < 2.0:  # Good adherence
            dev_score = 3
        elif dev < 3.0:  # Moderate
            dev_score = 2
        else:  # High deviation
            dev_score = 0

        details['deviation_score'] = dev_score
        score += dev_score

        return score, details

    def calculate_total_score(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Calculate total score (0-100 points)

        Returns:
            (total_score, breakdown_dict)
        """
        # Calculate all component scores
        trend_score, trend_details = self.score_trend_strength(df)
        momentum_score, momentum_details = self.score_momentum_quality(df)
        volume_score, volume_details = self.score_volume_profile(df)
        structure_score, structure_details = self.score_price_structure(df)
        risk_reward_score, risk_reward_details = self.score_risk_reward(df)
        trend_quality_score, trend_quality_details = self.score_trend_quality(df)

        total = trend_score + momentum_score + volume_score + \
                structure_score + risk_reward_score + trend_quality_score

        breakdown = {
            'total_score': total,
            'trend_strength': trend_score,
            'momentum_quality': momentum_score,
            'volume_profile': volume_score,
            'price_structure': structure_score,
            'risk_reward': risk_reward_score,
            'trend_quality': trend_quality_score,
            'details': {
                'trend': trend_details,
                'momentum': momentum_details,
                'volume': volume_details,
                'structure': structure_details,
                'risk_reward': risk_reward_details,
                'trend_quality': trend_quality_details
            }
        }

        return total, breakdown

    @staticmethod
    def assign_tier(score: float) -> str:
        """Assign tier based on score"""
        if score >= 80:
            return "Tier 1: Prime Movers"
        elif score >= 60:
            return "Tier 2: Solid Performers"
        elif score >= 40:
            return "Tier 3: Momentum Plays"
        else:
            return "Tier 4: Watch List"

    @staticmethod
    def adjust_tier_for_volatility(tier: str, volatility_20: float) -> str:
        """
        OPTION 1: Adjust tier based on volatility (if enabled in config)

        Rules:
        - Tier 1 + High Vol → Tier 2 (downgrade)
        - Tier 2 + Low Vol → Tier 1 (upgrade)
        - Tier 2 + High Vol → Tier 2 (no change)
        - Tier 3 + Low Vol → Tier 2 (upgrade)
        - Tier 3 + High Vol → Tier 3 (no change)
        - Tier 4 unchanged

        Args:
            tier: Current tier string
            volatility_20: 20-day volatility percentage

        Returns:
            Adjusted tier string
        """
        import config

        # Check if tier modifier is enabled
        if not getattr(config, 'ENABLE_VOLATILITY_TIER_MODIFIER', False):
            return tier  # Return unchanged if disabled

        # Get volatility thresholds from config
        vol_thresholds = getattr(config, 'VOLATILITY_TIER_THRESHOLDS', {
            'low': 25,
            'moderate': 40,
            'high': 40
        })

        low_threshold = vol_thresholds['low']
        high_threshold = vol_thresholds['high']

        # Determine volatility category
        is_low_vol = volatility_20 < low_threshold
        is_high_vol = volatility_20 > high_threshold

        # Apply tier adjustments
        if tier == "Tier 1: Prime Movers":
            if is_high_vol:
                logger.debug(f"Volatility modifier: Tier 1 → Tier 2 (high vol: {volatility_20:.1f}%)")
                return "Tier 2: Solid Performers"

        elif tier == "Tier 2: Solid Performers":
            if is_low_vol:
                logger.debug(f"Volatility modifier: Tier 2 → Tier 1 (low vol: {volatility_20:.1f}%)")
                return "Tier 1: Prime Movers"

        elif tier == "Tier 3: Momentum Plays":
            if is_low_vol:
                logger.debug(f"Volatility modifier: Tier 3 → Tier 2 (low vol: {volatility_20:.1f}%)")
                return "Tier 2: Solid Performers"

        # Tier 4 or no adjustment needed
        return tier


class UptrendScanner:
    """Main scanner class orchestrating the entire process"""

    def __init__(self, api_key: str, config: Optional[Dict] = None,
                 max_requests_per_minute: Optional[int] = None, strategy_id: Optional[str] = None):
        """
        Initialize scanner

        Args:
            api_key: Polygon.io API key
            config: Configuration dict
            max_requests_per_minute: API rate limit (None for unlimited)
            strategy_id: Strategy identifier (e.g., 'S1', 'S12', 'S1-3-5')
        """
        self.api = PolygonAPI(api_key, max_requests_per_minute=max_requests_per_minute)
        self.analyzer = TechnicalAnalyzer()
        self.classifier = UptrendClassifier()
        self.scorer = StockScorer(config)
        self.config = config or {}
        self.strategy_id = strategy_id

        # Update log file with strategy ID if provided
        if strategy_id:
            self._update_log_file(strategy_id)

    def _update_log_file(self, strategy_id: str):
        """
        Update the log file handler to include strategy ID in filename

        Args:
            strategy_id: Strategy identifier (e.g., 'S1', 'S12', 'S1-3-5')
        """
        global logger

        # Remove existing file handler
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)

        # Create new file handler with strategy ID in filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        strategy_suffix = f"_{strategy_id}" if strategy_id else ""
        log_filename = f'./output/logs/scan{strategy_suffix}_{timestamp}.log'

        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)

        # Create and add new file handler
        file_handler = logging.FileHandler(log_filename, mode='w')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Log file updated for strategy {strategy_id}: {log_filename}")

    def scan_stock(self, ticker: str, exchange: Optional[str] = None) -> Optional[Dict]:
        """
        Scan a single stock

        Args:
            ticker: Stock symbol
            exchange: Exchange code (e.g., 'XNAS', 'XNYS') - optional

        Returns:
            Dict with analysis results or None
        """
        # Get data (request 365 days to ensure we get at least 200 trading days)
        df = self.api.get_aggregates(ticker, days=365)
        if df is None or len(df) < 200:
            return None

        # Calculate indicators
        df = self.analyzer.calculate_all_indicators(df)

        # Classify uptrend type
        is_early, early_details = self.classifier.is_early_uptrend(df)
        is_established, established_details = self.classifier.is_established_uptrend(df)

        # Get ticker details (free float, shares outstanding)
        ticker_details = self.api.get_ticker_details(ticker)

        # Calculate effective volume (average volume as % of free float)
        # This shows how liquid the stock is relative to its float
        avg_volume = df['volume'].tail(50).mean()  # 50-day average volume
        float_shares = ticker_details.get('float_shares', 0)
        effective_volume_pct = (avg_volume / float_shares * 100) if float_shares > 0 else 0

        # Get latest row for technical indicators
        latest = df.iloc[-1]

        # Calculate smoothed price, velocity, and acceleration (Gaussian smoothing)
        derivatives = calculate_smoothed_velocity_acceleration(df, sigma=3)
        smoothed_price = derivatives['smoothed'].iloc[-1]
        velocity = derivatives['velocity'].iloc[-1]
        acceleration = derivatives['acceleration'].iloc[-1]

        result = {
            'ticker': ticker,
            'exchange': exchange,  # Add exchange info (XNAS=NASDAQ, XNYS=NYSE)
            'sector': ticker_details.get('sector', 'Unknown'),
            'industry_group': ticker_details.get('industry_group', 'Unknown'),
            'is_early_uptrend': is_early,
            'is_established_uptrend': is_established,
            'current_price': latest['close'],

            # Technical Indicators - Moving Averages
            'ma20': latest['ma_20'],
            'ma50': latest['ma_50'],
            'ma200': latest['ma_200'],

            # Technical Indicators - Momentum
            'rsi': latest['rsi'],
            'adx': latest['adx'],
            'macd': latest['macd'],
            'macd_signal': latest['macd_signal'],
            'macd_histogram': latest['macd_histogram'],

            # Technical Indicators - Bollinger Bands
            'bb_upper': latest['bb_upper'],
            'bb_middle': latest['bb_middle'],
            'bb_lower': latest['bb_lower'],

            # Smoothed Price / Velocity / Acceleration (Gaussian smoothing)
            'smoothed_price': smoothed_price,
            'velocity': velocity,
            'acceleration': acceleration,

            # Price relative to MAs (%)
            'pct_from_ma20': ((latest['close'] - latest['ma_20']) / latest['ma_20'] * 100) if latest['ma_20'] > 0 else 0,
            'pct_from_ma50': ((latest['close'] - latest['ma_50']) / latest['ma_50'] * 100) if latest['ma_50'] > 0 else 0,
            'pct_from_ma200': ((latest['close'] - latest['ma_200']) / latest['ma_200'] * 100) if latest['ma_200'] > 0 else 0,

            # Volume data
            'volume': latest['volume'],
            'avg_volume_50': avg_volume,

            # Volatility
            'volatility_20': latest['volatility_20'],
            'volatility_50': latest['volatility_50'],

            # Company info
            'shares_outstanding': ticker_details.get('shares_outstanding', 0),
            'float_shares': ticker_details.get('float_shares', 0),
            'free_float_pct': ticker_details.get('free_float_pct', 0),
            'market_cap': ticker_details.get('market_cap', 0),
            'effective_volume_pct': effective_volume_pct,
            'sic_code': ticker_details.get('sic_code', ''),
            'sic_description': ticker_details.get('sic_description', ''),

            # Uptrend classification details
            'early_details': early_details,
            'established_details': established_details
        }

        # Calculate score for ALL stocks (not just established uptrends)
        # This allows us to see scores even for stocks that don't qualify as uptrends
        score, breakdown = self.scorer.calculate_total_score(df)
        result['score'] = score
        tier = self.scorer.assign_tier(score)

        # OPTION 1: Apply volatility tier modifier (if enabled)
        tier = self.scorer.adjust_tier_for_volatility(tier, result['volatility_20'])
        result['tier'] = tier
        result['score_breakdown'] = breakdown

        return result

    def scan_market(self, exchanges: Optional[List[str]] = None,
                   ticker_type: str = 'CS',
                   min_price: float = 5.0,
                   min_volume: float = 500000,
                   min_market_cap: Optional[float] = None,
                   max_market_cap: Optional[float] = None,
                   min_free_float_shares: Optional[float] = None,
                   max_free_float_shares: Optional[float] = None,
                   min_free_float_pct: Optional[float] = None,
                   max_effective_volume_pct: Optional[float] = None,
                   max_stocks: Optional[int] = None) -> Dict:
        """
        Scan entire market

        Args:
            exchanges: List of exchanges ['XNAS', 'XNYS'] or None for all
            ticker_type: Type of ticker to filter ('CS' = common stock, None = all)
            min_price: Minimum stock price
            min_volume: Minimum average volume
            min_market_cap: Minimum market cap (None = no filter)
            max_market_cap: Maximum market cap (None = no limit)
            min_free_float_shares: Minimum free float shares (None = no filter)
            max_free_float_shares: Maximum free float shares (None = no filter)
            min_free_float_pct: Minimum free float percentage (None = no filter)
            max_effective_volume_pct: Maximum effective volume % of float (None = no limit)
            max_stocks: Max stocks to scan (for testing)

        Returns:
            Dict with 'early_uptrends' and 'established_uptrends' lists
        """
        logger.info("Fetching ticker list...")
        tickers = self.api.get_all_tickers(exchange=exchanges, ticker_type=ticker_type)

        # Filter tickers (keep both ticker and exchange info)
        filtered_tickers = []
        for ticker_data in tickers:
            ticker = ticker_data.get('ticker', '')

            # Skip complex tickers (ADRs, preferred shares, etc.)
            if any(char in ticker for char in ['.', '-', '^']):
                continue

            # Market cap filtering (if data available)
            if min_market_cap is not None or max_market_cap is not None:
                market_cap = ticker_data.get('market_cap')
                if market_cap is not None:
                    if min_market_cap is not None and market_cap < min_market_cap:
                        continue
                    if max_market_cap is not None and market_cap > max_market_cap:
                        continue

            # Store both ticker and exchange
            filtered_tickers.append({
                'ticker': ticker,
                'exchange': ticker_data.get('primary_exchange', 'Unknown')
            })

        if max_stocks:
            filtered_tickers = filtered_tickers[:max_stocks]

        logger.info(f"Scanning {len(filtered_tickers)} stocks...")

        early_uptrends = []
        established_uptrends = []
        all_scanned_stocks = []  # Track ALL scanned stocks

        for i, ticker_data in enumerate(filtered_tickers):
            ticker = ticker_data['ticker']
            exchange = ticker_data['exchange']

            # Print progress for every stock
            logger.info(f"[{i+1}/{len(filtered_tickers)}] Scanning {ticker}")

            result = self.scan_stock(ticker, exchange=exchange)
            if result is None:
                continue

            # Apply filters
            if result['current_price'] < min_price:
                continue

            # Apply free float filters
            if min_free_float_shares is not None:
                if result.get('float_shares', 0) < min_free_float_shares:
                    logger.debug(f"{ticker}: Float {result.get('float_shares', 0):,.0f} < {min_free_float_shares:,.0f} (filtered)")
                    continue

            if max_free_float_shares is not None:
                if result.get('float_shares', 0) > max_free_float_shares:
                    logger.debug(f"{ticker}: Float {result.get('float_shares', 0):,.0f} > {max_free_float_shares:,.0f} (filtered)")
                    continue

            if min_free_float_pct is not None:
                if result.get('free_float_pct', 0) < min_free_float_pct:
                    logger.debug(f"{ticker}: Free float {result.get('free_float_pct', 0):.1f}% < {min_free_float_pct}% (filtered)")
                    continue

            if max_effective_volume_pct is not None:
                if result.get('effective_volume_pct', 0) > max_effective_volume_pct:
                    logger.debug(f"{ticker}: Effective vol {result.get('effective_volume_pct', 0):.2f}% > {max_effective_volume_pct}% (filtered)")
                    continue

            # OPTION 3: Apply hard volatility filters by tier (if enabled)
            import config
            if getattr(config, 'ENABLE_VOLATILITY_FILTERS', False):
                tier = result.get('tier', '')
                volatility_20 = result.get('volatility_20', 0)

                # Get max volatility thresholds from config
                max_vol_tier1 = getattr(config, 'MAX_VOLATILITY_FOR_TIER_1', 35)
                max_vol_tier2 = getattr(config, 'MAX_VOLATILITY_FOR_TIER_2', 50)

                # Apply filters based on tier
                if "Tier 1" in tier and volatility_20 > max_vol_tier1:
                    logger.debug(f"{ticker}: Tier 1 vol {volatility_20:.1f}% > {max_vol_tier1}% (filtered)")
                    continue

                if "Tier 2" in tier and volatility_20 > max_vol_tier2:
                    logger.debug(f"{ticker}: Tier 2 vol {volatility_20:.1f}% > {max_vol_tier2}% (filtered)")
                    continue

            # Add to all scanned stocks (regardless of uptrend status)
            all_scanned_stocks.append(result)

            # Classify
            if result['is_early_uptrend']:
                early_uptrends.append(result)

            if result['is_established_uptrend']:
                established_uptrends.append(result)

        # Sort all lists by score (highest to lowest) for consistent ranking
        early_uptrends.sort(key=lambda x: x.get('score', 0), reverse=True)
        established_uptrends.sort(key=lambda x: x.get('score', 0), reverse=True)
        all_scanned_stocks.sort(key=lambda x: x.get('score', 0), reverse=True)

        logger.info(f"Scanned {len(all_scanned_stocks)} stocks total")
        logger.info(f"Found {len(early_uptrends)} early uptrends, "
                   f"{len(established_uptrends)} established uptrends")

        return {
            'early_uptrends': early_uptrends,
            'established_uptrends': established_uptrends,
            'all_scanned_stocks': all_scanned_stocks,
            'scan_date': datetime.now().isoformat()
        }

    def export_to_csv(self, results: Dict, output_dir: str = './output', strategy_id: str = None):
        """
        Export results to CSV files

        Args:
            results: Dictionary with scan results
            output_dir: Base output directory
            strategy_id: Strategy identifier (e.g., 'S1', 'S12', 'S1-3-5')
        """
        import os

        # Create directory structure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Add strategy identifier to filenames if provided
        strategy_suffix = f"_{strategy_id}" if strategy_id else ""

        # Create subdirectories for CSVs
        # New structure: output/csv/uptrend/early/, output/csv/uptrend/established/, output/csv/all_scanned/
        early_csv_dir = f"{output_dir}/csv/uptrend/early"
        established_csv_dir = f"{output_dir}/csv/uptrend/established"
        all_stocks_csv_dir = f"{output_dir}/csv/all_scanned"

        os.makedirs(early_csv_dir, exist_ok=True)
        os.makedirs(established_csv_dir, exist_ok=True)
        os.makedirs(all_stocks_csv_dir, exist_ok=True)

        # ====================================================================
        # EXPORT UPTRENDS (to ./output/csv/uptrend/early/ and established/)
        # ====================================================================

        # Export early uptrends
        if results['early_uptrends']:
            # Flatten early uptrend details into separate columns
            early_flat_data = []
            for stock in results['early_uptrends']:
                # Map exchange codes to readable names
                exchange_name = stock.get('exchange', 'Unknown')
                if exchange_name == 'XNAS':
                    exchange_display = 'NASDAQ'
                elif exchange_name == 'XNYS':
                    exchange_display = 'NYSE'
                else:
                    exchange_display = exchange_name

                early_details = stock.get('early_details', {})
                flat = {
                    # Sector/Industry first (per user requirement)
                    'sector': stock.get('sector', 'Unknown'),
                    'industry_group': stock.get('industry_group', 'Unknown'),
                    # Basic info (same as established)
                    'ticker': stock['ticker'],
                    'exchange': exchange_display,
                    'score': stock.get('score', 0),
                    'tier': stock.get('tier', ''),
                    'current_price': stock['current_price'],
                    'volatility_20': stock.get('volatility_20', 0),
                    'volatility_50': stock.get('volatility_50', 0),
                    'shares_outstanding': stock.get('shares_outstanding', 0),
                    'float_shares': stock.get('float_shares', 0),
                    'free_float_pct': stock.get('free_float_pct', 0),
                    'market_cap': stock.get('market_cap', 0),
                    'effective_volume_pct': stock.get('effective_volume_pct', 0),
                    'is_early_uptrend': stock.get('is_early_uptrend', False),
                    'is_established_uptrend': stock.get('is_established_uptrend', False),

                    # Score breakdown (same as established)
                    'trend_strength': stock['score_breakdown']['trend_strength'],
                    'momentum_quality': stock['score_breakdown']['momentum_quality'],
                    'volume_profile': stock['score_breakdown']['volume_profile'],
                    'price_structure': stock['score_breakdown']['price_structure'],
                    'risk_reward': stock['score_breakdown']['risk_reward'],
                    'trend_quality': stock['score_breakdown'].get('trend_quality', 0),

                    # Trend quality details (choppiness, efficiency ratio)
                    'choppiness_index': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('choppiness_index', 50.0),
                    'efficiency_ratio': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('efficiency_ratio', 0.0),

                    # Early uptrend specific indicators
                    'early_score': early_details.get('score', 0),
                    'ma20_cross_recent': early_details.get('ma20_cross_recent', False),
                    'volume_spike': early_details.get('volume_spike', False),
                    'rsi_healthy': early_details.get('rsi_healthy', False),
                    'rsi': early_details.get('rsi', 0),
                    'adx_rising': early_details.get('adx_rising', False),
                    'adx': early_details.get('adx', 0),
                    'macd_cross_recent': early_details.get('macd_cross_recent', False),
                    'breakout': early_details.get('breakout', False),
                }
                early_flat_data.append(flat)

            early_df = pd.DataFrame(early_flat_data)
            early_file = f"{early_csv_dir}/early_uptrends{strategy_suffix}_{timestamp}.csv"
            early_df.to_csv(early_file, index=False)
            logger.info(f"Saved early uptrends to {early_file}")

        # Export established uptrends
        if results['established_uptrends']:
            # Flatten the data for CSV
            flat_data = []
            for stock in results['established_uptrends']:
                # Map exchange codes to readable names
                exchange_name = stock.get('exchange', 'Unknown')
                if exchange_name == 'XNAS':
                    exchange_display = 'NASDAQ'
                elif exchange_name == 'XNYS':
                    exchange_display = 'NYSE'
                else:
                    exchange_display = exchange_name

                early_details = stock.get('early_details', {})
                flat = {
                    # Sector/Industry first (per user requirement)
                    'sector': stock.get('sector', 'Unknown'),
                    'industry_group': stock.get('industry_group', 'Unknown'),
                    # Basic info
                    'ticker': stock['ticker'],
                    'exchange': exchange_display,
                    'score': stock.get('score', 0),
                    'tier': stock.get('tier', ''),
                    'current_price': stock['current_price'],
                    'volatility_20': stock.get('volatility_20', 0),
                    'volatility_50': stock.get('volatility_50', 0),
                    'shares_outstanding': stock.get('shares_outstanding', 0),
                    'float_shares': stock.get('float_shares', 0),
                    'free_float_pct': stock.get('free_float_pct', 0),
                    'market_cap': stock.get('market_cap', 0),
                    'effective_volume_pct': stock.get('effective_volume_pct', 0),
                    'is_early_uptrend': stock.get('is_early_uptrend', False),
                    'is_established_uptrend': stock.get('is_established_uptrend', False),

                    # Score breakdown
                    'trend_strength': stock['score_breakdown']['trend_strength'],
                    'momentum_quality': stock['score_breakdown']['momentum_quality'],
                    'volume_profile': stock['score_breakdown']['volume_profile'],
                    'price_structure': stock['score_breakdown']['price_structure'],
                    'risk_reward': stock['score_breakdown']['risk_reward'],
                    'trend_quality': stock['score_breakdown'].get('trend_quality', 0),

                    # Trend quality details (choppiness, efficiency ratio)
                    'choppiness_index': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('choppiness_index', 50.0),
                    'efficiency_ratio': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('efficiency_ratio', 0.0),

                    # Early uptrend specific indicators (will be 0/False for established)
                    'early_score': early_details.get('score', 0),
                    'ma20_cross_recent': early_details.get('ma20_cross_recent', False),
                    'volume_spike': early_details.get('volume_spike', False),
                    'rsi_healthy': early_details.get('rsi_healthy', False),
                    'rsi': early_details.get('rsi', 0),
                    'adx_rising': early_details.get('adx_rising', False),
                    'adx': early_details.get('adx', 0),
                    'macd_cross_recent': early_details.get('macd_cross_recent', False),
                    'breakout': early_details.get('breakout', False),
                }
                flat_data.append(flat)

            est_df = pd.DataFrame(flat_data)
            est_file = f"{established_csv_dir}/established_uptrends{strategy_suffix}_{timestamp}.csv"
            est_df.to_csv(est_file, index=False)
            logger.info(f"Saved established uptrends to {est_file}")

        # ====================================================================
        # EXPORT ALL SCANNED STOCKS (to ./output/csv/all_scanned/)
        # ====================================================================

        if results.get('all_scanned_stocks'):
            # Flatten the data for CSV
            all_flat_data = []
            for stock in results['all_scanned_stocks']:
                # Map exchange codes to readable names
                exchange_name = stock.get('exchange', 'Unknown')
                if exchange_name == 'XNAS':
                    exchange_display = 'NASDAQ'
                elif exchange_name == 'XNYS':
                    exchange_display = 'NYSE'
                else:
                    exchange_display = exchange_name  # Keep original if not NASDAQ/NYSE

                early_details = stock.get('early_details', {})
                flat = {
                    # Sector/Industry first (per user requirement)
                    'sector': stock.get('sector', 'Unknown'),
                    'industry_group': stock.get('industry_group', 'Unknown'),
                    # Basic info
                    'ticker': stock['ticker'],
                    'exchange': exchange_display,
                    'score': stock.get('score', 0),
                    'tier': stock.get('tier', ''),
                    'current_price': stock['current_price'],
                    'volatility_20': stock.get('volatility_20', 0),
                    'volatility_50': stock.get('volatility_50', 0),
                    'shares_outstanding': stock.get('shares_outstanding', 0),
                    'float_shares': stock.get('float_shares', 0),
                    'free_float_pct': stock.get('free_float_pct', 0),
                    'market_cap': stock.get('market_cap', 0),
                    'effective_volume_pct': stock.get('effective_volume_pct', 0),
                    'is_early_uptrend': stock.get('is_early_uptrend', False),
                    'is_established_uptrend': stock.get('is_established_uptrend', False),

                    # Score breakdown
                    'trend_strength': stock['score_breakdown']['trend_strength'],
                    'momentum_quality': stock['score_breakdown']['momentum_quality'],
                    'volume_profile': stock['score_breakdown']['volume_profile'],
                    'price_structure': stock['score_breakdown']['price_structure'],
                    'risk_reward': stock['score_breakdown']['risk_reward'],
                    'trend_quality': stock['score_breakdown'].get('trend_quality', 0),

                    # Trend quality details (choppiness, efficiency ratio)
                    'choppiness_index': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('choppiness_index', 50.0),
                    'efficiency_ratio': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('efficiency_ratio', 0.0),

                    # Early uptrend specific indicators
                    'early_score': early_details.get('score', 0),
                    'ma20_cross_recent': early_details.get('ma20_cross_recent', False),
                    'volume_spike': early_details.get('volume_spike', False),
                    'rsi_healthy': early_details.get('rsi_healthy', False),
                    'rsi': early_details.get('rsi', 0),
                    'adx_rising': early_details.get('adx_rising', False),
                    'adx': early_details.get('adx', 0),
                    'macd_cross_recent': early_details.get('macd_cross_recent', False),
                    'breakout': early_details.get('breakout', False),
                }
                all_flat_data.append(flat)

            all_df = pd.DataFrame(all_flat_data)
            all_file = f"{all_stocks_csv_dir}/all_scanned{strategy_suffix}_{timestamp}.csv"
            all_df.to_csv(all_file, index=False)
            logger.info(f"Saved all {len(all_flat_data)} scanned stocks to {all_file}")

    def _prepare_stock_data_for_export(self, stock: Dict) -> Dict:
        """
        Helper method to prepare stock data for export (used by both CSV and Excel).
        Returns a flattened dictionary with sector/industry as first columns.
        """
        # Map exchange codes to readable names
        exchange_name = stock.get('exchange', 'Unknown')
        if exchange_name == 'XNAS':
            exchange_display = 'NASDAQ'
        elif exchange_name == 'XNYS':
            exchange_display = 'NYSE'
        else:
            exchange_display = exchange_name

        early_details = stock.get('early_details', {})

        # Get established details for days_in_uptrend
        established_details = stock.get('established_details', {})

        return {
            # Ticker first (per user requirement), then Sector/Industry
            'ticker': stock['ticker'],
            'sector': stock.get('sector', 'Unknown'),
            'industry_group': stock.get('industry_group', 'Unknown'),

            # Basic info
            'exchange': exchange_display,
            'score': stock.get('score', 0),
            'tier': stock.get('tier', ''),
            'current_price': stock.get('current_price', 0),

            # Technical Indicators - Moving Averages
            'ma20': stock.get('ma20', 0),
            'ma50': stock.get('ma50', 0),
            'ma200': stock.get('ma200', 0),

            # Price relative to MAs (%)
            'pct_from_ma20': stock.get('pct_from_ma20', 0),
            'pct_from_ma50': stock.get('pct_from_ma50', 0),
            'pct_from_ma200': stock.get('pct_from_ma200', 0),

            # Technical Indicators - Momentum
            'rsi': stock.get('rsi', early_details.get('rsi', 0)),
            'adx': stock.get('adx', early_details.get('adx', 0)),
            'macd': stock.get('macd', 0),
            'macd_signal': stock.get('macd_signal', 0),
            'macd_histogram': stock.get('macd_histogram', 0),

            # Technical Indicators - Bollinger Bands
            'bb_upper': stock.get('bb_upper', 0),
            'bb_middle': stock.get('bb_middle', 0),
            'bb_lower': stock.get('bb_lower', 0),

            # Smoothed Price / Velocity / Acceleration (Gaussian smoothing)
            'smoothed_price': stock.get('smoothed_price', 0),
            'velocity': stock.get('velocity', 0),
            'acceleration': stock.get('acceleration', 0),

            # Volume data
            'volume': stock.get('volume', 0),
            'avg_volume_50': stock.get('avg_volume_50', 0),

            # Volatility
            'volatility_20': stock.get('volatility_20', 0),
            'volatility_50': stock.get('volatility_50', 0),

            # Company info
            'shares_outstanding': stock.get('shares_outstanding', 0),
            'float_shares': stock.get('float_shares', 0),
            'free_float_pct': stock.get('free_float_pct', 0),
            'market_cap': stock.get('market_cap', 0),
            'effective_volume_pct': stock.get('effective_volume_pct', 0),

            # Uptrend classification
            'is_early_uptrend': stock.get('is_early_uptrend', False),
            'is_established_uptrend': stock.get('is_established_uptrend', False),
            'days_in_uptrend': established_details.get('days_in_uptrend', 0),
            'mas_stacked': established_details.get('mas_stacked', False),

            # Score breakdown
            'trend_strength': stock['score_breakdown']['trend_strength'],
            'momentum_quality': stock['score_breakdown']['momentum_quality'],
            'volume_profile': stock['score_breakdown']['volume_profile'],
            'price_structure': stock['score_breakdown']['price_structure'],
            'risk_reward': stock['score_breakdown']['risk_reward'],
            'trend_quality': stock['score_breakdown'].get('trend_quality', 0),

            # Trend quality details
            'choppiness_index': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('choppiness_index', 50.0),
            'efficiency_ratio': stock['score_breakdown'].get('details', {}).get('trend_quality', {}).get('efficiency_ratio', 0.0),

            # Early uptrend specific indicators
            'early_score': early_details.get('score', 0),
            'ma20_cross_recent': early_details.get('ma20_cross_recent', False),
            'volume_spike': early_details.get('volume_spike', False),
            'rsi_healthy': early_details.get('rsi_healthy', False),
            'adx_rising': early_details.get('adx_rising', False),
            'macd_cross_recent': early_details.get('macd_cross_recent', False),
            'breakout': early_details.get('breakout', False),
        }

    def export_to_excel(self, results: Dict, output_dir: str = './output', strategy_id: str = None):
        """
        Export results to Excel workbooks with multiple tabs.

        Creates 3 workbooks (one for each category: all_scanned, early, established).
        Each workbook contains:
        - Tab 1: "all" - All stocks sorted by score descending
        - Tab 2: "top20_per_sector" - Top 20 from each sector (or all if < 20)
        - Tabs 3-13: One tab per GICS sector with stocks in that sector

        Args:
            results: Dictionary with scan results
            output_dir: Base output directory
            strategy_id: Strategy identifier (e.g., 'S1', 'S12', 'S1-3-5')
        """
        import os

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        strategy_suffix = f"_{strategy_id}" if strategy_id else ""

        # Create Excel output directories (same structure as CSV)
        early_excel_dir = f"{output_dir}/excel/uptrend/early"
        established_excel_dir = f"{output_dir}/excel/uptrend/established"
        all_stocks_excel_dir = f"{output_dir}/excel/all_scanned"

        os.makedirs(early_excel_dir, exist_ok=True)
        os.makedirs(established_excel_dir, exist_ok=True)
        os.makedirs(all_stocks_excel_dir, exist_ok=True)

        def create_excel_workbook(stocks: List[Dict], output_path: str, workbook_type: str):
            """
            Create an Excel workbook with multiple tabs for a list of stocks.

            Args:
                stocks: List of stock dictionaries
                output_path: Path to save the Excel file
                workbook_type: Type identifier for logging ('all_scanned', 'early', 'established')
            """
            from openpyxl.styles import Font

            if not stocks:
                logger.info(f"No stocks to export for {workbook_type}")
                return

            # Prepare all stock data
            flat_data = [self._prepare_stock_data_for_export(stock) for stock in stocks]

            # Create main DataFrame sorted by score descending
            all_df = pd.DataFrame(flat_data)
            all_df = all_df.sort_values('score', ascending=False).reset_index(drop=True)

            # Define velocity colors
            velocity_positive_color = "5F9936"  # Green for positive velocity
            velocity_negative_color = "BA2020"  # Red for negative velocity

            def apply_velocity_formatting(worksheet, df):
                """Apply conditional font color to velocity column based on value."""
                # Find the velocity column index (1-based for openpyxl)
                columns = list(df.columns)
                if 'velocity' not in columns:
                    return

                velocity_col_idx = columns.index('velocity') + 1  # 1-based index

                # Apply formatting to each data row (skip header row 1)
                for row_idx in range(2, len(df) + 2):  # Start at row 2, go to len+1
                    cell = worksheet.cell(row=row_idx, column=velocity_col_idx)
                    try:
                        velocity_value = float(cell.value) if cell.value is not None else 0
                        if velocity_value > 0:
                            cell.font = Font(color=velocity_positive_color)
                        elif velocity_value < 0:
                            cell.font = Font(color=velocity_negative_color)
                    except (ValueError, TypeError):
                        pass  # Skip if value can't be converted to float

            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Tab 1: "all" - All stocks sorted by score
                all_df.to_excel(writer, sheet_name='all', index=False)
                apply_velocity_formatting(writer.sheets['all'], all_df)
                logger.debug(f"Created 'all' tab with {len(all_df)} stocks")

                # Tab 2: "top20_per_sector" - Top 20 (or all) from each sector
                top20_rows = []
                for sector in GICS_SECTORS:
                    sector_df = all_df[all_df['sector'] == sector].head(20)
                    if len(sector_df) > 0:
                        top20_rows.append(sector_df)

                if top20_rows:
                    top20_df = pd.concat(top20_rows, ignore_index=True)
                    # Sort by sector first, then by score within sector
                    top20_df = top20_df.sort_values(['sector', 'score'], ascending=[True, False]).reset_index(drop=True)
                    top20_df.to_excel(writer, sheet_name='top20_per_sector', index=False)
                    apply_velocity_formatting(writer.sheets['top20_per_sector'], top20_df)
                    logger.debug(f"Created 'top20_per_sector' tab with {len(top20_df)} stocks")

                # Tabs 3-13: One tab per GICS sector
                for sector in GICS_SECTORS:
                    sector_df = all_df[all_df['sector'] == sector].copy()
                    if len(sector_df) > 0:
                        # Excel sheet names have max 31 chars, truncate if needed
                        sheet_name = sector[:31] if len(sector) > 31 else sector
                        sector_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        apply_velocity_formatting(writer.sheets[sheet_name], sector_df)
                        logger.debug(f"Created '{sheet_name}' tab with {len(sector_df)} stocks")

            logger.info(f"Saved {workbook_type} Excel workbook to {output_path}")

        # Export ALL SCANNED stocks
        if results.get('all_scanned_stocks'):
            all_excel_file = f"{all_stocks_excel_dir}/all_scanned{strategy_suffix}_{timestamp}.xlsx"
            create_excel_workbook(results['all_scanned_stocks'], all_excel_file, 'all_scanned')

        # Export EARLY uptrends
        if results.get('early_uptrends'):
            early_excel_file = f"{early_excel_dir}/early_uptrends{strategy_suffix}_{timestamp}.xlsx"
            create_excel_workbook(results['early_uptrends'], early_excel_file, 'early_uptrends')

        # Export ESTABLISHED uptrends
        if results.get('established_uptrends'):
            established_excel_file = f"{established_excel_dir}/established_uptrends{strategy_suffix}_{timestamp}.xlsx"
            create_excel_workbook(results['established_uptrends'], established_excel_file, 'established_uptrends')

    def plot_stock_chart(self, ticker: str, output_dir: str = './output/charts', strategy_id: str = None, rank: int = None) -> Optional[str]:
        """
        Generate comprehensive chart for a stock showing price, indicators, and analysis.
        Uses same methodology as stock_trend_analyzer with Gaussian smoothing and
        velocity/acceleration panel with quadrant shading.

        Args:
            ticker: Stock ticker symbol
            output_dir: Directory to save charts
            strategy_id: Strategy identifier (e.g., 'S1', 'S2')
            rank: Optional rank number for filename prefix (e.g., 1 -> '01_')

        Returns:
            Path to saved chart file or None if failed
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Display period and warmup calculation
        display_days = 252  # ~1 year of trading days to display
        warmup_days = 200   # SMA200 requires 200 days of data before it's valid
        # Request extra days: display + warmup + buffer for weekends/holidays
        # 252 display + 200 warmup = 452 trading days
        # 452 * 7/5 ≈ 633 calendar days, add buffer = 700 calendar days
        fetch_days = 700

        # Get stock data with enough history for SMA200 warmup
        df = self.api.get_aggregates(ticker, days=fetch_days)
        if df is None or len(df) < warmup_days:
            logger.warning(f"Insufficient data to plot {ticker}")
            return None

        # Calculate ALL indicators on FULL data FIRST (before trimming)
        # This ensures SMA200 and Bollinger Bands have valid values from the start of display
        df = self.analyzer.calculate_all_indicators(df)

        # Get analysis results
        result = self.scan_stock(ticker)
        if result is None:
            logger.warning(f"Failed to analyze {ticker}")
            return None

        # Calculate Gaussian smoothed price, velocity, and acceleration on FULL data
        derivatives = calculate_smoothed_velocity_acceleration(df, sigma=3)

        # Detect swing points on FULL data
        df = detect_swing_points(df, window=5)

        # Now trim to display period AFTER all indicators are calculated
        # This ensures indicators have valid values from the start of display
        if len(df) > display_days:
            # Create display mask for last N days
            display_mask = pd.Series([False] * (len(df) - display_days) + [True] * display_days, index=df.index)

            # Apply mask to data and all indicator series
            df = df[display_mask]
            smoothed = derivatives['smoothed'][display_mask]
            velocity = derivatives['velocity'][display_mask]
            acceleration = derivatives['acceleration'][display_mask]
        else:
            smoothed = derivatives['smoothed']
            velocity = derivatives['velocity']
            acceleration = derivatives['acceleration']

        # Create sequential x-axis positions to eliminate gaps
        x_positions = np.arange(len(df))

        # Create figure with 5-panel layout (same as stock_trend_analyzer)
        # Height ratios: Price (2.5), Volume (0.7), RSI (0.7), Velocity/Acceleration (0.7), Summary (1.0)
        fig = plt.figure(figsize=(22, 16))
        gs = GridSpec(5, 1, figure=fig, height_ratios=[2.5, 0.7, 0.7, 0.7, 1.0], hspace=0.0)

        # Get date range for display
        date_range = f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"

        # ============================================
        # PANEL 1: PRICE WITH BOLLINGER BANDS AND MAs
        # ============================================
        ax1 = fig.add_subplot(gs[0])

        # Draw candlesticks
        candle_width = 0.8
        wick_width = 1.0

        # FIRST PASS: Draw ALL wicks (behind bodies)
        for i in range(len(df)):
            high_price = df['high'].iloc[i]
            low_price = df['low'].iloc[i]
            ax1.plot([x_positions[i], x_positions[i]], [low_price, high_price],
                     color='black', linewidth=wick_width, alpha=1.0, zorder=2)

        # SECOND PASS: Draw ALL bodies (on top of wicks)
        for i in range(len(df)):
            open_price = df['open'].iloc[i]
            close_price = df['close'].iloc[i]

            # Determine color: green for up, red for down
            if close_price >= open_price:
                body_color = '#56B05C'  # Green
            else:
                body_color = '#F77272'  # Light red

            body_bottom = min(open_price, close_price)
            body_height = abs(close_price - open_price)

            # If open == close, draw a small horizontal line (doji)
            if body_height == 0:
                ax1.plot([x_positions[i] - candle_width/2, x_positions[i] + candle_width/2],
                         [close_price, close_price], color=body_color, linewidth=1, zorder=3)
            else:
                rect = plt.Rectangle((x_positions[i] - candle_width/2, body_bottom),
                                      candle_width, body_height,
                                      facecolor=body_color, edgecolor=body_color,
                                      linewidth=0.5, alpha=1.0, zorder=3)
                ax1.add_patch(rect)

        # Plot moving averages (using sequential positions)
        ax1.plot(x_positions, df['ma_50'].values, label='MA50', color='orange', linewidth=1, alpha=0.7)
        # SMA 200 in magenta (dashed)
        ax1.plot(x_positions, df['ma_200'].values, label='SMA 200', color='magenta', linewidth=1.5, linestyle='--', alpha=0.8)

        # Bollinger Bands - draw boundary lines and fill
        ax1.plot(x_positions, df['bb_upper'].values, label='Upper BB (2σ)', color='g', linewidth=1, alpha=0.7, linestyle='--')
        ax1.plot(x_positions, df['bb_middle'].values, label='SMA (20)', color='b', linewidth=1)
        ax1.plot(x_positions, df['bb_lower'].values, label='Lower BB (2σ)', color='r', linewidth=1, alpha=0.7, linestyle='--')
        ax1.fill_between(x_positions, df['bb_lower'].values, df['bb_upper'].values, alpha=0.1, color='gray')

        # Smoothed price line (solid blue)
        ax1.plot(x_positions, smoothed.values, label='Smoothed', color=SMOOTHED_COLOR,
                 linewidth=1.2, alpha=0.8)

        # Add swing point labels (HH, HL, LH, LL)
        if 'swing_label' in df.columns:
            for idx in range(len(df)):
                label = df['swing_label'].iloc[idx]
                if label and label in SWING_LABEL_COLORS:
                    is_major = df['is_major_swing'].iloc[idx]

                    # Position label above highs, below lows
                    if label in ['HH', 'LH']:
                        y_pos = df['high'].iloc[idx]
                        va = 'bottom'
                        offset = df['high'].iloc[idx] * 0.01  # 1% offset
                    else:  # HL, LL
                        y_pos = df['low'].iloc[idx]
                        va = 'top'
                        offset = -df['low'].iloc[idx] * 0.01

                    # Same font size for all, but bold for major swings
                    fontweight = 'bold' if is_major else 'normal'
                    alpha = 1.0 if is_major else 0.7

                    ax1.annotate(label, xy=(x_positions[idx], y_pos + offset),
                                fontsize=8, fontweight=fontweight,
                                color=SWING_LABEL_COLORS[label],
                                ha='center', va=va, alpha=alpha,
                                zorder=6)

        # Title with score
        title = f'{ticker} - Uptrend Analysis | Score: {int(result["score"])}/100 | {result["tier"]}'
        ax1.set_title(title, fontsize=16, fontweight='bold')

        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.6)

        # Format x-axis with ticks but no date labels on price chart
        ax1.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax1.tick_params(axis='x', which='major', direction='in', length=8)
        ax1.tick_params(axis='x', which='minor', direction='in', length=5)
        ax1.tick_params(axis='x', which='major', labeltop=False, labelbottom=False)

        # Add secondary y-axis for price on right side
        ax1_right = ax1.twinx()
        ax1_right.set_ylim(ax1.get_ylim())
        ax1_right.set_ylabel('Price ($)', fontsize=12)

        # Add earnings markers ('E' on chart)
        try:
            earnings_dates = self.api.get_earnings_dates(ticker, days=365)
            if earnings_dates:
                y_min, y_max = ax1.get_ylim()
                y_pos = y_min

                for earn_date in earnings_dates:
                    earn_date_compare = pd.to_datetime(earn_date).date() if isinstance(earn_date, str) else earn_date.date() if hasattr(earn_date, 'date') else earn_date

                    for idx, (i, row) in enumerate(df.iterrows()):
                        row_date = i.date() if hasattr(i, 'date') else i
                        if row_date == earn_date_compare:
                            ax1.annotate('E', xy=(x_positions[idx], y_pos),
                                        fontsize=10, fontweight='bold',
                                        color='purple', ha='center', va='bottom',
                                        zorder=7)
                            break
        except Exception as e:
            logger.debug(f"Could not add earnings markers: {e}")

        # Add timestamp at lower right of price chart
        chart_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ax1.text(0.98, 0.02, f'Generated: {chart_timestamp}',
                transform=ax1.transAxes, fontsize=8,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        # ============================================
        # PANEL 2: VOLUME WITH EMA5/EMA20 ON SECONDARY AXIS
        # ============================================
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        # Plot volume bars - color based on price movement
        colors = ['green' if df['close'].iloc[i] >= df['open'].iloc[i] else 'red'
                  for i in range(len(df))]
        ax2.bar(x_positions, df['volume'].values, color=colors, alpha=0.65, width=0.8)

        # Volume MA50 on left axis
        vol_line = ax2.plot(x_positions, df['volume_ma_50'].values, label='Volume MA (50)', color='purple', linewidth=2, alpha=0.8)
        ax2.set_ylabel('Volume', fontsize=10)
        ax2.grid(True, alpha=0.6)
        ax2.tick_params(axis='x', which='major', direction='in', length=8)
        ax2.tick_params(axis='x', which='minor', direction='in', length=5)
        plt.setp(ax2.get_xticklabels(), visible=False)

        # Add secondary y-axis for SMAs (right side)
        ax2_price = ax2.twinx()
        price_ema5 = df['close'].ewm(span=5, adjust=False).mean()
        price_ema20 = df['close'].ewm(span=20, adjust=False).mean()
        ema5_line = ax2_price.plot(x_positions, price_ema5.values, label='SMA (5)', color='orange', linewidth=1, alpha=0.8)
        ema20_line = ax2_price.plot(x_positions, price_ema20.values, label='SMA (20)', color='blue', linewidth=1, alpha=0.8)
        ax2_price.set_ylabel('Price ($)', fontsize=10)
        ax2_price.tick_params(axis='y', labelsize=9)

        # Combine legends from both axes
        lines = vol_line + ema5_line + ema20_line
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper left', fontsize=8)

        # ============================================
        # PANEL 3: RSI WITH COLOR CODING
        # ============================================
        ax3 = fig.add_subplot(gs[2], sharex=ax1)

        # Plot RSI with color segments
        rsi = df['rsi']
        for i in range(len(rsi) - 1):
            if pd.isna(rsi.iloc[i]) or pd.isna(rsi.iloc[i + 1]):
                continue
            x = [x_positions[i], x_positions[i + 1]]
            y = [rsi.iloc[i], rsi.iloc[i + 1]]
            color = get_rsi_color(rsi.iloc[i])
            ax3.plot(x, y, color=color, linewidth=1)

        # Add horizontal reference lines
        ax3.axhline(y=70, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
        ax3.axhline(y=30, color='green', linestyle='--', linewidth=0.8, alpha=0.7)
        ax3.axhline(y=50, color='magenta', linestyle='-', linewidth=1, alpha=0.8)

        # Shade overbought/oversold regions
        ax3.fill_between(x_positions, 70, 100, alpha=0.1, color='red')
        ax3.fill_between(x_positions, 0, 30, alpha=0.1, color='green')

        ax3.set_ylabel('RSI (14)', fontsize=8)
        ax3.set_ylim(0, 100)

        # Create custom legend for RSI colors
        rsi_legend_elements = [
            mpatches.Patch(color=RSI_COLOR_OVERSOLD, label='RSI < 30 (Oversold)'),
            mpatches.Patch(color=RSI_COLOR_BEARISH, label='RSI 30-50 (Bearish)'),
            mpatches.Patch(color=RSI_COLOR_BULLISH, label='RSI 50-70 (Bullish)'),
            mpatches.Patch(color=RSI_COLOR_OVERBOUGHT, label='RSI > 70 (Overbought)')
        ]
        ax3.legend(handles=rsi_legend_elements, loc='upper left', fontsize=8, ncol=2)

        # Add current RSI value annotation
        if not pd.isna(rsi.iloc[-1]):
            current_rsi = rsi.iloc[-1]
            rsi_color = get_rsi_color(current_rsi)
            ax3.text(0.98, 0.95, f'Current RSI: {current_rsi:.1f}',
                    transform=ax3.transAxes, fontsize=10, fontweight='bold',
                    ha='right', va='top', color=rsi_color,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax3.grid(True, alpha=0.6)
        ax3.tick_params(axis='y', labelsize=8)
        ax3.tick_params(axis='x', which='major', direction='in', length=8)
        ax3.tick_params(axis='x', which='minor', direction='in', length=5)
        plt.setp(ax3.get_xticklabels(), visible=False)

        # ============================================
        # PANEL 4: VELOCITY & ACCELERATION (SHOWS DATES)
        # ============================================
        ax4 = fig.add_subplot(gs[3], sharex=ax1)

        # Velocity line (left Y axis) - blue
        ax4.plot(x_positions, velocity.values, color=VELOCITY_COLOR,
                 linewidth=1.2, label='Velocity', alpha=1.0)
        ax4.axhline(y=0, color=VELOCITY_COLOR, linestyle='-', linewidth=0.8, alpha=1.0)
        ax4.set_ylabel('Velocity', color=VELOCITY_COLOR, fontsize=10)
        ax4.tick_params(axis='y', labelcolor=VELOCITY_COLOR, labelsize=8)
        ax4.grid(True, alpha=0.3)

        # Acceleration line (right Y axis) - gold/amber
        ax4_right = ax4.twinx()
        ax4_right.plot(x_positions, acceleration.values, color=ACCEL_COLOR,
                       linewidth=1.2, label='Acceleration', alpha=0.8)
        ax4_right.axhline(y=0, color=ACCEL_COLOR, linestyle='-', linewidth=0.8, alpha=1.0)
        ax4_right.set_ylabel('Acceleration', color=ACCEL_COLOR, fontsize=10)
        ax4_right.tick_params(axis='y', labelcolor=ACCEL_COLOR, labelsize=8)

        # Shaded regions based on velocity/acceleration sign combinations
        vel_values = velocity.values
        acc_values = acceleration.values

        for i in range(len(vel_values)):
            vel_pos = vel_values[i] > 0
            acc_pos = acc_values[i] > 0

            if vel_pos and acc_pos:
                color = COLOR_VEL_POS_ACC_POS  # Bright green - rising & steepening
            elif vel_pos and not acc_pos:
                color = COLOR_VEL_POS_ACC_NEG  # Medium green - rising but flattening
            elif not vel_pos and acc_pos:
                color = COLOR_VEL_NEG_ACC_POS  # Medium red - falling but flattening
            else:
                color = COLOR_VEL_NEG_ACC_NEG  # Bright red - falling & steepening

            # Shade a vertical bar for this data point
            if i < len(x_positions):
                width = 1 if i == len(x_positions) - 1 else x_positions[min(i+1, len(x_positions)-1)] - x_positions[i]
                ax4.axvspan(x_positions[i], x_positions[i] + width,
                           facecolor=color, alpha=0.35, zorder=0)

        # =================================================================
        # Draw SOLID vertical lines at velocity zero crossings
        # =================================================================
        axes_for_vlines = [ax1, ax2, ax3, ax4]

        # Detect velocity zero crossings
        velocity_crossings = []
        for i in range(1, len(vel_values)):
            if vel_values[i-1] * vel_values[i] < 0:  # Sign change = zero crossing
                is_bullish = vel_values[i-1] < 0 and vel_values[i] > 0
                velocity_crossings.append((i, is_bullish))

        # Draw SOLID vertical lines at velocity zero crossings
        for idx, is_bullish in velocity_crossings:
            line_color = RSI_COLOR_BULLISH if is_bullish else 'darkorange'
            for ax in axes_for_vlines:
                ax.axvline(x=x_positions[idx], color=line_color, linestyle='-', alpha=1.0, linewidth=1.5)

        # Combined legend for velocity and acceleration
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_right.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

        # Calculate appropriate tick positions and labels
        num_ticks = min(10, len(df))
        tick_positions = np.linspace(0, len(df) - 1, num_ticks, dtype=int)
        tick_labels = [df.index[i].strftime('%m/%d/%y') for i in tick_positions]

        # Set x-axis limits with 3-day gap on the right
        x_min = 0
        x_max = len(df) - 1 + 3

        ax4.set_xlim(x_min, x_max)
        ax4.set_xticks(tick_positions)
        ax4.set_xticklabels(tick_labels, rotation=45, ha='right')
        ax4.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax4.tick_params(axis='x', which='major', direction='inout', length=10)
        ax4.tick_params(axis='x', which='minor', direction='inout', length=7)
        ax4.tick_params(axis='x', labelsize=9)

        # ============================================
        # PANEL 5: ANALYSIS SUMMARY
        # ============================================
        ax5 = fig.add_subplot(gs[4])
        ax5.axis('off')

        # Calculate days since breakout and get indicator values
        breakdown = result['score_breakdown']
        trend_details = breakdown['details']['trend']
        days_in_uptrend = trend_details.get('days_in_uptrend', 0)

        # Get RSI, ADX, and Volatility values from the latest data
        rsi_value = df.iloc[-1]['rsi']
        adx_value = df.iloc[-1]['adx']
        vol_20_value = df.iloc[-1]['volatility_20']

        # Get velocity and acceleration values
        latest_velocity = velocity.iloc[-1] if not pd.isna(velocity.iloc[-1]) else 0
        latest_accel = acceleration.iloc[-1] if not pd.isna(acceleration.iloc[-1]) else 0

        # Get free float data
        float_shares = result.get('float_shares', 0)
        float_millions = float_shares / 1_000_000 if float_shares > 0 else 0
        effective_vol_pct = result.get('effective_volume_pct', 0)

        # Build summary text with velocity/acceleration info
        info_text = f"ANALYSIS SUMMARY\n{'='*170}\n\n"
        info_text += f"Price: ${result['current_price']:.2f}  |  Score: {int(result['score'])}/100  |  RSI: {rsi_value:.1f}  |  Velocity: {latest_velocity:.4f}  |  Accel: {latest_accel:.4f}  |  ADX: {adx_value:.1f}  |  Vol(20d): {vol_20_value:.1f}%\n\n"
        info_text += f"Trend Strength: {int(breakdown['trend_strength'])}/25  |  Momentum Quality: {int(breakdown['momentum_quality'])}/20  |  Volume Profile: {int(breakdown['volume_profile'])}/20\n"
        info_text += f"Price Structure: {int(breakdown['price_structure'])}/20  |  Risk/Reward: {int(breakdown['risk_reward'])}/15  |  Days Above SMA20: {days_in_uptrend}  |  Float: {float_millions:.1f}M\n"
        info_text += f"\nDate Range: {date_range}\n"

        ax5.text(0.0, 0.95, info_text, transform=ax5.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        # ============================================
        # FINAL SAVE
        # ============================================

        # Adjust layout to center plots with balanced margins
        plt.subplots_adjust(left=0.08, right=0.92, top=0.97, bottom=0.05)

        # Save chart
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        strategy_suffix = f"_{strategy_id}" if strategy_id else ""
        rank_prefix = f"{rank:02d}_" if rank is not None else ""
        chart_file = f"{output_dir}/{rank_prefix}{ticker}{strategy_suffix}_{timestamp}.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        logger.info(f"Saved chart for {ticker} to {chart_file}")
        return chart_file

    def plot_watchlist(self, stocks: List[Dict], output_dir: str = './output/charts', strategy_id: str = None) -> List[str]:
        """
        Generate individual charts for a list of stocks

        Args:
            stocks: List of stock dictionaries (from scan results)
            output_dir: Directory to save charts
            strategy_id: Strategy identifier (e.g., 'S1', 'S2')

        Returns:
            List of paths to saved chart files
        """
        chart_files = []

        for i, stock in enumerate(stocks, 1):
            ticker = stock['ticker']
            logger.info(f"Generating chart {i}/{len(stocks)}: {ticker}")

            chart_file = self.plot_stock_chart(ticker, output_dir, strategy_id, rank=i)
            if chart_file:
                chart_files.append(chart_file)

        logger.info(f"Generated {len(chart_files)} charts in {output_dir}")
        return chart_files

    def plot_watchlist_by_sector(self, stocks: List[Dict], output_dir: str = './output/charts',
                                  strategy_id: str = None, charts_per_sector: int = 20,
                                  include_all_folder: bool = True, max_all_charts: int = None) -> Dict[str, List[str]]:
        """
        Generate charts organized by GICS sector into subfolders.

        Creates sector subfolders with top N stocks per sector, plus optionally
        an 'all' folder with top stocks overall.

        Args:
            stocks: List of stock dictionaries (from scan results)
            output_dir: Base directory to save charts (sector folders created inside)
            strategy_id: Strategy identifier (e.g., 'S1', 'S2')
            charts_per_sector: Number of top charts per sector (e.g., ZZ=20, YY=10, XX=10)
            include_all_folder: If True, create 'all' folder with top stocks overall
            max_all_charts: Max charts in 'all' folder (defaults to NUM_CHARTS_TO_PLOT)

        Returns:
            Dict mapping folder names to list of chart file paths
        """
        import os
        import config
        from collections import defaultdict

        if max_all_charts is None:
            max_all_charts = config.NUM_CHARTS_TO_PLOT

        chart_files_by_folder = defaultdict(list)

        # Sort stocks by score descending
        sorted_stocks = sorted(stocks, key=lambda x: x.get('score', 0), reverse=True)

        # Group stocks by sector
        stocks_by_sector = defaultdict(list)
        for stock in sorted_stocks:
            sector = stock.get('sector', 'Unknown')
            stocks_by_sector[sector].append(stock)

        # 1. Generate charts for 'all' folder (top stocks overall)
        if include_all_folder:
            all_dir = f"{output_dir}/all"
            os.makedirs(all_dir, exist_ok=True)

            all_stocks_to_plot = sorted_stocks[:max_all_charts]
            logger.info(f"Generating {len(all_stocks_to_plot)} charts in 'all' folder...")

            for i, stock in enumerate(all_stocks_to_plot, 1):
                ticker = stock['ticker']
                logger.info(f"[all {i}/{len(all_stocks_to_plot)}] Generating chart: {ticker}")

                chart_file = self.plot_stock_chart(ticker, all_dir, strategy_id, rank=i)
                if chart_file:
                    chart_files_by_folder['all'].append(chart_file)

        # 2. Generate charts for each sector folder
        for sector in GICS_SECTORS:
            sector_stocks = stocks_by_sector.get(sector, [])
            if not sector_stocks:
                continue

            # Take top N stocks for this sector
            sector_stocks_to_plot = sector_stocks[:charts_per_sector]

            # Create sector folder
            sector_dir = f"{output_dir}/{sector}"
            os.makedirs(sector_dir, exist_ok=True)

            logger.info(f"Generating {len(sector_stocks_to_plot)} charts in '{sector}' folder...")

            for i, stock in enumerate(sector_stocks_to_plot, 1):
                ticker = stock['ticker']
                logger.info(f"[{sector[:15]} {i}/{len(sector_stocks_to_plot)}] Generating chart: {ticker}")

                chart_file = self.plot_stock_chart(ticker, sector_dir, strategy_id, rank=i)
                if chart_file:
                    chart_files_by_folder[sector].append(chart_file)

        # Log summary
        total_charts = sum(len(files) for files in chart_files_by_folder.values())
        logger.info(f"Generated {total_charts} total charts across {len(chart_files_by_folder)} folders")

        for folder, files in chart_files_by_folder.items():
            logger.debug(f"  {folder}: {len(files)} charts")

        return dict(chart_files_by_folder)
