from __future__ import annotations

from typing import Any

from toss_auto_traders.api import endpoints
from toss_auto_traders.api.client import TossInvestClient


class MarketAPI:
    def __init__(self, client: TossInvestClient):
        self.client = client

    def get_price(self, symbol: str) -> dict[str, Any]:
        return self.client.get(endpoints.PRICE.format(symbol=symbol))

    def get_orderbook(self, symbol: str) -> dict[str, Any]:
        return self.client.get(endpoints.ORDERBOOK.format(symbol=symbol))
