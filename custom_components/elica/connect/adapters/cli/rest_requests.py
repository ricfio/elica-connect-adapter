"""REST client implementation for CLI."""

from typing import Any

import requests


class RequestsRestClient:
    """REST API client using requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(
        self,
        path: str,
        headers: dict | None = None,
    ):
        """Perform a GET request and return parsed JSON response."""
        r = requests.get(
            self.generate_url(path),
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: dict | None = None,
    ):
        """Perform a POST request and return parsed JSON response."""
        r = requests.post(
            self.generate_url(path),
            data=data,
            json=json,
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def generate_url(self, path: str):
        """Generate full URL from path."""
        return f"{self.base_url}/{path.lstrip('/')}"
