"""Device."""

from dataclasses import dataclass, field
from typing import Any

from .capabilities import Capability
from .device_state import DeviceState
from .hood_filter import HoodFilter


@dataclass
class Device:
    """Represents an device: core metadata + state + optional metadata.

    - core fields: used for identity, device_info and logic
    - metadata: dictionary with raw or selected extra info kept for UI/debug
    - filters: parsed list of HoodFilter
    """

    id: str
    cuid: str
    name: str
    device_type: str | None = None
    model_id: str | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    sw_version: str | None = None

    connected: bool | None = None
    is_legacy: bool | None = None
    data_model_version: int | None = None
    product_reference: str | None = None

    # device capabilities (determined from dataModel)
    capabilities: list[Capability] = field(default_factory=list)

    # dynamic state (DTO)
    state: DeviceState = field(default_factory=DeviceState)

    # optional parsed list of filters
    filters: list[HoodFilter] = field(default_factory=list)

    # raw or selected extra data kept for informational attributes
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_json(data: dict[str, Any]) -> "Device":
        """Create ElicaDevice from API JSON. Keep core fields and save metadata."""
        # core fields
        device_id = data["id"]
        cuid = data["cuid"]
        name = data.get("name", device_id)
        device_type = data.get("type")
        model_id = data.get("code12nc")
        serial = data.get("serialNumber")
        sw_ver = data.get("configuration", {}).get("revisionInfo")

        # state
        state = DeviceState.from_json(data)

        # parse capabilities from dataModel (keep raw mask too)
        data_model = data.get("dataModel", {}) or {}
        capabilities = []
        if Capability.LIGHT_BRIGHTNESS in data_model:
            capabilities.append(Capability.LIGHT_BRIGHTNESS)
        if Capability.FAN_SPEED in data_model:
            capabilities.append(Capability.FAN_SPEED)
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

        return Device(
            id=device_id,
            cuid=cuid,
            name=name,
            device_type=device_type,
            model_id=model_id,
            serial_number=serial,
            model=device_type,
            sw_version=sw_ver,
            connected=data.get("connected"),
            is_legacy=data.get("isLegacy"),
            data_model_version=data.get("dataModelVersion"),
            product_reference=data.get("prf"),
            capabilities=capabilities,
            state=state,
            filters=filters,
            metadata=metadata,
        )
