"""Simple trading strategy example."""

from dawnai.strategy import (
    Strategy,
    buy_polymarket,
    cron,
    get_news,
    sell_polymarket,
)


class SimpleStrategy(Strategy):
    """Basic sentiment-based trading strategy."""

    def __init__(self) -> None:
        super().__init__()
        self.sentiment = 0.0
        self.position_open = False
        self.market_id = "0x..."  # Set your market ID
        self.outcome = "Yes"

    @cron(interval="1m")
    def update_and_trade(self) -> None:
        """Update sentiment and execute trades."""
        # Update state
        news = get_news()
        if news:
            # Simplified sentiment calculation from news
            self.sentiment = 0.0  # In real implementation, calculate from news

        # Trading decision
        if self.sentiment > 0.5 and not self.position_open:
            buy_polymarket(market_id=self.market_id, outcome=self.outcome, amount=100)
            self.position_open = True
        elif self.sentiment < -0.5 and self.position_open:
            sell_polymarket(market_id=self.market_id, outcome=self.outcome, amount=100)
            self.position_open = False
