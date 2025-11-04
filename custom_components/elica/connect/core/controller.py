"""Async Controller (framework-agnostic)."""

import logging
from typing import Any

from ..domain import Capability, Device
from .auth import AuthProviderBase
from .rest import RestClientInterface


class Controller:
    """Asynchronous, framework-independent controller."""

    def __init__(
        self,
        auth_provider: AuthProviderBase,
        rest_client: RestClientInterface,
        command_timeout: int = 30000,
    ) -> None:
        """Initialize controller."""
        self.logger = logging.getLogger(__name__)
        self.auth_provider = auth_provider
        self.rest = rest_client
        self._command_timeout = command_timeout

    # --------------------------
    #  Helpers
    # --------------------------

    async def _invalidate_auth(self) -> None:
        await self.auth_provider.clear_tokens()

    # --------------------------
    #  Authentication
    # --------------------------

    async def login(self) -> str:
        """Authenticate user and return access token."""
        self.logger.debug("Authenticating user...")
        access_token = await self.auth_provider.ensure_authenticated()
        self.logger.info("User authenticated successfully")
        return access_token

    async def logout(self) -> None:
        """Logout the client."""
        self.logger.debug("Logging out user...")
        await self._invalidate_auth()
        self.logger.info("User logged out successfully")

    async def is_logged_in(self) -> bool:
        return await self.auth_provider.is_authenticated()

    # --------------------------
    #  REST endpoints
    # --------------------------

    async def get_profile(self) -> dict[str, Any]:
        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()
        return await self.rest.get("me", headers=headers)

    async def get_localized_content(self) -> dict[str, Any]:
        headers = self.auth_provider.get_header_for_client_auth()
        return await self.rest.get("localizedContent", headers=headers)

    async def get_devices(self) -> list[Device]:
        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()

        json_list = await self.rest.get("devices", headers=headers)

        return [Device.from_json(json) for json in json_list]

    async def get_device(self, device_id: str) -> Device:
        if not device_id:
            raise ValueError("Missing required parameter: device_id")

        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()

        json = await self.rest.get(f"devices/{device_id}", headers=headers)
        return Device.from_json(json)

    # --------------------------
    #  Device control
    # --------------------------

    def _get_command_capabilities(
        self, speed: int, boost: bool, aimatic: bool
    ) -> dict[str, int]:
        fan = speed >= 1 and speed <= 3
        boost = boost and fan

        mode = 0
        if fan:
            mode += 1
        if boost:
            mode += 4
        if aimatic:
            mode += 32

        capabilities = {Capability.FAN_MODE: mode}
        if not boost:
            capabilities[Capability.FAN_SPEED] = speed
        return capabilities

    async def set_fan_mode(
        self,
        device_id: str,
        aimatic: bool,
        speed: int,
        boost: bool,
    ) -> bool:
        capabilities = self._get_command_capabilities(speed, boost, aimatic)
        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()

        data = await self.rest.post(
            f"devices/{device_id}/commands",
            json={
                "async": True,
                "capabilities": capabilities,
                "name": "capabilities",
                "type": "Hood",
                "timeout": self._command_timeout,
            },
            headers=headers,
        )
        return data["status"] == "accepted"

    async def set_fan_speed(
        self, device_id: str, speed: int, boost: bool = False
    ) -> bool:
        if not (0 <= speed <= 3):
            raise ValueError("Speed must be between 0 and 3")

        device = await self.get_device(device_id)
        return await self.set_fan_mode(device_id, device.state.aimatic, speed, boost)

    async def toggle_aimatic(self, device_id: str, enabled: bool | None = None) -> bool:
        device = await self.get_device(device_id)
        return await self.set_fan_mode(
            device_id,
            enabled if enabled is not None else not device.state.aimatic,
            device.state.fan_speed,
            device.state.fan_boost,
        )

    async def set_light_brightness(self, device_id: str, brightness: int) -> bool:
        if not (0 <= brightness <= 100):
            raise ValueError("Brightness must be between 0 and 100")

        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()

        data = await self.rest.post(
            f"devices/{device_id}/commands",
            json={
                "async": True,
                "capabilities": {Capability.LIGHT_BRIGHTNESS: brightness},
                "name": "capabilities",
                "type": "Hood",
                "timeout": self._command_timeout,
            },
            headers=headers,
        )
        return data["status"] == "accepted"

    async def toggle_light(self, device_id: str, value: bool | None = None) -> bool:
        device = await self.get_device(device_id)
        if value is None:
            value = not device.state.light_on

        brightness = 0 if not value else (device.state.light_brightness or 100)
        return await self.set_light_brightness(device_id, brightness)
