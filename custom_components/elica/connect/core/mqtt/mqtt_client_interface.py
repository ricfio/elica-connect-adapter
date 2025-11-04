"""Interface for MQTT clients."""

from typing import Any, Callable, Protocol


class MqttClientInterface(Protocol):
    """MQTT client interface."""

    def initialize(
        self,
        host: str,
        port: int,
        client_id: str,
        username: str,
        password: str,
        keepalive: int = 60,
    ) -> None:
        """Configure the MQTT client with connection parameters."""

    def listen(
        self,
        devices: list[str],
        on_message: Callable[[str, Any], None],
    ) -> None:
        """Connect and subscribe to devices. Messages trigger on_message callback."""

    def stop(self) -> None:
        """Stop listening and disconnect."""
