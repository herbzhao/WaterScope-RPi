from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import os
import datetime
# Richard's fix gain
from set_picamera_gain import set_analog_gain, set_digital_gain
from serial_communication import serial_controller_class, Arduinos
import yaml

import numpy as np



while __name__ == "__main__":
    serial_controller = serial_controller_class()
    serial_controller.serial_connect(port_address='/dev/ttyS0', baudrate=9600)
    #serial_controller.serial_connect(port_names=['Micro'], baudrate=115200)
    serial_controller.serial_read_threading(options=['logging'], parsers=['waterscope_motor', 'temperature'])

    # accept user input
    while True:
        user_input = str(input())
        serial_controller.serial_write(user_input, 'waterscope')
