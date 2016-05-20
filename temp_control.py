import os
import time
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT) ## Setup GPIO Pin  to OUT

temp_sensor_1 = '/sys/bus/w1/devices/28-00042b6465ff/w1_slave'
temp_sensor_2 = '/sys/bus/w1/devices/28-00042b6579ff/w1_slave'

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

while (True):
	print (read_temp(temp_sensor_1))
	print (read_temp(temp_sensor_2))
	if read_temp(temp_sensor_1) < 37.5:
		GPIO.output(17,False) ## Turn on GPIO pin 7
		time.sleep(0.5)
		print 'heating'
	elif read_temp(temp_sensor_1) >= 37.5:
		GPIO.output(17,True) ## Turn on GPIO pin 7
		time.sleep(0.5)
		print 'cooling'
GPIO.cleanup()




