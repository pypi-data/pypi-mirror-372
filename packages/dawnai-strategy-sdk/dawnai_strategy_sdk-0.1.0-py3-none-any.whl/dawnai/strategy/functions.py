"""Tool functions for strategy development with strong typing."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Literal, TypedDict

import httpx
from pydantic import BaseModel

from ..config import configure as update_config
from ..config import get_config


class NewsItem(TypedDict):
    """Structure for a news item."""

    title: str
    content: str
    url: str
    published_at: str
    source: str
    relevance_score: float


class MarketPrice(BaseModel):
    """Market price data."""

    symbol: str
    price: Decimal
    timestamp: int
    volume: Decimal | None = None
    change_24h: Decimal | None = None


class PolymarketOrder(BaseModel):
    """Polymarket order details."""

    market_id: str
    side: Literal["buy", "sell"]
    size: Decimal
    price: Decimal
    order_id: str | None = None
    status: str | None = None


class PolymarketMarket(BaseModel):
    """Polymarket market details."""

    market_id: str
    question: str
    end_date: str
    volume: Decimal
    liquidity: Decimal
    outcomes: list[dict[str, Any]]
    current_prices: dict[str, Decimal]


class OrderBook(BaseModel):
    """Order book data."""

    bids: list[tuple[Decimal, Decimal]]  # List of (price, size) tuples
    asks: list[tuple[Decimal, Decimal]]  # List of (price, size) tuples
    spread: Decimal
    mid_price: Decimal


class TimeSeries(BaseModel):
    """Time series data point."""

    timestamp: int
    value: Decimal
    volume: Decimal | None = None


def configure(base_url: str | None = None, api_key: str | None = None) -> None:
    """Configure the SDK with API endpoints.

    Args:
        base_url: API base URL (optional, can be set via env or config file)
        api_key: API key (optional, can be set via env or config file)
    """
    kwargs = {}
    if base_url is not None:
        kwargs["base_url"] = base_url
    if api_key is not None:
        kwargs["api_key"] = api_key

    if kwargs:
        update_config(**kwargs)


def _call_tool(tool_name: str, params: dict[str, Any]) -> Any:
    """Internal function to call a tool via the API."""
    config = get_config()
    url = f"{config.base_url}/code-runner/execute"
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    payload = {"toolName": tool_name, "args": params, "context": config.get_context()}

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers, timeout=30.0)

        # Check if response is HTML (error)
        if response.headers.get("content-type", "").startswith("text/html"):
            error_msg = response.text
            # Try to extract meaningful error from HTML
            if "Error executing tool" in error_msg:
                raise ValueError(f"Tool execution error: {error_msg}")
            raise ValueError(f"Unexpected HTML response: {error_msg[:200]}")

        response.raise_for_status()

        # Parse JSON response
        try:
            return response.json()
        except Exception:
            # If JSON parsing fails, return empty dict for tools that don't return data
            return {}


def get_news(
    query: str | None = None,
    limit: int = 10,
) -> list[NewsItem]:
    """Fetch news articles using browser search.

    Args:
        query: Optional search query
        sources: Optional list of news sources to filter
        limit: Maximum number of articles to return

    Returns:
        List of news items
    """
    if not query:
        query = "news"

    result = _call_tool("browser_search", {"query": query, "limit": limit})

    # Convert search results to news items
    return [
        {
            "title": r.get("title", ""),
            "content": r.get("description", ""),
            "url": r.get("url", ""),
            "published_at": r.get("publishedDate", ""),
            "source": "browser_search",
            "relevance_score": 1.0,
        }
        for r in result.get("results", [])
    ]


def fetch_current_price(market_id: str) -> MarketPrice:
    """Fetch current market price for a Polymarket market.

    Args:
        market_id: Polymarket market ID

    Returns:
        Current market price data
    """
    result = _call_tool("get_polymarket_prices", {"marketId": market_id})

    # Handle the response structure
    price_data = result[0] if isinstance(result, list) and len(result) > 0 else result

    return MarketPrice(
        symbol=market_id,
        price=Decimal(str(price_data.get("price", 0))),
        timestamp=price_data.get("timestamp", 0),
        volume=Decimal(str(price_data.get("volume", 0))) if "volume" in price_data else None,
        change_24h=(
            Decimal(str(price_data.get("change_24h", 0))) if "change_24h" in price_data else None
        ),
    )


def buy_polymarket(
    market_id: str,
    outcome: str,
    amount: Decimal | float | int,
    price: Decimal | float | None = None,
) -> PolymarketOrder:
    """Place a buy order on Polymarket.

    Args:
        market_id: Polymarket market ID
        outcome: Outcome to buy (e.g., "Yes" or "No")
        amount: Amount to buy
        price: Optional limit price

    Returns:
        Order details
    """
    params = {
        "marketId": market_id,
        "outcome": outcome,
        "amount": str(amount),
        "side": "buy",
    }
    if price is not None:
        params["price"] = str(price)

    result = _call_tool("polymarket_execute_trade", params)

    return PolymarketOrder(
        market_id=market_id,
        side="buy",
        size=Decimal(str(amount)),
        price=Decimal(str(result.get("price", price or 0))),
        order_id=result.get("order_id"),
        status=result.get("status"),
    )


def sell_polymarket(
    market_id: str,
    outcome: str,
    amount: Decimal | float | int,
    price: Decimal | float | None = None,
) -> PolymarketOrder:
    """Place a sell order on Polymarket.

    Args:
        market_id: Polymarket market ID
        outcome: Outcome to sell
        amount: Amount to sell
        price: Optional limit price

    Returns:
        Order details
    """
    params = {
        "marketId": market_id,
        "outcome": outcome,
        "amount": str(amount),
        "side": "sell",
    }
    if price is not None:
        params["price"] = str(price)

    result = _call_tool("polymarket_execute_trade", params)

    return PolymarketOrder(
        market_id=market_id,
        side="sell",
        size=Decimal(str(amount)),
        price=Decimal(str(result.get("price", price or 0))),
        order_id=result.get("order_id"),
        status=result.get("status"),
    )


# ask_llm function removed - not available in the current API
# Use browser_search or other tools instead


def browser_search(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search the web for information.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        List of search results
    """
    result = _call_tool("browser_search", {"query": query, "limit": limit})
    return result.get("results", [])  # type: ignore[no-any-return]


