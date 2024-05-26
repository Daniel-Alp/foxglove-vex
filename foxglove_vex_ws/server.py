import asyncio
import orjson
import time
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer

async def main():
    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        chan_id = await server.add_channel(
            {
                "topic": "example_msg",
                "encoding": "json",
                "schemaName": "ExampleMsg",
                "schema": orjson.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "counter": {"type": "number"}
                        }
                    }
                ).decode("utf-8"),
                "schemaEncoding": "jsonschema"
            }
        )

        i = 0
        while True:
            await asyncio.sleep(0.01)
            timestamp = time.time_ns()

            i += 1 

            await server.send_message(
                chan_id,
                timestamp,
                orjson.dumps({"counter": i})
            )

if __name__ == "__main__":
    run_cancellable(main())      