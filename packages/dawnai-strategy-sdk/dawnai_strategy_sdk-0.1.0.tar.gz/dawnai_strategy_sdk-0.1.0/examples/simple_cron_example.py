"""Simple example with cron-only triggers."""

from dawnai.strategy import (
    Strategy,
    StrategyAnalyzer,
    cron,
    extract_triggers,
    fetch_current_price,
    get_news,
)


class CronStrategy(Strategy):
    """A simple strategy using only cron triggers."""

    def __init__(self) -> None:
        super().__init__()
        self.x = 1

    @cron(interval="1m")
    def fetch_and_trade_news(self) -> None:
        """Fetch news and trade based on sentiment every minute."""
        get_news()
        price_data = fetch_current_price("BTCUSDT")
        price = float(price_data.price)

        # Simplified sentiment check (in real implementation, calculate from news)
        sentiment_value = 0.0  # placeholder sentiment value
        if sentiment_value > 0.5:
            self.buy(100, price)
        else:
            self.sell(100, price)

    @cron(interval="5m")
    def check_market(self) -> None:
        """Check market conditions every 5 minutes."""
        price_data = fetch_current_price("BTCUSDT")
        print(f"BTC Price: ${price_data.price}")

    @cron(interval="1h")
    def hourly_report(self) -> None:
        """Generate hourly report."""
        print("Generating hourly report...")

    def buy(self, amount: float, price: float | None = None) -> None:
        """Execute buy logic."""
        print(f"Buying {amount} at price: {price}")

    def sell(self, amount: float, price: float | None = None) -> None:
        """Execute sell logic."""
        print(f"Selling {amount} at price: {price}")


def main() -> None:
    """Demonstrate extracting cron triggers."""
    print("=== Extract Triggers ===\n")

    # Simple extraction
    triggers = extract_triggers(CronStrategy)

    for method_name, config in triggers.items():
        print(f"{method_name}:")
        print(f"  Interval: {config['interval']}")
        print(f"  Seconds: {config['interval_seconds']}")
        print(f"  Method: {config['method'].__name__}\n")

    print("=== Using StrategyAnalyzer ===\n")

    analyzer = StrategyAnalyzer(CronStrategy)

    # Get all cron triggers
    cron_triggers = analyzer.get_cron_triggers()
    print("Cron Triggers:")
    for trigger in cron_triggers:
        print(f"  {trigger['method']}: every {trigger['interval']}")

    # Get trigger map with details
    print("\nTrigger Map:")
    trigger_map = analyzer.get_trigger_map()
    for method_name, details in trigger_map.items():
        print(f"\n{method_name}:")
        print(f"  Interval: {details['interval']}")
        print(f"  Seconds: {details['interval_seconds']}")
        print(f"  Signature: {details['method_signature']}")
        print(f"  Doc: {details['docstring']}")

    # Validate
    print("\n=== Validation ===")
    errors = analyzer.validate()
    if errors:
        print(f"Errors: {errors}")
    else:
        print("Strategy is valid!")

    # Get comprehensive info
    print("\n=== Strategy Info ===")
    info = analyzer.get_strategy_info()
    print(f"Class: {info['class_name']}")
    print(f"Total triggers: {info['trigger_count']}")


if __name__ == "__main__":
    main()
