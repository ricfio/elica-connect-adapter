"""MQTT client implementation for Home Assistant."""

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.core import HomeAssistant

from ...core.constants import MQTT_TOPIC_FORMAT  # noqa: TID252


class HaMqttClient:
    """MQTT client implementation using Home Assistant's MQTT integration."""

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.logger = logging.getLogger(__name__)
        self._unsubs: list[Callable[[], None]] = []

    @staticmethod
    def get_topic_url(cuid: str) -> str:
        """Get the MQTT topic URL for a device."""
        return MQTT_TOPIC_FORMAT.format(CUID=cuid)

    def initialize(
        self,
        host: str,
        port: int,
        client_id: str,
        username: str,
        password: str,
        keepalive: int = 60,
    ) -> None:
        """No-op for HA: connection handled by Home Assistant MQTT integration."""
        # In HA, non gestiamo connessione manuale: tutto è già configurato via integration
        self.logger.debug(
            "Home Assistant MQTT client initialized (HA manages broker connection)"
        )

    async def listen(
        self,
        devices: list[str],
        on_message: Callable[[str, Any], None],
    ) -> None:
        """Subscribe to devices and dispatch messages using HA MQTT bus."""
        if not mqtt.is_connected(self.hass):
            self.logger.warning("MQTT is not connected in Home Assistant")
            return

        if "mqtt" not in self.hass.data:
            self.logger.warning("MQTT integration not loaded")
            return

        async def _message_received(msg: ReceiveMessage) -> None:
            try:
                on_message(msg.topic, msg.payload)
            except Exception:
                self.logger.exception(
                    "Error processing MQTT message for topic %s", topic
                )

        for device_id in devices:
            topic = self.get_topic_url(device_id)
            self.logger.debug("MQTT (HA) > Subscribing to: %s", topic)
            unsub = await mqtt.async_subscribe(
                self.hass,
                topic,
                _message_received,
                qos=1,
            )
            self._unsubs.append(unsub)

        self.logger.info("MQTT (HA) > Listening to %d devices", len(devices))

    async def stop(self) -> None:
        """Unsubscribe from all topics."""
        for unsub in self._unsubs:
            try:
                unsub()
            except Exception:
                self.logger.exception("Error unsubscribing MQTT topic")
        self._unsubs.clear()
        self.logger.info("MQTT (HA) > All subscriptions removed")
