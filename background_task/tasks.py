#!/usr/bin/python
from celery import Celery
import subprocess
import time
import RPi.GPIO as GPIO


subprocess.Popen(["sudo","modprobe","w1-gpio"])
subprocess.Popen(["sudo","modprobe", "w1-therm"])



def temp_raw(sensor_location):
    f = open(sensor_location, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(sensor_location):

	lines = temp_raw(sensor_location)
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = temp_raw();
	temp_output = lines[1].find('t=')
	if temp_output != -1:
		temp_string = lines[1].strip()[temp_output+2:]
		temp_c = float(temp_string) / 1000.0
	return temp_c



#get the sensor location automatically
sensor_location = subprocess.check_output(["ls","/sys/bus/w1/devices/"])
sensor_location = sensor_location[0:15]
sensor_location = "/sys/bus/w1/devices/"+sensor_location+"/w1_slave"




# preperation celery worker
app = Celery('tasks', backend='redis://localhost:6379', broker='redis://localhost:6379')



@app.task
def temp_control(pin, incubate_temp):
	#set up GPIO using BCM numbering
	GPIO.setmode(GPIO.BCM)
	#GPIO.setwarnings(False)
	GPIO.setup(pin, GPIO.OUT) ## Setup GPIO Pin  to OUT
	time.sleep(0.2)
	while (True):
		print (read_temp(sensor_location))
		if read_temp(sensor_location) < incubate_temp:
			GPIO.output(pin,False) ## Turn on GPIO pin 7
			time.sleep(0.5)
			print 'heating'
		elif read_temp(sensor_location) >= incubate_temp:
			GPIO.output(pin,True) ## Turn on GPIO pin 7
			time.sleep(0.5)
			print 'cooling'
