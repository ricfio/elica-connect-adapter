"""REST client implementation for Home Assistant."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ...interfaces import RestClientInterface  # noqa: TID252


class AioHttpRestClient(RestClientInterface):
    """Asynchronous REST API client using Home Assistant's aiohttp session."""

    def __init__(
        self, hass: HomeAssistant, base_url: str, timeout: float = 10.0
    ) -> None:
        """Initialize REST client."""
        super().__init__()
        self.hass = hass
        self.base_url = base_url.rstrip("/")
        self.session = async_get_clientsession(hass)
        self.timeout = ClientTimeout(total=timeout)

    async def get(
        self,
        path: str,
        headers: dict | None = None,
    ) -> Any:
        """Perform an async GET request and return parsed JSON response."""
        url = self._generate_url(path)
        async with self.session.get(url, headers=headers, timeout=self.timeout) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: dict | None = None,
    ) -> Any:
        """Perform an async POST request and return parsed JSON response."""
        url = self._generate_url(path)
        async with self.session.post(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=self.timeout,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    def _generate_url(self, path: str) -> str:
        """Generate full URL from relative path."""
        return f"{self.base_url}/{path.lstrip('/')}"
