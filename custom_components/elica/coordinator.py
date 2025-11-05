"""Data Update Coordinator for Elica."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .connect.core import Controller
from .connect.domain import Device
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class ElicaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data Update Coordinator for Elica.

    self.data: dict with key "devices", value dict[str, Device]
    """

    def __init__(self, hass: HomeAssistant, controller: Controller) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=SCAN_INTERVAL,
        )
        self.controller = controller
        self._mqtt_started = False

    def get_device(self, device_id: str) -> Device:
        """Return a device by id, or raise if not found."""
        try:
            return self.data["devices"][device_id]
        except KeyError as err:
            raise RuntimeError(f"Device {device_id} not found in coordinator") from err

    async def async_start_mqtt_listener(self) -> None:
        """Start MQTT listener once devices are loaded."""
        if self._mqtt_started:
            return
        self._mqtt_started = True

        def _on_mqtt_message(topic: str, payload: str) -> None:
            self.logger.debug("MQTT message received: %s => %s", topic, payload)
            try:
                # qui puoi estrarre il device_id dal topic
                device_id = topic.split("/")[-1]
                device = self.data["devices"].get(device_id)
                if device:
                    # device.update_from_mqtt(payload)
                    # notifica HA dell’aggiornamento
                    self.async_set_updated_data(self.data)
            except Exception:
                self.logger.exception("Error handling MQTT message")

        await self.controller.listen(_on_mqtt_message)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest devices and their states."""
        try:
            devices = await self.controller.get_devices()
        except Exception as err:
            raise UpdateFailed(f"Error while fetching devices: {err}") from err
        else:
            if not self._mqtt_started:
                await self.async_start_mqtt_listener()
            return {
                "devices": {device.id: device for device in devices},
            }
