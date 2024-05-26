import asyncio
import serial
from cobs import cobs

def find_vex_port():
    pass 

async def read(ser: serial.Serial) -> str:
    raw_data = bytearray()
    while True:
        next = ser.read(1)
        if next == b'\0':
            break
        else:
            raw_data.extend(next)
        await asyncio.sleep(0)
    return cobs.decode(raw_data).decode("utf-8")[4:]

if __name__ == "__main__":
    pass