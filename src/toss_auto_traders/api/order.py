from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from toss_auto_traders.api import endpoints
from toss_auto_traders.api.client import TossInvestClient

OrderSide = Literal["buy", "sell"]
OrderType = Literal["limit", "market"]


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = "limit"
    price: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "orderType": self.order_type,
        }
        if self.price is not None:
            payload["price"] = self.price
        return payload

    @property
    def estimated_amount(self) -> int:
        if self.price is None:
            return 0
        return self.price * self.quantity


class OrderAPI:
    def __init__(self, client: TossInvestClient):
        self.client = client

    def create_order(self, order: OrderRequest) -> dict[str, Any]:
        return self.client.post(
            endpoints.CREATE_ORDER,
            payload=order.to_payload(),
            account_required=True,
        )

    def get_order(self, order_id: str) -> dict[str, Any]:
        return self.client.get(
            endpoints.ORDER_DETAIL.format(order_id=order_id),
            account_required=True,
        )

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        return self.client.post(
            endpoints.ORDER_CANCEL.format(order_id=order_id),
            account_required=True,
        )

    def list_orders(self, *, status: str = "OPEN", symbol: str | None = None) -> dict[str, Any]:
        query: dict[str, Any] = {"status": status}
        if symbol:
            query["symbol"] = symbol
        return self.client.get(endpoints.ORDERS, query=query, account_required=True)

    def get_buying_power(self, *, currency: str = "KRW") -> dict[str, Any]:
        return self.client.get(
            endpoints.BUYING_POWER,
            query={"currency": currency},
            account_required=True,
        )

    def get_sellable_quantity(self, symbol: str) -> dict[str, Any]:
        return self.client.get(
            endpoints.SELLABLE_QUANTITY,
            query={"symbol": symbol},
            account_required=True,
        )

    def get_commissions(self) -> dict[str, Any]:
        return self.client.get(endpoints.COMMISSIONS, account_required=True)
