"""REST client implementation (framework-agnostic)."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientResponse, ClientSession, ClientTimeout, ContentTypeError

from ...interfaces import RestClientInterface  # noqa: TID252

logger = logging.getLogger(__name__)


class AioHttpRestClient(RestClientInterface):
    """Asynchronous REST API client using aiohttp, independent from Home Assistant."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        """Initialize aiohttp client."""
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(total=timeout)
        self.session: ClientSession | None = None

    async def _get_session(self) -> ClientSession:
        """Ensure that the aiohttp session is initialized."""
        if not self.session or self.session.closed:
            self.session = await self._create_session()

        return self.session

    async def _create_session(self) -> ClientSession:
        """Create a new aiohttp session."""
        return ClientSession(timeout=self.timeout)

    async def close(self) -> None:
        """Close the aiohttp session if open."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def _handle_response(self, resp: ClientResponse) -> Any:
        logger.debug(
            "HTTP %s %s -> %s", resp.request_info.method, resp.url, resp.status
        )
        try:
            resp.raise_for_status()
            return await resp.json()
        except ContentTypeError:
            text = await resp.text()
            logger.debug("Non-JSON response: %s", text[:200])
            return text

    async def get(self, path: str, headers: dict | None = None) -> Any:
        """Perform an async GET request and return parsed JSON response."""
        url = self._generate_url(path)
        session = await self._get_session()
        async with session.get(url, headers=headers) as resp:
            return await self._handle_response(resp)

    async def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: dict | None = None,
    ) -> Any:
        """Perform an async POST request and return parsed JSON response."""
        url = self._generate_url(path)
        session = await self._get_session()
        async with session.post(
            url,
            data=data,
            json=json,
            headers=headers,
        ) as resp:
            return await self._handle_response(resp)

    def _generate_url(self, path: str) -> str:
        """Generate full URL from relative path."""
        return f"{self.base_url}/{path.lstrip('/')}"
