"""Capability constants and definitions for Elica devices."""

from __future__ import annotations


class Capability:
    """Device capabilities for Elica appliances.

    Maps capability codes reported in device telemetry to semantic identifiers
    for fan control, lighting, filters, and unmapped telemetry slots.
    """

    # --- Fan & Ventilation ---
    FAN_MODE = "64"
    """Fan mode bitmask (Bit 0: ON, Bit 2: BOOST, Bit 5: AIRMATIC)."""

    FAN_BOOST_TIMER = "69"
    """Fan boost shut-off timer (remaining minutes)."""

    FAN_SPEED = "110"
    """Fan speed level (0 = off, 1 = low, 2 = medium, 3 = high)."""

    FAN_SHUTOFF_TIMER = "432"
    """Fan automatic shut-off timer (remaining minutes)."""

    # --- Lighting ---
    LIGHT_BRIGHTNESS = "96"
    """Light brightness percentage (0-100 %)."""

    # --- Maintenance & Filters ---
    FILTER_SATURATION = "128"
    """Grease filter saturation percentage (0-100 %)."""

    # --- Unmapped / Reserved Telemetry Slots ---
    CAPABILITY_5 = "5"
    CAPABILITY_6 = "6"
    CAPABILITY_68 = "68"
    CAPABILITY_71 = "71"
    CAPABILITY_72 = "72"
    CAPABILITY_112 = "112"
    CAPABILITY_129 = "129"
    CAPABILITY_131 = "131"


class FanSpeed:
    """Fan speed numeric levels and labels."""

    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    LABELS = {
        OFF: "off",
        LOW: "low",
        MEDIUM: "medium",
        HIGH: "high",
    }
