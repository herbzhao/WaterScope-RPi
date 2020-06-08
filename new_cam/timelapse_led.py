import arducam_mipicamera as arducam
import v4l2 #sudo pip install v4l2
import time
import cv2 #sudo apt-get install python-opencv
import datetime
import yaml
import numpy as np
import threading

import cv2
import os
import datetime
from serial_communication import serial_controller_class, Arduinos
import yaml
import threading
import numpy as np


def align_down(size, align):
    return (size & ~((align)-1))

def align_up(size, align):
    return align_down(size + align - 1, align)

def set_controls(camera):
    try:
        print("Reset the focus...")
        camera.reset_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE)
    except Exception as e:
        print(e)
        print("The camera may not support this control.")

    try:
        print("Enable Auto Exposure...")
        camera.software_auto_exposure(enable = True)
        print("Enable Auto White Balance...")
        camera.software_auto_white_balance(enable = True)
    except Exception as e:
        print(e)


# NOTE: serial communication 
def initialise_serial_connection():
    ''' all the arduino connection is done via this function''' 
    try:
        # print(' serial connections already exist')
        Arduinos.serial_controllers
    except AttributeError:
        with open('config_serial.yaml') as config_serial_file:
            serial_controllers_config = yaml.load(config_serial_file)
        Arduinos.available_arduino_boards = []

        for board_name in serial_controllers_config:
            if serial_controllers_config[board_name]['connect'] is True:
                Arduinos.available_arduino_boards.append(board_name)

        print(Arduinos.available_arduino_boards)
        # initialise the serial port if it does not exist yet.
        #print('initialising the serial connections')
        Arduinos.serial_controllers = {}
        for name in Arduinos.available_arduino_boards:
            Arduinos.serial_controllers[name] = serial_controller_class()
            Arduinos.serial_controllers[name].serial_connect(
                port_address=serial_controllers_config[name]['port_address'],
                port_names=serial_controllers_config[name]['port_names'], 
                baudrate=serial_controllers_config[name]['baudrate'])
            Arduinos.serial_controllers[name].serial_read_threading(
                options=serial_controllers_config[name]['serial_read_options'], 
                parsers=serial_controllers_config[name]['serial_read_parsers'])

def send_serial(serial_command = "LED_ON"):
    initialise_serial_connection()
    Arduinos.serial_controllers['waterscope'].serial_write(serial_command, parser='waterscope')


if __name__ == "__main__":
    time_per_image_in_seconds = 2
    while True:
        time.sleep(time_per_image_in_seconds)
        break
    try:
        camera = arducam.mipi_camera()
        print("Open camera...")
        camera.init_camera()
        print("Setting the resolution...")
        fmt = camera.set_resolution(4656, 3496)
        print("Current resolution is {}".format(fmt))
        set_controls(camera)

        time.sleep(2)
        send_serial("LED_on")
        time.sleep(2)
        frame = camera.capture(encoding = 'jpeg')
        
        filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        frame.as_array.tofile("{}.jpg".format(filename))

        time.sleep(2)
        send_serial("LED_off")
        time.sleep(1)
        # Release memory
        del frame
        print("Close camera...")
        camera.close_camera()
    except Exception as e:
        print(e)
