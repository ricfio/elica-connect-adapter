"""Utility functions for Elica integration."""

from homeassistant.core import HomeAssistant

from .connect import API_BASE_URL, API_CLIENT_ID, API_CLIENT_SECRET, APPLICATION_UUID
from .connect.adapters.ha import AioHttpRestClient, HaAuthProvider
from .connect.core import AuthService, Controller
from .connect.adapters.shared import MqttClientAiomqtt


def create_controller(hass: HomeAssistant, username: str, password: str):
    """Create the Controller instance with the given username and password."""
    auth_service = AuthService(
        API_BASE_URL, APPLICATION_UUID, API_CLIENT_ID, API_CLIENT_SECRET,
    )

    auth_provider = HaAuthProvider(
        hass,
        auth_service=auth_service,
        username=username,
        password=password,
    )

    rest_client = AioHttpRestClient(
        hass,
        API_BASE_URL,
        10,
    )

    mqtt_client = MqttClientAiomqtt()

    return Controller(
        auth_provider=auth_provider,
        rest_client=rest_client,
        mqtt_client=mqtt_client,
        command_timeout=30000,
    )
