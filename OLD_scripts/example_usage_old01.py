"""
Example Usage Scripts for Uptrend Momentum Scanner
===================================================

This file demonstrates 12 different scanning strategies and use cases.

Usage:
    python example_usage.py <strategy_number>

    Example:
    python example_usage.py 1   # Run Strategy 1: Quick test scan
    python example_usage.py 12  # Run Strategy 12: Micro cap momentum
"""

import sys
from uptrend_scanner import UptrendScanner
import config


def export_and_plot_results(scanner, results, num_charts=None, strategy_id=None):
    """
    Helper function to export CSVs and generate charts for both uptrends and all scanned stocks

    Args:
        scanner: UptrendScanner instance
        results: Scan results dictionary
        num_charts: Number of charts to generate (defaults to config.NUM_CHARTS_TO_PLOT)
        strategy_id: Strategy identifier (e.g., 'S1', 'S12') for file naming
    """
    from datetime import datetime

    if num_charts is None:
        num_charts = config.NUM_CHARTS_TO_PLOT

    # Generate timestamp for this scan
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Add strategy suffix for directory and file names
    strategy_suffix = f"_{strategy_id}" if strategy_id else ""

    # Export all CSVs (uptrends + all scanned stocks)
    scanner.export_to_csv(results, strategy_id=strategy_id)

    # Generate charts for established uptrend stocks (to ./output/uptrends/charts/established/established_Sx_TIMESTAMP/)
    if results['established_uptrends']:
        top_established = results['established_uptrends'][:num_charts]
        established_dir = f'./output/uptrends/charts/established/established{strategy_suffix}_{timestamp}'
        print(f"\n{'='*70}")
        print(f"Generating {len(top_established)} charts for established uptrend stocks...")
        print("=" * 70)
        established_chart_files = scanner.plot_watchlist(top_established, output_dir=established_dir, strategy_id=strategy_id)
        print(f"✓ Generated {len(established_chart_files)} established uptrend charts in {established_dir}/")

    # Generate charts for early uptrend stocks (to ./output/uptrends/charts/early/early_Sx_TIMESTAMP/)
    if results['early_uptrends']:
        top_early = results['early_uptrends'][:num_charts]
        early_dir = f'./output/uptrends/charts/early/early{strategy_suffix}_{timestamp}'
        print(f"\n{'='*70}")
        print(f"Generating {len(top_early)} charts for early uptrend stocks...")
        print("=" * 70)
        early_chart_files = scanner.plot_watchlist(top_early, output_dir=early_dir, strategy_id=strategy_id)
        print(f"✓ Generated {len(early_chart_files)} early uptrend charts in {early_dir}/")

    # Generate charts for ALL scanned stocks (to ./output/all_scanned/charts/charts_TIMESTAMP/)
    if results.get('all_scanned_stocks'):
        # Determine how many charts to generate for all_scanned stocks
        # Priority: USE_NUM_CHARTS_FOR_ALL_SCANNED controls behavior
        # False (default): Generate charts for ALL scanned stocks (respects MAX_STOCKS_TO_SCAN)
        # True: Limit to NUM_CHARTS_TO_PLOT
        if config.USE_NUM_CHARTS_FOR_ALL_SCANNED:
            num_all_scanned_charts = num_charts
            all_stocks = results['all_scanned_stocks'][:num_all_scanned_charts]
        else:
            # Use all scanned stocks (they're already limited by MAX_STOCKS_TO_SCAN during scanning)
            all_stocks = results['all_scanned_stocks']
            num_all_scanned_charts = len(all_stocks)

        all_scanned_dir = f'./output/all_scanned/charts/charts{strategy_suffix}_{timestamp}'
        print(f"\n{'='*70}")
        print(f"Generating {len(all_stocks)} charts for all scanned stocks...")
        if config.USE_NUM_CHARTS_FOR_ALL_SCANNED:
            print(f"(Limited by NUM_CHARTS_TO_PLOT={num_charts})")
        else:
            print(f"(Using all scanned stocks - controlled by MAX_STOCKS_TO_SCAN)")
        print("=" * 70)
        all_chart_files = scanner.plot_watchlist(all_stocks, output_dir=all_scanned_dir, strategy_id=strategy_id)
        print(f"✓ Generated {len(all_chart_files)} charts in {all_scanned_dir}/")

    print(f"\n{'='*70}")
    print("OUTPUT SUMMARY:")
    print("=" * 70)
    print(f"  Early Uptrends CSV:          ./output/uptrends/csv/early/early_uptrends{strategy_suffix}_{timestamp}.csv")
    print(f"  Established Uptrends CSV:    ./output/uptrends/csv/established/established_uptrends{strategy_suffix}_{timestamp}.csv")
    print(f"  Established Uptrends Charts: ./output/uptrends/charts/established/established{strategy_suffix}_{timestamp}/")
    print(f"  Early Uptrends Charts:       ./output/uptrends/charts/early/early{strategy_suffix}_{timestamp}/")
    print(f"  All Scanned CSV:             ./output/all_scanned/csv/all_scanned{strategy_suffix}_{timestamp}.csv")
    print(f"  All Scanned Charts:          ./output/all_scanned/charts/charts{strategy_suffix}_{timestamp}/")
    print("=" * 70)


