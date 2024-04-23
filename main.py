import serial

ser = serial.Serial('/dev/ttyACM1', baudrate=115200, timeout=1)

while True:
    data = ser.readline()[6:].decode('utf-8')
    print(data, end='')