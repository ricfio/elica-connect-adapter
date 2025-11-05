"""MQTT Subscriber AioMqtt."""

import asyncio
import contextlib
import logging

from aiomqtt import Client, MqttError

from .mqtt_subscriber_interface import MqttSubscriberInterface, OnMessageType

logger = logging.getLogger(__name__)


class MqttSubscriberAiomqtt(MqttSubscriberInterface):
    """MQTT Subscriber AioMqtt."""

    def __init__(self) -> None:
        """Initialize the MQTT subscriber."""
        self._client: Client | None = None
        self._topics: list[str] = []
        self._on_message: OnMessageType | None = None
        self._task: asyncio.Task | None = None
        self._running: bool = False

    async def initialize(
        self,
        host: str,
        port: int,
        client_id: str,
        username: str,
        password: str,
        tls: bool = True,
        keepalive: int = 60,
    ) -> None:
        """Configure the MQTT client."""
        self._client = Client(
            hostname=host,
            port=port,
            identifier=username,
            username=username,
            password=password,
            # tls=tls,
            # client_id=client_id,
            keepalive=keepalive,
        )

    async def _message_loop(self) -> None:
        assert self._client is not None
        # if self._client is None:
        #     return
        try:
            async with self._client as client:
                for topic in self._topics:
                    await client.subscribe(topic)
                async for message in client.messages:
                    if not self._running:
                        break
                    if self._on_message:
                        result = self._on_message(message.topic.value, message.payload)
                        if asyncio.iscoroutine(result):
                            await result
        except MqttError as err:
            logger.error(f"MQTT error {err}")
        finally:
            self._running = False

    async def start(
        self,
        topics: list[str],
        on_message: OnMessageType,
    ) -> None:
        """Start the subscription and message handling loop."""
        self._topics = topics
        self._on_message = on_message
        self._running = True
        if self._client is None:
            raise RuntimeError("Client not initialized. Call initialize() first.")
        self._task = asyncio.create_task(self._message_loop())

    async def stop(self) -> None:
        """Stop the subscriber and disconnect."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        self._task = None
        logger.info("MQTT subscriber stopped")
