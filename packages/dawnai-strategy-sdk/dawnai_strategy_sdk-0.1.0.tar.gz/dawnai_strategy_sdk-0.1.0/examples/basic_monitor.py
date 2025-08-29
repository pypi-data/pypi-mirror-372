"""Basic price monitoring strategy."""

from dawnai.strategy import Strategy, cron, fetch_current_price


class PriceMonitor(Strategy):
    """Monitor cryptocurrency prices at regular intervals."""

    def __init__(self) -> None:
        super().__init__()
        self.last_btc_price = 0.0
        self.last_eth_price = 0.0

    @cron(interval="1m")
    def check_prices(self) -> None:
        """Check BTC and ETH prices every minute."""
        btc = fetch_current_price("BTCUSDT")
        eth = fetch_current_price("ETHUSDT")

        btc_price = float(btc.price)
        eth_price = float(eth.price)

        if self.last_btc_price > 0:
            btc_change = ((btc_price - self.last_btc_price) / self.last_btc_price) * 100
            eth_change = ((eth_price - self.last_eth_price) / self.last_eth_price) * 100
            print(f"BTC: ${btc_price:,.2f} ({btc_change:+.2f}%)")
            print(f"ETH: ${eth_price:,.2f} ({eth_change:+.2f}%)")
        else:
            print(f"BTC: ${btc_price:,.2f}")
            print(f"ETH: ${eth_price:,.2f}")

        self.last_btc_price = btc_price
        self.last_eth_price = eth_price
