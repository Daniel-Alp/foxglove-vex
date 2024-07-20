from abc import ABCMeta, abstractmethod
from cobs import cobs
import serial
import serial.tools
import serial.tools.list_ports

import time

class BaseConnection(object, metaclass=ABCMeta):
    def __init__(self, ser: serial.Serial):
        self.ser = ser

    # Read until delimiter \x00 and return bytes
    @abstractmethod
    def read(self) -> bytes:
        raise NotImplementedError

class DirectConnection(BaseConnection):
    def read(self) -> bytes:
        data = bytearray()
        while True:
            next = self.ser.read()
            if next == b'\x00':
                break
            data.extend(next)
        return cobs.decode(data)        

def create_connection() -> BaseConnection:
    # TODO instead of specifying port find it automatically
    pass


class WirelessConnection(BaseConnection):
    def read(self) -> bytes:                       
        return bytes()

if __name__ == "__main__":
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(port)

    ser = serial.Serial(port="/dev/ttyACM0",
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1)
    
    transfer_channel_request = bytes([0xc9, 0x36, 0xb8, 0x47, 0x56, 0x10, 0x02, 0x01, 0x01, 0xa9, 0x48])

    ser.write(transfer_channel_request)
    time.sleep(1)
    response = ser.read_all()

    read_request = bytes([0xc9, 0x36, 0xb8, 0x47, 0x56, 0x27, 0x02, 0x01, 0x00, 0xc4, 0xad])
        
    while True:
        ser.write(read_request)

        header = ser.read(2)
        id = ser.read()

        size = int.from_bytes(ser.read(), 'little') 
        if size & 0x80 == 0x80:
            size &= 0x7f
            size <<= 7
            size += int.from_bytes(ser.read(), 'little')
    
        payload = ser.read(size)

        if size > 5:
            print("header", header.hex())
            print("id", id.hex())
            print("payload", payload)
            print("="*150)
