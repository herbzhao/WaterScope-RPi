from celery import Celery
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

#~ while (True):
	#~ print (read_temp(temp_sensor_1))
	#~ print (read_temp(temp_sensor_2))
	#~ if read_temp(temp_sensor_1) < 37.5:
		#~ GPIO.output(17,False) ## Turn on GPIO pin 7
		#~ time.sleep(0.5)
		#~ print 'heating'
	#~ elif read_temp(temp_sensor_1) >= 37.5:
		#~ GPIO.output(17,True) ## Turn on GPIO pin 7
		#~ time.sleep(0.5)
		#~ print 'cooling'
#~ GPIO.cleanup()





#~ from IOT-RPi import RPiControl

app = Celery('tasks', backend='redis://localhost:6379', broker='redis://localhost:6379')


		
    
    
@app.task
def temp_loop(i,incubator):
	if i == 1:
		while True:  # a while loop to achieve what I want to do
			incubator.temp_control()

@app.task
def temp_control():
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

			
		

#~ app.conf.update(
    #~ CELERY_TASK_SERIALIZER='json',
    #~ CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    #~ CELERY_RESULT_SERIALIZER='json',
    #~ CELERY_ENABLE_UTC=True,
#~ )
#~ app.conf.update(
	#~ CELERYBEAT_SCHEDULE = {
		#~ 'add-every-1-seconds': {
			#~ 'task': 'tasks.count',
			#~ 'schedule': timedelta(seconds=1),
			#~ #'args': (16, 16)
			#~ 'args': [1]
		#~ },
	#~ }
#~ )


    
#~ @app.task
#~ def count(i):
	#~ if i == 1:  # turn on command
		#~ while True:  # a while loop to achieve what I want to do
			#~ i = i+1
			#~ return i
	#~ elif i == 0: # turn off command given by flask
		#~ return i
