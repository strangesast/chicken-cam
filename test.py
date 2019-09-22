import serial
import time

print('opening')
with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as ser:
    print('reading')
    print(ser.readline())
    print('writing')
    ser.write(b'1');
