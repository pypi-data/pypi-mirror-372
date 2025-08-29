"""NATS Context that controls communication with nats-py async functions"""

import asyncio
import nats
from nats.aio.subscription import Subscription
from nats.aio.msg import Msg


class NATSSub:
    """NATS subscriber"""

    def __init__(self, loop: asyncio.AbstractEventLoop, sub: Subscription):
        self._loop = loop
        self._sub = sub

    def unsubscribe(self):
        """Unsubscribe to the current nats topic"""
        self._loop.run_until_complete(self._sub.unsubscribe())

    def recv(self, timeout: float | None = None) -> Msg:
        """Receive a single nats message from the nats context

        Args:
            timeout (float | None, optional): Timeout to wait until raising a TimeoutError. Defaults to None.

        Returns:
            Msg: NATS Msg object
        """
        return self._loop.run_until_complete(self._sub.next_msg(timeout=timeout))

    def respond(self, req_msg: Msg, reply: bytes):
        """Respond to a given message

        Args:
            req_msg (Msg): NATS message to reply to
            reply (bytes): Reply payload
        """
        self._loop.run_until_complete(req_msg.respond(reply))


class NATSContext:
    """
    Simple NATS context that wraps the native nats async library for synchronous (blocking, non async) applications
    """

    def __init__(self, nats_url: str | list[str]):
        self._loop = asyncio.new_event_loop()
        self._nc = self._loop.run_until_complete(nats.connect(nats_url))

    def subscribe(self, topic: str) -> NATSSub:
        """
        Subscribe to a single topic

        Args:
            topic (str): nats topic
        """
        nats_sub = self._loop.run_until_complete(self._nc.subscribe(topic))
        return NATSSub(self._loop, nats_sub)

    def publish(self, topic: str, msg: bytes):
        """Publish a single message on the given topic

        Args:
            topic (bytes): NATS topic to send on
            msg (bytes): message to send
        """
        self._loop.run_until_complete(self._nc.publish(topic, msg))

    def request(self, topic: str, msg: bytes, timeout: float | None = None) -> Msg:
        """Request a message on a given topic

        Args:
            topic (str): NATS topic
            msg (bytes): Message to send
            timeout (float | None, optional): Timeout to wait. If None, will block forever. Defaults to None.

        Returns:
            Msg: The reply message
        """
        timeout = timeout if timeout is not None else float("inf")
        return self._loop.run_until_complete(
            self._nc.request(topic, msg, timeout=timeout)
        )
