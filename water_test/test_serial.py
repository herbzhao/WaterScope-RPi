import serial
import serial.tools.list_ports
import time
import sys
import threading

available_ports = list(serial.tools.list_ports.comports())
for port in available_ports:
    print(port)
    print(port[2])

    arduino_port = '/dev/ttyUSB0'


with serial.Serial(arduino_port,9600) as ser: #change ACM number as found from ls /dev/tty/ACM*
    ser.baudrate=9600
    # initialisation
    time.sleep(5)

    while True:
        line = ser.readline()
        print(line)
        time.sleep(5)
	print('turn on led')
	ser.write('66')
	time.sleep(5)
	print('moving up 1000')
	ser.write('-500')
	time.sleep(5)
	ser.write('-66')




        # For arduino, positive is move up
        #command = input('Enter your input:')
        #try:
            #ser.write('command')
            #print('moving now')
        #except:
        #    pass
    


