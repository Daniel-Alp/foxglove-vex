import asyncio
import serial
from cobs import cobs

class VexSerial:
    def __init__(self):
        # In the future, needs to automatically find the port that the device is connected to
        self.ser = serial.Serial('/dev/ttyACM1', baudrate=115200, timeout=0.01)

    async def read_packet(self) -> str:
        raw_data = bytearray()
        while True:
            next = self.ser.read(1)
            if next == b'\0':
                break
            else:
                raw_data.extend(next)
            await asyncio.sleep(0)
        return cobs.decode(raw_data).decode("utf-8")[4:]

if __name__ == "__main__":
    pass