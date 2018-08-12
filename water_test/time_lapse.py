#!/usr/bin/python3

from __future__ import division # this is how python3 do division
import time
import RPi.GPIO as GPIO
from picamera import PiCamera


# initialise the GPIO
GPIOPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIOPIN, GPIO.OUT)
GPIO.output(GPIOPIN, GPIO.LOW)

GPIO.output(GPIOPIN,GPIO.HIGH)
# initialise the camera
camera = PiCamera()
camera.resolution = (3280,2464)
#camera.shutter_speed = 25000
#camera.exposure_mode = 'off'

# time lapse settings in minutes 
time_interval = 20

while True:
	for i in range(1000): 
		filename = 'timelapse_{:03d}'.format(i)
		time_elapsed = i * time_interval
		GPIO.output(GPIOPIN, GPIO.HIGH)
		print('LED on')
		time.sleep(5)
		camera.capture(filename, format = 'jpeg', bayer = True)
		print('image taken: image number: {}, time elapsed: {:f}'.format(i, time_elapsed))
		time.sleep(5)
		GPIO.output(GPIOPIN, GPIO.LOW)
		print('LED off')
		
		time.sleep(time_interval*60)


