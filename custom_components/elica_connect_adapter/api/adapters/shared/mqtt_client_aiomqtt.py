"""MQTT Subscriber AioMqtt."""

import asyncio
import logging

from aiomqtt import Client, MqttError

from ...interfaces import (  # noqa: TID252
    MqttClientInterface,
    OnMqttConnectionCallback,
    OnMqttMessageCallback,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class MqttClientAiomqtt(MqttClientInterface):
    """MQTT Subscriber using AioMqtt."""

    def __init__(self) -> None:
        """Initialize the MQTT subscriber."""
        super().__init__()
        self._client: Client | None = None
        self._topics: list[str] = []
        self._on_message: OnMqttMessageCallback | None = None
        self._on_connection: OnMqttConnectionCallback | None = None
        self._task: asyncio.Task | None = None
        self._running: bool = False

    async def initialize(
        self,
        hostname: str,
        port: int,
        identifier: str,
        username: str,
        password: str,
        tls: bool = True,
        keepalive: int = 60,
    ) -> None:
        """Configure the MQTT client."""
        self.hostname = hostname
        self.port = port

        # TLS context was prepared here previously but not used; remove allocation to avoid unused variable

        self._client = Client(
            hostname=hostname,
            port=port,
            identifier=identifier,
            username=username,
            password=password,
            # If TLS is needed in future, pass a `tls_context` created by `ssl.create_default_context()`
            keepalive=keepalive,
        )

        _LOGGER.info(
            f"MQTT client configured for {self.hostname}:{self.port} "
            f"(TLS={'on' if tls else 'off'}, keepalive={keepalive}s)"
        )

    async def start(
        self,
        topics: list[str],
        on_message: OnMqttMessageCallback,
        on_connection: OnMqttConnectionCallback | None = None,
    ) -> None:
        """Start subscription and message handling loop."""
        if self._running:
            _LOGGER.warning("MQTT subscriber already running")
            return

        if self._client is None:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        if not topics:
            _LOGGER.warning("No MQTT topics to subscribe to")
            return

        self._topics = topics
        self._on_message = on_message
        self._on_connection = on_connection
        self._running = True
        self._task = asyncio.create_task(self._message_loop())

        _LOGGER.info("MQTT subscriber task started")

    async def _message_loop(self) -> None:  # noqa: C901
        """Handle MQTT connection, subscribe to topics, and dispatch messages.
        Automatically reconnects on MqttError with exponential backoff while running.
        """
        if self._client is None:
            _LOGGER.error("MQTT client not initialized in message loop")
            return

        reconnect_delay = 5
        max_reconnect = 60

        try:
            while self._running:
                try:
                    # connect with timeout
                    # async with asyncio.timeout(30):
                    _LOGGER.debug("Attempting MQTT connection...")
                    async with self._client as client:
                        _LOGGER.debug("MQTT connection established, subscribing...")
                        for topic in self._topics:
                            await client.subscribe(topic)
                        _LOGGER.info(
                            f"Connected to {self.hostname}:{self.port}, "  # noqa: G004
                            f"subscribed to topics: {self._topics}"
                        )
                        if self._on_connection:
                            res = self._on_connection(True)
                            if asyncio.iscoroutine(res):
                                await res

                        # reset backoff after successful connection
                        reconnect_delay = 5

                        async for message in client.messages:
                            if not self._running:
                                break
                            await self._handle_message(message)

                except asyncio.CancelledError:
                    _LOGGER.debug("MQTT message loop cancelled")
                    raise

                except TimeoutError as err:
                    if not self._running:
                        break
                    _LOGGER.warning(f"Timeout {err}, reconnecting in {reconnect_delay}s")
                    if self._on_connection:
                        res = self._on_connection(False)
                        if asyncio.iscoroutine(res):
                            await res
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect)

                except MqttError as err:
                    if not self._running:
                        break
                    _LOGGER.warning(
                        f"MQTT error: {err}, reconnecting in {reconnect_delay}s"
                    )
                    if self._on_connection:
                        res = self._on_connection(False)
                        if asyncio.iscoroutine(res):
                            await res
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect)

                except Exception as err:
                    _LOGGER.error(f"Unexpected error in MQTT loop: {err}")
                    if self._on_connection:
                        res = self._on_connection(False)
                        if asyncio.iscoroutine(res):
                            await res
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = 5
        finally:
            if self._on_connection:
                try:
                    res = self._on_connection(False)
                    if asyncio.iscoroutine(res):
                        await res
                except Exception:
                    _LOGGER.exception("Error in on_connection callback during shutdown")

            # clean internal state after stopping
            self._on_message = None
            self._on_connection = None
            self._topics.clear()
            self._task = None
            _LOGGER.info("MQTT subscriber loop terminated")

    async def _handle_message(self, message) -> None:
        """Decode payload and call the callback."""
        if self._on_message:
            payload = message.payload.decode("utf-8", errors="replace")
            result = self._on_message(message.topic.value, payload)
            if asyncio.iscoroutine(result):
                await result

    async def stop(self) -> None:
        """Stop the subscriber safely."""
        if not self._running:
            _LOGGER.debug("MQTT subscriber already stopped")
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                _LOGGER.debug("MQTT task cancelled successfully")
            except Exception as err:
                _LOGGER.warning(f"Error while stopping MQTT subscriber: {err}")
            finally:
                self._task = None

        # clean internal state
        self._on_message = None
        self._topics.clear()

        _LOGGER.info("MQTT subscriber stopped")
