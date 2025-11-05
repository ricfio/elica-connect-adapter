"""Async AuthProvider implementation for Home Assistant."""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.core import HomeAssistant

from ...core.auth.auth_provider_base import AuthProviderBase  # noqa: TID252
from ...core.auth.auth_service import AuthService  # noqa: TID252

_LOGGER = logging.getLogger(__name__)


class HaAuthProvider(AuthProviderBase):
    """Asynchronous Authentication Provider for Home Assistant."""

    def __init__(
        self,
        hass: HomeAssistant,
        auth_service: AuthService,
        username: str,
        password: str,
    ):
        super().__init__(auth_service, username, password)
        self.hass = hass
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0

        # Cache dei token in memoria (evita accesso a disco)
        hass.data.setdefault("elica_auth", {})

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _is_expiring(self, threshold: int = 60) -> bool:
        return time.time() >= (self._expires_at - threshold)

    def _store_auth(self, auth: dict[str, Any]) -> None:
        """Store authentication tokens in hass.data cache."""
        expires_in = float(auth.get("expires_in", 3600))
        self._expires_at = time.time() + expires_in
        self._access_token = auth.get("access_token")
        self._refresh_token = auth.get("refresh_token")
        self.hass.data["elica_auth"] = {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_at": self._expires_at,
        }

    def _load_auth(self) -> dict[str, Any] | None:
        """Load auth data from hass.data cache."""
        auth_data = self.hass.data.get("elica_auth")
        if not isinstance(auth_data, dict) or not auth_data.get("access_token"):
            return None
        return auth_data

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    async def get_auth(self) -> dict[str, Any] | None:
        return self._load_auth()

    async def authenticate_with_password(self, username: str, password: str) -> None:
        """Authenticate using username and password."""
        _LOGGER.debug("Authenticating with username/password...")
        auth = await self.auth_service.login(username, password)
        self._store_auth(auth)

    async def get_access_token(self) -> str | None:
        """Return a valid access token, refreshing if needed."""
        if not self._access_token:
            cached = self._load_auth()
            if cached:
                self._access_token = cached.get("access_token")
                self._refresh_token = cached.get("refresh_token")
                self._expires_at = cached.get("expires_at", 0)
            else:
                return None

        if self._is_expiring():
            if self._refresh_token:
                new_token = await self.refresh_access_token()
                if new_token:
                    return new_token
            return None

        return self._access_token

    async def refresh_access_token(self) -> str | None:
        """Refresh the access token using the refresh token."""
        if not self._refresh_token:
            return None

        _LOGGER.debug("Refreshing access token...")
        auth = await self.auth_service.refresh_token(self._refresh_token)
        self._store_auth(auth)
        return self._access_token

    async def get_refresh_token(self) -> str | None:
        return self._refresh_token

    async def authenticate_with_token(self, access_token: str) -> None:
        """Authenticate using an existing access token."""
        self._access_token = access_token
        self._expires_at = time.time() + 3600  # Default 1h unless known otherwise
        self.hass.data["elica_auth"].update(
            {
                "access_token": access_token,
                "expires_at": self._expires_at,
            }
        )

    def debug_tokens(self) -> dict[str, Any]:
        """Return token info (for logging/debugging)."""
        return {
            "access_token": bool(self._access_token),
            "refresh_token": bool(self._refresh_token),
            "expires_in": max(0, int(self._expires_at - time.time())),
        }
