from __future__ import annotations

import os


def endpoint(env_name: str, default: str) -> str:
    return os.getenv(env_name, default)


# Keep endpoint paths here until the OpenAPI JSON is wired into generated clients.
AUTH_TOKEN = endpoint("TOSSINVEST_TOKEN_PATH", "/oauth2/token")
ACCOUNTS = endpoint("TOSSINVEST_ACCOUNTS_PATH", "/api/v1/accounts")
HOLDINGS = endpoint("TOSSINVEST_HOLDINGS_PATH", "/api/v1/holdings")
PRICES = endpoint("TOSSINVEST_PRICES_PATH", "/api/v1/prices")
ORDERBOOK = endpoint("TOSSINVEST_ORDERBOOK_PATH", "/api/v1/orderbook")
STOCKS = endpoint("TOSSINVEST_STOCKS_PATH", "/api/v1/stocks")
EXCHANGE_RATE = endpoint("TOSSINVEST_EXCHANGE_RATE_PATH", "/api/v1/exchange-rate")
MARKET_CALENDAR_KR = endpoint("TOSSINVEST_MARKET_CALENDAR_KR_PATH", "/api/v1/market-calendar/KR")
MARKET_CALENDAR_US = endpoint("TOSSINVEST_MARKET_CALENDAR_US_PATH", "/api/v1/market-calendar/US")
ORDERS = endpoint("TOSSINVEST_ORDERS_PATH", "/api/v1/orders")
BUYING_POWER = endpoint("TOSSINVEST_BUYING_POWER_PATH", "/api/v1/buying-power")
SELLABLE_QUANTITY = endpoint("TOSSINVEST_SELLABLE_QUANTITY_PATH", "/api/v1/sellable-quantity")
COMMISSIONS = endpoint("TOSSINVEST_COMMISSIONS_PATH", "/api/v1/commissions")
CREATE_ORDER = endpoint("TOSSINVEST_CREATE_ORDER_PATH", "/api/v1/orders")
ORDER_DETAIL = endpoint("TOSSINVEST_ORDER_DETAIL_PATH", "/api/v1/orders/{order_id}")
ORDER_CANCEL = endpoint("TOSSINVEST_ORDER_CANCEL_PATH", "/api/v1/orders/{order_id}/cancel")
