
import RPi.GPIO as GPIO

import time

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT) ## Setup GPIO Pin  to OUT

while (True):
	GPIO.output(17,False) ## Turn on GPIO pin 7
	time.sleep(10)
	GPIO.output(17,True) ## Turn on GPIO pin 7
	time.sleep(10)

GPIO.cleanup()


