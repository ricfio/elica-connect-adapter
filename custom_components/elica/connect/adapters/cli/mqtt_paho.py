"""MQTT client implementation for CLI."""

import logging
import time

from typing import Any, Callable

import paho.mqtt.client as mqtt

from connect.core.constants import MQTT_TOPIC_FORMAT


class PahoMqttClient:
    """MQTT client implementation using Paho."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.client: mqtt.Client | None = None
        self._host: str | None = None
        self._port: int | None = None
        self._keepalive: int = 60
        self._on_message = None
        self._running = False

    @staticmethod
    def get_topic_url(cuid: str) -> str:
        """Get the MQTT topic URL for a device."""
        return MQTT_TOPIC_FORMAT.format(CUID=cuid)

    def _subscribe_to_device(self, device_id: str) -> None:
        """Subscribe to updates for a specific device."""
        if self.client is None:
            raise RuntimeError("MQTT client not initialized")

        topic = self.get_topic_url(device_id)
        self.logger.debug("MQTT > Subscribe request to: %s", topic)
        result, mid = self.client.subscribe(topic, qos=1)
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.logger.info("MQTT > Subscribe success to: %s (mid=%s) ", topic, mid)
        else:
            self.logger.error("MQTT > Subscribe failure to: %s (err=%s)", topic, result)

    def initialize(
        self,
        host: str,
        port: int,
        client_id: str,
        username: str,
        password: str,
        keepalive: int = 60,
    ) -> None:
        """Configure MQTT client without connecting."""
        self.client = mqtt.Client(client_id=client_id, clean_session=True)
        self.client.username_pw_set(username, password)
        self.client.reconnect_delay_set(min_delay=1, max_delay=60)
        self._host = host
        self._port = port
        self._keepalive = keepalive

    def listen(
        self,
        devices: list[str],
        on_message: Callable[[str, Any], None],
    ) -> None:
        """Connect, subscribe to devices, and dispatch messages via callback."""
        if self.client is None or self._host is None or self._port is None:
            raise RuntimeError("MQTT client not initialized")

        self._on_message = on_message
        self._running = True

        # on_connect callback
        def _on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.logger.info(
                    "MQTT > Connected to broker: %s:%d", self._host, self._port
                )
                for device_id in devices:
                    self._subscribe_to_device(device_id)
            else:
                self.logger.error("MQTT > Connecting error: %d", rc)

        # on_message callback
        def _on_message(client, userdata, msg):
            payload = msg.payload.decode("utf-8")
            try:
                if self._on_message:
                    self._on_message(msg.topic, payload)
            except Exception:
                self.logger.exception("Error handling message for topic %s", msg.topic)

        self.client.on_connect = _on_connect
        self.client.on_message = _on_message

        # Connect with retry
        if not self._connect_with_retry():
            raise RuntimeError("Could not connect to MQTT broker")

        # Keep loop running until stopped
        while self._running:
            time.sleep(0.1)

    def _connect_with_retry(self, max_attempts: int = 5, delay: float = 2.0) -> bool:
        """Try connecting to broker multiple times."""
        if self.client is None or self._host is None or self._port is None:
            raise RuntimeError("MQTT client not initialized")

        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.debug(
                    "Connecting to broker (%d/%d)...", attempt, max_attempts
                )
                self.client.connect(self._host, self._port, self._keepalive)
                self.client.loop_start()
                return True
            except Exception as e:
                self.logger.warning("Connection attempt %d failed: %s", attempt, e)
                time.sleep(delay)
        self.logger.error("All connection attempts failed")
        return False

    def stop(self) -> None:
        """Stop MQTT loop and disconnect."""
        self.logger.info("Stopping MQTT client...")
        self._running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
