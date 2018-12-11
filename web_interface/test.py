import serial
import time

with serial.Serial() as ser:
    ser.baudrate = 9600
    ser.port = '/dev/ttyUSB0'
    ser.open()
    while True:
        if ser.in_waiting:
        # time.sleep(0.5)
            print(ser.readline())