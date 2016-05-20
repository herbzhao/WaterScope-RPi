from tasks import temp_control
from IOT_RPi import RPiControl


incubator = RPiControl(17, '/sys/bus/w1/devices/28-00042b6465ff/w1_slave',\
				37.5)
				
				
incubator.set_pin()

task = temp_loop.delay(1,incubator)


