import serial
from cobs import cobs

def find_vex_port():
    pass 

def read(ser: serial.Serial) -> str:
    raw_data = bytearray()
    while True:
        next = ser.read(1)
        if next == b'\0':
            break
        else:
            raw_data.extend(next)
    return cobs.decode(raw_data).decode("utf-8")[4:]

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyACM1', baudrate=115200, timeout=1)

    while True:
        print(read(ser))