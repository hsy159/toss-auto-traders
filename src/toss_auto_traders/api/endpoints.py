from __future__ import annotations

import os


def endpoint(env_name: str, default: str) -> str:
    return os.getenv(env_name, default)


# Keep endpoint paths here until the OpenAPI JSON is wired into generated clients.
AUTH_TOKEN = endpoint("TOSSINVEST_TOKEN_PATH", "/oauth2/token")
ACCOUNTS = endpoint("TOSSINVEST_ACCOUNTS_PATH", "/api/v1/accounts")
HOLDINGS = endpoint("TOSSINVEST_HOLDINGS_PATH", "/api/v1/account/holdings")
PRICE = endpoint("TOSSINVEST_PRICE_PATH", "/api/v1/market/prices/{symbol}")
ORDERBOOK = endpoint("TOSSINVEST_ORDERBOOK_PATH", "/api/v1/market/orderbook/{symbol}")
CREATE_ORDER = endpoint("TOSSINVEST_CREATE_ORDER_PATH", "/api/v1/orders")
ORDER_DETAIL = endpoint("TOSSINVEST_ORDER_DETAIL_PATH", "/api/v1/orders/{order_id}")
ORDER_CANCEL = endpoint("TOSSINVEST_ORDER_CANCEL_PATH", "/api/v1/orders/{order_id}/cancel")
