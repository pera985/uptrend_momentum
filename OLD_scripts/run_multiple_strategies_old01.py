"""
Run Multiple Strategies
========================

Execute multiple scanning strategies in sequence.

Usage:
    python run_multiple_strategies.py 3 4 5 8
    python run_multiple_strategies.py 1 9
"""

import sys
import time
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


def main():
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
    }

    if len(sys.argv) < 2:
        print("\nRun Multiple Strategies")
        print("=" * 70)
        print("\nUsage: python run_multiple_strategies.py <strategy_numbers...>")
        print("\nExamples:")
        print("  python run_multiple_strategies.py 3 4 5 8")
        print("  python run_multiple_strategies.py 1 9")
        print("  python run_multiple_strategies.py 3 4 5")
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

        # Format elapsed time
        if strategy_elapsed < 60:
            time_str = f"{strategy_elapsed:.1f} seconds"
        elif strategy_elapsed < 3600:
            mins = int(strategy_elapsed // 60)
            secs = int(strategy_elapsed % 60)
            time_str = f"{mins} min {secs} sec"
        else:
            hours = int(strategy_elapsed // 3600)
            mins = int((strategy_elapsed % 3600) // 60)
            time_str = f"{hours} hr {mins} min"

        print(f"\n✓ Completed Strategy {num}: {name} (Time: {time_str})")

    overall_elapsed = time.time() - overall_start_time

    print("\n" + "=" * 70)
    print(f"ALL {len(strategy_nums)} STRATEGIES COMPLETED!")
    print("=" * 70)

    # Print time summary
    print("\nTIME SUMMARY:")
    print("-" * 70)
    for num, name, elapsed in strategy_times:
        if elapsed < 60:
            time_str = f"{elapsed:.1f} seconds"
        elif elapsed < 3600:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            time_str = f"{mins} min {secs} sec"
        else:
            hours = int(elapsed // 3600)
            mins = int((elapsed % 3600) // 60)
            time_str = f"{hours} hr {mins} min"
        print(f"  Strategy {num} ({name}): {time_str}")

    # Format total time
    if overall_elapsed < 60:
        total_time_str = f"{overall_elapsed:.1f} seconds"
    elif overall_elapsed < 3600:
        mins = int(overall_elapsed // 60)
        secs = int(overall_elapsed % 60)
        total_time_str = f"{mins} min {secs} sec"
    else:
        hours = int(overall_elapsed // 3600)
        mins = int((overall_elapsed % 3600) // 60)
        total_time_str = f"{hours} hr {mins} min"

    print("-" * 70)
    print(f"  TOTAL TIME: {total_time_str}")
    print("\nResults saved to ./output/")


if __name__ == '__main__':
    main()
