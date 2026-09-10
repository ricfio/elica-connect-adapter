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

    # Light brightness (value = 0-100)
    LIGHT_BRIGHTNESS = "96"

    # Fan mode (bitmask: fan on/off, intensive on/off, airmatic on/off)
    FAN_MODE = "64"

    # Grease filter saturation (value = 0-100)
    FILTER_SATURATION = "128"

    CAPABILITY_129 = "129"

    CAPABILITY_131 = "131"

    CAPABILITY_68 = "68"

    CAPABILITY_69 = "69"

    CAPABILITY_5 = "5"

    CAPABILITY_6 = "6"

    CAPABILITY_71 = "71"

    CAPABILITY_72 = "72"

    # Fan speed (value = 0=off, 1=low, 2=medium, 3=high)
    FAN_SPEED = "110"

    CAPABILITY_112 = "112"
