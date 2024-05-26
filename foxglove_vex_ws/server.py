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
        ser = serial.Serial('/dev/ttyACM1', baudrate=115200, timeout=1)

        while True:
            await asyncio.sleep(0.01)
            timestamp = time.time_ns()

            data = await read(ser)
            if data[:5].upper() != "DATA:":
                continue

            json = orjson.loads(data[5:])
            print(orjson.dumps(json, option=orjson.OPT_INDENT_2).decode("utf-8"))

if __name__ == "__main__":
    run_cancellable(main())      