"""
Run Multiple Strategies
========================

Execute multiple scanning strategies in sequence.

Usage:
    python3 run_multiple_strategies.py 3 4 5 8
    python3 run_multiple_strategies.py 1 9
"""

import sys
import time
import logging
from example_usage import (
    strategy_1_quick_test,
    strategy_2_full_market_scan,
    strategy_3_large_cap_quality,
    strategy_4_aggressive_momentum,
    strategy_5_early_breakouts,
    strategy_6_custom_scoring,
    strategy_7_swing_trade_setups,
    strategy_8_multi_timeframe_concept,
    strategy_9_curated_watchlist,
    strategy_10_small_cap_focus,
    strategy_11_medium_cap_focus
)
import config

# Get logger from uptrend_scanner module
logger = logging.getLogger(__name__)


def format_time_hms(seconds: float) -> str:
    """Format seconds into hh:mm:ss format."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    # Helper to get stock count display for each strategy
    def get_stock_count(strategy_config_key):
        strategy_config = getattr(config, strategy_config_key, {})
        max_stocks = strategy_config.get('max_stocks', config.MAX_STOCKS_TO_SCAN)
        return 'all' if max_stocks is None else str(max_stocks)

    strategies = {
        '1': (f'Quick Test Scan ({get_stock_count("STRATEGY_1")} stocks)', strategy_1_quick_test),
        '2': ('Full Market Scan (all stocks)', strategy_2_full_market_scan),
        '3': (f'Large Cap Quality ({get_stock_count("STRATEGY_3")} stocks)', strategy_3_large_cap_quality),
        '4': (f'Aggressive Momentum ({get_stock_count("STRATEGY_4")} stocks)', strategy_4_aggressive_momentum),
        '5': (f'Early Breakouts ({get_stock_count("STRATEGY_5")} stocks)', strategy_5_early_breakouts),
        '6': (f'Custom Scoring ({get_stock_count("STRATEGY_6")} stocks)', strategy_6_custom_scoring),
        '7': (f'Swing Trade Setups ({get_stock_count("STRATEGY_7")} stocks)', strategy_7_swing_trade_setups),
        '8': (f'Multi-Timeframe Concept ({get_stock_count("STRATEGY_8")} stocks)', strategy_8_multi_timeframe_concept),
        '9': ('Curated Watchlist', strategy_9_curated_watchlist),
        '10': (f'Small Cap Focus ({get_stock_count("STRATEGY_10")} stocks)', strategy_10_small_cap_focus),
        '11': (f'Medium Cap Focus ({get_stock_count("STRATEGY_11")} stocks)', strategy_11_medium_cap_focus),
    }

    if len(sys.argv) < 2:
        print("\nRun Multiple Strategies")
        print("=" * 70)
        print("\nUsage: python3 run_multiple_strategies.py <strategy_numbers...>")
        print("\nExamples:")
        print("  python3 run_multiple_strategies.py 3 4 5 8")
        print("  python3 run_multiple_strategies.py 1 9")
        print("  python3 run_multiple_strategies.py 3 4 5")
        print("\nAvailable Strategies:")
        for num, (name, _) in strategies.items():
            print(f"  {num}. {name}")
        sys.exit(1)

    # Check API key
    if config.POLYGON_API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  ERROR: Please set your Polygon.io API key in config.py")
        print("Get your key at: https://polygon.io/dashboard/api-keys")
        sys.exit(1)

    # Get strategy numbers from command line
    strategy_nums = sys.argv[1:]

    # Validate all strategies first
    for num in strategy_nums:
        if num not in strategies:
            print(f"Error: Strategy {num} not found")
            print(f"Valid strategies: {', '.join(strategies.keys())}")
            sys.exit(1)

    # Run strategies in sequence
    print("\n" + "=" * 70)
    print(f"Running {len(strategy_nums)} strategies in sequence")
    print("=" * 70)

    overall_start_time = time.time()
    strategy_times = []

    for i, num in enumerate(strategy_nums, 1):
        name, strategy_func = strategies[num]

        print(f"\n\n{'='*70}")
        print(f"RUNNING STRATEGY {i}/{len(strategy_nums)}: {name}")
        print("=" * 70)

        strategy_start = time.time()

        # Run the strategy (Strategy 9 needs parameters)
        if num == '9':
            # Use None for both parameters to apply config defaults
            # Or specify values to override (e.g., strategy_func(500, 20))
            strategy_func(None, None)  # Use config defaults for both
        else:
            strategy_func()

        strategy_elapsed = time.time() - strategy_start
        strategy_times.append((num, name, strategy_elapsed))

        # Format elapsed time in hh:mm:ss
        time_str = format_time_hms(strategy_elapsed)

        print(f"\n✓ Completed Strategy {num}: {name} (Time: {time_str})")
        logger.info(f"Completed Strategy {num}: {name} - Time: {time_str}")

    overall_elapsed = time.time() - overall_start_time

    print("\n" + "=" * 70)
    print(f"ALL {len(strategy_nums)} STRATEGIES COMPLETED!")
    print("=" * 70)

    # Print time summary
    print("\nEXECUTION TIME SUMMARY:")
    print("-" * 70)
    logger.info("=" * 50)
    logger.info("EXECUTION TIME SUMMARY:")
    logger.info("=" * 50)
    for num, name, elapsed in strategy_times:
        time_str = format_time_hms(elapsed)
        print(f"  Strategy {num} ({name}): {time_str}")
        logger.info(f"Strategy {num} ({name}): {time_str}")

    # Format total time in hh:mm:ss
    total_time_str = format_time_hms(overall_elapsed)

    print("-" * 70)
    print(f"  TOTAL TIME: {total_time_str}")
    logger.info("-" * 50)
    logger.info(f"TOTAL TIME: {total_time_str}")
    print("\nResults saved to ./output/")


if __name__ == '__main__':
    main()
