"""
Example showing the pub sub pattern in a synchronous fashion

This requires a nats server to be running on localhost
docker run -p 4222:4222 -ti nats:latest -p 4222
"""

import nats_sync


nc = nats_sync.connect("nats://localhost:4222")
sub = nc.subscribe("hello")
while True:
    msg = sub.recv()
    print(f"Received {msg.data.decode()} on topic {msg.subject}")
