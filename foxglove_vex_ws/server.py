from foxglove_websocket.server import FoxgloveServer
from mcap.writer import Writer
from json_schema import build_schema
from vex_serial import create_connection, BaseConnection
import time
import asyncio
import signal
from typing import Any, Coroutine
from datetime import datetime
import logging
import orjson
import serial.serialutil

logger = logging.getLogger("FoxgloveServer")

async def main(ser: BaseConnection, writer: Writer):
    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        # map topic to channel id
        ws_channel_ids = {}
        mcap_channel_ids = {}

        while True:
            timestamp = time.time_ns()

            try: 
                data = await ser.read()
            except serial.serialutil.SerialException:
                logger.error("Device disconnected.")
                break

            if data == b"foxglove\n": # flag sent by robot to indicate new session
                # TODO create a new recording for each session
                await server.reset_session_id(str(timestamp))
                continue
        
            try:
                json = orjson.loads(data)
            except orjson.JSONDecodeError:
                continue

            print(data)
            
            if ("topic" not in json or 
                "payload" not in json or 
                type(json["topic"]) is not str):
                logger.error("Incorrect message format (https://foxglove-vex-docs.vercel.app/connecting-to-data).")
                continue

            topic = json["topic"]
            payload = json["payload"]

            if topic not in ws_channel_ids:
                schema = orjson.dumps(build_schema(payload))

                schema_id = writer.register_schema(
                    name=topic,
                    encoding="jsonschema",
                    data=schema
                )
                mcap_channel_id = writer.register_channel(
                    schema_id=schema_id,
                    topic=topic,
                    message_encoding="json"
                )
                mcap_channel_ids[topic] = mcap_channel_id

                ws_channel_id = await server.add_channel(
                    {
                        "topic": topic,
                        "encoding": "json",
                        "schemaName": topic,
                        "schema": schema.decode("utf-8"),
                        "schemaEncoding": "jsonschema"
                    }
                )
                ws_channel_ids[topic] = ws_channel_id
            else:
                ws_channel_id = ws_channel_ids[topic]

            writer.add_message(
                channel_id=mcap_channel_id,
                log_time=timestamp,
                data=orjson.dumps(payload),
                publish_time=timestamp
            )

            await server.send_message(
                ws_channel_id, 
                timestamp, 
                orjson.dumps(payload)
            )
def run():
    try:
        ser = create_connection()
    except serial.serialutil.SerialException:
        logger.error("Failed to connect. Zero or multiple devices connected.")
        return
    
    writer = Writer(f"recordings/{datetime.fromtimestamp(time.time())}.mcap")
    writer.start()

    loop = asyncio.get_event_loop()
    task = loop.create_task(main(ser, writer))
    try:
        loop.add_signal_handler(signal.SIGINT, task.cancel)
    except NotImplementedError:
        # signal handlers are not available on Windows, KeyboardInterrupt will be raised instead
        pass

    try:
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass

    writer.finish()

if __name__ == "__main__":
    run()