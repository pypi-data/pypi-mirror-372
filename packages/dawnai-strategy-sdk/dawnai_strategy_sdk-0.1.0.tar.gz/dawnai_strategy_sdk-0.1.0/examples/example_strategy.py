"""Example trading strategy using the DawnAI SDK."""

from decimal import Decimal

from dawnai.strategy import (
    Strategy,
    cron,
    fetch_current_price,
    get_news,
    polymarket_smart_search,
)


class NewsBasedTradingStrategy(Strategy):
    """A strategy that monitors news sentiment and market prices to make trading decisions.

    This strategy:
    1. Fetches news every minute
    2. Analyzes sentiment of the news
    3. Monitors BTC price changes
    4. Makes buy/sell decisions based on sentiment and price movements
    """

    def __init__(self) -> None:
        super().__init__()
        # Initialize state
        self.position: Decimal = Decimal(0)
        self.last_sentiment: float = 0.0
        self.entry_price: float | None = None

    @cron(interval="1m")
    def fetch_and_trade_news(self) -> None:
        """Fetch news and analyze sentiment every minute."""
        try:
            # Get latest crypto news
            news = get_news(query="bitcoin cryptocurrency", limit=5)

            if not news:
                print("No news found")
                return

            # Analyze sentiment (simplified for example)
            # In real implementation, calculate sentiment from news
            sentiment_value = 0.0  # placeholder
            confidence_value = 0.5  # placeholder
            self.last_sentiment = sentiment_value

            print(f"News sentiment: {sentiment_value:.2f}")
            print(f"Confidence: {confidence_value:.2f}")

            # Get current BTC price
            price_data = fetch_current_price("BTCUSDT")
            current_price = float(price_data.price)

            # Trading logic based on sentiment
            if sentiment_value > 0.5 and confidence_value > 0.7:
                if self.position == 0:
                    # Strong positive sentiment - consider buying
                    self.execute_buy(current_price)
            elif sentiment_value < -0.5 and confidence_value > 0.7:
                if self.position > 0:
                    # Strong negative sentiment - consider selling
                    self.execute_sell(current_price)

        except Exception as e:
            print(f"Error in fetch_and_trade_news: {e}")

    @cron(interval="5m")
    def on_market_price_check(self) -> None:
        """Check BTC price every 5 minutes."""
        price_data = fetch_current_price("BTCUSDT")
        price = float(price_data.price)
        print(f"BTC price updated: ${price:,.2f}")

        if self.entry_price is not None:
            # Calculate profit/loss
            pnl_pct = ((price - self.entry_price) / self.entry_price) * 100
            print(f"Current P&L: {pnl_pct:.2f}%")

            # Risk management: Stop loss at -2%
            if pnl_pct < -2.0 and self.position > 0:
                print("Stop loss triggered!")
                self.execute_sell(price)
            # Take profit at +5%
            elif pnl_pct > 5.0 and self.position > 0:
                print("Take profit triggered!")
                self.execute_sell(price)

    @cron(interval="5m")
    def check_polymarket_opportunities(self) -> None:
        """Check for related Polymarket opportunities every 5 minutes."""
        try:
            # Search for crypto-related markets
            markets = polymarket_smart_search("bitcoin price", limit=3)

            for market in markets:
                print(f"Market: {market.question}")
                print(f"Volume: ${market.volume:,.2f}")
                print(f"Liquidity: ${market.liquidity:,.2f}")

                # Check if sentiment aligns with market prices
                for outcome, price in market.current_prices.items():
                    print(f"  {outcome}: {price:.2%}")

        except Exception as e:
            print(f"Error checking Polymarket: {e}")

    def execute_buy(self, price: float) -> None:
        """Execute a buy order."""
        amount = Decimal(100)  # Buy $100 worth
        self.position += amount
        self.entry_price = price
        self.set_state("position", float(self.position))
        self.set_state("entry_price", price)
        print(f"BOUGHT ${amount} at ${price:,.2f}")

    def execute_sell(self, price: float) -> None:
        """Execute a sell order."""
        if self.position > 0:
            amount = self.position
            self.position = Decimal(0)
            self.entry_price = None
            self.set_state("position", 0)
            self.set_state("entry_price", None)

            print(f"SOLD ${amount} at ${price:,.2f}")

    def initialize(self) -> None:
        """Initialize the strategy."""
        super().initialize()
        print("News-based trading strategy initialized")
        print("Monitoring BTC price and crypto news sentiment...")

    def shutdown(self) -> None:
        """Clean up when strategy stops."""
        print("Strategy shutting down...")
        if self.position > 0:
            print(f"Warning: Open position of ${self.position}")
        super().shutdown()


if __name__ == "__main__":
    # Run the strategy
    from dawnai.strategy import StrategyAnalyzer

    engine = StrategyAnalyzer(NewsBasedTradingStrategy)

    # Validate before running
    errors = engine.validate()
    if errors:
        print("Validation errors:", errors)
    else:
        print("Strategy validated successfully!")
        print("Strategy Analysis:")
        print(engine.get_strategy_info())
