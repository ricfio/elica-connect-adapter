"""Data Update Coordinator for Elica."""

from datetime import timedelta
import logging
from typing import Any

from elica_connect_api.core import Controller
from elica_connect_api.domain import Device
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class ElicaConnectCoordinator(DataUpdateCoordinator[dict[str, Any]]):
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
        self.data = {"devices": {}}

    def get_device(self, device_id: str) -> Device:
        """Return a device by id, or raise if not found."""
        try:
            return self.data["devices"][device_id]
        except KeyError as err:
            raise RuntimeError(f"Device {device_id} not found in coordinator") from err

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest devices and their states."""
        try:
            devices = await self.controller.get_devices()
            # Start MQTT listener if not started
            if not self._mqtt_started:
                self._mqtt_started = True

                # Log which device CUIDs we will listen for (if available)
                cuids = [getattr(d, "cuid", None) for d in devices]
                _LOGGER.debug("Starting MQTT listener for cuids: %s", cuids)

                async def _mqtt_logging_wrapper(topic: str, payload: str) -> None:
                    try:
                        # Log incoming message (truncate large payloads)
                        display_payload = payload
                        try:
                            if isinstance(payload, (str, bytes)) and len(str(payload)) > 1024:
                                display_payload = str(payload)[:1024] + "...(truncated)"
                        except Exception:
                            display_payload = "<unserializable>"

                        _LOGGER.info("MQTT message received: %s - %s", topic, display_payload)
                        # Delegate to coordinator handler
                        await self._async_update_from_mqtt(topic, payload)
                    except Exception:
                        _LOGGER.exception("Error while processing MQTT message for topic %s", topic)

                await self.controller.listen(_mqtt_logging_wrapper)

            return {
                "devices": {device.id: device for device in devices},
            }
        except Exception as err:
            raise UpdateFailed(f"Error while fetching devices: {err}") from err

    async def _async_update_from_mqtt(self, topic: str, payload: str) -> None:
        _LOGGER.info("MQTT message received: %s - %s", topic, payload)
        cuid = topic.split("/")[-2]
        # device = self.data["devices"].get(device_id)
        device = next(
            (
                d
                for d in self.data.get("devices", {}).values()
                if getattr(d, "cuid", None) == cuid
            ),
            None,
        )
        if device:
            device.update_from_mqtt(payload)
            self.async_set_updated_data(self.data)
