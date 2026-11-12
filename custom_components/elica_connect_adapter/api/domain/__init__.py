"""Elica Connect API - Domain package module."""  # noqa: EXE002

from .capabilities import Capability, FanSpeed, normalize_data_model  # noqa: F401
from .device import MANUFACTURER, Device  # noqa: F401
from .device_state import DeviceState  # noqa: F401
from .fan_preset import FanPreset  # noqa: F401
