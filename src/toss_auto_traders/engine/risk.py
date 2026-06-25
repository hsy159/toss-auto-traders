from __future__ import annotations

from dataclasses import dataclass

from toss_auto_traders.api.order import OrderRequest
from toss_auto_traders.config import Settings


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str


class RiskManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.daily_order_count = 0

    def check_order(self, order: OrderRequest) -> RiskDecision:
        if order.quantity <= 0:
            return RiskDecision(False, "Order quantity must be positive.")

        if order.side == "buy" and order.estimated_amount <= 0:
            return RiskDecision(False, "Buy orders require a limit price for risk checks.")

        if order.estimated_amount > self.settings.max_order_amount_krw:
            return RiskDecision(False, "Estimated order amount exceeds MAX_ORDER_AMOUNT_KRW.")

        if self.daily_order_count >= self.settings.max_daily_order_count:
            return RiskDecision(False, "Daily order count exceeds MAX_DAILY_ORDER_COUNT.")

        return RiskDecision(True, "Order passed local risk checks.")

    def record_order_attempt(self) -> None:
        self.daily_order_count += 1
