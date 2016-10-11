import os
import time
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT) ## Setup GPIO Pin  to OUT

temp_sensor = '/sys/bus/w1/devices/28-00042b6579ff/w1_slave'


l = open('temp_log', 'w')
l.write("begin of log")
l.write("\n")
l.close()
    

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def temp_log():
    l = open('temp_log', 'a')
    l.write("%s"  %(read_temp()))
    l.write("\n")
    l.close()


def read_temp():
	lines = temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = temp_raw();
	temp_output = lines[1].find('t=')
	if temp_output != -1:
		temp_string = lines[1].strip()[temp_output+2:]
		temp_c = float(temp_string) / 1000.0
	return temp_c


while (True):
	print (read_temp())
	temp_log()
	if read_temp() < 37:
		GPIO.output(17,False) ## Turn on GPIO pin 7
		time.sleep(0.5)
		print 'heating'
	elif read_temp() >= 37:
		GPIO.output(17,True) ## Turn on GPIO pin 7
		time.sleep(0.5)
		print 'cooling'

GPIO.cleanup()
