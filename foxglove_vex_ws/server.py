import asyncio
import time
import orjson
import serial
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer
from json_util import build_shema
from serial_util import read

async def main():
    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        ser = serial.Serial('/dev/ttyACM1', baudrate=115200, timeout=0.01)

        topic_dict = {}

        while True:
            timestamp = time.time_ns()

            data = await read(ser)
            if data[:5].upper() != "DATA:":
                continue

            json = orjson.loads(data[5:])

            # need to handle these keys not existing
            topic = json["topic"]
            payload = json["payload"]

            if topic not in topic_dict:
                chan_id = await server.add_channel(
                    {
                        "topic": topic,
                        "encoding": "json",
                        "schemaName": topic,
                        "schema": orjson.dumps(build_shema(payload)).decode("utf-8"),
                        "schemaEncoding": "jsonschema"
                    }
                )
                topic_dict[topic] = chan_id
            else:
                chan_id = topic_dict[topic]

            await server.send_message(chan_id, timestamp, orjson.dumps(payload))

if __name__ == "__main__":
    run_cancellable(main())      