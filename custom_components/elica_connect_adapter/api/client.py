"""Compatibility client wrapper for tests.

Provides a simple synchronous `ElicaClient` wrapper used by tests that
expect a synchronous client interface.
"""

from __future__ import annotations

import asyncio
from typing import Any

from .core.auth.auth_service import AuthService


class ElicaClient:
    """Thin synchronous wrapper around the async AuthService used in tests.

    This avoids changing tests that expect a simple `client.login(...)` call.
    It is intentionally small and only implements what tests need.
    """

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret

    def login(self, username: str, password: str, app_uuid: str) -> str | None:
        """Perform an authentication request and return the access token string.

        Runs the underlying async `AuthService.login` in an event loop and
        returns the `access_token` if successful, otherwise `None`.
        """
        auth_service = AuthService(
            self.base_url, app_uuid, self.client_id, self.client_secret
        )

        try:
            result: dict[str, Any] = asyncio.run(
                auth_service.login(username, password)  # type: ignore
            )
        except Exception:
            return None

        return result.get("access_token")
