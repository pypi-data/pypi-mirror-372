from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .core.api_client import BaseAPIClient


RequestHandler = Callable[[str, str, Optional[Dict[str, Any]]], Any]


class WhoLoginAPI(BaseAPIClient):
    def __init__(self, api_url: str, api_key: str) -> None:
        super().__init__(api_url, api_key)
        self.profile = ProfileAPI(self._request)
        self.proxy = ProxyAPI(self._request)
        self.tag = TagAPI(self._request)


class ProfileAPI:
    def __init__(self, request: RequestHandler) -> None:
        self._request = request

    def _to_create_payload(self, obj: Any) -> Any:
        if hasattr(obj, "_build_payload"):
            return obj._build_payload()
        return obj

    def _to_update_payload(self, obj: Any) -> Any:
        if hasattr(obj, "_build_update_payload"):
            return obj._build_update_payload()
        return obj

    def create(self, payload: Any) -> Any:
        """Create a profile.

        Args:
            payload: Dict payload or a ProfileBuilder instance.
        Returns:
            Created profile object (dict).
        """
        return self._request(
            "/profile/create", "POST", self._to_create_payload(payload)
        )

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all profiles (not in trash)."""
        r = self._request("/profile/all", "GET")
        return r if isinstance(r, list) else (r or {}).get("profiles", [])

    def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search profiles by query body."""
        r = self._request("/profile/search", "POST", query)
        return r if isinstance(r, list) else (r or {}).get("profiles", [])

    def get_list_open(self) -> List[Dict[str, Any]]:
        """Get profiles currently open on the WhoLogin app."""
        r = self._request("/profile/list-open", "GET")
        return r if isinstance(r, list) else (r or {}).get("profiles", [])

    def get_by_id(self, profile_id: str) -> Any:
        """Get profile details by id."""
        return self._request(f"/profile/{profile_id}", "GET")

    def update(self, profile_id: str, payload: Any) -> Any:
        """Update a profile by id.

        Args:
            profile_id: Target profile id.
            payload: Dict payload or a ProfileBuilder instance.
        """
        return self._request(
            f"/profile/{profile_id}/update", "POST", self._to_update_payload(payload)
        )

    def delete(self, profile_id: str) -> Any:
        """Move a profile to trash by id."""
        return self._request(f"/profile/{profile_id}/delete", "GET")

    def open(self, profile_id: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        """Open a profile and optionally request debugging port/headless.

        Returns:
            WebSocket URL string when applicable.
        """
        return self._request(f"/profile/{profile_id}/open", "POST", payload or {})

    def close(self, profile_id: str) -> Any:
        """Close an opened profile by id."""
        return self._request(f"/profile/{profile_id}/close", "GET")

    def add_tags(self, profile_id: str, tags: List[str]) -> Any:
        """Add tags to a profile."""
        return self._request(f"/profile/{profile_id}/add-tags", "POST", tags)

    def remove_tags(self, profile_id: str, tags: List[str]) -> Any:
        """Remove tags from a profile."""
        return self._request(f"/profile/{profile_id}/remove-tags", "POST", tags)

    def export_cookies(self, profile_id: str) -> Any:
        """Export cookies of a profile."""
        return self._request(f"/profile/{profile_id}/export-cookies", "GET")

    def import_cookies(self, profile_id: str, cookies: Any) -> Any:
        """Import cookies into a profile."""
        return self._request(f"/profile/{profile_id}/import-cookies", "POST", cookies)

    def geolocate(self, profile_id: str) -> Any:
        """Geolocate a profile by id (server-side)."""
        return self._request(f"/profile/{profile_id}/geolocate", "GET")

    def get_trash(self) -> List[Dict[str, Any]]:
        """Get profiles currently in trash."""
        r = self._request("/profile/trash", "GET")
        return r if isinstance(r, list) else (r or {}).get("profiles", [])

    def delete_from_trash(self, profile_id: str) -> Any:
        """Permanently delete a profile from trash."""
        return self._request(f"/profile/trash/{profile_id}/delete", "GET")

    def clean_trash(self) -> Any:
        """Clean all profiles from trash."""
        return self._request("/profile/trash/clean", "GET")

    def restore_all_from_trash(self) -> Any:
        """Restore all profiles from trash."""
        return self._request("/profile/trash/restore-all", "GET")

    def restore_from_trash(self, profile_id: str) -> Any:
        """Restore a profile from trash by id."""
        return self._request(f"/profile/trash/{profile_id}/restore", "GET")

    def install_extensions(self, profile_id: str, paths: List[str]) -> Any:
        """Install extensions into profile by paths (crx or folder)."""
        return self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"installPaths": paths}}},
        )

    def disable_extensions(self, profile_id: str, ids: List[str]) -> Any:
        """Disable extensions by ids."""
        return self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"disabledIds": ids}}},
        )

    def pin_extensions(self, profile_id: str, ids: List[str]) -> Any:
        """Pin extensions by ids."""
        return self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"pinnedIds": ids}}},
        )

    def uninstall_extensions(self, profile_id: str, ids: List[str]) -> Any:
        """Uninstall extensions by ids."""
        return self._request(
            f"/profile/{profile_id}/update",
            "POST",
            {"data": {"extensionManager": {"uninstallIds": ids}}},
        )

    def get_extensions(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get read-only list of current extensions in profile."""
        d = self._request(f"/profile/{profile_id}", "GET")
        return (((d or {}).get("data") or {}).get("extensionManager", {}) or {}).get(
            "list"
        ) or []


class ProxyAPI:
    def __init__(self, request: RequestHandler) -> None:
        self._request = request

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all proxies."""
        r = self._request("/proxy/all", "GET")
        return r if isinstance(r, list) else (r or {}).get("proxies", [])

    def create(self, payload: Dict[str, Any]) -> Any:
        """Create a proxy.

        Args:
            payload: Proxy create request body.
        """
        return self._request("/proxy/create", "POST", payload)

    def update(self, proxy_id: str, payload: Dict[str, Any]) -> Any:
        """Update a proxy by id."""
        return self._request(f"/proxy/{proxy_id}/update", "POST", payload)

    def delete(self, proxy_id: str) -> Any:
        """Delete a proxy by id."""
        return self._request(f"/proxy/{proxy_id}/delete", "GET")

    def geolocate_by_id(self, proxy_id: str) -> Any:
        """Geolocate a proxy by id."""
        return self._request(f"/proxy/{proxy_id}/geolocate", "GET")

    def geolocate(self, payload: Dict[str, Any]) -> Any:
        """Geolocate a host via request body (no id)."""
        return self._request("/proxy/geolocate", "POST", payload)


class TagAPI:
    def __init__(self, request: RequestHandler) -> None:
        self._request = request

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all tags."""
        r = self._request("/tag/all", "GET")
        return r if isinstance(r, list) else (r or {}).get("tags", [])

    def create(self, payload: Dict[str, Any]) -> Any:
        """Create a tag."""
        return self._request("/tag/create", "POST", payload)

    def update(self, tag_id: str, payload: Dict[str, Any]) -> Any:
        """Update a tag by id.

        Accepts either {'data': {'name': '...'}} or a short {'name': '...'} payload.
        """
        p = (
            {"name": ((payload or {}).get("data") or {}).get("name")}
            if isinstance(payload, dict)
            and isinstance((payload or {}).get("data"), dict)
            and "name" in (payload or {}).get("data")
            else payload
        )
        return self._request(f"/tag/{tag_id}/update", "POST", p)

    def delete(self, tag_id: str) -> Any:
        """Delete a tag by id."""
        return self._request(f"/tag/{tag_id}/delete", "GET")
