"""Interface for REST API clients."""

from typing import Any, Protocol


class RestClientInterface(Protocol):
    """Interface for REST API clients."""

    def get(
        self,
        path: str,
        headers: dict | None = None,
    ) -> Any:
        """Perform a GET request and return parsed JSON response.

        Args:
            path: API endpoint relative to base_url.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """

    def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: dict | None = None,
    ) -> Any:
        """Perform a POST request and return parsed JSON response.

        Args:
            path: API endpoint relative to base_url.
            data: Optional form-encoded body.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
