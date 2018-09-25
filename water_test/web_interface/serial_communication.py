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
        self.starting_time = time.time()

    def time_logger(self):
        self.time_elapsed = '{:.1f}'.format(time.time() - self.starting_time)


    def connect_serial(self, port_names=['Serial', 'serial', 'SERIAL'], baudrate=9600, ):
        ''' automatically detect the Ardunio port and connect '''
        # Find Arduino serial port first
        available_ports = list(serial.tools.list_ports.comports())
        for port in available_ports:
            for name in port_names:
                if name in port[1]:
                    serial_port = port[0]
                    print('Serial port: '+ serial_port)

        # TODO: not sure whether this will cause problem, the with statement
        with serial.Serial() as self.ser:
            self.ser.port = serial_port
            self.ser.baudrate = baudrate
            # TODO: check the meaning of the time out
            self.ser.timeout = 1
            self.ser.flush()

    def send_arduino_command(self):
        ''' purly sending the serial information to arduino, the parsing is done in other methods '''
        self.ser.write('{} \n\r'.format(str(self.serial_command)).encode())

    def parsing_waterscope(self, serial_command):
        self.serial_command = serial_command
        if 'move' in serial_command:
            serial_command.
        pass


    def serial_read(self):
        while True:
        # only when serial is available to read
        # if ser.in_waiting:
            if self.ser.in_waiting:
                self.serial_output = self.ser.readline()
                print(self.serial_output)
    
    def serial_read_quiet(self):
        ''' read the serial output but not print it ''' 
        while True:
        # only when serial is available to read
        # if ser.in_waiting:
            if self.ser.in_waiting:
                self.serial_output = self.ser.readline()

    def serial_read_record(self):
        ''' read the serial output and log in a file for further analysis ''' 
        while True:
        # only when serial is available to read
        # if ser.in_waiting:
            if self.ser.in_waiting:
                serial_output = self.ser.readline()

                with open() as log_file:
                    pass

    
    def serial_read_threading(self, option='quite'):
        ''' used to start threading for '''
        if option == 'quiet':
            # now threading1 runs regardless of user input
            self.threading_ser_read = threading.Thread(target=self.serial_read_quiet)
        elif option == 'logging':
            self.threading_ser_read = threading.Thread(target=self.serial_read)
        else:
            self.threading_ser_read = threading.Thread(target=self.serial_read)

        self.threading_ser_read.daemon = True
        self.threading_ser_read.start()
        time.sleep(2)

#############################################
# code starts here
if __name__ == '__main__':
    serial_controller = serial_controller_class()
    serial_controller.serial_read_threading(quiet=False)

    while True:
        user_input = str(raw_input())
        serial_controller.send_arduino_command(user_input)