from __future__ import division

from picamera import PiCamera
import threading
import serial.tools.list_ports
import serial
import time
import datetime
import sys
import os
# read config from a txt file
from read_config import initialise_config



def send_arduino_command(ser, serial_command):
    # does not read ser yet
    print('command: {}'.format(serial_command))

    if 'move' in serial_command:
    # parse the string
        distance = serial_command.replace('move','').replace(' ','')
        print('arduino move {}'.format(distance))
        serial_command = distance

    ser.write('{} \n\r'.format(str(serial_command)).encode())

def serial_read_silent(ser):
    while True:
    # only when serial is available to read
    # if ser.in_waiting:
        if ser.in_waiting:
            serial_output = ser.readline()


def serial_read(ser):
    while True:
    # only when serial is available to read
    # if ser.in_waiting:
        if ser.in_waiting:
            serial_output = ser.readline()
            # disable the print for now 
            print(serial_output)



def connect_serial():

    # Find Arduino serial port first
    available_ports = list(serial.tools.list_ports.comports())

    for port in available_ports:
        print(port[0])
        print(port[1])
        if 'Linux' in port[1] or 'Serial' in port[1]:
            arduino_port = port[0]
            print('Arduino port: '+ arduino_port)

    #arduino_port = '/dev/ttyUSB0'
    print('Initialisation of the stage. \n Waiting for the temperature reading to show up. \n Then you can type the command \n')
    #with serial.Serial(arduino_port,9600) as ser: #change ACM number as found from ls /dev/tty/ACM*
    ser = serial.Serial(arduino_port, 9600)
    ser.baudrate=9600
    ser.flush()

    return ser



#############################################
# code starts here
if __name__ == '__main__':

        
    ser = connect_serial()

    # now threading1 runs regardless of user input
    threading1 = threading.Thread(target=serial_read, args=[ser])
    threading1.daemon = True
    threading1.start()

    while True:
        user_input = str(raw_input())
        send_arduino_command(ser, user_input)