def strategy_1_quick_test():
    """
    Strategy 1: Quick Test Scan (50 stocks)
    =======================================
    Purpose: Test the system quickly with limited stocks
    Use case: Initial setup, testing, debugging
    """
    print("=" * 70)
    print(f"STRATEGY 1: Quick Test Scan ({config.MAX_STOCKS_TO_SCAN} stocks)")
    print("=" * 70)

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S1')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_1['min_price'],
        min_volume=config.STRATEGY_1['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    print(f"\nResults:")
    print(f"All scanned stocks: {len(results.get('all_scanned_stocks', []))}")
    print(f"Early uptrends: {len(results['early_uptrends'])}")
    print(f"Established uptrends: {len(results['established_uptrends'])}")

    # Show top 5 established uptrends
    if results['established_uptrends']:
        print("\nTop 5 Established Uptrends:")
        for stock in results['established_uptrends'][:5]:
            print(f"  {stock['ticker']}: Score {stock['score']:.1f} - {stock['tier']}")

    # Export CSVs and generate charts for both uptrends and all scanned stocks
    export_and_plot_results(scanner, results, strategy_id='S1')


def strategy_2_full_market_scan():
    """
    Strategy 2: Full Market Scan
    ============================
    Purpose: Scan entire NYSE + NASDAQ
    Use case: Daily after-market scan, weekend analysis
    """
    print("=" * 70)
    print("STRATEGY 2: Full Market Scan (All NYSE + NASDAQ)")
    print("=" * 70)
    print("This will take 1-2 hours depending on API rate limits...")

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S2')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.MIN_PRICE,
        min_volume=config.MIN_VOLUME,
        max_stocks=None  # No limit - scan all
    )

    print(f"\nResults:")
    print(f"Early uptrends: {len(results['early_uptrends'])}")
    print(f"Established uptrends: {len(results['established_uptrends'])}")

    # Show tier breakdown
    tier_counts = {}
    for stock in results['established_uptrends']:
        tier = stock['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("\nTier Breakdown:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  {tier}: {count} stocks")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S2')


