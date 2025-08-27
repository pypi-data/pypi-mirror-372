from __future__ import annotations

from typing import Any, Callable, Dict, Optional, List

from .core.async_api_client import AsyncBaseAPIClient

RequestHandlerAsync = Callable[[str, str, Optional[Dict[str, Any]]], Any]


class AsyncWhoLoginAPI(AsyncBaseAPIClient):
    def __init__(self, api_url: str, api_key: str) -> None:
        super().__init__(api_url, api_key)
        self.profile = AsyncProfileAPI(self._request)
        self.proxy = AsyncProxyAPI(self._request)
        self.tag = AsyncTagAPI(self._request)


def _unify_list(resp, key: str):
    if isinstance(resp, list):
        return resp
    return (resp or {}).get(key, [])


class AsyncProfileAPI:
    def __init__(self, request: RequestHandlerAsync) -> None:
        self._request = request

    def _to_create_payload(self, obj: Any) -> Any:
        if hasattr(obj, "_build_payload"):
            return obj._build_payload()
        return obj

    def _to_update_payload(self, obj: Any) -> Any:
        if hasattr(obj, "_build_update_payload"):
            return obj._build_update_payload()
        return obj

    async def create(self, payload: Any):
        """Create a profile (awaitable).

        payload can be a dict or ProfileBuilder instance.
        """
        return await self._request(
            "/profile/create", "POST", self._to_create_payload(payload)
        )

    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all profiles (awaitable)."""
        r = await self._request("/profile/all", "GET")
        return _unify_list(r, "profiles")

    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search profiles (awaitable)."""
        r = await self._request("/profile/search", "POST", query)
        return _unify_list(r, "profiles")

    async def get_list_open(self) -> List[Dict[str, Any]]:
        """Get open profiles (awaitable)."""
        r = await self._request("/profile/list-open", "GET")
        return _unify_list(r, "profiles")

    async def get_by_id(self, profile_id: str) -> Any:
        """Get profile by id (awaitable)."""
        return await self._request(f"/profile/{profile_id}", "GET")

    async def update(self, profile_id: str, payload: Any) -> Any:
        """Update a profile by id (awaitable)."""
        return await self._request(
            f"/profile/{profile_id}/update", "POST", self._to_update_payload(payload)
        )

    async def delete(self, profile_id: str) -> Any:
        return await self._request(f"/profile/{profile_id}/delete", "GET")

    async def open(
        self, profile_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Open a profile and get WebSocket URL (awaitable)."""
        return await self._request(f"/profile/{profile_id}/open", "POST", payload or {})

    async def close(self, profile_id: str) -> Any:
        return await self._request(f"/profile/{profile_id}/close", "GET")

    async def add_tags(self, profile_id: str, tags: List[str]) -> Any:
        """Add tags (awaitable)."""
        return await self._request(f"/profile/{profile_id}/add-tags", "POST", tags)

    async def remove_tags(self, profile_id: str, tags: List[str]) -> Any:
        """Remove tags (awaitable)."""
        return await self._request(f"/profile/{profile_id}/remove-tags", "POST", tags)

    async def export_cookies(self, profile_id: str) -> Any:
        """Export cookies (awaitable)."""
        return await self._request(f"/profile/{profile_id}/export-cookies", "GET")

    async def import_cookies(self, profile_id: str, cookies: Any) -> Any:
        """Import cookies (awaitable)."""
        return await self._request(
            f"/profile/{profile_id}/import-cookies", "POST", cookies
        )

    async def geolocate(self, profile_id: str) -> Any:
        return await self._request(f"/profile/{profile_id}/geolocate", "GET")

    async def get_trash(self) -> List[Dict[str, Any]]:
        """Get trash (awaitable)."""
        r = await self._request("/profile/trash", "GET")
        return _unify_list(r, "profiles")

    async def delete_from_trash(self, profile_id: str) -> Any:
        return await self._request(f"/profile/trash/{profile_id}/delete", "GET")

    async def clean_trash(self) -> Any:
        return await self._request("/profile/trash/clean", "GET")

    async def restore_all_from_trash(self) -> Any:
        return await self._request("/profile/trash/restore-all", "GET")

    async def restore_from_trash(self, profile_id: str) -> Any:
        return await self._request(f"/profile/trash/{profile_id}/restore", "GET")

    async def install_extensions(self, profile_id: str, paths: List[str]) -> Any:
        """Install extensions (awaitable)."""
        return await self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"installPaths": paths}}},
        )

    async def disable_extensions(self, profile_id: str, ids: List[str]) -> Any:
        """Disable extensions (awaitable)."""
        return await self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"disabledIds": ids}}},
        )

    async def pin_extensions(self, profile_id: str, ids: List[str]) -> Any:
        """Pin extensions (awaitable)."""
        return await self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"pinnedIds": ids}}},
        )

    async def uninstall_extensions(self, profile_id: str, ids: List[str]) -> Any:
        """Uninstall extensions (awaitable)."""
        return await self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"uninstallIds": ids}}},
        )

    async def get_extensions(self, profile_id: str) -> List[Dict[str, Any]]:
        d = await self._request(f"/profile/{profile_id}", "GET")
        return (((d or {}).get("data") or {}).get("extensionManager", {}) or {}).get(
            "list"
        ) or []


class AsyncProxyAPI:
    def __init__(self, request: RequestHandlerAsync) -> None:
        self._request = request

    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all proxies (awaitable)."""
        r = await self._request("/proxy/all", "GET")
        return _unify_list(r, "proxies")

    async def create(self, payload: Dict[str, Any]) -> Any:
        """Create proxy (awaitable)."""
        return await self._request("/proxy/create", "POST", payload)

    async def update(self, proxy_id: str, payload: Dict[str, Any]) -> Any:
        """Update proxy (awaitable)."""
        return await self._request(f"/proxy/{proxy_id}/update", "POST", payload)

    async def delete(self, proxy_id: str) -> Any:
        return await self._request(f"/proxy/{proxy_id}/delete", "GET")

    async def geolocate_by_id(self, proxy_id: str) -> Any:
        return await self._request(f"/proxy/{proxy_id}/geolocate", "GET")

    async def geolocate(self, payload: Dict[str, Any]) -> Any:
        return await self._request("/proxy/geolocate", "POST", payload)


class AsyncTagAPI:
    def __init__(self, request: RequestHandlerAsync) -> None:
        self._request = request

    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all tags (awaitable)."""
        r = await self._request("/tag/all", "GET")
        return _unify_list(r, "tags")

    async def create(self, payload: Dict[str, Any]) -> Any:
        return await self._request("/tag/create", "POST", payload)

    async def update(self, tag_id: str, payload: Dict[str, Any]) -> Any:
        p = (
            {"name": ((payload or {}).get("data") or {}).get("name")}
            if isinstance(payload, dict)
            and isinstance((payload or {}).get("data"), dict)
            and "name" in (payload or {}).get("data")
            else payload
        )
        return await self._request(f"/tag/{tag_id}/update", "POST", p)

    async def delete(self, tag_id: str) -> Any:
        return await self._request(f"/tag/{tag_id}/delete", "GET")
