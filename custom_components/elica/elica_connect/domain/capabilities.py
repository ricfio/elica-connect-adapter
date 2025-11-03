"""Capability constants for Elica devices.

This module defines the capabilities that can be queried or controlled
on Elica devices, such as lights, fans, and hood features.
Unknown capabilities are included for completeness and future decoding.
"""


class Capability:
    """Device capabilities for Elica devices.

    Each attribute represents a specific controllable or observable
    feature. The value corresponds to the device-specific code.
    Unknown capabilities are left for future analysis.
    """

    # Main known features
    # Cooktop / hood light intensity
    LIGHT_BRIGHTNESS = "96"  # Light brightness (value = 0-100)
    FAN_MODE = "64"  # Fan mode (bitmask: fan on/off, intensive on/off, aimatic on/off)
    FAN_SPEED = "110"  # Fan speed (value = 0=off, 1=low, 2=medium, 3=high)

    # Other capabilities (unknown / to be decoded)
    UNKNOWN_5 = "5"
    UNKNOWN_6 = "6"
    UNKNOWN_68 = "68"
    UNKNOWN_69 = "69"
    UNKNOWN_71 = "71"
    UNKNOWN_72 = "72"
    UNKNOWN_112 = "112"
    UNKNOWN_128 = "128"
    UNKNOWN_129 = "129"
    UNKNOWN_131 = "131"
