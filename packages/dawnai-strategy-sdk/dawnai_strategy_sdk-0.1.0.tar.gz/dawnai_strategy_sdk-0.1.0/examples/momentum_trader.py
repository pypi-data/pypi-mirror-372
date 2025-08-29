"""Price momentum trading strategy."""

from dawnai.strategy import (
    Strategy,
    buy_polymarket,
    cron,
    fetch_current_price,
    polymarket_smart_search,
    sell_polymarket,
)


class MomentumTrader(Strategy):
    """Trade based on price momentum indicators."""

    def __init__(self) -> None:
        super().__init__()
        self.prices: list[float] = []
        self.position_open = False
        self.market_id: str | None = None
        self.outcome = "Yes"

    @cron(interval="1m")
    def update_momentum(self) -> None:
        """Update price history and check momentum."""
        # Update state: track price history
        price_data = fetch_current_price("BTCUSDT")
        current_price = float(price_data.price)
        self.prices.append(current_price)

        # Keep only last 20 prices
        if len(self.prices) > 20:
            self.prices.pop(0)

        # Need at least 10 prices to calculate momentum
        if len(self.prices) < 10:
            return

        # Calculate momentum
        recent_avg = sum(self.prices[-5:]) / 5
        older_avg = sum(self.prices[-10:-5]) / 5
        momentum = (recent_avg - older_avg) / older_avg * 100

        # Find relevant market if not set
        if not self.market_id:
            markets = polymarket_smart_search("bitcoin price", limit=1)
            if markets:
                self.market_id = markets[0].market_id

        # Trading decision
        if self.market_id:
            if momentum > 2.0 and not self.position_open:
                # Strong upward momentum
                buy_polymarket(market_id=self.market_id, outcome=self.outcome, amount=100)
                self.position_open = True
                print(f"BUY: momentum={momentum:.2f}%")

            elif momentum < -2.0 and self.position_open:
                # Strong downward momentum
                sell_polymarket(market_id=self.market_id, outcome=self.outcome, amount=100)
                self.position_open = False
                print(f"SELL: momentum={momentum:.2f}%")
