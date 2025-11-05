"""Utility functions for Elica integration."""

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback

from .connect import API_BASE_URL, API_CLIENT_ID, API_CLIENT_SECRET, APPLICATION_UUID
from .connect.adapters.ha import AioHttpRestClient, HaAuthProvider, HaMqttClient
from .connect.core import AuthService, Controller
from .const import DOMAIN


async def create_mqtt_client(hass: HomeAssistant, topics: list[str]):
    """Subscribe to devices and dispatch messages using HA MQTT bus."""
    # Ensure the mqtt client is ready (blocks until available)
    await mqtt.async_wait_for_mqtt_client(hass)

    @callback
    def message_received(msg):
        # msg is the MQTT message object - attributes like topic, payload, qos
        payload_text = msg.payload.decode()  # decode bytes -> string
        # process payload_text...
        # hass.helpers.event.async_call_later(0, lambda _now: None)  # esempio di uso

    # subscribe and keep unsubscribe function to cleanup on unload
    unsubscribes = []
    for topic in topics:
        unsubscribe = await mqtt.async_subscribe(hass, topic, message_received, qos=1)
        unsubscribes.append(unsubscribe)

    hass.data.setdefault(DOMAIN, {})["mqtt_unsubscribes"] = unsubscribes
    return True


def create_controller(hass: HomeAssistant, username: str, password: str):
    """Create the Controller instance with the given username and password."""
    mqtt_client = HaMqttClient(hass)
    rest_client = AioHttpRestClient(
        hass,
        API_BASE_URL,
        10,
    )
    auth_service = AuthService(
        API_BASE_URL, APPLICATION_UUID, API_CLIENT_ID, API_CLIENT_SECRET
    )
    auth_provider = HaAuthProvider(
        hass,
        auth_service=auth_service,
        username=username,
        password=password,
    )

    return Controller(
        auth_provider=auth_provider,
        rest_client=rest_client,
        mqtt_client=mqtt_client,
        command_timeout=30000,
    )
