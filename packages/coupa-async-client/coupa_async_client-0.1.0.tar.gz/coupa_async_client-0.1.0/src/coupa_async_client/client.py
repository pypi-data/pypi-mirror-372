from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, Iterable, List, Mapping, Optional, Sequence, cast

import httpx
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type

from .auth import OAuth2ClientCredentials
from .types import JSONObject


class CoupaAsyncClient:
    """
    Minimal async Coupa client.

    You pass:
      - base_url: e.g. "https://yourcompany.coupahost.com/api"
      - token_url + client_id + client_secret [+ scopes]
      - resource: e.g. "approvals"
      - params: dict with Coupa filters (go straight into querystring)
      - fields: optional raw fields string (Coupa style)
      - offset_start / offset_end: range control (inclusive start, exclusive end)
      - page_size: stride between offsets (Coupa commonly defaults to 50)
      - concurrent: number of parallel page requests
      - until_empty: stop when one full batch returns only empty pages

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
        default_concurrent: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._oauth = OAuth2ClientCredentials(token_url, client_id, client_secret, scopes)
        self._timeout = timeout
        self._default_page_size = default_page_size
        self._default_concurrent = default_concurrent
        self._client = httpx.AsyncClient(timeout=self._timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "CoupaAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _url(self, resource: str) -> str:
        return f"{self.base_url}/{resource.lstrip('/')}"

    async def _auth_header(self) -> str:
        token = await self._oauth.get_access_token()
        return f"Bearer {token}"

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPError),
        wait=wait_exponential_jitter(initial=1, max=30),
        stop=stop_after_attempt(6),
    )
    async def _get(self, url: str, headers: Mapping[str, str], params: Mapping[str, Any]) -> httpx.Response:
        resp = await self._client.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    await asyncio.sleep(float(retry_after))
                except Exception:
                    pass
            raise httpx.HTTPStatusError("429 Too Many Requests", request=resp.request, response=resp)
        resp.raise_for_status()
        return resp

    async def iter_pages(
        self,
        resource: str,
        *,
        params: Dict[str, Any],
        fields: Optional[str] = None,
        offset_start: int = 0,
        offset_end: Optional[int] = None,
        page_size: Optional[int] = None,
        concurrent: Optional[int] = None,
        until_empty: bool = True,
        accept: str = "application/json",
    ) -> AsyncIterator[List[JSONObject]]:
        """
        Yield pages (list[JSONObject]) fetched in parallel by offsets.

        If `offset_end` is provided, offsets are bounded in [offset_start, offset_end).
        If `until_empty` is True, stop when a full batch returns only empty pages (no errors).
        """
        url = self._url(resource)
        auth = await self._auth_header()
        headers = {"Authorization": auth, "Accept": accept}

        ps = page_size or self._default_page_size
        cc = max(1, concurrent or self._default_concurrent)
        current = max(0, offset_start)

        def build_params(off: int) -> Dict[str, Any]:
            q = dict(params)
            q["offset"] = str(off)
            if fields:
                q["fields"] = fields
            return q

        while True:
            offsets: List[int] = []
            for i in range(cc):
                off = current + i * ps
                if offset_end is not None and off >= offset_end:
                    break
                offsets.append(off)
            if not offsets:
                break

            coros = [self._get(url, headers=headers, params=build_params(off)) for off in offsets]
            results: Sequence[httpx.Response | BaseException] = await asyncio.gather(
                *coros,
                return_exceptions=True,
            )

            had_error = False
            had_non_empty = False

            for resp in results:
                if isinstance(resp, BaseException):
                    had_error = True
                    continue

                data = resp.json()
                # Runtime guard: Coupa typically returns a JSON array of objects
                if isinstance(data, list):
                    # keep only dictionaries
                    rows = [row for row in data if isinstance(row, dict)]
                    if rows:
                        had_non_empty = True
                        yield cast(List[JSONObject], rows)
                # else: unexpected shape; ignore silently (or log, if you add hooks)

            # advance to the next window based on the last offset we actually used
            current = offsets[-1] + ps

            if offset_end is not None and current >= offset_end:
                break
            if until_empty and not had_error and not had_non_empty:
                break

    async def iter_items(
        self,
        resource: str,
        *,
        params: Dict[str, Any],
        **kwargs: Any,
    ) -> AsyncIterator[JSONObject]:
        """Flatten page iterator into an item stream."""
        async for page in self.iter_pages(resource, params=params, **kwargs):
            for item in page:
                yield item
