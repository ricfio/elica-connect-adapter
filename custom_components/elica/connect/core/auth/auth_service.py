"""Authentication REST API helper."""

from base64 import b64encode

import aiohttp


class AuthService:
    """Encapsulates authentication-related REST calls."""

    def __init__(
        self,
        base_url: str,
        app_uuid: str,
        client_id: str,
        client_secret: str,
    ):
        self.base_url = base_url
        self.app_uuid = app_uuid
        self.client_id = client_id
        self.client_secret = client_secret

    def _generate_headers(self):
        """Generate http headers for private requests."""
        client_token = self.generate_basic_token(self.client_id, self.client_secret)
        return {"Authorization": f"Basic {client_token}"}

    @staticmethod
    def generate_basic_token(username: str, password: str) -> str:
        """Generate client token for authentication basic header."""
        client_identifier = f"{username}:{password}"
        return b64encode(client_identifier.encode()).decode()

    def get_client_token(self) -> str:
        """Generate client token for authentication basic header."""
        return self.generate_basic_token(self.client_id, self.client_secret)

    async def login(self, username: str, password: str) -> dict:
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/oauth/token",
                data={
                    "scope": "default",
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "app_uuid": self.app_uuid,
                },
                timeout=aiohttp.ClientTimeout(total=10),
                headers=self._generate_headers(),
            ) as response,
        ):
            response.raise_for_status()
            return await response.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh token."""
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                f"{self.base_url}/oauth/token",
                data={
                    "scope": "default",
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "app_uuid": self.app_uuid,
                },
                timeout=aiohttp.ClientTimeout(total=10),
                headers=self._generate_headers(),
            ) as response,
        ):
            response.raise_for_status()
            return await response.json()
