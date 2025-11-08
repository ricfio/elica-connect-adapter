"""Async interface for Authentication providers."""

from typing import Any, Protocol


class AuthProviderInterface(Protocol):
    """Asynchronous interface for Authentication providers."""

    async def is_authenticated(self) -> bool | None:
        """Return True if authenticated."""

    async def get_auth(self) -> dict[str, Any] | None:
        """Return authentication data."""

    async def get_access_token(self) -> str | None:
        """Return the current access token if available."""

    async def clear_tokens(self) -> None:
        """Clear stored tokens and force new authentication."""

    async def get_refresh_token(self) -> str | None:
        """Return the current refresh token if available."""

    async def authenticate_with_password(self, username: str, password: str) -> None:
        """Authenticate using username and password."""

    async def authenticate_with_token(self, access_token: str) -> None:
        """Authenticate using an existing token."""

    async def refresh_access_token(self) -> str | None:
        """Refresh access token using the refresh token if available."""

    async def ensure_authenticated(self) -> str | None:
        """Ensure that a valid access token is available."""

    @staticmethod
    def generate_auth_for_client(
        client_id: str, client_secret: str
    ) -> dict[str, str] | None:
        """Generate authorization basic header for the client."""

    async def get_client_token(self) -> dict[str, str] | None:
        """Generate client token for authentication basic header."""

    def get_header_user_auth(self) -> dict[str, str] | None:
        """Generate authorization bearer header for the user account."""
