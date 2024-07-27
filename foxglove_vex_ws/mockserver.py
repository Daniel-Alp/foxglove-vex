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
        chan_id_1 = await server.add_channel(
            {
                "topic": "small_circle",
                "encoding": "json",
                "schemaName": "odometry",
                "schema": orjson.dumps(schema).decode("utf-8"),
                "schemaEncoding": "jsonschema"
            }
        )
        chan_id_2 = await server.add_channel(
            {
                "topic": "big_circle",
                "encoding": "json",
                "schemaName": "odometry",
                "schema": orjson.dumps(schema).decode("utf-8"),
                "schemaEncoding": "jsonschema"
            }
        )

        # Simulate the robot moving in a circle
        x = 0
        y = 0
        i = 0
        theta = 0

        while True:
            timestamp = time.time_ns()
            x = 24 * math.cos(i * math.pi / 180)
            y = 24 * math.sin(i * math.pi / 180)
            theta = ((360 - i) % 360) * math.pi / 180
            i = (i + 1) % 360

            payload_1 = {
                "x": x,
                "y": y,
                "theta": theta
            }

            payload_2 = {
                "x": 2 * x,
                "y": 2 * y,
                "theta": theta
            }

            await server.send_message(chan_id_1, timestamp, orjson.dumps(payload_1))
            await server.send_message(chan_id_2, timestamp, orjson.dumps(payload_2))
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    run_cancellable(main())