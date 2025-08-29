"""
Example showing the pub sub pattern in a synchronous fashion

This requires a nats server to be running on localhost
docker run -p 4222:4222 -ti nats:latest -p 4222
"""

import time
import nats_sync


client = nats_sync.connect("nats://localhost:4222")
while True:
    msg = client.request("request", "hello world".encode())
    print(f"Received Reply {msg.data.decode()} on topic {msg.subject}")
    time.sleep(1.0)
