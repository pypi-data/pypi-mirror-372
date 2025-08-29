"""Example of extracting trigger mappings from a strategy."""

from dawnai.strategy import (
    Strategy,
    StrategyAnalyzer,
    cron,
    extract_triggers,
)


class ExampleStrategy(Strategy):
    """Example strategy for demonstration."""

    @cron(interval="5m")
    def check_market_every_5_min(self) -> None:
        """Check market conditions every 5 minutes."""
        print("Checking market...")

    @cron(interval="1h")
    def hourly_analysis(self) -> None:
        """Perform hourly analysis."""
        print("Running hourly analysis...")

    @cron(interval="5m")
    def on_btc_price_check(self) -> None:
        """Check BTC price every 5 minutes."""
        print("Checking BTC price...")

    @cron(interval="10m")
    def on_eth_price_check(self) -> None:
        """Check ETH price every 10 minutes."""
        print("Checking ETH price...")


def main() -> None:
    """Demonstrate trigger extraction."""
    print("=== Method 1: Using StrategyAnalyzer ===\n")

    # Create analyzer for the strategy class
    analyzer = StrategyAnalyzer(ExampleStrategy)

    # Get the full trigger map with detailed information
    trigger_map = analyzer.get_trigger_map()

    print("Trigger Map:")
    for trigger_id, details in trigger_map.items():
        print(f"\nTrigger ID: {trigger_id}")
        print(f"  Type: {details['type']}")
        print(f"  Method: {details['method_name']}")
        print(f"  Params: {details['params']}")
        print(f"  Signature: {details['method_signature']}")
        print(f"  Doc: {details['docstring']}")

    print("\n=== Method 2: Simple extraction ===\n")

    # Get a simple mapping of triggers to methods
    simple_map = extract_triggers(ExampleStrategy)

    print("Simple Trigger Map:")
    for key, method in simple_map.items():
        if hasattr(method, "__name__"):
            print(f"  {key} -> {method.__name__}")
        else:
            print(f"  {key} -> {method}")

    print("\n=== Method 3: Get specific trigger types ===\n")

    # Get cron triggers
    cron_triggers = analyzer.get_cron_triggers()
    print("Cron Triggers:")
    for trigger in cron_triggers:
        print(f"  {trigger['method']}: runs every {trigger['interval']}")

    # Note: market_price_update triggers not available in current implementation

    print("\n=== Method 4: Get comprehensive strategy info ===\n")

    # Get all strategy information
    info = analyzer.get_strategy_info()

    print(f"Strategy: {info['class_name']}")
    print(f"Total triggers: {info['trigger_summary']['total']}")
    print("Triggers by type:")
    for ttype, count in info["trigger_summary"]["by_type"].items():
        print(f"  {ttype}: {count}")

    # Validate the strategy
    errors = info["validation_errors"]
    if errors:
        print(f"\nValidation errors: {errors}")
    else:
        print("\nStrategy is valid!")

    print("\n=== Method 5: Analyze from file ===\n")

    # You can also analyze a strategy from a file
    print("(analyze_strategy_file can be used to analyze external strategy files)")


if __name__ == "__main__":
    main()
