"""Simple trading strategy demonstrating basic DawnAI SDK usage."""

from dawnai.strategy import Strategy, cron, fetch_current_price


class SimpleStrategy(Strategy):
    """Basic strategy that monitors price at regular intervals."""

    def __init__(self) -> None:
        super().__init__()
        self.last_price = 0.0

    @cron(interval="1m")
    def monitor_price(self) -> None:
        """Check price every minute."""
        price_data = fetch_current_price("BTCUSDT")
        current_price = float(price_data.price)

        if self.last_price > 0:
            change = ((current_price - self.last_price) / self.last_price) * 100
            print(f"BTC Price: ${current_price:,.2f} ({change:+.2f}%)")
        else:
            print(f"BTC Price: ${current_price:,.2f}")

        self.last_price = current_price


if __name__ == "__main__":
    from dawnai.strategy import StrategyAnalyzer

    engine = StrategyAnalyzer(SimpleStrategy)
    print("Strategy Analysis:")
    print(engine.get_strategy_info())
