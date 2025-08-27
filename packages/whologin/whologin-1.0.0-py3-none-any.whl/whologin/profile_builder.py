from __future__ import annotations

from typing import Any, Dict, List, Optional


class ProfileBuilder:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._tags: List[str] = []
        self._id: Optional[str] = None

    # Basic
    def with_id(self, profile_id: str) -> "ProfileBuilder":
        self._id = profile_id
        return self

    def with_profile_name(self, name: str) -> "ProfileBuilder":
        self._data["profileName"] = name
        return self

    def with_note(self, note: str) -> "ProfileBuilder":
        self._data["note"] = note
        return self

    def with_tag(self, tag: str) -> "ProfileBuilder":
        self._tags.append(tag)
        return self

    def with_tags(self, tags: List[str]) -> "ProfileBuilder":
        self._tags = list(tags)
        return self

    # OS
    def with_os(self, os: Dict[str, Any]) -> "ProfileBuilder":
        self._data["os"] = os
        return self

    def with_windows_os(self) -> "ProfileBuilder":
        return self.with_os({"type": "windows"})

    def with_linux_os(self) -> "ProfileBuilder":
        return self.with_os({"type": "linux"})

    def with_android_os(self) -> "ProfileBuilder":
        return self.with_os({"type": "android"})

    # Browser
    def with_browser(self, browser: Dict[str, Any]) -> "ProfileBuilder":
        self._data["browser"] = browser
        return self

    def with_specter_browser(self, version: Optional[str] = None) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"type": "specter"}
        if version is not None:
            payload["version"] = version
        return self.with_browser(payload)

    # Proxy helpers
    def with_direct_proxy(
        self, geo_from_ip: Optional[Dict[str, Any]] = None
    ) -> "ProfileBuilder":
        self._data["proxy"] = {"type": "direct", "geoFromIp": geo_from_ip}
        return self

    def with_http_proxy(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        geo_from_ip: Optional[Dict[str, Any]] = None,
    ) -> "ProfileBuilder":
        payload = {"type": "http", "host": host, "port": port}
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        if geo_from_ip is not None:
            payload["geoFromIp"] = geo_from_ip
        self._data["proxy"] = payload
        return self

    def with_wireguard_proxy(self, **kwargs: Any) -> "ProfileBuilder":
        payload = {"type": "wireguard"}
        payload.update(kwargs)
        self._data["proxy"] = payload
        return self

    # Do Not Track
    def with_do_not_track_enabled(self) -> "ProfileBuilder":
        self._data["doNotTrack"] = True
        return self

    def with_do_not_track_disabled(self) -> "ProfileBuilder":
        self._data["doNotTrack"] = False
        return self

    # User Agent
    def with_user_agent(self, ua: Dict[str, Any]) -> "ProfileBuilder":
        self._data["userAgent"] = ua
        return self

    def with_user_agent_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_user_agent(payload)

    def with_user_agent_custom(
        self, value: str, metadata: Optional[Dict[str, Any]] = None
    ) -> "ProfileBuilder":
        ua = self._data.get("userAgent") or {"mode": "custom"}
        ua["custom"] = (
            {"value": value, "metadata": metadata}
            if metadata is not None
            else {"value": value}
        )
        self._data["userAgent"] = ua
        return self

    def with_system_user_agent(self) -> "ProfileBuilder":
        return self.with_user_agent_mode("system")

    def with_mask_user_agent(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_user_agent_mode("mask", seed)

    # Navigator
    def with_navigator(self, nav: Dict[str, Any]) -> "ProfileBuilder":
        self._data["navigator"] = nav
        return self

    def with_navigator_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_navigator(payload)

    def with_navigator_custom(self, custom: Dict[str, Any]) -> "ProfileBuilder":
        nav = self._data.get("navigator") or {"mode": "custom"}
        nav["custom"] = custom
        self._data["navigator"] = nav
        return self

    def with_system_navigator(self) -> "ProfileBuilder":
        return self.with_navigator_mode("system")

    def with_mask_navigator(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_navigator_mode("mask", seed)

    # Screen
    def with_screen(self, screen: Dict[str, Any]) -> "ProfileBuilder":
        self._data["screen"] = screen
        return self

    def with_screen_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_screen(payload)

    def with_screen_custom(self, custom: Dict[str, Any]) -> "ProfileBuilder":
        screen = self._data.get("screen") or {"mode": "custom"}
        screen["custom"] = custom
        self._data["screen"] = screen
        return self

    def with_system_screen(self) -> "ProfileBuilder":
        return self.with_screen_mode("system")

    def with_mask_screen(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_screen_mode("mask", seed)

    def with_media_devices(self, media: Dict[str, Any]) -> "ProfileBuilder":
        self._data["mediaDevices"] = media
        return self

    def with_media_devices_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_media_devices(payload)

    def with_system_media_devices(self) -> "ProfileBuilder":
        return self.with_media_devices_mode("system")

    def with_webgl_metadata(self, metadata: Dict[str, Any]) -> "ProfileBuilder":
        self._data["webGLMetadata"] = metadata
        return self

    def with_webgl_metadata_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_webgl_metadata(payload)

    def with_webgl_metadata_custom(self, custom: Dict[str, Any]) -> "ProfileBuilder":
        val = self._data.get("webGLMetadata") or {"mode": "custom"}
        val["custom"] = custom
        self._data["webGLMetadata"] = val
        return self

    def with_mask_webgl_metadata(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_webgl_metadata_mode("mask", seed)

    def with_webgl_image(self, image: Dict[str, Any]) -> "ProfileBuilder":
        self._data["webGLImage"] = image
        return self

    def with_webgl_image_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_webgl_image(payload)

    def with_mask_webgl_image(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_webgl_image_mode("mask", seed)

    def with_time_zone(self, tz: Dict[str, Any]) -> "ProfileBuilder":
        self._data["timeZone"] = tz
        return self

    def with_time_zone_mode(
        self, mode: str, value: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if value is not None:
            payload["value"] = value
        return self.with_time_zone(payload)

    def with_system_time_zone(self) -> "ProfileBuilder":
        return self.with_time_zone_mode("system")

    def with_based_ip_time_zone(self) -> "ProfileBuilder":
        return self.with_time_zone_mode("based-ip")

    def with_custom_time_zone(self, timezone: str) -> "ProfileBuilder":
        return self.with_time_zone_mode("custom", timezone)

    def with_language(self, lang: Dict[str, Any]) -> "ProfileBuilder":
        self._data["language"] = lang
        return self

    def with_language_mode(
        self, mode: str, value: Optional[List[str]] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if value is not None:
            payload["value"] = value
        return self.with_language(payload)

    def with_system_language(self) -> "ProfileBuilder":
        return self.with_language_mode("system")

    def with_based_ip_language(self) -> "ProfileBuilder":
        return self.with_language_mode("based-ip")

    def with_custom_language(self, languages: List[str]) -> "ProfileBuilder":
        return self.with_language_mode("custom", languages)

    def with_geolocation(self, geo: Dict[str, Any]) -> "ProfileBuilder":
        self._data["geolocation"] = geo
        return self

    def with_geolocation_mode(self, mode: str) -> "ProfileBuilder":
        return self.with_geolocation({"mode": mode})

    def with_based_ip_geolocation(self) -> "ProfileBuilder":
        return self.with_geolocation_mode("based-ip")

    def with_custom_geolocation(
        self, latitude: float, longitude: float, accuracy: float
    ) -> "ProfileBuilder":
        return self.with_geolocation(
            {
                "mode": "custom",
                "custom": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy,
                },
            }
        )

    def with_canvas(self, canvas: Dict[str, Any]) -> "ProfileBuilder":
        self._data["canvas"] = canvas
        return self

    def with_canvas_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_canvas(payload)

    def with_mask_canvas(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_canvas_mode("mask", seed)

    def with_audio_context(self, audio: Dict[str, Any]) -> "ProfileBuilder":
        self._data["audioContext"] = audio
        return self

    def with_audio_context_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_audio_context(payload)

    def with_mask_audio_context(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_audio_context_mode("mask", seed)

    def with_client_rects(self, rects: Dict[str, Any]) -> "ProfileBuilder":
        self._data["clientRects"] = rects
        return self

    def with_client_rects_mode(
        self, mode: str, seed: Optional[str] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_client_rects(payload)

    def with_mask_client_rects(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_client_rects_mode("mask", seed)

    def with_font(self, font: Dict[str, Any]) -> "ProfileBuilder":
        self._data["font"] = font
        return self

    def with_font_mode(self, mode: str, seed: Optional[str] = None) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if seed is not None:
            payload["seed"] = seed
        return self.with_font(payload)

    def with_mask_font(self, seed: Optional[str] = None) -> "ProfileBuilder":
        return self.with_font_mode("mask", seed)

    def with_extension_manager(self, manager: Dict[str, Any]) -> "ProfileBuilder":
        self._data["extensionManager"] = manager
        return self

    def with_extensions(self, extensions: List[Dict[str, Any]]) -> "ProfileBuilder":
        mgr = self._data.get("extensionManager") or {}
        mgr["list"] = extensions
        self._data["extensionManager"] = mgr
        return self

    def with_permissions(self, permissions: Dict[str, Any]) -> "ProfileBuilder":
        self._data["permissions"] = permissions
        return self

    def with_geolocation_permission(self, state: str) -> "ProfileBuilder":
        perms = self._data.get("permissions") or {}
        perms["geolocation"] = state
        self._data["permissions"] = perms
        return self

    def with_notification_permission(self, state: str) -> "ProfileBuilder":
        perms = self._data.get("permissions") or {}
        perms["notifications"] = state
        self._data["permissions"] = perms
        return self

    def with_dns(self, dns: Dict[str, Any]) -> "ProfileBuilder":
        self._data["dns"] = dns
        return self

    def with_dns_address(self, address: str) -> "ProfileBuilder":
        return self.with_dns({"address": address})

    def with_restore_on_startup(self, ros: Dict[str, Any]) -> "ProfileBuilder":
        self._data["restoreOnStartup"] = ros
        return self

    def with_restore_on_startup_mode(
        self, mode: str, urls: Optional[List[str]] = None
    ) -> "ProfileBuilder":
        payload: Dict[str, Any] = {"mode": mode}
        if urls is not None:
            payload["urls"] = urls
        return self.with_restore_on_startup(payload)

    def with_command_line_switches(self, switches: List[str]) -> "ProfileBuilder":
        self._data["commandLineSwitches"] = switches
        return self

    def with_socks5_proxy(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        geo_from_ip: Optional[Dict[str, Any]] = None,
    ) -> "ProfileBuilder":
        payload = {"type": "socks5", "host": host, "port": port}
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        if geo_from_ip is not None:
            payload["geoFromIp"] = geo_from_ip
        self._data["proxy"] = payload
        return self

    def _build_payload(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "tags": self._tags,
            "data": self._data,
        }

    def _build_update_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"data": self._data}
        if self._tags:
            payload["tags"] = self._tags
        return payload
