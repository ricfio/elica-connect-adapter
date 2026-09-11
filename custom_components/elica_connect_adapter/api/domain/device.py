"""Device."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from .capabilities import Capability
from .device_extra import Group, Media, Owner, Share, SnapTimer, Temperature
from .device_state import DeviceState
from .hood_filter import HoodFilter

_LOGGER = logging.getLogger(__name__)


@dataclass
class Device:
    """Represents an device: core metadata + state + optional metadata.

    - core fields: used for identity, device_info and logic
    - metadata: dictionary with raw or selected extra info kept for UI/debug
    - filters: parsed list of HoodFilter
    """

    uid: str
    cuid: str
    name: str
    manufacturer: str | None = None
    device_type: str | None = None
    model: str | None = None
    model_id: str | None = None
    serial_number: str | None = None
    sw_version: str | None = None

    is_legacy: bool | None = None
    data_model: dict[str, int] = field(default_factory=dict)
    data_model_version: int | None = None
    product_reference: str | None = None

    # device capabilities (determined from dataModel)
    capabilities: list[str] = field(default_factory=list)
    # capabilities: dict[Capability, int] = field(default_factory=dict)

    # dynamic state (DTO)
    state: DeviceState = field(default_factory=DeviceState)

    # optional parsed list of filters
    filters: list[HoodFilter] = field(default_factory=list)

    # raw or selected extra data kept for informational attributes
    metadata: dict[str, Any] = field(default_factory=dict)

    # --- NEW FIELDS: keep all above untouched, add missing JSON fields here ---
    owner: Owner | None = None
    groups: list[Group] = field(default_factory=list)
    shares: list[Share] = field(default_factory=list)
    media: Media | None = None
    snap_timer: SnapTimer | None = None
    temperature: Temperature | None = None
    never_connected: bool | None = None
    purchase_date: int | None = None
    # --- end new fields ----------------------------------------------------

    @staticmethod
    def create_from_json(data: dict[str, Any]) -> "Device":
        """Create ElicaDevice from API JSON. Keep core fields and save metadata."""
        # core fields
        device_id = data["id"]
        cuid = data["cuid"]
        name = data.get("name", device_id)
        manufacturer = "Elica"
        device_type = data.get("type")
        model_id = data.get("code12nc")
        serial = data.get("serialNumber")
        sw_ver = data.get("configuration", {}).get("revisionInfo")

        # parse capabilities from dataModel (keep raw mask too)
        data_model = data.get("dataModel", {}) or {}

        capabilities = []
        # capabilities: dict[Capability, int] = field(default_factory=dict)

        if Capability.LIGHT_BRIGHTNESS in data_model:
            capabilities.append(Capability.LIGHT_BRIGHTNESS)
        if Capability.FAN_SPEED in data_model:
            capabilities.append(Capability.FAN_SPEED)
        if Capability.FILTER_SATURATION in data_model:
            capabilities.append(Capability.FILTER_SATURATION)
        if Capability.FAN_BOOST in data_model:
            capabilities.append(Capability.FAN_BOOST)
        # you may also keep the raw data_model for reference in metadata

        # parse filters (if any)
        filters_raw = data.get("filters", []) or []
        filters = [
            HoodFilter(
                id=f.get("id"),
                type=f.get("type"),
                status=f.get("status"),
                efficiency=f.get("efficiency"),
                saturation_alert=f.get("saturationAlert"),
                installation_date=f.get("installationDate"),
                last_reset=f.get("lastReset"),
                model=f.get("model"),
            )
            for f in filters_raw
        ]

        # build metadata with selected useful fields + raw dataModel
        metadata = {
            "iot": data.get("iot"),
            "demo": data.get("demo"),
            "timeZone": data.get("timeZone"),
            "modules": data.get("modules"),
            "dataModelIdx": data.get("dataModelIdx"),
            "dataModel": data_model,
            "filters_raw": filters_raw,
            # keep entire raw payload if desired:
            # "raw": data
        }

        # state from dataModel
        state = DeviceState.from_json(data)

        # ------------------ NEW: parse missing JSON fields into sub-structures ------------------
        owner = Owner.from_json(data.get("owner"))

        groupsJson = list(data.get("groups", []) or [])
        groups: list[Group] = []
        for g in groupsJson:
            g = Group.from_json(g)
            if g is not None:
                groups.append(g)

        sharesJson = list(data.get("shares", []) or [])
        shares: list[Share] = []
        for s in sharesJson:
            s = Share.from_json(s)
            if s is not None:
                shares.append(s)

        media = Media.from_json(data.get("media"))
        snap_timer = SnapTimer.from_json(data.get("snapTimer"))
        temperature = Temperature.from_json(
            data.get("temperature"), data.get("temperatureUnit")
        )

        never_connected = data.get("neverConnected")
        purchase_date = data.get("purchaseDate")
        # ---------------------------------------------------------------------------------------

        return Device(
            uid=device_id,
            cuid=cuid,
            name=name,
            manufacturer=manufacturer,
            device_type=device_type,
            model_id=model_id,
            serial_number=serial,
            model=device_type,
            sw_version=sw_ver,
            is_legacy=data.get("isLegacy"),
            data_model=data_model,
            data_model_version=data.get("dataModelVersion"),
            product_reference=data.get("prf"),
            capabilities=capabilities,
            state=state,
            filters=filters,
            metadata=metadata,
            # new fields added to constructor (all optional)
            owner=owner,
            groups=groups,
            shares=shares,
            media=media,
            snap_timer=snap_timer,
            temperature=temperature,
            never_connected=never_connected,
            purchase_date=purchase_date,
        )

    def update_from_mqtt(self, payload: str) -> None:
        """Update the device state based on MQTT payload."""
        try:
            raw = json.loads(payload)
        except json.JSONDecodeError:
            _LOGGER.warning("Invalid MQTT payload for device %s: %s", self.uid, payload)
            return

        try:
            data = raw[0]
        except (KeyError, IndexError, TypeError):
            _LOGGER.warning(
                "Unexpected MQTT payload structure for device %s: %s", self.uid, payload
            )
            return

        self._parse_mqtt_payload(data)

    def _parse_mqtt_payload(self, data: dict) -> None:
        if "connected" in data:
            self._update_connection_state(data["connected"])
            return

        if "dataModel" in data:
            self._update_capabilities_state(data["dataModel"])
            return

        _LOGGER.debug("Device %s ignored unknown MQTT payload: %s", self.uid, data)

    def _update_connection_state(self, connected: bool) -> None:
        if self.state.connected != connected:
            self.state.connected = connected
            _LOGGER.debug(
                "Device %s updated connection state: %s", self.uid, self.state.connected
            )

    def _update_capabilities_state(self, dataModel: dict) -> None:
        state_changed = False

        for key, value in dataModel.items():
            if self.data_model.get(key) != value:
                self.data_model[key] = value
                state_changed = True

        if Capability.FAN_SPEED in dataModel:
            if self.state.fan_speed != dataModel[Capability.FAN_SPEED]:
                self.state.fan_speed = dataModel[Capability.FAN_SPEED]
                state_changed = True

        if Capability.FAN_BOOST in dataModel:
            boost_timer = dataModel[Capability.FAN_BOOST]
            is_boost = bool(boost_timer > 0)
            if self.state.fan_boost != is_boost:
                self.state.fan_boost = is_boost
                state_changed = True

        if Capability.LIGHT_BRIGHTNESS in dataModel:
            if self.state.light_brightness != dataModel[Capability.LIGHT_BRIGHTNESS]:
                self.state.light_brightness = dataModel[Capability.LIGHT_BRIGHTNESS]
                state_changed = True

        if Capability.FILTER_SATURATION in dataModel:
            if self.state.filter_saturation != dataModel[Capability.FILTER_SATURATION]:
                self.state.filter_saturation = dataModel[Capability.FILTER_SATURATION]
                state_changed = True

        if state_changed:
            _LOGGER.debug("Device %s updated from MQTT: %s", self.uid, dataModel)
