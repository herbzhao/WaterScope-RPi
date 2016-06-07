import time
import RPi.GPIO as GPIO


#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT) ## Setup GPIO Pin  to OUT
GPIO.output(17,False) ## Turn on GPIO pin 7
#time.sleep(0.5)
print 'heating'
		

#GPIO.cleanup()
