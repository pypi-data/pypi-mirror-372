# nats-py-sync

Synchronous wrapper around native [nats-py](https://github.com/nats-io/nats.py) async library

This is not a comprehensive, feature complete wrapper. It has the main features described in the [nats-py](https://github.com/nats-io/nats.py) readme

---
> [!TIP] Who is this library for?
> This library if mainly useful for people who need nats functionality in their non-async based python code. If you can use async in your codebase, use nats-py directly

---
> [!TIP] How does this library work?
> The NATSContext object maintains its own event loop and queries nats.NATSConnection tasks to complete and return.
> NATSContext calls are blocking until the nats.NATSConnection futures finish

## Installation

```shell
pip install nats-py-sync
```

## Publisher/Subscriber

```python
# subscriber
import nats_sync


nc = nats_sync.connect("nats://localhost:4222")
sub = nc.subscribe("hello")
while True:
    msg = sub.recv()
    print(f"Received {msg.data.decode()} on topic {msg.subject}")
```

```python
# publisher
import time
import nats_sync


NATS_TOPIC = "hello"

nc = nats_sync.connect("nats://localhost:4222")
while True:
    nc.publish(NATS_TOPIC, b"hello world")
    print(f"Published message on {NATS_TOPIC}")
    time.sleep(0.1)
```

## Request/Response

```python
# request
import time
import nats_sync


client = nats_sync.connect("nats://localhost:4222")
while True:
    msg = client.request("request", "hello world".encode())
    print(f"Received Reply {msg.data.decode()} on topic {msg.subject}")
    time.sleep(1.0)
```

```python
# response
import nats_sync


nc = nats_sync.connect("nats://localhost:4222")
sub = nc.subscribe("request")
while True:
    msg = sub.recv()
    print(f"Received {msg.data.decode()} on topic {msg.subject}")
    sub.respond(msg, "Reply".encode())
```
