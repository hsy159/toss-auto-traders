from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _as_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    api_key: str
    secret_key: str
    account: str | None
    base_url: str
    token_path: str
    dry_run: bool
    max_order_amount_krw: int
    max_daily_order_count: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        api_key = os.getenv("TOSSINVEST_API_KEY", "")
        secret_key = os.getenv("TOSSINVEST_SECRET_KEY", "")
        if not api_key or not secret_key:
            raise RuntimeError(
                "TOSSINVEST_API_KEY and TOSSINVEST_SECRET_KEY must be set."
            )

        return cls(
            api_key=api_key,
            secret_key=secret_key,
            account=os.getenv("TOSSINVEST_ACCOUNT") or None,
            base_url=os.getenv("TOSSINVEST_BASE_URL", "https://openapi.tossinvest.com"),
            token_path=os.getenv("TOSSINVEST_TOKEN_PATH", "/oauth2/token"),
            dry_run=_as_bool(os.getenv("DRY_RUN"), default=True),
            max_order_amount_krw=int(os.getenv("MAX_ORDER_AMOUNT_KRW", "10000")),
            max_daily_order_count=int(os.getenv("MAX_DAILY_ORDER_COUNT", "3")),
        )
