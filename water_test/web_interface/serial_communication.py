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


class serial_controller_class():
    def __init__(self):
        self.connect_serial()

    def connect_serial(self):

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
        self.ser = serial.Serial(arduino_port, 9600)
        self.ser.baudrate=9600
        self.ser.flush()

    def send_arduino_command(self, serial_command):
        # does not read ser yet
        #print('command: {}'.format(serial_command))

        if 'move' in serial_command:
        # parse the string
            distance = serial_command.replace('move','').replace(' ','')
            # print('arduino move {}'.format(distance))
            serial_command = distance

        self.ser.write('{} \n\r'.format(str(serial_command)).encode())


    def serial_read(self):
        while True:
        # only when serial is available to read
        # if ser.in_waiting:
            if self.ser.in_waiting:
                serial_output = self.ser.readline()
                # disable the print for now 
                print(serial_output)
    
    def serial_read_quiet(self):
        while True:
        # only when serial is available to read
        # if ser.in_waiting:
            if self.ser.in_waiting:
                serial_output = self.ser.readline()

    
    def serial_read_threading(self, quiet=True):
        ''' used to start threading for '''
        if quiet is True:
            # now threading1 runs regardless of user input
            self.threading1 = threading.Thread(target=self.serial_read_quiet)
        else:
            self.threading1 = threading.Thread(target=self.serial_read)

        self.threading1.daemon = True
        self.threading1.start()
        time.sleep(2)

#############################################
# code starts here
if __name__ == '__main__':

        
    serial_controller = serial_controller_class()
    serial_controller.serial_read_threading(quiet=False)

    while True:
        user_input = str(raw_input())
        serial_controller.send_arduino_command(user_input)