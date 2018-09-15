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

'''
To run the code, use 
$ python focus_and_timelapse.py
then type number for stage movement, 66/-66 for LED and tl for timelapse

To run the code for timelapse in background direclty
$ nohup python focus_and_timelapse.py tl &
'''


def temperature_reading():
    global ser
    global starting_time
    while True:
        temperature_log = open('/home/pi/WaterScope-RPi/water_test/timelapse/{}/{}.txt'.format(starting_time, starting_time), 'a+')        
        
        # clear the inputs and read the two lines, now it doenst care about sync problem
        ser.flushInput()
        for i in range(2):
            serial_output = ser.readline()
            print(serial_output)
            temperature_log.writelines(serial_output)
        temperature_log.close()
        time.sleep(10)
    
def send_arduino_command(user_input):
    # does not read ser yet
    global ser
    ser.write(user_input)
    print('command: {}'.format(user_input))


def start_time_lapse(time_interval=10):       
    global ser
    # initialise the camera
    camera = PiCamera()
    camera.resolution = (3280,2464)
    print('start timelapse')

    # read configs for consistent imaging
    config = initialise_config()
    config.read_config_file()
    camera.awb_mode = config.awb_mode
    camera.awb_gains = config.awb_gains
    camera.iso = config.iso
    camera.shutter_speed = config.shutter_speed
    camera.saturation = config.saturation


    while True:
        for i in range(1000): 
            print('timelapse_{}th_cycle'.format(i))
            filename = '/home/pi/WaterScope-RPi/water_test/timelapse/{}/timelapse_{:03d}.jpg'.format(starting_time, i)
            # time_elapsed = i * time_interval
            # turn on the LED by serial code
            ser.flush()
            send_arduino_command('66')
            print('LED on')
            time.sleep(10)
            # take photo
            camera.capture(filename, format = 'jpeg', bayer = True)
            print('image taken: image number: {}'.format(i))
            time.sleep(15)
            # turn off the LED by serial code
            ser.flush()
            send_arduino_command('-66')
            print('LED off')

            time.sleep(time_interval*60)

#############################################
# code starts here

# Save the temperature log to a file with datetime
starting_time = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
# make a directory in case previously didnt exist
os.mkdir('/home/pi/WaterScope-RPi/water_test/timelapse')
os.mkdir('/home/pi/WaterScope-RPi/water_test/timelapse/{}'.format(starting_time))

# Find Arduino serial port first
available_ports = list(serial.tools.list_ports.comports())

for port in available_ports:
    if 'Linux' in port[1]:
        arduino_port = port[0]
        print('Arduino port: '+ arduino_port)

#arduino_port = '/dev/ttyUSB0'
print('Initialisation of the stage. \n Waiting for the temperature reading to show up. \n Then you can type the command \n')
with serial.Serial(arduino_port,9600) as ser: #change ACM number as found from ls /dev/tty/ACM*
    ser.baudrate=9600
    ser.flush()

    # now threading1 runs regardless of user input
    threading1 = threading.Thread(target=temperature_reading)
    threading1.daemon = True
    threading1.start()

    # if there is any additional sys.arg, then start time lapse automatically
    if len(sys.argv) > 1:
        time.sleep(5)
        start_time_lapse(time_interval=5)

    # if run the code without arg, just do the traditional thing
    else:
        while True:
            #print('type the distance whenever you want')
            # python 2.7 raw_input
            user_input = str(raw_input())
            if user_input == 'tl':
                start_time_lapse(time_interval=20/60)
            else:
                send_arduino_command(user_input)
            print(user_input)




