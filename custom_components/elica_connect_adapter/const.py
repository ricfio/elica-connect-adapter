"""Constants for the Elica Connect integration."""  # noqa: EXE002

from .api.core.constants import (
    API_BASE_URL,
)
from .api.domain import FanPreset

DOMAIN = "elica_connect_adapter"

USER_AGENT = "okhttp/4.11.0"

OAUTH_TOKEN_URL = f"{API_BASE_URL}/oauth/token"

FAN_PRESET = [
    FanPreset.LOW,
    FanPreset.MEDIUM,
    FanPreset.HIGH,
    FanPreset.BOOST,
]
