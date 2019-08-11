import serial
import time

ser = serial.Serial('/dev/ttyS0')
while True:
    time.sleep(0.5)
    print(ser.readline())