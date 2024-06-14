# Send mock messages to test 2D VEX extension if no VEX brain on hand

import asyncio
import time
import orjson
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer
import math

async def main():
    schema = {
        "type": "object",
        "properties": {
            "x": {"type": "number"},
            "y": {"type": "number"},
            "theta": {"type": "number"}
        }
    }

    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        chan_id = await server.add_channel(
            {
                "topic": "example_trajectory",
                "encoding": "json",
                "schemaName": "odometry",
                "schema": orjson.dumps(schema).decode("utf-8"),
                "schemaEncoding": "jsonschema"
            }
        )

        # Simulate the robot moving in a circle
        x = 0
        y = 0
        heading_deg = 0

        while True:
            timestamp = time.time_ns()
            heading_deg = (heading_deg + 1) % 360
            heading_rad = heading_deg * math.pi / 180;
            x += math.cos(math.pi * 0.5 - heading_rad);
            y += math.sin(math.pi * 0.5 - heading_rad);

            payload = {
                "x": x,
                "y": y,
                "theta": heading_rad
            }

            await server.send_message(chan_id, timestamp, orjson.dumps(payload))
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    run_cancellable(main())