"""Fan Mode."""

from enum import IntFlag


class FanMode(IntFlag):
    """Representing of the fan mode (bit flags)."""

    OFF = 0
    ON = 1
    BOOST = 4
    AIRMATIC = 32
