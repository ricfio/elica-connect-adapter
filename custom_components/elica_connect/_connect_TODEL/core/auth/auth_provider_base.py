"""Base class for Authentication Providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
import time

from .auth_provider_interface import AuthProviderInterface
from .auth_service import AuthService


class AuthProviderBase(ABC, AuthProviderInterface):
    """Abstract base class for Authentication Providers."""

    _access_token: str | None = None
    _refresh_token: str | None = None
    _expires_at: float = 0

    def __init__(self, auth_service: AuthService, username: str, password: str):
        self.auth_service = auth_service
        self.username = username
        self.password = password

    @abstractmethod
    async def authenticate_with_password(self, username: str, password: str) -> None:
        """Authenticate using username and password."""

    @abstractmethod
    async def refresh_access_token(self) -> str | None:
        """Refresh the access token using the refresh token if available."""

    @abstractmethod
    async def get_access_token(self) -> str | None:
        """Return the current access token (refreshing if possible)."""

    def _is_expiring(self, threshold: int = 60) -> bool:
        """Check if the access token is expiring soon."""
        return time.time() >= (self._expires_at - threshold)

    async def ensure_authenticated(self) -> str:
        """Ensure a valid access token."""
        token = await self.get_access_token()
        if token:
            return token

        if self._refresh_token:
            new_token = await self.refresh_access_token()
            if new_token:
                return new_token

        if self.username and self.password:
            await self.authenticate_with_password(self.username, self.password)
            if not self._access_token:
                raise RuntimeError("Authentication failed: no token received.")
            return self._access_token

        raise RuntimeError("Authentication required.")

    async def is_authenticated(self) -> bool:
        """Return True if authenticated."""
        token = await self.get_access_token()
        return bool(token)

    def get_header_for_client_auth(self) -> dict[str, str]:
        """Generate authorization basic header for the client."""
        client_token = self.auth_service.get_client_token()
        return {"Authorization": f"Basic {client_token}"}

    async def get_header_for_user_auth(self) -> dict[str, str]:
        """Generate authorization bearer header for the user."""
        access_token = await self.ensure_authenticated()
        return {"Authorization": f"Bearer {access_token}"}
