"""REST client implementation (framework-agnostic)."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import (ClientResponse, ClientSession, ClientTimeout,
                     ContentTypeError, TCPConnector)

from ...interfaces import RestClientInterface

_LOGGER = logging.getLogger(__name__)


class AioHttpRestClient(RestClientInterface):
    """Asynchronous REST API client using aiohttp, independent from Home Assistant."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        """Initialize aiohttp client."""
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(
            total=timeout,
            connect=5.0,
            sock_connect=5.0,
            sock_read=timeout,
        )
        self.session: ClientSession | None = None

    # ----------------------------
    # Context manager support
    # ----------------------------
    async def __aenter__(self) -> AioHttpRestClient:
        """Allow usage with 'async with'."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Ensure session closure when exiting context."""
        await self.close()

    # ----------------------------
    # Session management
    # ----------------------------
    async def _get_session(self) -> ClientSession:
        """Ensure that the aiohttp session is initialized."""
        if self.session is None or self.session.closed:
            self.session = self._create_session()
        return self.session

    def _create_session(self) -> ClientSession:
        """Create a new aiohttp session with persistent TCPConnector."""
        connector = TCPConnector(
            limit=10,
            limit_per_host=5,
            keepalive_timeout=60.0,
            enable_cleanup_closed=True,
        )
        return ClientSession(connector=connector, timeout=self.timeout)

    async def close(self) -> None:
        """Close the aiohttp session if open."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    # ----------------------------
    # Core HTTP methods
    # ----------------------------
    async def get(self, path: str, headers: dict | None = None) -> Any:
        """Perform an async GET request and return parsed response."""
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
        """Perform an async POST request and return parsed response."""
        url = self._generate_url(path)
        session = await self._get_session()
        async with session.post(url, data=data, json=json, headers=headers) as resp:
            return await self._handle_response(resp)

    # ----------------------------
    # Response handling
    # ----------------------------
    async def _handle_response(self, resp: ClientResponse) -> Any:
        """Process the HTTP response and return parsed JSON or text."""
        _LOGGER.debug(
            "HTTP %s %s -> %s", resp.request_info.method, resp.url, resp.status
        )

        try:
            resp.raise_for_status()
            return await resp.json(content_type=None)
        except ContentTypeError:
            text = await resp.text()
            _LOGGER.debug("Non-JSON response: %s", text[:200])
            return text
        except Exception as exc:
            text = await resp.text()
            _LOGGER.error(
                "Request failed [%s %s]: %s\nResponse: %s",
                resp.request_info.method,
                resp.url,
                exc,
                text[:200],
            )
            raise

    # ----------------------------
    # Helpers
    # ----------------------------
    def _generate_url(self, path: str) -> str:
        """Generate full URL from relative path."""
        return f"{self.base_url}/{path.lstrip('/')}"
