#!/usr/bin/python
import subprocess
import time


subprocess.Popen(["sudo","rm","-r","w1.log"])
subprocess.Popen(["sudo","rm","-r","w1.pid"])
subprocess.Popen(["sudo","rm","-r","dump.rdb"])



subprocess.Popen(["redis-server"])


#subprocess.Popen(["celery","multi","start", "w1", "-A", "tasks" ,"-l" ,"info"])

subprocess.Popen(["celery","multi","start", "w1", "-A", "tasks" ,"-l" ,"info"],cwd="/var/www/html/")

#subprocess.Popen(["celery","-A","/var/www/html/tasks","worker", "-l", "info"],cwd="/var/www/html/")

#subprocess.Popen(["celery","-A","tasks","worker", "-l", "info"],cwd = "/var/www/html/")




#subprocess.call(["celery","multi","stop", "w1", "-A", "tasks" ,"-l" ,"info"])


#time.sleep(3)

#from tasks import temp_control

#result = temp_control.delay(17,37)

#import tasks from path
from sys import path
path.append('/var/www/html/')
from tasks import temp_control
time.sleep(0.5)
result = temp_control.delay(17,37)

time.sleep(5)

#time.sleep(10)