def tweet_finder(query: str, username: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """Find tweets matching criteria.

    Args:
        query: Search query
        username: Optional username filter
        limit: Maximum results

    Returns:
        List of tweets
    """
    params = {"query": query, "limit": limit}
    if username:
        params["username"] = username

    result = _call_tool("tweet_finder", params)
    return result.get("tweets", [])  # type: ignore[no-any-return]


def get_polymarket_market_details(market_id: str) -> PolymarketMarket:
    """Get detailed information about a Polymarket market.

    Args:
        market_id: Market ID

    Returns:
        Market details
    """
    result = _call_tool("get_polymarket_market_details", {"marketId": market_id})

    return PolymarketMarket(
        market_id=market_id,
        question=result.get("question", ""),
        end_date=result.get("end_date", ""),
        volume=Decimal(str(result.get("volume", 0))),
        liquidity=Decimal(str(result.get("liquidity", 0))),
        outcomes=result.get("outcomes", []),
        current_prices={k: Decimal(str(v)) for k, v in result.get("current_prices", {}).items()},
    )


def get_polymarket_order_book(market_id: str, side: str = "YES") -> OrderBook:
    """Get order book for a Polymarket market.

    Args:
        market_id: Market ID
        side: Side to get order book for ("YES" or "NO")

    Returns:
        Order book data
    """
    result = _call_tool("get_polymarket_order_book", {"marketId": market_id, "side": side})

    bids = [(Decimal(str(p)), Decimal(str(s))) for p, s in result.get("bids", [])]
    asks = [(Decimal(str(p)), Decimal(str(s))) for p, s in result.get("asks", [])]

    return OrderBook(
        bids=bids,
        asks=asks,
        spread=Decimal(str(result.get("spread", 0))),
        mid_price=Decimal(str(result.get("mid_price", 0))),
    )


def get_polymarket_timeseries(
    market_id: str, side: str = "YES", period: str = "1d"
) -> list[TimeSeries]:
    """Get time series data for a Polymarket market.

    Args:
        market_id: Market ID
        side: Side to get data for ("YES" or "NO")
        period: Time period (e.g., "1h", "1d", "1w")

    Returns:
        List of time series data points
    """
    result = _call_tool(
        "get_polymarket_timeseries",
        {"marketId": market_id, "side": side, "period": period},
    )

    return [
        TimeSeries(
            timestamp=point.get("timestamp", 0),
            value=Decimal(str(point.get("value", 0))),
            volume=Decimal(str(point.get("volume", 0))) if "volume" in point else None,
        )
        for point in result.get("data", [])
    ]


def get_polymarket_prices(market_id: str) -> MarketPrice:
    """Get current price for a Polymarket market.

    Args:
        market_id: Polymarket market ID

    Returns:
        Market price data
    """
    result = _call_tool("get_polymarket_prices", {"marketId": market_id})

    # Handle response structure
    data = result[0] if isinstance(result, list) and len(result) > 0 else result

    return MarketPrice(
        symbol=market_id,
        price=Decimal(str(data.get("price", 0))),
        timestamp=data.get("timestamp", 0),
        volume=Decimal(str(data.get("volume", 0))) if "volume" in data else None,
        change_24h=Decimal(str(data.get("change_24h", 0))) if "change_24h" in data else None,
    )


def read_portfolio() -> dict[str, Any]:
    """Read the current portfolio balance and positions.

    Returns:
        Dictionary containing:
        - available_balance: Available funds for trading
        - total_balance: Total portfolio value
        - positions: Current open positions
    """
    result = _call_tool("read_portfolio", {})
    return {
        "available_balance": Decimal(str(result.get("available_balance", 0))),
        "total_balance": Decimal(str(result.get("total_balance", 0))),
        "positions": result.get("positions", []),
    }


def polymarket_smart_search(query: str, limit: int = 10) -> list[PolymarketMarket]:
    """Smart search for Polymarket markets.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        List of matching markets
    """
    result = _call_tool("polymarket_smart_search", {"query": query, "limit": limit})

    markets = []
    for market_data in result.get("markets", []):
        # Handle outcomes - could be a string or list
        outcomes = market_data.get("outcomes", [])
        if isinstance(outcomes, str):
            # Parse JSON string if needed
            try:
                outcomes = json.loads(outcomes)
            except Exception:
                outcomes = []

        # Convert string outcomes to dict format if needed
        if outcomes and isinstance(outcomes[0], str):
            outcomes = [{"name": outcome} for outcome in outcomes]

        markets.append(
            PolymarketMarket(
                market_id=market_data.get("market_id", ""),
                question=market_data.get("question", ""),
                end_date=market_data.get("end_date", ""),
                volume=Decimal(str(market_data.get("volume", 0))),
                liquidity=Decimal(str(market_data.get("liquidity", 0))),
                outcomes=outcomes,
                current_prices={
                    k: Decimal(str(v)) for k, v in market_data.get("current_prices", {}).items()
                },
            )
        )

    return markets
