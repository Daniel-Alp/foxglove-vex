import asyncio
import time
from base64 import b64encode
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer
from foxglove_schemas_protobuf.Point2_pb2 import Point2
from protobuf_util import build_file_descriptor_set

async def main():
    async with FoxgloveServer("0.0.0.0", 8765, "Foxglove and VEX V5 Bridge") as server:
        chan_id = await server.add_channel(
            {
                "topic": "test_msg",
                "encoding": "protobuf",
                "schemaName": Point2.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(Point2).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        await asyncio.sleep(3) 

        i = 0
        while True:
            await asyncio.sleep(0.01)   
            now = time.time_ns()
            
            i += 1
            point = Point2()
            point.x = i
            point.y = i

            await server.send_message(chan_id, now, point.SerializeToString())

if __name__ == "__main__":
    run_cancellable(main())