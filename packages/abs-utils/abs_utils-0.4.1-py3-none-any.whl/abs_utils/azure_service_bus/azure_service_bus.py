from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage, ServiceBusReceiveMode,TransportType
from azure.servicebus.exceptions import ServiceBusError
import json
import asyncio
from typing import Dict, Any
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

class AzureServiceBus:
    def __init__(self, connection_string: str, queue_name: str):
        self.connection_string = connection_string
        self.queue_name = queue_name
        # Create an async client (no network I/O yet)
        self.client: ServiceBusClient = ServiceBusClient.from_connection_string(
            conn_str=connection_string,

            logging_enable=False,
            transport_type=TransportType.Amqp,
            connection_idle_timeout=30,
        )
        # Async context managers + opened objects
        self._sender_cm = None
        self._receiver_cm = None
        self.sender = None
        self.receiver = None
        self._connected = False
        self._lock = asyncio.Lock()                   # serialize open/send/recv

    async def connect(self):
        """Open AMQP links for sender and receiver."""
        async with self._lock:
            if self._connected:
                return
            try:
                # Build context managers
                self._sender_cm = self.client.get_queue_sender(queue_name=self.queue_name)
                self._receiver_cm = self.client.get_queue_receiver(
                    queue_name=self.queue_name,
                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                )
                # OPEN them (this is what was missing)
                self.sender = await self._sender_cm.__aenter__()
                self.receiver = await self._receiver_cm.__aenter__()
                self._connected = True
                logger.info(f"Connected to queue: {self.queue_name}")
            except Exception as e:
                # ensure partial opens are closed
                await self._safe_close(ignore_errors=True)
                self._connected = False
                logger.error(f"Connection error: {e}")
                raise

    async def _safe_close(self, ignore_errors: bool = False):
        """Close links and client via context manager exits."""
        try:
            if self._sender_cm:
                try:
                    await self._sender_cm.__aexit__(None, None, None)
                finally:
                    self._sender_cm = None
                    self.sender = None
            if self._receiver_cm:
                try:
                    await self._receiver_cm.__aexit__(None, None, None)
                finally:
                    self._receiver_cm = None
                    self.receiver = None
        except Exception as e:
            if not ignore_errors:
                raise e
        finally:
            # Close the client last
            try:
                await self.client.close()
            except Exception:
                if not ignore_errors:
                    raise

    async def disconnect(self):
        """Close connections cleanly."""
        async with self._lock:
            try:
                await self._safe_close(ignore_errors=False)
                logger.info("Disconnected from Service Bus")
            finally:
                # Recreate a fresh client for next connect()
                self.client = ServiceBusClient.from_connection_string(
                    conn_str=self.connection_string,
                    logging_enable=False,
                    transport_type=TransportType.Amqp,
                    connection_idle_timeout=30,
                )
                self._connected = False

    async def _ensure_connected(self):
        if not self._connected:
            await self.connect()

    async def send(self, event_payload: Dict[str, Any]):
        """Send one message with one hard retry after reconnect."""
        await self._ensure_connected()
        try:
            async with self._lock:
                message = ServiceBusMessage(
                    body=json.dumps(event_payload, ensure_ascii=False),
                    content_type="application/json",
                )
                await self.sender.send_messages(message)
                logger.info("Message sent")
        except (ServiceBusError, AttributeError) as e:
            # Rebuild links and try once more
            logger.warning(f"Send failed ({type(e).__name__}): {e}. Reconnecting and retrying once...")
            await self.disconnect()
            await self.connect()
            async with self._lock:
                message = ServiceBusMessage(
                    body=json.dumps(event_payload, ensure_ascii=False),
                    content_type="application/json",
                )
                await self.sender.send_messages(message)
                logger.info("Message sent (after reconnect)")

    async def receive_messages(self, max_message_count: int = 1, timeout: int = 30):
        """Receive messages; if link is stale, reconnect and retry once."""
        await self._ensure_connected()
        try:
            async with self._lock:
                msgs = await self.receiver.receive_messages(
                    max_message_count=max_message_count,
                    max_wait_time=timeout,
                )
                return msgs
        except (ServiceBusError, AttributeError) as e:
            logger.warning(f"Receive failed ({type(e).__name__}): {e}. Reconnecting and retrying once...")
            await self.disconnect()
            await self.connect()
            async with self._lock:
                msgs = await self.receiver.receive_messages(
                    max_message_count=max_message_count,
                    max_wait_time=timeout,
                )
                return msgs

    async def complete_message(self, message):
        """Complete a received message; if link died, reconnect and try once."""
        await self._ensure_connected()
        try:
            async with self._lock:
                await self.receiver.complete_message(message)
                logger.info("Message completed")
        except (ServiceBusError, AttributeError) as e:
            logger.warning(f"Complete failed ({type(e).__name__}): {e}. Reconnecting and retrying once...")
            await self.disconnect()
            await self.connect()
            async with self._lock:
                await self.receiver.complete_message(message)
                logger.info("Message completed (after reconnect)")