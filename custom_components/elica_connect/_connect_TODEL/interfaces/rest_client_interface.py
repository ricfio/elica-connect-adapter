"""Interface for REST API clients."""

from typing import Any, Protocol


class RestClientInterface(Protocol):
    """Interface for REST API clients."""

    def get(
        self,
        path: str,
        headers: dict | None = None,
    ) -> Any:
        """Perform a GET request and return parsed JSON response."""

    def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: dict | None = None,
    ) -> Any:
        """Perform a POST request and return parsed JSON response."""
