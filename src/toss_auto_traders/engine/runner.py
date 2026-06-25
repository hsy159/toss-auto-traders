from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from toss_auto_traders.api.order import OrderAPI, OrderRequest
from toss_auto_traders.config import Settings
from toss_auto_traders.engine.risk import RiskManager
from toss_auto_traders.strategy import moving_average_signal


@dataclass(frozen=True)
class DryRunResult:
    symbol: str
    signal: dict[str, Any]
    proposed_order: dict[str, Any] | None
    risk: dict[str, Any] | None
    dry_run: bool


class TradingRunner:
    def __init__(self, settings: Settings, order_api: OrderAPI | None = None):
        self.settings = settings
        self.order_api = order_api
        self.risk_manager = RiskManager(settings)

    def evaluate_prices(
        self,
        *,
        symbol: str,
        prices: list[float],
        quantity: int = 1,
    ) -> DryRunResult:
        signal = moving_average_signal(prices)
        proposed_order: OrderRequest | None = None
        risk = None

        if signal.action in {"buy", "sell"}:
            proposed_order = OrderRequest(
                symbol=symbol,
                side=signal.action,
                quantity=quantity,
                order_type="limit",
                price=int(prices[-1]),
            )
            risk = self.risk_manager.check_order(proposed_order)

            if risk.allowed and not self.settings.dry_run:
                if self.order_api is None:
                    raise RuntimeError("OrderAPI is required when DRY_RUN=false.")
                self.risk_manager.record_order_attempt()
                self.order_api.create_order(proposed_order)

        return DryRunResult(
            symbol=symbol,
            signal=asdict(signal),
            proposed_order=proposed_order.to_payload() if proposed_order else None,
            risk=asdict(risk) if risk else None,
            dry_run=self.settings.dry_run,
        )
