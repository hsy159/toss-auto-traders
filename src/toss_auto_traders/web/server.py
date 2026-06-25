from __future__ import annotations

import json
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from typing import Any, Callable

from toss_auto_traders.api.client import TossInvestAPIError
from toss_auto_traders.bootstrap import AppContext, create_app_context
from toss_auto_traders.web.holdings_view import build_holdings_view


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Any) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _html_response(handler: BaseHTTPRequestHandler, html: str) -> None:
    body = html.encode()
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _get_public_ip() -> str | None:
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
            return response.read().decode().strip()
    except OSError:
        return None


def _query_value(query: dict[str, list[str]], key: str, default: str = "") -> str:
    return (query.get(key) or [default])[0].strip()


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def create_handler(context: AppContext):
    dashboard_html = (
        resources.files("toss_auto_traders.web").joinpath("dashboard.html").read_text(encoding="utf-8")
    )

    class DashboardHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _handle_api(self, handler: Callable[[], Any]) -> None:
            try:
                _json_response(self, HTTPStatus.OK, handler())
            except TossInvestAPIError as error:
                _json_response(
                    self,
                    error.status,
                    {
                        "error": "tossinvest_api_error",
                        "status": error.status,
                        "body": error.body,
                    },
                )
            except RuntimeError as error:
                _json_response(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {"error": "runtime_error", "message": str(error)},
                )

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            if path == "/":
                _html_response(self, dashboard_html)
                return

            routes: dict[str, Callable[[], Any]] = {
                "/api/status": lambda: {
                    "dry_run": context.settings.dry_run,
                    "account": context.settings.account,
                    "public_ip": _get_public_ip(),
                },
                "/api/check-ip": lambda: {"public_ip": _get_public_ip()},
                "/api/auth-token": lambda: {
                    "access_token_preview": (
                        f"{context.client.get_access_token(force_refresh=True)[:12]}..."
                    ),
                    "message": "Token re-issued successfully.",
                },
                "/api/accounts": context.accounts.list_accounts,
                "/api/holdings": context.accounts.get_holdings,
                "/api/exchange-rate": lambda: context.market.get_exchange_rate(
                    base_currency=_query_value(query, "baseCurrency", "USD"),
                    quote_currency=_query_value(query, "quoteCurrency", "KRW"),
                    date_time=_query_value(query, "dateTime") or None,
                ),
                "/api/market-calendar/kr": context.market.get_market_calendar_kr,
                "/api/market-calendar/us": context.market.get_market_calendar_us,
                "/api/orders": lambda: context.orders.list_orders(
                    status=_query_value(query, "status", "OPEN"),
                    symbol=_query_value(query, "symbol") or None,
                ),
                "/api/buying-power": lambda: context.orders.get_buying_power(
                    currency=_query_value(query, "currency", "KRW"),
                ),
                "/api/commissions": context.orders.get_commissions,
                "/api/dashboard": lambda: build_holdings_view(
                    context.accounts.get_holdings(),
                    exchange_rate=_num(
                        context.market.get_exchange_rate().get("result", {}).get("rate")
                    ),
                ),
            }

            if path in routes:
                self._handle_api(routes[path])
                return

            if path == "/api/price":
                symbol = _query_value(query, "symbol")
                if not symbol:
                    _json_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        {"error": "symbol query parameter is required"},
                    )
                    return
                self._handle_api(lambda: context.market.get_price(symbol))
                return

            if path == "/api/orderbook":
                symbol = _query_value(query, "symbol")
                if not symbol:
                    _json_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        {"error": "symbol query parameter is required"},
                    )
                    return
                self._handle_api(lambda: context.market.get_orderbook(symbol))
                return

            if path == "/api/stocks":
                symbols = _query_value(query, "symbols")
                if not symbols:
                    _json_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        {"error": "symbols query parameter is required"},
                    )
                    return
                self._handle_api(lambda: context.market.get_stocks(symbols))
                return

            if path == "/api/sellable-quantity":
                symbol = _query_value(query, "symbol")
                if not symbol:
                    _json_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        {"error": "symbol query parameter is required"},
                    )
                    return
                self._handle_api(lambda: context.orders.get_sellable_quantity(symbol))
                return

            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})

    return DashboardHandler


def run_server(*, host: str = "127.0.0.1", port: int = 8765) -> None:
    context = create_app_context()
    handler = create_handler(context)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Toss dashboard running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
    finally:
        server.server_close()
