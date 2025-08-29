"""Multi-signal trading strategy combining multiple indicators."""

from dawnai.strategy import (
    Strategy,
    browser_search,
    buy_polymarket,
    cron,
    fetch_current_price,
    get_news,
    sell_polymarket,
)


class MultiSignalTrader(Strategy):
    """Combine multiple signals for trading decisions."""

    def __init__(self) -> None:
        super().__init__()
        # Signal states
        self.signals: dict[str, float] = {
            "sentiment": 0.0,
            "momentum": 0.0,
            "volume": 0.0,
        }
        self.price_history: list[float] = []
        self.position_open = False

        # Polymarket config
        self.market_id = "0x..."  # Set your market ID
        self.outcome = "Yes"

    @cron(interval="5m")
    def update_sentiment_signal(self) -> None:
        """Update sentiment signal from news."""
        news = get_news(query="bitcoin crypto market", limit=5)
        if news:
            # Simplified sentiment calculation from news
            self.signals["sentiment"] = 0.0  # In real implementation, calculate from news

    @cron(interval="1m")
    def update_price_signals(self) -> None:
        """Update momentum and volume signals."""
        price_data = fetch_current_price("BTCUSDT")
        current_price = float(price_data.price)
        self.price_history.append(current_price)

        if len(self.price_history) > 20:
            self.price_history.pop(0)

        # Calculate momentum signal
        if len(self.price_history) >= 10:
            recent = sum(self.price_history[-5:]) / 5
            older = sum(self.price_history[-10:-5]) / 5
            momentum_pct = (recent - older) / older * 100
            self.signals["momentum"] = momentum_pct / 10  # Normalize to -1 to 1 range

    @cron(interval="10m")
    def update_market_volume(self) -> None:
        """Check market activity via search."""
        results = browser_search("bitcoin trading volume 24h")
        # Simple heuristic: more results = more activity
        self.signals["volume"] = min(len(results) / 10, 1.0) if results else 0.0

    @cron(interval="1m")
    def execute_trades(self) -> None:
        """Combine all signals and execute trades."""
        # Calculate composite signal
        weights = {"sentiment": 0.4, "momentum": 0.4, "volume": 0.2}
        composite_score = sum(self.signals[signal] * weight for signal, weight in weights.items())

        # Trading decision with threshold
        threshold = 0.3
        if composite_score > threshold and not self.position_open:
            # Buy signal
            buy_polymarket(
                market_id=self.market_id,
                outcome=self.outcome,
                amount=150,  # Larger position for higher confidence
            )
            self.position_open = True
            print(f"BUY: composite={composite_score:.2f}")
            print(f"  Signals: {self.signals}")

        elif composite_score < -threshold and self.position_open:
            # Sell signal
            sell_polymarket(market_id=self.market_id, outcome=self.outcome, amount=150)
            self.position_open = False
            print(f"SELL: composite={composite_score:.2f}")
            print(f"  Signals: {self.signals}")
