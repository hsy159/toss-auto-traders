from __future__ import annotations

from typing import Any


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _price_to_krw(price: dict[str, Any] | None, *, rate: float) -> float:
    if not price:
        return 0.0
    return _num(price.get("krw")) + _num(price.get("usd")) * rate


def _profit_from_rate(*, profit_rate: float, purchase_amount_krw: float) -> float:
    return profit_rate * purchase_amount_krw


def build_holdings_view(holdings: dict[str, Any], *, exchange_rate: float) -> dict[str, Any]:
    result = holdings.get("result") or {}
    items = result.get("items") or []
    rate = exchange_rate

    enriched_items: list[dict[str, Any]] = []
    for item in items:
        currency = item.get("currency", "KRW")
        market_value = _num(item.get("marketValue", {}).get("amount"))
        purchase_amount = _num(item.get("marketValue", {}).get("purchaseAmount"))
        profit_rate = _num(item.get("profitLoss", {}).get("rate"))
        daily_rate = _num(item.get("dailyProfitLoss", {}).get("rate"))
        daily_amount = _num(item.get("dailyProfitLoss", {}).get("amount"))
        last_price = _num(item.get("lastPrice"))

        if currency == "USD":
            purchase_amount_krw = purchase_amount * rate
            krw_view = {
                "lastPrice": last_price * rate,
                "marketValue": market_value * rate,
                "purchaseAmount": purchase_amount_krw,
                "profitLoss": _profit_from_rate(
                    profit_rate=profit_rate,
                    purchase_amount_krw=purchase_amount_krw,
                ),
                "dailyProfitLoss": _profit_from_rate(
                    profit_rate=daily_rate,
                    purchase_amount_krw=purchase_amount_krw,
                ),
            }
        else:
            krw_view = {
                "lastPrice": last_price,
                "marketValue": market_value,
                "purchaseAmount": purchase_amount,
                "profitLoss": _profit_from_rate(
                    profit_rate=profit_rate,
                    purchase_amount_krw=purchase_amount,
                ),
                "dailyProfitLoss": _profit_from_rate(
                    profit_rate=daily_rate,
                    purchase_amount_krw=purchase_amount,
                ),
            }

        enriched_items.append({**item, "krwView": krw_view})

    all_market_value = _price_to_krw(result.get("marketValue", {}).get("amount"), rate=rate)
    all_purchase_amount = _price_to_krw(result.get("totalPurchaseAmount"), rate=rate)
    all_profit_rate = _num(result.get("profitLoss", {}).get("rate"))
    all_daily_profit_rate = _num(result.get("dailyProfitLoss", {}).get("rate"))
    all_profit_loss = _profit_from_rate(
        profit_rate=all_profit_rate,
        purchase_amount_krw=all_purchase_amount,
    )
    all_daily_profit_loss = _profit_from_rate(
        profit_rate=all_daily_profit_rate,
        purchase_amount_krw=all_purchase_amount,
    )

    def _segment_summary(market_country: str | None) -> dict[str, Any]:
        segment_items = enriched_items
        if market_country is not None:
            segment_items = [item for item in enriched_items if item.get("marketCountry") == market_country]

        if market_country == "US":
            market_value = sum(_num(item.get("marketValue", {}).get("amount")) for item in segment_items)
            purchase_amount = sum(_num(item.get("marketValue", {}).get("purchaseAmount")) for item in segment_items)
            profit_loss = sum(_num(item.get("profitLoss", {}).get("amount")) for item in segment_items)
            daily_profit_loss = sum(_num(item.get("dailyProfitLoss", {}).get("amount")) for item in segment_items)
            profit_rate = profit_loss / purchase_amount if purchase_amount else 0.0
            daily_profit_rate = daily_profit_loss / purchase_amount if purchase_amount else 0.0
            currency = "USD"
            digits = 2
        else:
            market_value = sum(_num(item.get("marketValue", {}).get("amount")) for item in segment_items)
            purchase_amount = sum(_num(item.get("marketValue", {}).get("purchaseAmount")) for item in segment_items)
            profit_loss = sum(_num(item.get("profitLoss", {}).get("amount")) for item in segment_items)
            daily_profit_loss = sum(_num(item.get("dailyProfitLoss", {}).get("amount")) for item in segment_items)
            profit_rate = profit_loss / purchase_amount if purchase_amount else 0.0
            daily_profit_rate = daily_profit_loss / purchase_amount if purchase_amount else 0.0
            currency = "KRW"
            digits = 0

        return {
            "currency": currency,
            "digits": digits,
            "marketValue": market_value,
            "purchaseAmount": purchase_amount,
            "profitLoss": profit_loss,
            "dailyProfitLoss": daily_profit_loss,
            "profitRate": profit_rate,
            "dailyProfitRate": daily_profit_rate,
        }

    return {
        "exchangeRate": rate,
        "summary": {
            "ALL": {
                "currency": "KRW",
                "digits": 0,
                "marketValue": all_market_value,
                "purchaseAmount": all_purchase_amount,
                "profitLoss": all_profit_loss,
                "dailyProfitLoss": all_daily_profit_loss,
                "profitRate": _num(result.get("profitLoss", {}).get("rate")),
                "dailyProfitRate": _num(result.get("dailyProfitLoss", {}).get("rate")),
            },
            "KR": _segment_summary("KR"),
            "US": _segment_summary("US"),
        },
        "items": enriched_items,
        "raw": result,
    }
