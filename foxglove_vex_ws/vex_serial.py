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
    pass

# TODO create WirelessConnection subclsas

if __name__ == "__main__":
    # ports = serial.tools.list_ports.comports()
    # for port in ports:
    #     print(port)

    ser = serial.Serial(port="/dev/ttyACM1",
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1)

    connection = DirectConnection(ser)
    while True:
        data = connection.read()
        print(data.decode("utf-8"))
