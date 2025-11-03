"""Utility functions for Elica integration."""

from .const import API_BASE_URL, APP_UUID, CLIENT_ID, CLIENT_SECRET, USER_AGENT
from .elica_connect.api.api import ElicaAPI
from .elica_connect.api.client import ElicaClient


def create_client(username, password):
    """Creates an Elica client instance with the given username and password."""
    api = ElicaAPI(
        base_url=API_BASE_URL,
        user_agent=USER_AGENT,
    )

    client = ElicaClient(
        api=api,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=username,
        password=password,
        # app_uuid=entry.data.get("app_uuid", "home-assistant"),
        app_uuid=APP_UUID,
        token=None,
    )

    return client
