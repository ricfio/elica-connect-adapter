"""Low-level REST JSON API client module.

Provides the `ElicaAPI` class for HTTP communication with any RESTful JSON API.
Intended for higher-level clients, with reusable helpers for GET/POST requests
and optional authorization headers.

Example usage:

    from elica_connect.api import ElicaAPI

    api = ElicaAPI("https://example.com/api/v1", user_agent="my-app")

    auth_header = {"Authorization": "Bearer YOUR_TOKEN"}
    response = api.get("devices", auth=auth_header)
    response = api.post("devices/123/commands", json={"command": "start"}, auth=auth_header)
"""

import requests

from ..domain import Capability


class ElicaAPI:
    """Low-level REST JSON API client.

    Attributes:
        base_url (str): Base URL of the API.
        session (requests.Session): Persistent HTTP session with headers/cookies.
        timeout (int): Default request timeout in seconds.
    """

    def __init__(self, base_url: str, user_agent: str, timeout: int = 10) -> None:
        """Initialize the API client with base URL, User-Agent, and timeout."""
        self.base_url = base_url.rstrip("/")  # Ensure no trailing slash
        self.timeout = timeout
        self.session = requests.Session()  # Persistent session for requests
        self.session.headers.update(
            {"User-Agent": user_agent, "Accept-Encoding": "gzip"}
        )

    @staticmethod
    def _auth_basic(client_token: str) -> dict[str, str]:
        return {"Authorization": f"Basic {client_token}"}

    @staticmethod
    def _auth_bearer(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    def _get(self, path: str, auth: dict[str, str] | None = None, **kwargs) -> dict:
        """Perform a GET request and return parsed JSON response.

        Args:
            path: API endpoint relative to base_url.
            auth: Optional authorization header.
            **kwargs: Additional arguments for `requests.get`.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.get(
            f"{self.base_url}/{path.lstrip('/')}",
            headers={**self.session.headers, **(auth or {})},  # Merge headers
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json() or {}

    def _post(
        self,
        path: str,
        auth: dict[str, str] | None = None,
        data=None,
        json=None,
        **kwargs,
    ) -> dict:
        """Perform a POST request and return parsed JSON response.

        Args:
            path: API endpoint relative to base_url.
            data: Optional form-encoded body.
            json: Optional JSON body.
            auth: Optional authorization header.
            **kwargs: Additional arguments for `requests.post`.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.post(
            f"{self.base_url}/{path.lstrip('/')}",
            data=data,
            json=json,
            headers={**self.session.headers, **(auth or {})},  # Merge headers
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json() or {}

    def get_localized_content(self, client_token: str) -> dict:
        """Retrieve localized content for the client ui.

        Args:
            client_token: Client token obtained from Elica's login API.

        Returns:
            Localized content as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._get("localizedContent", auth=self._auth_basic(client_token))

    def login(
        self, client_token: str, username: str, password: str, app_uuid: str
    ) -> dict:
        """Retrieve the access token.

        Args:
            client_token: Client token obtained from Elica's login API.
            username: Username to authenticate.
            password: Password to authenticate.
            app_uuid: UUID of the client app.

        Returns:
            Access token as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
            ValueError: If any of the required arguments are missing.
        """
        if not all([username, password, app_uuid]):
            raise ValueError("username, password and app_uuid must be provided")

        return self._post(
            "oauth/token",
            data={
                "scope": "default",
                "grant_type": "password",
                "username": username,
                "password": password,
                "app_uuid": app_uuid,
            },
            auth=self._auth_basic(client_token),
        )

    def get_me(self, access_token: str) -> dict:
        """Retrieve information about the authenticated user.

        Args:
            access_token: Access token obtained from login.

        Returns:
            Information about the authenticated user as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._get("me", auth=self._auth_bearer(access_token))

    def post_me_clients(self, access_token: str) -> dict:
        """Create a new client connection (output useful for MQTT subscriptions?).

        Args:
            access_token: Access token obtained from login.

        Returns:
            Information about the created client as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._post("me/clients", auth=self._auth_bearer(access_token))

    def get_presets(self, access_token: str) -> dict:
        """Retrieve the list of presets.

        Args:
            access_token: Access token obtained from login.

        Returns:
            A list of presets as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._get("presets", auth=self._auth_bearer(access_token))

    def get_devices(self, access_token: str) -> dict:
        """Retrieve the list of devices.

        Args:
            access_token: Access token obtained from login.

        Returns:
            A list of devices as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._get("devices", auth=self._auth_bearer(access_token))

    def get_device(self, device_id: str, access_token: str) -> dict:
        """Retrieve information about a specific device.

        Args:
            device_id: The ID of the device to retrieve.
            access_token: Access token obtained from login.

        Returns:
            Information about the device as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._get(f"devices/{device_id}", auth=self._auth_bearer(access_token))

    def get_device_filters(self, device_id: str, access_token: str) -> dict:
        """Retrieve the list of filters installed on a device.

        Args:
            device_id: The ID of the device to retrieve.
            access_token: Access token obtained from login.

        Returns:
            A list of filters installed on the device as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._get(
            f"devices/{device_id}/installedFilters",
            auth=self._auth_bearer(access_token),
        )

    def set_light_brightness(
        self,
        access_token: str,
        device_id: str,
        brightness: int,
    ) -> dict:
        """Set the brightness of a light device.

        Args:
            device_id: The ID of the device to control.
            brightness: The brightness to set, between 0 and 255.
            access_token: Access token obtained from login.

        Returns:
            Result of the set command as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        return self._post(
            f"devices/{device_id}/commands",
            json={
                "async": True,
                "capabilities": {Capability.LIGHT_BRIGHTNESS: brightness},
                "name": "capabilities",
                "type": "Hood",
                "timeout": 30000,
            },
            auth=self._auth_bearer(access_token),
        )

    def set_fan_mode(
        self,
        access_token: str,
        device_id: str,
        speed: int = 0,
        boost: bool = False,
        aimatic: bool = False,
    ) -> dict:
        """Set the fan mode of a device.

        Args:
            device_id: The ID of the device to control.
            speed: The fan speed to set, between 0 and 3.
            boost: Whether to set the fan to boost mode.
            aimatic: Whether to set the fan to aimatic mode.
            access_token: Access token obtained from login.

        Returns:
            Result of the set command as a dictionary.

        Raises:
            requests.HTTPError: On non-successful HTTP status.
        """
        if speed < 0 or speed > 3:
            raise ValueError("speed must be between 0 and 3")

        fan = speed >= 1 and speed <= 3
        boost = boost and fan

        fan_mode = 0
        if fan:
            fan_mode += 1
        if boost:
            fan_mode += 4
        if aimatic:
            fan_mode += 32

        capabilities = {Capability.FAN_MODE: fan_mode}
        if boost is False:
            capabilities[Capability.FAN_SPEED] = speed

        return self._post(
            f"devices/{device_id}/commands",
            json={
                "async": True,
                "capabilities": capabilities,
                "name": "capabilities",
                "type": "Hood",
                "timeout": 30000,
            },
            auth=self._auth_bearer(access_token),
        )
