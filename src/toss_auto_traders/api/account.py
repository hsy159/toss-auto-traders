from __future__ import annotations

from typing import Any

from toss_auto_traders.api import endpoints
from toss_auto_traders.api.client import TossInvestClient


class AccountAPI:
    def __init__(self, client: TossInvestClient):
        self.client = client

    def list_accounts(self) -> dict[str, Any]:
        return self.client.get(endpoints.ACCOUNTS, account_required=False)

    def get_holdings(self) -> dict[str, Any]:
        return self.client.get(endpoints.HOLDINGS, account_required=True)
