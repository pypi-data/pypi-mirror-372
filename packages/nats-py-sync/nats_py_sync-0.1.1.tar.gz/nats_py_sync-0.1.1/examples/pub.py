"""
Example showing the pub sub pattern in a synchronous fashion

This requires a nats server to be running on localhost

docker run -p 4222:4222 -ti nats:latest -p 4222
"""

import time
import nats_sync


NATS_TOPIC = "hello"

nc = nats_sync.connect("nats://localhost:4222")
while True:
    nc.publish(NATS_TOPIC, b"hello world")
    print(f"Published message on {NATS_TOPIC}")
    time.sleep(0.1)
