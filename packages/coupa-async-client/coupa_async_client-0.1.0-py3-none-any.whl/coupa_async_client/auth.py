from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Iterable, Optional

import httpx

from .errors import CoupaAuthError


@dataclass
class Token:
    access_token: str
    expires_at: float


class OAuth2ClientCredentials:
    """
    Simple in-memory OAuth2 (client_credentials) token manager.
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scopes: Optional[Iterable[str]] = None,
        timeout: float = 30.0,
    ) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = list(scopes or [])
        self._timeout = timeout
        self._lock = asyncio.Lock()
        self._token: Optional[Token] = None

    async def _fetch(self) -> Token:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
            if self._scopes:
                data["scope"] = " ".join(self._scopes)

            try:
                resp = await client.post(self._token_url, data=data)
                resp.raise_for_status()
            except httpx.HTTPError as e:
                status = getattr(getattr(e, "response", None), "status_code", "N/A")
                text = getattr(getattr(e, "response", None), "text", "") or str(e)
                raise CoupaAuthError(f"Token request failed: {status} {text[:200]}") from e

            payload = resp.json()
            access_token = payload["access_token"]
            ttl = float(payload.get("expires_in", 3600))
            expires_at = time.time() + max(ttl - 60.0, 300.0)
            return Token(access_token=access_token, expires_at=expires_at)

    async def get_access_token(self) -> str:
        async with self._lock:
            now = time.time()
            if self._token is None or now >= self._token.expires_at:
                self._token = await self._fetch()
            return self._token.access_token
