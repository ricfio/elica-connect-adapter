"""Async Controller (framework-agnostic)."""

from collections.abc import Awaitable, Callable
from functools import wraps
import logging
from typing import Any, ParamSpec, TypeVar

from aiohttp import ClientConnectionError, ClientResponseError

from ..adapters.shared import MqttClientAiomqtt  # noqa: TID252
from ..core.constants import (  # noqa: TID252
    MQTT_HOST,
    MQTT_KEEPALIVE,
    MQTT_PORT,
    MQTT_TOPIC_FORMAT,
)
from ..domain import Capability, Device  # noqa: TID252
from ..interfaces import (  # noqa: TID252
    RestClientInterface,
    MqttClientInterface,
    OnMqttMessageCallback,
)
from .auth import AuthProviderBase

P = ParamSpec("P")
R = TypeVar("R")


def handle_network_errors(
    action: str,
) -> Callable[[Callable[..., Awaitable[R]]], Callable[..., Awaitable[R | None]]]:
    """Decorator for consistent async network error handling."""

    def decorator(func: Callable[P, Awaitable[R]]):
        @wraps(func)
        async def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
            try:
                return await func(self, *args, **kwargs)  # type: ignore
            except ClientResponseError as e:
                self.logger.error(
                    "%s failed: HTTP %d - %s", action, e.status, e.message
                )
            except ClientConnectionError as e:
                self.logger.error("%s failed: %s", action, e)
            except TimeoutError:
                self.logger.error("%s failed: Timeout", action)
            return None

        return wrapper

    return decorator


class Controller:
    """Asynchronous, framework-independent controller."""

    def __init__(
        self,
        auth_provider: AuthProviderBase,
        rest_client: RestClientInterface,
        mqtt_client: MqttClientInterface,
        command_timeout: int = 30000,
    ) -> None:
        """Initialize controller."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.auth_provider = auth_provider
        self.rest = rest_client
        self._mqtt_subscriber = MqttClientAiomqtt()
        self._command_timeout = command_timeout

    # --------------------------
    #  Helpers
    # --------------------------

    async def _invalidate_auth(self) -> None:
        await self.auth_provider.clear_tokens()

    async def _ensure_mqtt_initialized(self):
        """Ensure MQTT client is initialized."""
        auth = await self.auth_provider.get_auth()
        if auth is None:
            raise RuntimeError("Auth data missing")

        if auth.get("mqtt_usr") and auth.get("mqtt_psw"):
            await self._mqtt_subscriber.initialize(
                host=MQTT_HOST,
                port=MQTT_PORT,
                identifier=auth["mqtt_usr"],
                username=auth["mqtt_usr"],
                password=auth["mqtt_psw"],
                keepalive=MQTT_KEEPALIVE,
            )

    # --------------------------
    #  Authentication
    # --------------------------

    @handle_network_errors("Login")
    async def login(self) -> str | None:
        """Authenticate and Return the access token."""
        access_token = await self.auth_provider.ensure_authenticated()
        self.logger.info("Login success")
        return access_token

    @handle_network_errors("Logout")
    async def logout(self) -> None:
        """Logout the client."""
        await self._invalidate_auth()
        self.logger.info("Logout success")

    async def is_logged_in(self) -> bool:
        """Return True if authenticated."""
        return await self.auth_provider.is_authenticated()

    # --------------------------
    #  REST endpoints
    # --------------------------

    async def get_profile(self) -> dict[str, Any]:
        """Return the account information."""
        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()
        return await self.rest.get("me", headers=headers)

    async def get_localized_content(self) -> dict[str, Any]:
        """Return the localized content."""
        headers = self.auth_provider.get_header_for_client_auth()
        return await self.rest.get("localizedContent", headers=headers)

    async def get_devices(self) -> list[Device]:
        """Return the list of devices associated with the account."""
        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()

        json_list = await self.rest.get("devices", headers=headers)

        return [Device.create_from_json(json) for json in json_list]

    async def get_device(self, device_id: str) -> Device:
        """Return the device information."""
        if not device_id:
            raise ValueError("Missing required parameter: device_id")

        await self.auth_provider.ensure_authenticated()
        headers = await self.auth_provider.get_header_for_user_auth()

        json = await self.rest.get(f"devices/{device_id}", headers=headers)
        return Device.create_from_json(json)

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

    async def get_aimatic_state(self, device_id: str) -> bool:
        """Return the AIMatic state for the device."""
        device = await self.get_device(device_id)
        return device.state.aimatic

    async def get_fan_speed(self, device_id: str) -> int:
        """Return the fan speed for the device."""
        device = await self.get_device(device_id)
        return device.state.fan_speed

    async def get_fan_boot(self, device_id: str) -> bool:
        """Return the fan boost state for the device."""
        device = await self.get_device(device_id)
        return device.state.fan_boost

    async def get_light_brightness(self, device_id: str) -> int:
        """Return the light brightness for the device."""
        device = await self.get_device(device_id)
        return device.state.light_brightness

    async def set_fan_mode(
        self,
        device_id: str,
        aimatic: bool,
        speed: int,
        boost: bool,
    ) -> bool:
        """Set the fan mode for the device."""
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
        """Set the fan speed for the device."""
        if not (0 <= speed <= 3):
            raise ValueError("Speed must be between 0 and 3")

        device = await self.get_device(device_id)
        return await self.set_fan_mode(device_id, device.state.aimatic, speed, boost)

    async def toggle_aimatic(self, device_id: str, enabled: bool | None = None) -> bool:
        """Toggle the aimatic mode for the device."""
        device = await self.get_device(device_id)
        return await self.set_fan_mode(
            device_id,
            enabled if enabled is not None else not device.state.aimatic,
            device.state.fan_speed,
            device.state.fan_boost,
        )

    async def set_light_brightness(self, device_id: str, brightness: int) -> bool:
        """Set the light brightness for the device."""
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
        """Toggle the light for the device."""
        device = await self.get_device(device_id)
        if value is None:
            value = not device.state.light_on

        brightness = 0 if not value else (device.state.light_brightness or 100)
        return await self.set_light_brightness(device_id, brightness)

    # async def listen(self, callback: Callable[[str, Any], None]):
    async def listen(self, callback: OnMqttMessageCallback):
        """Start listening for device updates via MQTT."""
        await self._ensure_mqtt_initialized()

        devices = await self.get_devices()
        cuids = [device.cuid for device in devices if device.cuid]
        topics = [MQTT_TOPIC_FORMAT.format(CUID=cuid) for cuid in cuids]
        self.logger.debug("Listen updates for devices: %s", devices)
        try:
            await self._mqtt_subscriber.start(topics=topics, on_message=callback)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, stopping MQTT client...")
        # finally:
        # await self.mqtt.stop()
