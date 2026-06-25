from __future__ import annotations

from dataclasses import dataclass

from toss_auto_traders.api.account import AccountAPI
from toss_auto_traders.api.client import TossInvestClient
from toss_auto_traders.api.market import MarketAPI
from toss_auto_traders.api.order import OrderAPI
from toss_auto_traders.config import Settings


@dataclass
class AppContext:
    settings: Settings
    client: TossInvestClient
    accounts: AccountAPI
    market: MarketAPI
    orders: OrderAPI


def create_app_context() -> AppContext:
    settings = Settings.from_env()
    client = TossInvestClient(settings)
    return AppContext(
        settings=settings,
        client=client,
        accounts=AccountAPI(client),
        market=MarketAPI(client),
        orders=OrderAPI(client),
    )
