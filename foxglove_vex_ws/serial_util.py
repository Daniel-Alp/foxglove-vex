import asyncio
import serial
from cobs import cobs

def find_vex_port():
    pass 

async def pyserial_read_byte_wrapper(ser: serial.Serial):
    return ser.read(1)

async def read(ser: serial.Serial) -> str:
    raw_data = bytearray()
    while True:
        next = await pyserial_read_byte_wrapper(ser)
        if next == b'\0':
            break
        else:
            raw_data.extend(next)
    return cobs.decode(raw_data).decode("utf-8")[4:]

if __name__ == "__main__":
    pass