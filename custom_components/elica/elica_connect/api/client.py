"""High-level Elica IoT API client module.

This module provides the `ElicaClient` class, which wraps the low-level
`ElicaAPI` client and exposes user-friendly methods for interacting with
Elica devices, such as hoods and lights.

Key features:
- Authentication (login, token management)
- Retrieving user information
- Managing devices (listing, getting details)
- Controlling device features (light brightness, hood speed)
- Presets and device filters

Example usage:

    from elica_connect.api import ElicaClient, Capability

    client = ElicaClient(
        base_url="https://cloudprod.elica.com/eiot-api/v1",
        client_id="XXXX",
        client_secret="XXXX",
    )

    token = client.login(username="user", password="pass", app_uuid="home-assistant")
    devices = client.get_devices()
    client.turn_on_light(device_id="mtpdsa")
"""

from base64 import b64encode

from .api import ElicaAPI
from ..domain.device import Device
from ..domain.device_state import DeviceState


class ElicaClient:
    """High-level client for the Elica IoT API.

    Wraps the low-level `JsonAPI` and provides convenient methods
    to interact with Elica devices.

    Attributes:
        api (JsonAPI): Low-level API client used internally.
        client_id (str): API client ID.
        client_secret (str): API client secret.
        username (str): Username for authentication.
        password (str): Password for authentication.
        app_uuid (str): Application UUID of the application.
        token (str | None): Bearer token used for authentication.
        timeout (int): Request timeout in seconds.

    Methods:
        is_logged_in() -> bool:
            Returns True if the client has a valid token.
        login(username: str, password: str, app_uuid: str) -> str | None:
            Authenticates with the Elica API and returns a Bearer token.
        get_me() -> dict:
            Retrieves information about the current user.
        get_devices() -> dict:
            Retrieves all devices for the current user.
        get_device(device_name: str) -> dict:
            Retrieves details for a specific device.
        set_light_brightness(device_id: str, brightness: int) -> dict:
            Sets the brightness of a device light.
        turn_on_light(device_id: str):
            Turns on the light of a device.
        turn_off_light(device_id: str):
            Turns off the light of a device.
    """

    def __init__(
        self,
        api: ElicaAPI,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        app_uuid: str,
        token: str | None = None,
        timeout=10,
    ) -> None:
        """Initializes the Elica client.

        Args:
            api (JsonAPI): Low-level API client used internally.
            client_id (str): API client ID.
            client_secret (str): API client secret.
            username (str): Username for authentication.
            password (str): Password for authentication.
            app_uuid (str): Application UUID of the application.
            token (str | None): Bearer token used for authentication.
            timeout (int): Request timeout in seconds.

        Attributes:
            api (JsonAPI): Low-level API client used internally.
            client_id (str): API client ID.
            client_secret (str): API client secret.
            username (str): Username for authentication.
            password (str): Password for authentication.
            app_uuid (str): Application UUID of the application.
            token (str | None): Bearer token used for authentication.
            timeout (int): Request timeout in seconds.
        """
        self.api = api
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.app_uuid = app_uuid
        self.token = token
        self.timeout = timeout

    def is_logged_in(self) -> bool:
        """Checks if the client is logged in.

        Returns:
            bool: True if the client has a valid Bearer token, False otherwise.
        """
        return self.token is not None

    def _get_client_token(self) -> str:
        client_identifier = f"{self.client_id}:{self.client_secret}"
        return b64encode(client_identifier.encode()).decode()

    def _get_access_token(self) -> str:
        """Returns the current access token.

        Ensures the client is logged in first. If the token is missing, attempts an
        automatic login using stored credentials. Raises ValueError if
        credentials are not available.

        Returns:
            str: The current access token.
        """
        if self.token is None:
            self.login()
            if self.token is None:
                raise ValueError("Access Token missing")

        return self.token

    # --------------------------
    # API concrete methods
    # --------------------------

    def get_localized_content(self) -> dict:
        """Returns localized content.

        Returns:
            dict: The localized content from the Elica Connect APP.
        """
        return self.api.get_localized_content(self._get_client_token())

    def login(self) -> str:
        """Logs in the client using stored credentials.

        If the client is not already logged in, this method will attempt to login using
        stored credentials. The access token is then stored in the client and returned.

        Raises:
            ValueError: If the access token is missing from the response.

        Returns:
            str: The access token.
        """
        json_response = self.api.login(
            client_token=self._get_client_token(),
            username=self.username,
            password=self.password,
            app_uuid=self.app_uuid,
        )

        # Check response
        token = json_response.get("access_token")
        if token is None:
            raise ValueError("access token missing")

        # Save token
        self.token = token

        return self.token

    def get_me(self) -> dict:
        """Returns the current user's profile information.

        Returns:
            dict: The user profile information from the Elica Connect APP.
        """
        return self.api.get_me(self._get_access_token())

    def post_me_clients(self) -> dict:
        """Posts the current user's client information to the Elica Connect APP.

        Returns:
            dict: The response from the Elica Connect APP.
        """
        return self.api.post_me_clients(self._get_access_token())

    def get_devices(self) -> list[Device]:
        """Returns the list of the user's devices.

        Returns:
            list[Device]: A list of Device objects.
        """
        jsons = self.api.get_devices(self._get_access_token())
        return [Device.from_json(json) for json in jsons]

    def get_device(self, device_id: str) -> Device:
        """Returns the data of the specified user's device.

        Args:
            device_id (str): The device id of the device to retrieve.

        Returns:
            Device: An Elica Device object representing the user's device.

        Raises:
            ValueError: If the device_id parameter is missing or empty.
        """
        if not device_id:
            raise ValueError("Missing required parameter: device_id")
        json = self.api.get_device(device_id, self._get_access_token())
        return Device.from_json(json)

    def get_device_filters(self, device_id: str) -> dict:
        """Retrieves the filters of a device.

        Args:
            device_id (str): The id of the device to retrieve the filters of.

        Returns:
            dict: A dictionary containing the filters of the device.

        Raises:
            ValueError: If the device_id parameter is missing or empty.
        """
        if not device_id:
            raise ValueError("Missing required parameter: device_id")

        return self.api.get_device_filters(device_id, self._get_access_token())

    def get_presets(self) -> dict:
        """Returns the presets of the user's devices.

        Returns:
            dict: A dictionary containing the presets of the user's devices.
        """
        return self.api.get_presets(self._get_access_token())

    def get_light_brightness(self, device_id: str) -> int:
        """Retrieves the brightness of a light device.

        Args:
            device_id (str): The id of the light device to retrieve the brightness of.

        Returns:
            int: The brightness of the light device.

        Raises:
            ValueError: If the device_id parameter is missing or empty.
        """
        device = self.get_device(device_id)
        return device.state.light_brightness

    def get_fan_speed(self, device_id: str) -> int:
        """Retrieves the fan speed of a device.

        Args:
            device_id (str): The id of the device to retrieve the fan speed of.

        Returns:
            int: The fan speed of the device.

        Raises:
            ValueError: If the device_id parameter is missing or empty.
        """
        device = self.get_device(device_id)
        return device.state.fan_speed

    def toggle_aimatic(self, device: Device, enable: bool | None = None) -> bool:
        """Toggle, Enable or Disable the AIMatic mode.

        Args:
            device: Target device.
            enable: True to Enable, False to Disable, None to Toggle.

        Returns:
            True if command accepted, else False.
        """

        # Determine AIMatic value to set
        if enable is None:
            aimatic = not device.state.aimatic
        else:
            aimatic = enable

        # Send command
        data = self.api.set_fan_mode(
            self._get_access_token(),
            device_id=device.id,
            speed=device.state.fan_speed,
            boost=device.state.fan_boost,
            aimatic=aimatic,
        )

        # Update local state if command accepted
        accepted = data["status"] == "accepted"
        if accepted:
            device.state.aimatic = aimatic

        # Refresh local state
        # device.state = self.get_device(device.id).state

        return accepted

    def set_fan_speed(self, device: Device, speed: int, boost: bool = False) -> bool:
        """Set fan speed (0, 1, 2, 3).

        Args:
            device: Target fan device.
            speed: Fan speed to set (0, 1, 2, 3).
            boost: True to boost, False to not boost.

        Returns:
            True if command accepted, else False.

        Raises:
            ValueError: If speed is out of range.
        """

        if not (0 <= speed <= 3):
            raise ValueError("Speed must be between 0 (off) and 3 (max)")

        # Send command
        data = self.api.set_fan_mode(
            self._get_access_token(), device.id, speed, boost, device.state.aimatic
        )

        # Update local state if command accepted
        accepted = data["status"] == "accepted"
        if accepted:
            device.state.fan_speed = speed
            device.state.fan_boost = boost

        # Refresh local state
        # device.state = self.get_device(device.id).state

        return accepted

    def set_light_brightness(self, device: Device, brightness: int) -> bool:
        """Set light brightness (0-100).

        Args:
            device: Target light device.
            brightness: Brightness value between 0 and 100.

        Returns:
            True if command accepted, else False.

        Raises:
            ValueError: If brightness is out of range.
        """
        if not (0 <= brightness <= 100):
            raise ValueError("Brightness must be between 0 and 100")

        # Send command
        data = self.api.set_light_brightness(
            self._get_access_token(),
            device.id,
            brightness,
        )

        # Update local state if command accepted
        accepted = data["status"] == "accepted"
        if accepted:
            device.state.light_brightness = brightness

        # Refresh local state
        # device.state = self.get_device(device.id).state

        return accepted

    def turn_on_light(self, device: Device) -> bool:
        """Turn on the device light."""
        brightness = device.state.light_brightness or 100
        return self.set_light_brightness(device, brightness)

    def turn_off_light(self, device: Device) -> bool:
        """Turn off the device light."""
        return self.set_light_brightness(device, 0)

    def set_fan_mode(
        self,
        device: Device,
        speed: int = 0,
        boost: bool = False,
        aimatic: bool = False,
    ) -> DeviceState:
        """Sets the fan mode of the given device.

        Args:
            device (Device): Target fan device with ID and current state.
            speed (int, optional): Fan speed to set, must be between 0 (off) and 3 (max). Defaults to 0.
            boost (bool, optional): Whether the fan should run in boost mode. Defaults to False.
            aimatic (bool, optional): Whether the fan should run in aimatic mode. Defaults to False.

        Returns:
            DeviceState: Updated state after applying new fan mode.

        Raises:
            ValueError: If speed is not between 0 and 3.
        """

        access_token = self._get_access_token()
        data = self.api.set_fan_mode(
            access_token,
            device.id,
            speed=min(speed, 3),
            boost=boost,
            aimatic=aimatic,
        )
        return DeviceState.from_json(data)

    def turn_on_fan(self, device: Device, speed: int | None = None) -> DeviceState:
        """Turns on the fan of the given device with the given speed.

        Args:
            device (Device): Target fan device with ID and current state.
            speed (int | None, optional): Fan speed to set, must be between 0 (off) and 3 (max). Defaults to 1.

        Returns:
            DeviceState: Updated state after applying new fan mode.

        Raises:
            ValueError: If speed is not between 0 and 3.
        """
        speed = speed or 1

        return self.set_fan_mode(
            device,
            speed=speed,
            boost=False,
            # TODO: Should be unchanged
            aimatic=False,
        )

    def turn_off_fan(self, device: Device) -> DeviceState:
        """Turns off the fan of the given device.

        Args:
            device (Device): Target fan device with ID and current state.

        Returns:
            DeviceState: Updated state after applying new fan mode.

        """
        return self.set_fan_mode(
            device,
            speed=0,
            boost=False,
            # TODO: Should be unchanged
            aimatic=False,
        )
