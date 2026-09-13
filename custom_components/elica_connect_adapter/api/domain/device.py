import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .capabilities import Capability
from .device_extra import Group, Media, Owner, Share, SnapTimer, Temperature
from .device_state import DeviceState
from .fan_mode import FanMode
from .hood_filter import HoodFilter

_LOGGER = logging.getLogger(__name__)

MANUFACTURER = "Elica"

_PRODUCTS_DATA = None

def _get_products_data():
    global _PRODUCTS_DATA
    if _PRODUCTS_DATA is not None:
        return _PRODUCTS_DATA

    products_file = (
        Path(__file__).parent.parent.parent / "manufaturer" / "products.json"
    )
    if products_file.exists():
        with open(products_file, encoding="utf-8") as f:
            _PRODUCTS_DATA = json.load(f)
    else:
        _PRODUCTS_DATA = {}
    return _PRODUCTS_DATA

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
    installation_type: str | None = None
    usage_frequency: str | None = None
    commercial_name: str | None = None
    product_url: str | None = None
    # --- end new fields ----------------------------------------------------

    # Optimistic locking fields
    airmatic_lock_until: float = field(default=0.0, repr=False)
    expected_airmatic: bool | None = field(default=None, repr=False)
    fan_speed_lock_until: float = field(default=0.0, repr=False)
    expected_fan_speed: int | None = field(default=None, repr=False)
    fan_boost_lock_until: float = field(default=0.0, repr=False)
    expected_fan_boost: bool | None = field(default=None, repr=False)
    light_lock_until: float = field(default=0.0, repr=False)
    expected_light_brightness: int | None = field(default=None, repr=False)

    def set_airmatic_optimistic(self, enabled: bool) -> None:
        """Set airmatic state optimistically with a lock grace period."""
        self.state.airmatic = enabled
        self.expected_airmatic = enabled
        self.airmatic_lock_until = time.time() + 25.0

    def set_fan_speed_optimistic(self, speed: int) -> None:
        """Set fan speed state optimistically with a lock grace period."""
        self.state.fan_speed = speed
        self.expected_fan_speed = speed
        self.fan_speed_lock_until = time.time() + 25.0

    def set_fan_boost_optimistic(self, boost: bool) -> None:
        """Set fan boost state optimistically with a lock grace period."""
        self.state.fan_boost = boost
        self.expected_fan_boost = boost
        self.fan_boost_lock_until = time.time() + 25.0

    def set_light_brightness_optimistic(self, brightness: int) -> None:
        """Set light brightness state optimistically with a lock grace period."""
        self.state.light_brightness = brightness
        self.expected_light_brightness = brightness
        self.light_lock_until = time.time() + 25.0

    @staticmethod
    def create_from_json(data: dict[str, Any]) -> "Device":
        """Create ElicaDevice from API JSON. Keep core fields and save metadata."""
        # core fields
        device_id = data["id"]
        cuid = data["cuid"]
        name = data.get("name", device_id)
        manufacturer = MANUFACTURER
        device_type = data.get("type")
        model_id = data.get("code12nc")
        serial = data.get("serialNumber")
        config = data.get("configuration", {}) or {}
        revision_info = config.get("revisionInfo")
        ts = config.get("ts")
        sw_ver = f"{revision_info} ({ts})" if revision_info and ts else revision_info

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
        if Capability.FAN_BOOST_TIMER in data_model:
            capabilities.append(Capability.FAN_BOOST_TIMER)
        if Capability.FAN_SHUTOFF_TIMER in data_model:
            capabilities.append(Capability.FAN_SHUTOFF_TIMER)
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
            "configuration": data.get("configuration"),
            "autoLightPauseInterval": data.get("autoLightPauseInterval"),
            "productManualUrl": data.get("productManualUrl"),
            "accessoriesURL": data.get("accessoriesURL"),
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
        installation_type = data.get("installationType")
        usage_frequency = data.get("usageFrequency")

        product_ref = data.get("prf")
        commercial_name = None
        product_url = None

        products_data = _get_products_data()
        if product_ref in products_data:
            prod_info = products_data[product_ref]
            commercial_name = prod_info.get("name")
            product_url = prod_info.get("url")

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
            product_reference=product_ref,
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
            installation_type=installation_type,
            usage_frequency=usage_frequency,
            commercial_name=commercial_name,
            product_url=product_url,
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

        if Capability.FAN_MODE in dataModel:
            try:
                fan_mode_val = int(dataModel[Capability.FAN_MODE])
                fan_mode = FanMode(fan_mode_val)

                is_airmatic = bool(fan_mode & FanMode.AIRMATIC)
                if time.time() < self.airmatic_lock_until:
                    if self.expected_airmatic == is_airmatic:
                        self.airmatic_lock_until = 0.0
                    else:
                        is_airmatic = self.state.airmatic
                if self.state.airmatic != is_airmatic:
                    self.state.airmatic = is_airmatic
                    state_changed = True

                is_boost = bool(fan_mode & FanMode.BOOST)
                if time.time() < self.fan_boost_lock_until:
                    if self.expected_fan_boost == is_boost:
                        self.fan_boost_lock_until = 0.0
                    else:
                        is_boost = self.state.fan_boost
                if self.state.fan_boost != is_boost:
                    self.state.fan_boost = is_boost
                    state_changed = True
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Invalid fan mode value: %s", dataModel[Capability.FAN_MODE]
                )

        if Capability.FAN_SPEED in dataModel:
            speed = dataModel[Capability.FAN_SPEED]
            if time.time() < self.fan_speed_lock_until:
                if self.expected_fan_speed == speed:
                    self.fan_speed_lock_until = 0.0
                else:
                    speed = self.state.fan_speed
            if self.state.fan_speed != speed:
                self.state.fan_speed = speed
                state_changed = True

        if Capability.FAN_BOOST_TIMER in dataModel:
            boost_timer = dataModel[Capability.FAN_BOOST_TIMER]
            is_boost = bool(boost_timer > 0)
            if time.time() < self.fan_boost_lock_until:
                if self.expected_fan_boost == is_boost:
                    self.fan_boost_lock_until = 0.0
                else:
                    is_boost = self.state.fan_boost
            if self.state.fan_boost != is_boost:
                self.state.fan_boost = is_boost
                state_changed = True

        if Capability.FAN_SHUTOFF_TIMER in dataModel:
            shutoff_timer = dataModel[Capability.FAN_SHUTOFF_TIMER]
            if self.state.shutoff_timer != shutoff_timer:
                self.state.shutoff_timer = shutoff_timer
                state_changed = True

        if Capability.LIGHT_BRIGHTNESS in dataModel:
            brightness = dataModel[Capability.LIGHT_BRIGHTNESS]
            if time.time() < self.light_lock_until:
                if self.expected_light_brightness == brightness:
                    self.light_lock_until = 0.0
                else:
                    brightness = self.state.light_brightness
            if self.state.light_brightness != brightness:
                self.state.light_brightness = brightness
                state_changed = True

        if Capability.FILTER_SATURATION in dataModel:
            if self.state.filter_saturation != dataModel[Capability.FILTER_SATURATION]:
                self.state.filter_saturation = dataModel[Capability.FILTER_SATURATION]
                state_changed = True

        if state_changed:
            _LOGGER.debug("Device %s updated from MQTT: %s", self.uid, dataModel)
