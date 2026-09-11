"""Constants for the Elica Connect integration."""  # noqa: EXE002

from .api.domain import Capability, FanPreset

DOMAIN = "elica_connect_adapter"

API_BASE_URL = "https://cloudprod.elica.com/eiot-api/v1"
USER_AGENT = "okhttp/4.11.0"

CLIENT_ID = "eiot-app"
CLIENT_SECRET = "VqwG1KTB77UeROu"

OAUTH_TOKEN_URL = f"{API_BASE_URL}/oauth/token"

APP_UUID = "0ba86de295087670"

CAPABILITIES = [
    Capability.LIGHT_BRIGHTNESS,
    Capability.FAN_MODE,
    Capability.FILTER_SATURATION,
    Capability.CAPABILITY_129,
    Capability.CAPABILITY_131,
    Capability.CAPABILITY_68,
    Capability.FAN_BOOST,
    Capability.CAPABILITY_5,
    Capability.CAPABILITY_6,
    Capability.CAPABILITY_71,
    Capability.CAPABILITY_72,
    Capability.FAN_SPEED,
    Capability.CAPABILITY_112,
]

FAN_PRESET = [
    FanPreset.NORMAL,
    FanPreset.INTENSIVE,
]
