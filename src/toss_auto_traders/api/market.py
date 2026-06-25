from __future__ import annotations

from typing import Any

from toss_auto_traders.api import endpoints
from toss_auto_traders.api.client import TossInvestClient


class MarketAPI:
    def __init__(self, client: TossInvestClient):
        self.client = client

    def get_price(self, symbol: str) -> dict[str, Any]:
        return self.client.get(endpoints.PRICES, query={"symbols": symbol})

    def get_orderbook(self, symbol: str) -> dict[str, Any]:
        return self.client.get(endpoints.ORDERBOOK, query={"symbol": symbol})

    def get_stocks(self, symbols: str) -> dict[str, Any]:
        return self.client.get(endpoints.STOCKS, query={"symbols": symbols})

    def get_exchange_rate(
        self,
        *,
        base_currency: str = "USD",
        quote_currency: str = "KRW",
        date_time: str | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "baseCurrency": base_currency,
            "quoteCurrency": quote_currency,
        }
        if date_time:
            query["dateTime"] = date_time
        return self.client.get(endpoints.EXCHANGE_RATE, query=query)

    def get_market_calendar_kr(self) -> dict[str, Any]:
        return self.client.get(endpoints.MARKET_CALENDAR_KR)

    def get_market_calendar_us(self) -> dict[str, Any]:
        return self.client.get(endpoints.MARKET_CALENDAR_US)
