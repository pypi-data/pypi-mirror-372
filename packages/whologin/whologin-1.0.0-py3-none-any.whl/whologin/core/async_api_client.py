from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

from .error import WhoLoginAPIError


class AsyncBaseAPIClient:
    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url[:-1] if api_url.endswith("/") else api_url
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def _request(
        self, endpoint: str, method: str, body: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = f"{self.api_url}{endpoint}"
        try:
            resp = await self._client.request(method, url, json=body)
        except httpx.RequestError as e:
            raise WhoLoginAPIError(f"Network request failed: {str(e)}")

        content_type = resp.headers.get("content-type", "")
        if "application/json" not in content_type:
            if resp.is_success:
                return None
            raise WhoLoginAPIError(f"HTTP Error: {resp.status_code}")

        decoded = resp.json()
        if decoded.get("success") is True:
            return decoded.get("data")
        raise WhoLoginAPIError(decoded.get("errorMessage", "Unknown API error"))

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncBaseAPIClient":
        return self

    async def __aexit__(self, exc_type, exc: Exception, tb) -> None:
        await self.aclose()
