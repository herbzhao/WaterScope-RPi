import time
import RPi.GPIO as GPIO


#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT) ## Setup GPIO Pin  to OUT
#time.sleep(0.5)

GPIO.output(17,True) ## Turn on GPIO pin 7
print 'cooling'
		

#GPIO.cleanup()
