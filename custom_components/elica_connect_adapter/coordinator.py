"""Data Update Coordinator for Elica."""

from datetime import datetime, timedelta
import json
import logging
from typing import Any

from .api.core import Controller
from .api.domain import Device
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class ElicaConnectCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data Update Coordinator for Elica.

    self.data: dict with key "devices", value dict[str, Device]
    """

    def __init__(
        self, hass: HomeAssistant, controller: Controller, config_entry: ConfigEntry
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=SCAN_INTERVAL,
        )
        self.controller = controller
        self.config_entry = config_entry
        self._mqtt_started = False
        self.data = {
            "devices": {},
            "mqtt_stats": {
                "last_message": None,
                "messages_received": 0,
                "connected": False,
                "last_disconnect": None,
            },
        }
        # Options
        # self._mqtt_enabled = bool(config_entry.options.get("enable_mqtt", False))
        self._mqtt_enabled = True

    def get_device(self, device_id: str) -> Device:
        """Return a device by id, or raise if not found."""
        try:
            return self.data["devices"][device_id]
        except KeyError as err:
            raise RuntimeError(f"Device {device_id} not found in coordinator") from err

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest devices and their states."""
        try:
            _LOGGER.debug(
                "Starting data update. Current data structure: %s",
                {k: "..." if k == "devices" else v for k, v in self.data.items()},
            )

            devices = await self.controller.get_devices()
            _LOGGER.debug(
                "Received devices from controller: %s",
                [
                    {
                        "id": d.uid,
                        "name": d.name,
                        "dataModel": getattr(d, "dataModel", {})
                        if hasattr(d, "dataModel")
                        else {},
                    }
                    for d in devices
                ],
            )

            # Ensure mqtt_stats exists
            if "mqtt_stats" not in self.data:
                _LOGGER.warning("Reinitializing missing mqtt_stats in coordinator data")
                self.data["mqtt_stats"] = {
                    "last_message": None,
                    "messages_received": 0,
                    "connected": False,
                    "last_disconnect": None,
                }

            # Start MQTT listener if not started
            if self._mqtt_enabled and not self._mqtt_started:
                self._mqtt_started = True

                # Log which device CUIDs we will listen for (if available)
                cuids = [getattr(d, "cuid", None) for d in devices]
                _LOGGER.debug("Starting MQTT listener for cuids: %s", cuids)

                async def _mqtt_logging_wrapper(topic: str, payload: str) -> None:
                    try:
                        # Log incoming message (truncate large payloads)
                        display_payload = payload
                        try:
                            if (
                                isinstance(payload, (str, bytes))
                                and len(str(payload)) > 1024
                            ):
                                display_payload = str(payload)[:1024] + "...(truncated)"
                        except Exception:
                            display_payload = "<unserializable>"

                        _LOGGER.debug(
                            "MQTT message received [stats: %s]: %s - %s",
                            "present" if "mqtt_stats" in self.data else "missing",
                            topic,
                            display_payload,
                        )
                        # Delegate to coordinator handler
                        await self._async_update_from_mqtt(topic, payload)
                    except Exception:
                        _LOGGER.exception(
                            "Error while processing MQTT message for topic %s", topic
                        )

                await self.controller.listen(_mqtt_logging_wrapper)
        except Exception as err:
            raise UpdateFailed(f"Error while fetching devices: {err}") from err
        else:
            # Update devices while preserving mqtt_stats
            self.data["devices"] = {device.uid: device for device in devices}
            return self.data

    async def _mqtt_connection_changed(self, connected: bool) -> None:
        """Handle MQTT connection state changes."""
        self.data["mqtt_stats"]["connected"] = connected
        if not connected:
            self.data["mqtt_stats"]["last_disconnect"] = datetime.now().isoformat()
        self.async_set_updated_data(self.data)

    async def _async_update_from_mqtt(self, topic: str, payload: str) -> None:
        """Process MQTT update message."""
        _LOGGER.debug(
            "Processing MQTT message with data structure: %s",
            {k: "..." if k == "devices" else v for k, v in self.data.items()},
        )

        # Ensure mqtt_stats exists
        if "mqtt_stats" not in self.data:
            _LOGGER.warning("Reinitializing missing mqtt_stats in MQTT handler")
            self.data["mqtt_stats"] = {
                "last_message": None,
                "messages_received": 0,
                "connected": False,
                "last_disconnect": None,
            }

        # Update MQTT statistics
        mqtt_stats = self.data["mqtt_stats"]
        mqtt_stats["last_message"] = datetime.now().isoformat()
        mqtt_stats["messages_received"] = mqtt_stats.get("messages_received", 0) + 1
        mqtt_stats["connected"] = True

        _LOGGER.debug("Updated MQTT stats: %s", mqtt_stats)

        cuid = topic.split("/")[-2]

        try:
            # Parse the JSON payload
            data = json.loads(
                payload.decode() if isinstance(payload, bytes) else payload
            )

            # Log parsed data at debug level for diagnostics
            _LOGGER.debug("Parsed MQTT data: %s", data)

            # Find device by CUID
            device = next(
                (
                    d
                    for d in self.data.get("devices", {}).values()
                    if getattr(d, "cuid", None) == cuid
                ),
                None,
            )

            if device and data:
                # Extract dataModel from the first message object if present
                if isinstance(data, list) and data:
                    # Log the received data structure
                    _LOGGER.debug("Received MQTT data structure: %s", data)

                    if "dataModel" in data[0]:
                        dataModel = data[0]["dataModel"]
                        # Store raw dataModel values on device
                        if not hasattr(device, "dataModel"):
                            _LOGGER.info(
                                "Initializing dataModel for device %s", device.uid
                            )
                            setattr(device, "dataModel", {})

                        # Update with new values
                        device.dataModel.update(
                            {str(k): v for k, v in dataModel.items()}
                        )
                        _LOGGER.debug(
                            "Updated device %s dataModel: %s",
                            device.uid,
                            device.dataModel,
                        )
                    else:
                        _LOGGER.warning(
                            "No dataModel found in MQTT message for device %s. Message: %s",
                            device.uid,
                            data[0],
                        )

                # Call original update method
                device.update_from_mqtt(payload)
                self.async_set_updated_data(self.data)
            else:
                _LOGGER.warning("No matching device found for CUID: %s", cuid)
        except Exception as err:
            _LOGGER.exception("Error processing MQTT message: %s", err)
