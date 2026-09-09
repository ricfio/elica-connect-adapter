"""MQTT Subscriber Interface."""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

OnMqttMessageCallback = Callable[[str, Any], None | Awaitable[None]]
OnMqttConnectionCallback = Callable[[bool], None | Awaitable[None]]


class MqttClientInterface(Protocol):
    """MQTT Subscriber Interface."""

    async def initialize(
        self,
        hostname: str,
        port: int,
        identifier: str,
        username: str,
        password: str,
        tls: bool = True,
        keepalive: int = 60,
    ) -> None:
        """Configure the MQTT subscriber."""

    async def start(
        self,
        topics: list[str],
        on_message: OnMqttMessageCallback,
        on_connection: OnMqttConnectionCallback | None = None,
    ) -> None:
        """Connect and Subscribe to the topics."""

    async def stop(self) -> None:
        """Unsubscribe from the topics and Disconnect."""
