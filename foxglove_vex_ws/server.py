from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer
from json_schema import build_schema
from vex_serial import create_connection
import time
import logging
import orjson
import serial
import serial.serialutil

async def main():
    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        logger = logging.getLogger("FoxgloveServer")

        try:
            ser = create_connection()
        except serial.serialutil.SerialException:
            logger.error("Failed to connect. Zero or multiple devices connected.")
            return

        topic_dict = {}
        while True:
            timestamp = time.time_ns()

            try: 
                data = await ser.read()
            except serial.serialutil.SerialException:
                logger.error("Device disconnected.")
                break

            if data == b"foxglove\n":
                await server.reset_session_id(str(timestamp))
                continue
        
            try:
                json = orjson.loads(data)
            except orjson.JSONDecodeError:
                continue
            
            if ("topic" not in json or 
                "payload" not in json or 
                type(json["topic"]) is not str):
                logger.error("Incorrect message format (https://foxglove-vex-docs.vercel.app/connecting-to-data).")
                continue

            topic = json["topic"]
            payload = json["payload"]

            if topic not in topic_dict:
                channel_id = await server.add_channel(
                    {
                        "topic": topic,
                        "encoding": "json",
                        "schemaName": topic,
                        "schema": orjson.dumps(build_schema(payload)).decode("utf-8"),
                        "schemaEncoding": "jsonschema"
                    }
                )
                topic_dict[topic] = channel_id
            else:
                channel_id = topic_dict[topic]

            await server.send_message(channel_id, timestamp, orjson.dumps(payload))

if __name__ == "__main__":
    run_cancellable(main())