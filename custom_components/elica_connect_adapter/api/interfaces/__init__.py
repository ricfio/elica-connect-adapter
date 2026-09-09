"""Elica Connect - Interfaces."""

from .mqtt_client_interface import (  # noqa: F401, I001
    MqttClientInterface,
    OnMqttMessageCallback,
)
from .rest_client_interface import RestClientInterface  # noqa: F401
