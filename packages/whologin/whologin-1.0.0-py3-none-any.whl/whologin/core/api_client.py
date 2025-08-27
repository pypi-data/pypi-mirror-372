from __future__ import annotations

import json
from typing import Any, Dict, Optional, TypeVar, Generic
import urllib.request
import urllib.error

from .error import WhoLoginAPIError

T = TypeVar("T")


class BaseAPIClient(Generic[T]):
    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url[:-1] if api_url.endswith("/") else api_url
        self.api_key = api_key

    def _request(
        self, endpoint: str, method: str, body: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = f"{self.api_url}{endpoint}"
        data = None if body is None else json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url=url, method=method)
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, data=data) as resp:
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read()
                if "application/json" not in content_type:
                    if 200 <= resp.status < 300:
                        return None
                    raise WhoLoginAPIError(f"HTTP Error: {resp.status}")
                decoded = json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                decoded = json.loads(e.read().decode("utf-8"))
                # fallthrough to unified handling
            except Exception:
                raise WhoLoginAPIError(f"HTTP Error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise WhoLoginAPIError(f"Network request failed: {e.reason}")

        if decoded.get("success") is True:
            return decoded.get("data")
        raise WhoLoginAPIError(decoded.get("errorMessage", "Unknown API error"))