def strategy_3_large_cap_quality():
    """
    Strategy 3: Large Cap Quality Focus
    ===================================
    Purpose: Find high-quality large cap uptrends
    Use case: Conservative position trading, retirement accounts
    """
    print("=" * 70)
    print("STRATEGY 3: Large Cap Quality Focus")
    print("=" * 70)

    # Custom config for quality focus
    quality_config = {
        'weights': {
            'trend_strength': 30,  # Increase trend weight
            'momentum_quality': 15,
            'volume_profile': 15,
            'price_structure': 25,  # Increase structure weight
            'risk_reward': 15
        }
    }

    scanner = UptrendScanner(config.POLYGON_API_KEY, config=quality_config,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S3')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_3['min_price'],
        min_volume=config.STRATEGY_3['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    # Filter for Tier 1 only
    tier_1_stocks = [s for s in results['established_uptrends']
                     if s['tier'] == 'Tier 1: Prime Movers']

    print(f"\nFound {len(tier_1_stocks)} Tier 1 large cap stocks")

    if tier_1_stocks:
        print("\nTop 10 Large Cap Quality Stocks:")
        for stock in tier_1_stocks[:10]:
            print(f"  {stock['ticker']}: Score {stock['score']:.1f} @ ${stock['current_price']:.2f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S3')


def strategy_4_aggressive_momentum():
    """
    Strategy 4: Aggressive Momentum Plays
    =====================================
    Purpose: Find high-momentum stocks (higher risk/reward)
    Use case: Active trading, smaller position sizes
    """
    print("=" * 70)
    print("STRATEGY 4: Aggressive Momentum Plays")
    print("=" * 70)

    # Custom config emphasizing momentum
    momentum_config = {
        'weights': {
            'trend_strength': 20,
            'momentum_quality': 35,  # Heavy momentum weight
            'volume_profile': 25,    # High volume weight
            'price_structure': 10,
            'risk_reward': 10
        }
    }

    scanner = UptrendScanner(config.POLYGON_API_KEY, config=momentum_config,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S4')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_4['min_price'],
        min_volume=config.STRATEGY_4['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    # Filter for high momentum scores
    high_momentum = []
    for stock in results['established_uptrends']:
        momentum_score = stock['score_breakdown']['momentum_quality']
        if momentum_score >= 15:  # High momentum component
            high_momentum.append(stock)

    print(f"\nFound {len(high_momentum)} high-momentum stocks")

    if high_momentum:
        # Sort by momentum score
        high_momentum.sort(
            key=lambda x: x['score_breakdown']['momentum_quality'],
            reverse=True
        )

        print("\nTop 15 Momentum Stocks:")
        for stock in high_momentum[:15]:
            mom_score = stock['score_breakdown']['momentum_quality']
            print(f"  {stock['ticker']}: Momentum {mom_score:.1f}/20, "
                  f"Total {stock['score']:.1f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S4')


def strategy_5_early_breakouts():
    """
    Strategy 5: Early Breakout Detection
    ====================================
    Purpose: Find stocks just starting to uptrend
    Use case: Ground floor opportunities, early positioning
    """
    print("=" * 70)
    print("STRATEGY 5: Early Breakout Detection")
    print("=" * 70)

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S5')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_5['min_price'],
        min_volume=config.STRATEGY_5['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    early_uptrends = results['early_uptrends']

    print(f"\nFound {len(early_uptrends)} early breakout candidates")

    if early_uptrends:
        # Sort by early detection score
        early_uptrends.sort(
            key=lambda x: x['early_details'].get('score', 0),
            reverse=True
        )

        print("\nTop 20 Early Breakouts:")
        for stock in early_uptrends[:20]:
            score = stock['early_details'].get('score', 0)
            price = stock['current_price']
            print(f"  {stock['ticker']}: Score {score}/8 @ ${price:.2f}")

            # Show which signals triggered
            details = stock['early_details']
            signals = []
            if details.get('ma20_cross_recent'):
                signals.append("MA20 Cross")
            if details.get('volume_spike'):
                signals.append("Volume Spike")
            if details.get('macd_cross_recent'):
                signals.append("MACD Cross")
            if details.get('breakout'):
                signals.append("Breakout")

            print(f"    Signals: {', '.join(signals)}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S5')


def strategy_6_custom_scoring():
    """
    Strategy 6: Custom Scoring Weights
    ==================================
    Purpose: Demonstrate custom scoring for specific preferences
    Use case: Tailoring the system to your trading style
    """
    print("=" * 70)
    print("STRATEGY 6: Custom Scoring Weights")
    print("=" * 70)

    # Example: Prioritize risk/reward and structure over momentum
    custom_config = {
        'weights': {
            'trend_strength': 25,
            'momentum_quality': 10,   # Lower
            'volume_profile': 20,
            'price_structure': 25,    # Higher
            'risk_reward': 20         # Higher
        }
    }

    scanner = UptrendScanner(config.POLYGON_API_KEY, config=custom_config,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S6')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_6['min_price'],
        min_volume=config.STRATEGY_6['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    print(f"\nEstablished uptrends: {len(results['established_uptrends'])}")

    if results['established_uptrends']:
        print("\nTop 10 with Custom Scoring:")
        for stock in results['established_uptrends'][:10]:
            breakdown = stock['score_breakdown']
            print(f"  {stock['ticker']}: {stock['score']:.1f}")
            print(f"    Structure: {breakdown['price_structure']:.1f}, "
                  f"Risk/Reward: {breakdown['risk_reward']:.1f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S6')


def strategy_7_swing_trade_setups():
    """
    Strategy 7: Swing Trade Setups (Near Support)
    =============================================
    Purpose: Find stocks near MA20 support for entry
    Use case: Swing trading, pullback entries
    """
    print("=" * 70)
    print("STRATEGY 7: Swing Trade Setups (Near Support)")
    print("=" * 70)

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S7')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_7['min_price'],
        min_volume=config.STRATEGY_7['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    # Filter for stocks close to MA20 (good risk/reward)
    near_support = []
    for stock in results['established_uptrends']:
        # Check risk/reward details
        rr_details = stock['score_breakdown']['details']['risk_reward']
        distance = abs(rr_details.get('distance_from_ma20_pct', 999))

        if distance < config.STRATEGY_7['max_distance_from_ma20'] and stock['score'] >= 60:  # Within configured % of MA20, Tier 2+
            near_support.append((stock, distance))

    # Sort by distance (closest to MA20 first)
    near_support.sort(key=lambda x: x[1])

    print(f"\nFound {len(near_support)} swing trade setups (near MA20 support)")

    if near_support:
        print("\nTop 15 Swing Trade Setups:")
        for stock, distance in near_support[:15]:
            print(f"  {stock['ticker']}: {distance:.2f}% from MA20, "
                  f"Score {stock['score']:.1f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S7')


def strategy_8_multi_timeframe_concept():
    """
    Strategy 8: Multi-Timeframe Concept
    ===================================
    Purpose: Demonstrate checking both daily and weekly trends
    Use case: Higher conviction trades, position trading
    Note: This is a concept demo - full implementation would fetch weekly data
    """
    print("=" * 70)
    print("STRATEGY 8: Multi-Timeframe Concept (Daily + Weekly)")
    print("=" * 70)
    print("Note: This is a simplified concept demonstration")

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S8')

    # Scan daily timeframe
    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_8['min_price'],
        min_volume=config.STRATEGY_8['min_volume'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    tier_1_stocks = [s for s in results['established_uptrends']
                     if s['tier'] == 'Tier 1: Prime Movers']

    print(f"\nFound {len(tier_1_stocks)} Tier 1 stocks on daily timeframe")

    # In a full implementation, you would:
    # 1. Fetch weekly data for these stocks
    # 2. Check if weekly MA20 is also rising
    # 3. Confirm weekly uptrend criteria
    # 4. Only keep stocks that are uptrending on BOTH timeframes

    print("\nIn production, these stocks would be validated on weekly timeframe")
    print("This provides higher conviction for position trades")

    if tier_1_stocks:
        print("\nTier 1 stocks (would check weekly):")
        for stock in tier_1_stocks[:10]:
            print(f"  {stock['ticker']}: {stock['score']:.1f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S8')


def strategy_9_curated_watchlist(num_stocks_to_scan=None, num_charts_to_plot=None):
    """
    Strategy 9: Curated Watchlist Generator
    =======================================
    Purpose: Generate a focused watchlist of top opportunities
    Use case: Daily monitoring, position trading prep

    Args:
        num_stocks_to_scan: Number of stocks to scan (default from config, None for all)
        num_charts_to_plot: Number of charts to generate (default from config)
    """
    # Use config defaults if not specified
    if num_stocks_to_scan is None:
        num_stocks_to_scan = config.MAX_STOCKS_STRATEGY_9
    if num_charts_to_plot is None:
        num_charts_to_plot = config.NUM_CHARTS_TO_PLOT

    print("=" * 70)
    print("STRATEGY 9: Curated Watchlist Generator")
    print("=" * 70)
    if num_stocks_to_scan is None:
        print(f"Scanning entire market (all stocks)...")
    else:
        print(f"Scanning {num_stocks_to_scan} stocks...")
    print(f"Will generate charts for top {num_charts_to_plot} stocks")

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S9')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_9['min_price'],
        min_volume=config.STRATEGY_9['min_volume'],
        max_stocks=num_stocks_to_scan
    )

    # Build curated watchlist with specific criteria
    watchlist = []

    for stock in results['established_uptrends']:
        score = stock['score']
        breakdown = stock['score_breakdown']

        # Criteria for watchlist inclusion:
        # 1. Tier 1 or high Tier 2 (score >= 70)
        # 2. Good risk/reward (within 5% of MA20)
        # 3. Strong trend (ADX > 30)
        # 4. Not overbought (RSI < 70)

        if score >= 70:
            trend_details = breakdown['details']['trend']
            rr_details = breakdown['details']['risk_reward']
            mom_details = breakdown['details']['momentum']

            adx = trend_details.get('adx', 0)
            distance = abs(rr_details.get('distance_from_ma20_pct', 999))
            rsi = mom_details.get('rsi', 100)

            if adx > 30 and distance < 5.0 and rsi < 70:
                watchlist.append(stock)

    print(f"\nCurated watchlist: {len(watchlist)} stocks")

    if watchlist:
        # Sort by score
        watchlist.sort(key=lambda x: x['score'], reverse=True)

        print("\n" + "=" * 70)
        print(f"TOP {num_charts_to_plot} WATCHLIST STOCKS")
        print("=" * 70)

        for i, stock in enumerate(watchlist[:num_charts_to_plot], 1):
            breakdown = stock['score_breakdown']
            trend_details = breakdown['details']['trend']
            mom_details = breakdown['details']['momentum']

            print(f"\n{i}. {stock['ticker']} - Score: {stock['score']:.1f}/100")
            print(f"   Price: ${stock['current_price']:.2f}")
            print(f"   Tier: {stock['tier']}")
            print(f"   ADX: {trend_details.get('adx', 0):.1f}")
            print(f"   RSI: {mom_details.get('rsi', 0):.1f}")
            print(f"   Days in uptrend: {trend_details.get('days_in_uptrend', 0)}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, num_charts=num_charts_to_plot, strategy_id='S9')

    # Save watchlist tickers to text file
    if watchlist:
        with open('./output/watchlist_tickers.txt', 'w') as f:
            for stock in watchlist[:num_charts_to_plot]:
                f.write(f"{stock['ticker']}\n")
        print("\nWatchlist saved to: ./output/watchlist_tickers.txt")


def strategy_10_small_cap_focus():
    """
    Strategy 10: Small Cap Focus ($300M - $2B)
    ==========================================
    Purpose: Find high-quality small cap stocks in uptrends
    Use case: Higher growth potential, higher risk
    """
    print("=" * 70)
    print(f"STRATEGY 10: Small Cap Focus ({config.MAX_STOCKS_TO_SCAN} stocks)")
    print("Market Cap: $300M - $2B")
    print("=" * 70)

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S10')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_10['min_price'],
        min_volume=config.STRATEGY_10['min_volume'],
        min_market_cap=config.STRATEGY_10['min_market_cap'],
        max_market_cap=config.STRATEGY_10['max_market_cap'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    print(f"\nResults:")
    print(f"Early uptrends: {len(results['early_uptrends'])}")
    print(f"Established uptrends: {len(results['established_uptrends'])}")

    # Show tier breakdown
    tier_counts = {}
    for stock in results['established_uptrends']:
        tier = stock['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("\nTier Breakdown:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  {tier}: {count} stocks")

    if results['established_uptrends']:
        print("\nTop 10 Small Cap Stocks:")
        for stock in results['established_uptrends'][:10]:
            market_cap_b = stock.get('market_cap', 0) / 1_000_000_000
            print(f"  {stock['ticker']}: Score {stock['score']:.1f}, "
                  f"Market Cap ${market_cap_b:.2f}B, Price ${stock['current_price']:.2f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S10')


def strategy_11_medium_cap_focus():
    """
    Strategy 11: Medium Cap Focus ($2B - $10B)
    ==========================================
    Purpose: Find high-quality medium cap stocks in uptrends
    Use case: Balance of growth potential and stability
    """
    print("=" * 70)
    print(f"STRATEGY 11: Medium Cap Focus ({config.MAX_STOCKS_TO_SCAN} stocks)")
    print("Market Cap: $2B - $10B")
    print("=" * 70)

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S11')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_11['min_price'],
        min_volume=config.STRATEGY_11['min_volume'],
        min_market_cap=config.STRATEGY_11['min_market_cap'],
        max_market_cap=config.STRATEGY_11['max_market_cap'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    print(f"\nResults:")
    print(f"Early uptrends: {len(results['early_uptrends'])}")
    print(f"Established uptrends: {len(results['established_uptrends'])}")

    # Show tier breakdown
    tier_counts = {}
    for stock in results['established_uptrends']:
        tier = stock['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("\nTier Breakdown:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  {tier}: {count} stocks")

    if results['established_uptrends']:
        print("\nTop 10 Medium Cap Stocks:")
        for stock in results['established_uptrends'][:10]:
            market_cap_b = stock.get('market_cap', 0) / 1_000_000_000
            print(f"  {stock['ticker']}: Score {stock['score']:.1f}, "
                  f"Market Cap ${market_cap_b:.2f}B, Price ${stock['current_price']:.2f}")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S11')


def strategy_12_micro_cap_momentum():
    """
    Strategy 12: Micro Cap Momentum ($50M - $300M)
    ==============================================
    Purpose: Find high-momentum micro cap stocks with tight floats
    Use case: Aggressive growth strategy, higher risk/reward
    Warning: Lower liquidity - use careful position sizing
    """
    print("=" * 70)
    print(f"STRATEGY 12: Micro Cap Momentum ({config.MAX_STOCKS_TO_SCAN} stocks)")
    print("Market Cap: $50M - $300M")
    print("Float Range: 5M - 100M shares")
    print("⚠️  WARNING: Micro caps have higher risk - use careful position sizing!")
    print("=" * 70)

    scanner = UptrendScanner(config.POLYGON_API_KEY,
                              max_requests_per_minute=config.MAX_REQUESTS_PER_MINUTE,
                              strategy_id='S12')

    results = scanner.scan_market(
        exchanges=config.EXCHANGES,
        min_price=config.STRATEGY_12['min_price'],
        min_volume=config.STRATEGY_12['min_volume'],
        min_market_cap=config.STRATEGY_12['min_market_cap'],
        max_market_cap=config.STRATEGY_12['max_market_cap'],
        min_free_float_shares=config.STRATEGY_12['min_free_float_shares'],
        max_free_float_shares=config.STRATEGY_12['max_free_float_shares'],
        max_stocks=config.MAX_STOCKS_TO_SCAN
    )

    print(f"\nResults:")
    print(f"Early uptrends: {len(results['early_uptrends'])}")
    print(f"Established uptrends: {len(results['established_uptrends'])}")

    # Show tier breakdown
    tier_counts = {}
    for stock in results['established_uptrends']:
        tier = stock['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("\nTier Breakdown:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  {tier}: {count} stocks")

    if results['established_uptrends']:
        print("\nTop 10 Micro Cap Momentum Stocks:")
        for stock in results['established_uptrends'][:10]:
            market_cap_m = stock.get('market_cap', 0) / 1_000_000
            float_m = stock.get('float_shares', 0) / 1_000_000
            volatility = stock.get('volatility_20', 0)
            print(f"  {stock['ticker']}: Score {stock['score']:.1f}, "
                  f"MCap ${market_cap_m:.1f}M, Float {float_m:.1f}M, "
                  f"Vol {volatility:.1f}%, Price ${stock['current_price']:.2f}")

    # Show liquidity metrics
    if results['established_uptrends']:
        print("\n💡 Position Sizing Recommendations:")
        print("   - Micro caps are illiquid - keep positions <0.5% of daily volume")
        print("   - Higher volatility - use wider stops and smaller position sizes")
        print("   - Monitor float % closely - tight floats can gap violently")

    # Export CSVs and generate charts with proper directory structure
    export_and_plot_results(scanner, results, strategy_id='S12')


def main():
    """Main entry point"""
    strategies = {
        '1': (f'Quick Test Scan ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_1_quick_test),
        '2': ('Full Market Scan', strategy_2_full_market_scan),
        '3': (f'Large Cap Quality ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_3_large_cap_quality),
        '4': (f'Aggressive Momentum ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_4_aggressive_momentum),
        '5': (f'Early Breakouts ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_5_early_breakouts),
        '6': (f'Custom Scoring ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_6_custom_scoring),
        '7': (f'Swing Trade Setups ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_7_swing_trade_setups),
        '8': (f'Multi-Timeframe Concept ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_8_multi_timeframe_concept),
        '9': ('Curated Watchlist', strategy_9_curated_watchlist),
        '10': (f'Small Cap Focus ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_10_small_cap_focus),
        '11': (f'Medium Cap Focus ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_11_medium_cap_focus),
        '12': (f'Micro Cap Momentum ({config.MAX_STOCKS_TO_SCAN} stocks)', strategy_12_micro_cap_momentum),
    }

    if len(sys.argv) < 2:
        print("\nUptrend Momentum Scanner - Example Strategies")
        print("=" * 70)
        print("\nUsage: python example_usage.py <strategy_number> [options]")
        print("\nAvailable Strategies:")
        for num, (name, _) in strategies.items():
            print(f"  {num}. {name}")
        print("\nExamples:")
        print("  python example_usage.py 1")
        print(f"  python example_usage.py 9                    # Default: scan {config.MAX_STOCKS_STRATEGY_9}, plot {config.NUM_CHARTS_TO_PLOT}")
        print(f"  python example_usage.py 9 200               # Scan 200 stocks, plot {config.NUM_CHARTS_TO_PLOT} (default)")
        print("  python example_usage.py 9 500 25            # Scan 500 stocks, plot 25")
        sys.exit(1)

    strategy_num = sys.argv[1]

    if strategy_num not in strategies:
        print(f"Error: Strategy {strategy_num} not found")
        print(f"Valid strategies: {', '.join(strategies.keys())}")
        sys.exit(1)

    # Check API key
    if config.POLYGON_API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  ERROR: Please set your Polygon.io API key in config.py")
        print("Get your key at: https://polygon.io/dashboard/api-keys")
        sys.exit(1)

    # Run selected strategy
    _, strategy_func = strategies[strategy_num]

    # Strategy 9 accepts optional parameters
    if strategy_num == '9':
        num_stocks_to_scan = int(sys.argv[2]) if len(sys.argv) > 2 else None  # None = use config default
        num_charts_to_plot = int(sys.argv[3]) if len(sys.argv) > 3 else None  # None = use config default
        strategy_func(num_stocks_to_scan, num_charts_to_plot)
    else:
        strategy_func()

    print("\n" + "=" * 70)
    print("Scan complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
