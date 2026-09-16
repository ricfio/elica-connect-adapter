"""Data Update Coordinator for Elica."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

from .api.core import Controller
from .api.domain import Device, normalize_data_model
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ElicaConnectCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Elica data update coordinator."""

    def __init__(
        self, hass: HomeAssistant, controller: Controller, config_entry: ConfigEntry
    ) -> None:
        # Options
        self._scan_interval = config_entry.options.get("scan_interval", 60)
        self._mqtt_updates = config_entry.options.get("mqtt_updates", True)
        self._mqtt_debug = config_entry.options.get("mqtt_debug", False)
        self._debug = config_entry.options.get("debug", False)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=self._scan_interval),
        )
        self.controller = controller
        self.config_entry = config_entry
        self._mqtt_started = False
        self.data = {
            "devices": {},
            "mqtt_stats": {
                "connected": False,
                "last_connection": None,
                "last_disconnection": None,
                "last_message_timestamp": None,
                "last_message_payload": None,
                "total_messages": 0,
            },
        }
        if self._debug:
            _LOGGER.setLevel(logging.DEBUG)

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
                        "dataModel": (
                            getattr(d, "dataModel", {})
                            if hasattr(d, "dataModel")
                            else {}
                        ),
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
            if self._mqtt_updates and not self._mqtt_started:
                self._mqtt_started = True

                # Log which device CUIDs we will listen for (if available)
                cuids = [getattr(d, "cuid", None) for d in devices]
                _LOGGER.debug("Starting MQTT listener for cuids: %s", cuids)

                async def _mqtt_logging_wrapper(
                    topic: str, payload: str, retain: bool = False
                ) -> None:
                    if not self._mqtt_updates:
                        return
                    try:
                        # Log incoming message (truncate large payloads)
                        display_payload = payload
                        try:
                            if (
                                isinstance(payload, str | bytes)
                                and len(str(payload)) > 1024
                            ):
                                display_payload = str(payload)[:1024] + "...(truncated)"
                        except Exception:
                            display_payload = "<unserializable>"

                        if self._mqtt_debug:
                            _LOGGER.info(
                                "MQTT message received [retained=%s, stats: %s]: %s - %s",
                                retain,
                                "present" if "mqtt_stats" in self.data else "missing",
                                topic,
                                display_payload,
                            )
                        else:
                            _LOGGER.debug(
                                "MQTT message received [retained=%s, stats: %s]: %s - %s",
                                retain,
                                "present" if "mqtt_stats" in self.data else "missing",
                                topic,
                                display_payload,
                            )
                        # Delegate to coordinator handler
                        await self._async_update_from_mqtt(
                            topic, payload, retain=retain
                        )
                    except Exception:
                        _LOGGER.exception(
                            "Error while processing MQTT message for topic %s", topic
                        )

                await self.controller.listen(
                    _mqtt_logging_wrapper,
                    on_connection=self._mqtt_connection_changed,
                )
        except Exception as err:
            raise UpdateFailed(f"Error while fetching devices: {err}") from err
        else:
            # Update devices while preserving mqtt_stats immutably
            self.data = {
                **self.data,
                "devices": {device.uid: device for device in devices},
            }
            return self.data

    async def _mqtt_connection_changed(self, connected: bool) -> None:
        """Handle MQTT connection state changes."""
        mqtt_stats = dict(self.data.get("mqtt_stats", {}))
        mqtt_stats["connected"] = connected
        if connected:
            mqtt_stats["last_connection"] = datetime.now().isoformat()
        else:
            mqtt_stats["last_disconnection"] = datetime.now().isoformat()

        self.data = {
            **self.data,
            "mqtt_stats": mqtt_stats,
        }
        self.async_set_updated_data(self.data)

    async def _async_update_from_mqtt(
        self, topic: str, payload: str, retain: bool = False
    ) -> None:
        """Process MQTT update message."""
        if not self._mqtt_updates:
            return
        _LOGGER.debug(
            "Processing MQTT message with data structure: %s",
            {k: "..." if k == "devices" else v for k, v in self.data.items()},
        )

        # Ensure mqtt_stats exists (immutably)
        mqtt_stats = dict(
            self.data.get(
                "mqtt_stats",
                {
                    "connected": False,
                    "last_connection": None,
                    "last_disconnection": None,
                    "last_message_timestamp": None,
                    "last_message_payload": None,
                    "total_messages": 0,
                    "retained_messages": 0,
                    "last_message_retained": False,
                },
            )
        )
        if "mqtt_stats" not in self.data:
            _LOGGER.warning("Reinitializing missing mqtt_stats in MQTT handler")

        # Update MQTT statistics
        mqtt_stats["connected"] = True
        now_str = datetime.now().isoformat()
        if not mqtt_stats.get("last_connection"):
            mqtt_stats["last_connection"] = now_str
        mqtt_stats["last_message_timestamp"] = now_str
        mqtt_stats["last_message_payload"] = payload
        mqtt_stats["total_messages"] = mqtt_stats.get("total_messages", 0) + 1
        if retain:
            mqtt_stats["retained_messages"] = mqtt_stats.get("retained_messages", 0) + 1
        mqtt_stats["last_message_retained"] = retain

        _LOGGER.debug("Updated MQTT stats: %s", mqtt_stats)

        cuid = topic.split("/")[-2]

        try:
            # Parse the JSON payload
            json_payload: str
            if isinstance(payload, bytes):
                json_payload = payload.decode()
            else:
                json_payload = payload
            data = json.loads(json_payload)

            # Log parsed data at debug level for diagnostics
            _LOGGER.debug("Parsed MQTT data: %s", data)

            # Find device by CUID
            devices = dict(self.data.get("devices", {}))
            device = next(
                (d for d in devices.values() if getattr(d, "cuid", None) == cuid),
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
                            device.dataModel = {}

                        # Update with new values
                        device.dataModel.update(normalize_data_model(dataModel))
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
                self.data = {
                    **self.data,
                    "mqtt_stats": mqtt_stats,
                    "devices": devices,
                }
                self.async_set_updated_data(self.data)
            else:
                _LOGGER.warning("No matching device found for CUID: %s", cuid)
                self.data = {
                    **self.data,
                    "mqtt_stats": mqtt_stats,
                }
                self.async_set_updated_data(self.data)
        except Exception as err:
            _LOGGER.exception("Error processing MQTT message: %s", err)
            self.data = {
                **self.data,
                "mqtt_stats": mqtt_stats,
            }
            self.async_set_updated_data(self.data)
