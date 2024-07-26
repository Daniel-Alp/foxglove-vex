from abc import ABCMeta, abstractmethod
from collections import deque
from cobs import cobs
import time
import serial
import serial.tools
import serial.tools.list_ports

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
        try:
            return cobs.decode(data)[4:]        
        except cobs.DecodeError:
            return bytes()

class WirelessConnection(BaseConnection):
    def __init__(self, ser: serial.Serial):
        super().__init__(ser)
        
        change_channel_request = bytes([0xc9, 0x36, 0xb8, 0x47, 0x56, 0x10, 0x02, 0x01, 0x01, 0xa9, 0x48])
        self.ser.write(change_channel_request)
        time.sleep(2)
        self.ser.read_all()

        self.all_data = deque()

    def read(self) -> bytes:
        data = bytearray()
        read_request = bytes([0xc9, 0x36, 0xb8, 0x47, 0x56, 0x27, 0x02, 0x01, 0x00, 0xc4, 0xad])
        while True:
            while len(self.all_data) > 0:
                next = self.all_data.popleft()
                if next == 0x00:
                    try:
                        return cobs.decode(data)[4:]
                    except cobs.DecodeError:
                        return bytes()
                elif next:
                    data.append(next)

            self.ser.write(read_request)

            metadata = self.ser.read(3) # Header bytes and ID byte
            if metadata != bytes([0xaa, 0x55, 0x56]):
                self.ser.read_all()
                continue

            size = int.from_bytes(self.ser.read(), 'little') # Size sent in either 2 or 1 bytes
            if size & 0x80 == 0x80:
                size &= 0x7f
                size <<= 7
                size += int.from_bytes(self.ser.read(), 'little')
        
            payload = self.ser.read(size) # Extended ID byte, acknowledge byte, channel byte, new data bytes, checksum bytes
            if payload[0] != 0x27 or payload[1] != 0x76:
                self.ser.read_all()
                continue

            self.all_data.extend(payload[3:-2])

def create_connection() -> BaseConnection:
    ports = serial.tools.list_ports.comports()
    ports = [p for p in ports if p.vid == 0x2888] # VEX vendor ID

    # A controller will show up as one port.
    controller_ports = [p for p in ports if p.location.endswith("1")]

    # A brain will show up as two ports, the user and communication port.
    # User port is for reading from the robot's stdio.
    brain_user_ports = [p for p in ports if p.location.endswith("2")]

    ports = controller_ports + brain_user_ports

    if len(ports) != 1:
        raise serial.SerialException

    port = ports[0]
    direct_connection = port.location.endswith("2")

    ser = serial.Serial(port=port.device,
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1)
    
    if direct_connection:
        return DirectConnection(ser)
    else:
        return WirelessConnection(ser)

if __name__ == "__main__":
    try:
        connection = create_connection()
        while True:
            print(connection.read().decode("utf-8"))
    except serial.SerialException:
        print("Failed to connect. Zero or multiple devices connected.")