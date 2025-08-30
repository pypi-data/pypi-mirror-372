from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, cast

import httpx
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type

from .types import JSONObject


class OAuth2ClientCredentialsSync:
    """
    Simple in-memory OAuth2 (client_credentials) token manager (sync).
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
        self._token: Optional[tuple[str, float]] = None  # (access_token, expires_at)

    def _fetch(self) -> tuple[str, float]:
        with httpx.Client(timeout=self._timeout) as client:
            data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
            if self._scopes:
                data["scope"] = " ".join(self._scopes)

            resp = client.post(self._token_url, data=data)
            resp.raise_for_status()
            payload = resp.json()
            access_token: str = payload["access_token"]
            ttl = float(payload.get("expires_in", 3600))
            # refresh slightly early (≥5min headroom)
            expires_at = time.time() + max(ttl - 60.0, 300.0)
            return access_token, expires_at

    def get_access_token(self) -> str:
        now = time.time()
        if self._token is None or now >= self._token[1]:
            self._token = self._fetch()
        return self._token[0]


class CoupaClient:
    """
    Minimal sync Coupa client (single-threaded).

    You pass:
      - base_url: e.g. "https://yourcompany.coupahost.com/api"
      - token_url + client_id + client_secret [+ scopes]
      - resource: e.g. "approvals"
      - params: dict with Coupa filters (go straight into querystring)
      - fields: optional raw fields string (Coupa style)
      - offset_start / offset_end: range control (inclusive start, exclusive end)
      - page_size: stride between offsets (Coupa commonly defaults to 50)
      - until_empty: stop when a page returns empty

    Library ONLY returns JSON (pages or items). No persistence.
    """

    def __init__(
        self,
        base_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        scopes: Optional[Iterable[str]] = None,
        *,
        timeout: float = 60.0,
        default_page_size: int = 50,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._oauth = OAuth2ClientCredentialsSync(token_url, client_id, client_secret, scopes)
        self._timeout = timeout
        self._default_page_size = default_page_size
        self._client = httpx.Client(timeout=self._timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CoupaClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _url(self, resource: str) -> str:
        return f"{self.base_url}/{resource.lstrip('/')}"

    def _auth_header(self) -> str:
        token = self._oauth.get_access_token()
        return f"Bearer {token}"

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPError),
        wait=wait_exponential_jitter(initial=1, max=30),
        stop=stop_after_attempt(6),
    )
    def _get(self, url: str, headers: Mapping[str, str], params: Mapping[str, Any]) -> httpx.Response:
        resp = self._client.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    time.sleep(float(retry_after))
                except Exception:
                    pass
            # force retry via tenacity
            raise httpx.HTTPStatusError("429 Too Many Requests", request=resp.request, response=resp)
        resp.raise_for_status()
        return resp

    def pages(
        self,
        resource: str,
        *,
        params: Dict[str, Any],
        fields: Optional[str] = None,
        offset_start: int = 0,
        offset_end: Optional[int] = None,  # exclusive; if None, unbounded
        page_size: Optional[int] = None,
        until_empty: bool = True,
        accept: str = "application/json",
    ) -> Iterator[List[JSONObject]]:
        """
        Yield pages (list[JSONObject]) sequentially (sync).
        """
        url = self._url(resource)
        headers = {"Authorization": self._auth_header(), "Accept": accept}

        ps = page_size or self._default_page_size
        current = max(0, offset_start)

        def build_params(off: int) -> Dict[str, Any]:
            q = dict(params)
            q["offset"] = str(off)
            if fields:
                q["fields"] = fields
            return q

        while True:
            if offset_end is not None and current >= offset_end:
                break

            resp = self._get(url, headers=headers, params=build_params(current))
            data = resp.json()

            if isinstance(data, list):
                rows = [row for row in data if isinstance(row, dict)]
                if rows:
                    yield cast(List[JSONObject], rows)
                elif until_empty:
                    break
            else:
                # unexpected shape → treat as empty page
                if until_empty:
                    break

            current += ps

    def items(
        self,
        resource: str,
        *,
        params: Dict[str, Any],
        **kwargs: Any,
    ) -> Iterator[JSONObject]:
        """Flatten page iterator into an item stream (sync)."""
        for page in self.pages(resource, params=params, **kwargs):
            for item in page:
                yield item

    def collect_items(
        self,
        resource: str,
        *,
        params: Dict[str, Any],
        **kwargs: Any,
    ) -> List[JSONObject]:
        """Convenience: return all items as a list (sync)."""
        return [row for row in self.items(resource, params=params, **kwargs)]
