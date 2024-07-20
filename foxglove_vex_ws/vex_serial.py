from abc import ABCMeta, abstractmethod
from cobs import cobs
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

# Connected to brain
class DirectConnection(BaseConnection):
    # For direct connection read from User Port
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
    
    # command to request to read from stdio (hardcoded because I only need this command)
    # 
    # 0xc9, 0x36, 0xb8, 0x47 header for device-bound message
    # 0x56                   command ID
    # 0x27                   extended command ID
    # 0x02                   payload size
    # 0x01                   channel 
    # 0x00                   write length (0x56 0x27 is also used as a write command)
    # 0xc4, 0xad             CRC-16-CCITT checksum
    read_command = bytes([0xc9, 0x36, 0xb8, 0x47, 0x56, 0x27, 0x02, 0x01, 0x00, 0xc4, 0xad])

    ser.write(read_command)
    while True:
        next = ser.read()
        print(next)
