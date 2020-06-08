import arducam_mipicamera as arducam
import v4l2 #sudo pip install v4l2
import time
import cv2 #sudo apt-get install python-opencv

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
        # print("set exposure manually")
        # camera.write_sensor_reg(0x020E, 3)
        # camera.write_sensor_reg(0x0214, 3)
        # camera.set_control(v4l2.V4L2_CID_EXPOSURE, 10e6)

        print("Enable Auto White Balance...")
        camera.software_auto_white_balance(enable = True)

    except Exception as e:
        print(e)


def measure_focus(image):
    focus_value = cv2.Laplacian(image, cv2.CV_64F).var()
    focus_text = 'f: {:.2f}'.format(focus_value)
    # CV font
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(
        image, focus_text,
        (int(image.shape[0]*0.1), int(image.shape[1]*0.1)), 
        font, 2, (0, 0, 255))

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
    R_value = G_value = B_value = 20
    try:
        camera = arducam.mipi_camera()
        print("Open camera...")
        camera.init_camera()
        print("Setting the resolution...")
        fmt = camera.set_resolution(1920, 1080)
        print("Current resolution is {}".format(fmt))
        set_controls(camera)
        while True:
            frame = camera.capture(encoding = 'i420')
            height = int(align_up(fmt[1], 16))
            width = int(align_up(fmt[0], 32))
            image = frame.as_array.reshape(int(height * 1.5), width)
            image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
            height = image.shape[0]/2
            width = image.shape[1]/2
            # downsize a bit
            image = cv2.resize(image, (width, height ))
            measure_focus(image)

            key = cv2.waitKey(1) & 0xFF

            cv2.imshow("Arducam", image)

            if key == ord("q"):
                # Release memory
                del frame
                print("Close camera...")
                camera.close_camera()
                cv2.destroyAllWindows()
                break
            
            elif key == ord("["):
                R_value = G_value = B_value = B_value - 10
                send_serial('LED_RGB={},{},{}'.format(R_value, G_value, B_value))
            elif key == ord("]"):
                R_value = G_value = B_value = B_value + 10
                send_serial('LED_RGB={},{},{}'.format(R_value, G_value, B_value))
            elif key == ord("o"):
                send_serial("LED_on")
            elif key == ord("f"):
                send_serial("LED_off")
            elif key == ord("c"):
                camera.set_resolution(4656, 3496)
                set_controls(camera)
                frame = camera.capture(encoding = 'jpeg')
                filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                frame.as_array.tofile("{}.jpg".format(filename))
                camera.set_resolution(1920, 1080)
                set_controls(camera)

    except Exception as e:
        print(e)
