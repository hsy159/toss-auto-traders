from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import asdict
from typing import Any

from toss_auto_traders.api.account import AccountAPI
from toss_auto_traders.api.client import TossInvestAPIError, TossInvestClient
from toss_auto_traders.api.order import OrderAPI
from toss_auto_traders.config import Settings
from toss_auto_traders.engine.runner import TradingRunner
from toss_auto_traders.web import run_server


def _print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _get_public_ip() -> str:
    with urllib.request.urlopen("https://api.ipify.org", timeout=10) as response:
        return response.read().decode().strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="toss-trader")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check-ip", help="Show the public IP seen by outbound API calls.")
    subparsers.add_parser("auth-token", help="Issue an OAuth access token.")
    subparsers.add_parser("accounts", help="List TossInvest accounts.")
    subparsers.add_parser("holdings", help="List holdings for TOSSINVEST_ACCOUNT.")

    dry_run = subparsers.add_parser("dry-run", help="Evaluate a strategy without live orders.")
    dry_run.add_argument("--symbol", required=True)
    dry_run.add_argument("--quantity", type=int, default=1)
    dry_run.add_argument("--prices", nargs="+", type=float, required=True)

    web = subparsers.add_parser("web", help="Run a local read-only dashboard.")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)

    return parser


def main() -> None:
    try:
        args = build_parser().parse_args()
        settings = Settings.from_env()
        client = TossInvestClient(settings)

        if args.command == "check-ip":
            _print_json(
                {
                    "public_ip": _get_public_ip(),
                    "hint": "Register this exact IP in Toss WTS > Settings > Open API for the same client_id.",
                }
            )
            return

        if args.command == "auth-token":
            token = client.get_access_token()
            _print_json({"access_token_preview": f"{token[:8]}...", "expires": "cached"})
            return

        if args.command == "accounts":
            _print_json(AccountAPI(client).list_accounts())
            return

        if args.command == "holdings":
            _print_json(AccountAPI(client).get_holdings())
            return

        if args.command == "dry-run":
            runner = TradingRunner(settings, OrderAPI(client))
            result = runner.evaluate_prices(
                symbol=args.symbol,
                prices=args.prices,
                quantity=args.quantity,
            )
            _print_json(asdict(result))
            return

        if args.command == "web":
            run_server(host=args.host, port=args.port)
            return

        raise AssertionError(f"Unhandled command: {args.command}")
    except TossInvestAPIError as error:
        _print_json(
            {
                "error": "tossinvest_api_error",
                "status": error.status,
                "body": error.body,
            }
        )
        sys.exit(1)
    except RuntimeError as error:
        _print_json({"error": "runtime_error", "message": str(error)})
        sys.exit(1)


if __name__ == "__main__":
    main()
