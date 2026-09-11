"""Device State.

This module defines the DeviceState dataclass, which represents
the current state of an device (e.g., a hood). It provides properties
to easily query fan and light status, as well as validation of state values.
"""

from dataclasses import dataclass

from .capabilities import Capability
from .fan_mode import FanMode


@dataclass
class DeviceState:
    """Represents the current state of a device.

    Attributes:
        connected (bool): Device is connected.
        airmatic (bool): Automatic fan mode that adjusts speed based on air quality.
        fan_speed (int): Current fan speed (0 = off, 1-3 = normal speeds).
        fan_boost (bool): Intensive fan mode active (timer > 0 minutes).
        light_on (bool): Light is on.
        light_brightness (int): Current light brightness (0-100).
    """

    # Connected
    connected: bool | None = None

    # Fan
    airmatic: bool = False
    fan_speed: int = 0
    fan_boost: bool = False  # Intensive mode / temporary max speed

    # Filter
    filter_saturation: int = 0  # Grease filter saturation (0-100)

    # Light
    light_brightness: int = 0

    @staticmethod
    def from_json(data: dict) -> "DeviceState":
        """Create from API JSON data."""
        capabilities = data.get("dataModel", {})
        fan_mode = FanMode(capabilities.get(Capability.FAN_MODE, 0))

        # fan_on = bool(fan_mode & FanMode.ON)

        fan_speed = capabilities.get(Capability.FAN_SPEED, 0)

        boost_timer = capabilities.get(Capability.FAN_BOOST, 0)
        fan_boost = bool(boost_timer > 0) or bool(fan_mode & FanMode.BOOST)

        airmatic = bool(fan_mode & FanMode.AIRMATIC)

        return DeviceState(
            connected=data.get("connected"),
            airmatic=airmatic,
            fan_speed=fan_speed,
            fan_boost=fan_boost,
            filter_saturation=capabilities.get(Capability.FILTER_SATURATION, 0),
            light_brightness=capabilities.get(Capability.LIGHT_BRIGHTNESS, 0),
        )

    @property
    def fan_on(self) -> bool:
        """Return True if the fan is active (any speed or boost)."""
        return self.fan_speed > 0 or self.fan_boost

    @property
    def fan_off(self) -> bool:
        """Return True if the fan is inactive."""
        return not self.fan_on

    @property
    def fan_mode(self) -> FanMode:
        """Return the fan mode as a bitmask of FanMode flags."""
        mode = FanMode.OFF

        if self.fan_on:
            mode |= FanMode.ON
        if self.fan_boost:
            mode |= FanMode.BOOST
        if self.airmatic:
            mode |= FanMode.AIRMATIC

        return mode

    @property
    def light_on(self) -> bool:
        """Return True if the light is on (brightness > 0)."""
        return self.light_brightness > 0

    @property
    def light_off(self) -> bool:
        """Return True if the light is off (brightness = 0)."""
        return not self.light_on

    def __post_init__(self):
        """Validate fan_speed and light_brightness after initialization.

        Raises:
            ValueError: If fan_speed is not between 0 and 3, or
                        light_brightness is not between 0 and 100.
        """
        if not 0 <= self.fan_speed <= 3:
            raise ValueError("fan_speed must be between 0 and 3")
        if not 0 <= self.light_brightness <= 100:
            raise ValueError("light_brightness must be between 0 and 100")

    def __repr__(self):
        """Return a detailed string representation of the device state."""
        fan_status = "on" if self.fan_on else "off"
        fan_parts = [f"fan={fan_status}"]

        if self.fan_on:
            fan_parts.append(f"speed={self.fan_speed}")
            if self.fan_boost:
                fan_parts.append("boost=on")

        fan_parts.append(f"airmatic={'on' if self.airmatic else 'off'}")
        fan_str = ", ".join(fan_parts)

        light_status = "on" if self.light_on else "off"
        light_parts = [f"light={light_status}"]
        if self.light_on:
            light_parts.append(f"brightness={self.light_brightness}")
        light_str = ", ".join(light_parts)

        return f"<DeviceState {fan_str}, {light_str}>"
