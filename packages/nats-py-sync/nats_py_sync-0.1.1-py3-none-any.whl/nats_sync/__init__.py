"""NATS Synchronous client wrapper around the native nats-py library"""

from . import nats_ctx


__all__ = ["connect"]


def connect(
    servers: str | tuple[str, ...] = ("nats://localhost:4222",),
) -> nats_ctx.NATSContext:
    """Construct a Synchronous NATS Context
    This NATS Context maintains its own event loop and handles running NATS coroutines until they finish

    Args:
        servers (_type_, optional): a single nats url or a list of them. Defaults to ["nats://localhost:4222"].

    Returns:
        nats_ctx.NATSContext: Created Synchronous NATS Context
    """
    nats = nats_ctx.NATSContext(nats_url=servers)
    return nats
