"""AuthProvider implementation for CLI."""

import json
from pathlib import Path
import time
from typing import Any

from ...core import AuthProviderBase, AuthService  # noqa: TID252


class LocalAuthProvider(AuthProviderBase):
    """Local Authentication Provider."""

    AUTH_FILE = Path.home() / ".elica/connect/auth.json"

    def __init__(
        self,
        auth_service: AuthService,
        username: str = "",
        password: str = "",
    ):
        super().__init__(
            auth_service,
            username=username,
            password=password,
        )
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0
        self._load_auth()

    # --------------------------------------------------
    # Internal methods
    # --------------------------------------------------

    def _load_auth(self) -> dict[str, Any] | None:
        """Load the auth data from the local file system cache."""
        if not self.AUTH_FILE.exists():
            return None
        try:
            auth = json.loads(self.AUTH_FILE.read_text())
            self._access_token = auth.get("access_token")
            self._refresh_token = auth.get("refresh_token")
            self._expires_at = auth.get("expires_at", 0)
            return auth
        except (OSError, json.JSONDecodeError):
            pass

        return None

    def _save_auth(self, auth: dict[str, Any], expires_in: float = 3600):
        """Save the auth data into local file system cache."""
        expires_in = float(auth.get("expires_in", expires_in))
        auth["expires_at"] = time.time() + expires_in
        self.AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.AUTH_FILE.write_text(json.dumps(auth, indent=2))

    def _is_expiring(self, threshold: int = 60) -> bool:
        return time.time() >= (self._expires_at - threshold)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def get_auth(self) -> dict[str, Any] | None:
        """Return authentication data."""
        return self._load_auth()

    def authenticate_with_password(self, username: str, password: str) -> None:
        """Authenticate using username and password."""
        auth = self.auth_service.login(username, password)
        self._access_token = auth["access_token"]
        self._refresh_token = auth["refresh_token"]
        self._save_auth(auth)

    def get_access_token(self) -> str | None:
        """Return a valid access token, refreshing if possible."""
        if not self._access_token:
            return None

        if self._is_expiring():
            if self._refresh_token:
                new_token = self.refresh_access_token()
                if new_token:
                    return new_token
            return None

        return self._access_token

    def get_refresh_token(self) -> str | None:
        """Return the current refresh token if available."""
        return self._refresh_token

    def authenticate_with_token(self, access_token: str) -> None:
        """Authenticate using an existing access token."""
        self._access_token = access_token

    def refresh_access_token(self) -> str | None:
        """Refresh the access token using the refresh token if available."""
        if not self._refresh_token:
            return None

        auth = self.auth_service.refresh_token(self._refresh_token)
        self._save_auth(auth)
        return self._access_token
