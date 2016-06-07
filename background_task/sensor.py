import subprocess
import time

subprocess.Popen(["modprobe","w1-gpio"])
subprocess.Popen(["modprobe", "w1-therm"])


#get the sensor location automatically
sensor_location = subprocess.check_output(["ls","/sys/bus/w1/devices/"])
sensor_location = sensor_location[0:15]
sensor_location = "/sys/bus/w1/devices/"+sensor_location+"/w1_slave"

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

while True:
        print(read_temp(sensor_location))
        time.sleep(0.2)


