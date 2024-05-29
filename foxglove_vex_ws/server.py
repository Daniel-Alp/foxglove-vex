import time
import logging
import orjson
import serial
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer
import serial.serialutil
from json_util import build_shema
from serial_util import VexSerial

async def main():
    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        logger = logging.getLogger("FoxgloveServer")

        try:
            ser = VexSerial()
        except serial.serialutil.SerialException:
            logger.error("User port not found")
            return

        topic_dict = {}

        while True:
            timestamp = time.time_ns()

            try: 
                data = await ser.read_packet()
            except serial.serialutil.SerialException:
                logger.error("Device disconnected")
                break

            try:
                json = orjson.loads(data)
            except orjson.JSONDecodeError:
                continue

            if "topic" not in json or "payload" not in json:
                example = '{"topic": <string>, "payload": <JSON object>}'
                logger.error(f"Message does not follow format: {example}")
                continue

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