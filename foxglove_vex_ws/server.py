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

def invalid_json(json: Any) -> bool:
    return ("topic" not in json or 
            "payload" not in json or 
            type(json["topic"]) is not str)

def add_mcap_channel(writer: Writer, topic: str, schema_bytes: bytes, mcap_channel_ids: dict[str, int]):
    schema_id = writer.register_schema(
        name=topic,
        encoding="jsonschema",
        data=schema_bytes
    )
    mcap_channel_ids[topic] = writer.register_channel(
        schema_id=schema_id,
        topic=topic,
        message_encoding="json"
    )

async def add_ws_channel(server: FoxgloveServer, topic: str, schema_bytes: bytes, ws_channel_ids: dict[str, int]):
    ws_channel_ids[topic] = await server.add_channel(
        {
            "topic": topic,
            "encoding": "json",
            "schemaName": topic,
            "schema": schema_bytes.decode("utf-8"),
            "schemaEncoding": "jsonschema"
        }
    )

async def live_connection(ser: BaseConnection, writer: Writer):
    async with FoxgloveServer("0.0.0.0", 8765, "foxglove-vex-bridge") as server:
        # Map topic to channel ID
        ws_channel_ids = {}
        mcap_channel_ids = {}

        while True:
            timestamp = time.time_ns()

            try: 
                message = await ser.read()
            except serial.serialutil.SerialException:
                logger.error("Device disconnected.")
                break

            if message == b"foxglove\n": # Flag to indicate new session
                await server.reset_session_id(str(timestamp))
                continue
        
            try:
                json = orjson.loads(message)
            except orjson.JSONDecodeError:
                continue
            
            if invalid_json(json):
                logger.error("Incorrect message format (https://foxglove-vex-docs.vercel.app/connecting-to-data).")
                continue

            topic = json["topic"]
            payload = json["payload"]

            payload_bytes = orjson.dumps(payload)

            if topic not in ws_channel_ids:
                schema_bytes = orjson.dumps(build_schema(payload))
                add_mcap_channel(writer, topic, schema_bytes, mcap_channel_ids)
                await add_ws_channel(server, topic, schema_bytes, ws_channel_ids)                     

            writer.add_message(
                channel_id=mcap_channel_ids[topic],
                log_time=timestamp,
                data=payload_bytes,
                publish_time=timestamp
            )
            await server.send_message(
                ws_channel_ids[topic], 
                timestamp, 
                payload_bytes
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
    task = loop.create_task(live_connection(ser, writer))
    
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