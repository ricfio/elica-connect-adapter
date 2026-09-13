"""Constants for the Elica Connect integration."""  # noqa: EXE002

from .api.domain import Capability, FanPreset
from .api.core.constants import (
    API_BASE_URL,
    API_CLIENT_ID as CLIENT_ID,
    API_CLIENT_SECRET as CLIENT_SECRET,
    APPLICATION_UUID as APP_UUID,
)

DOMAIN = "elica_connect_adapter"

USER_AGENT = "okhttp/4.11.0"

OAUTH_TOKEN_URL = f"{API_BASE_URL}/oauth/token"

FAN_PRESET = [
    FanPreset.BOOST,
]
