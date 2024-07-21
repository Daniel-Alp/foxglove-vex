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
    time.sleep(2)
    response = ser.read_all()
    print(response)

    all_data = bytearray()

    read_request = bytes([0xc9, 0x36, 0xb8, 0x47, 0x56, 0x27, 0x02, 0x01, 0x00, 0xc4, 0xad])        
    try:
        while True:
            delimeter_index = all_data.find(0x00)
            if delimeter_index != -1:
                try:
                    print(cobs.decode(all_data[:delimeter_index]).decode("utf-8"))
                except cobs.DecodeError:
                    print("failed to decode")
                all_data = all_data[delimeter_index:]
                all_data.pop(0)
                continue

            ser.write(read_request)

            header = ser.read(2)

            if header != bytes([0xaa, 0x55]):
                ser.read_all()
                continue

            id = ser.read()

            if id != bytes([0x56]):
                ser.read_all()
                continue

            size = int.from_bytes(ser.read(), 'little') 
            if size & 0x80 == 0x80:
                size &= 0x7f
                size <<= 7
                size += int.from_bytes(ser.read(), 'little')
        
            payload = ser.read(size)

            extended_id = payload[0]
            acknowledge = payload[1]
            data = payload[3:-2]

            all_data.extend(data)

    except KeyboardInterrupt:
        time.sleep(1)
        ser.read_all()