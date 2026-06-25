from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from toss_auto_traders.config import Settings


class TossInvestAPIError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"TossInvest API request failed: status={status}, body={body}")
        self.status = status
        self.body = body


@dataclass
class AccessToken:
    value: str
    expires_at: float

    @property
    def is_valid(self) -> bool:
        return time.time() < self.expires_at - 30


class TossInvestClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._token: AccessToken | None = None

    def get_access_token(self) -> str:
        if self._token is not None and self._token.is_valid:
            return self._token.value

        payload = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.settings.api_key,
                "client_secret": self.settings.secret_key,
            }
        ).encode()

        response = self._send_raw(
            "POST",
            self.settings.token_path,
            body=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=False,
        )
        access_token = response["access_token"]
        expires_in = int(response.get("expires_in", 3600))
        self._token = AccessToken(access_token, time.time() + expires_in)
        return access_token

    def get(
        self,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        account_required: bool = False,
    ) -> dict[str, Any]:
        return self._request("GET", path, query=query, account_required=account_required)

    def post(
        self,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        account_required: bool = False,
    ) -> dict[str, Any]:
        return self._request("POST", path, payload=payload, account_required=account_required)

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        account_required: bool = False,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
        }
        if account_required:
            if not self.settings.account:
                raise RuntimeError("TOSSINVEST_ACCOUNT must be set for account/order APIs.")
            headers["X-Tossinvest-Account"] = self.settings.account

        body = json.dumps(payload).encode() if payload is not None else None
        return self._send_raw(method, path, query=query, body=body, headers=headers)

    def _send_raw(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        del auth  # Reserved for future auth variants if the OpenAPI spec requires them.

        url = self._build_url(path, query)
        request = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read().decode()
        except urllib.error.HTTPError as error:
            raise TossInvestAPIError(error.code, error.read().decode()) from error

        if raw == "":
            return {}
        return json.loads(raw)

    def _build_url(self, path: str, query: dict[str, Any] | None) -> str:
        url = f"{self.settings.base_url.rstrip('/')}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        return url
