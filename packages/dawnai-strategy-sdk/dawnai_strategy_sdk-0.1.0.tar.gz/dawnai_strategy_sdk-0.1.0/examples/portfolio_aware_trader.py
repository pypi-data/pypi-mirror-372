"""Portfolio-aware trading strategy with risk management."""

from decimal import Decimal

from dawnai.strategy import (
    Strategy,
    buy_polymarket,
    cron,
    get_news,
    read_portfolio,
    sell_polymarket,
)


class PortfolioAwareTrader(Strategy):
    """Trade with proper position sizing based on portfolio balance."""

    def __init__(self) -> None:
        super().__init__()
        self.sentiment_score = 0.0
        self.position_open = False
        self.market_id = "0x..."  # Set your market ID
        self.outcome = "Yes"
        self.max_position_pct = 0.1  # Max 10% of portfolio per trade

    @cron(interval="5m")
    def update_sentiment_and_trade(self) -> None:
        """Update sentiment and execute trades with portfolio awareness."""
        # Update sentiment state
        get_news(query="bitcoin cryptocurrency", limit=10)
        # Read portfolio before trading
        portfolio = read_portfolio()
        available = portfolio["available_balance"]

        # Calculate position size (10% of available balance)
        position_size = float(available * Decimal(str(self.max_position_pct)))

        # Only trade if we have sufficient balance
        if position_size < 10:  # Minimum $10 position
            print(f"Insufficient balance: ${available:.2f}")
            return

        # Trading decision
        if self.sentiment_score > 0.5 and not self.position_open:
            # Buy with calculated position size
            buy_polymarket(market_id=self.market_id, outcome=self.outcome, amount=position_size)
            self.position_open = True
            print(f"BUY ${position_size:.2f} (10% of ${available:.2f})")

        elif self.sentiment_score < -0.5 and self.position_open:
            # Check current positions before selling
            positions = portfolio["positions"]
            for pos in positions:
                if pos.get("market_id") == self.market_id:
                    # Sell entire position
                    sell_amount = pos.get("amount", position_size)
                    sell_polymarket(
                        market_id=self.market_id, outcome=self.outcome, amount=sell_amount
                    )
                    self.position_open = False
                    print(f"SELL ${sell_amount:.2f}")
