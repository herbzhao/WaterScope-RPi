import threading
import serial.tools.list_ports
import serial
import time
import datetime
import sys


def temperature_reading():
    global ser
    global file_name
    while True:
        #ser.flush()
        serial_output = ser.readline()
        print(serial_output)
        time.sleep(2)
        # Save the temperature log to a file with datetime
        temperature_log.writelines(serial_output)
        temperature_log.close()
    
def send_arduino_commend(user_input):
    global ser
    ser.write(user_input)
    print('command: {}'.format(user_input))


# code starts here
file_name = str(datetime.datetime.now())
temperature_log = open('/home/pi/temperature_log/{}.txt'.format(file_name), 'a+')


# Find Arduino serial port first
available_ports = list(serial.tools.list_ports.comports())

for port in available_ports:
    if 'Linux' in port[1]:
        arduino_port = port[0]
        print('Arduino port: '+arduino_port)

#arduino_port = '/dev/ttyUSB0'
print('Initialisation of the stage. \n Waiting for the temperature reading to show up. \n Then you can type the command')
with serial.Serial(arduino_port,9600) as ser: #change ACM number as found from ls /dev/tty/ACM*
    ser.baudrate=9600
    ser.flush()

    # now threading1 runs regardless of user input
    threading1 = threading.Thread(target=temperature_reading)
    threading1.daemon = True
    threading1.start()

    while True:
        #print('type the distance whenever you want')
        # python 2.7 raw_input
        user_input = str(raw_input())
        send_arduino_commend(user_input)