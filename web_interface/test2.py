import requests
import time

URL = "http://localhost:5000/" 
while True:
    time.sleep(0.5)
    waterscope_motor_status_url = "http://10.0.0.1:5000/waterscope_motor_status"
    waterscope_motor_status = requests.get(waterscope_motor_status_url).json()
    print(waterscope_motor_status)
    print(type(waterscope_motor_status))
    print(waterscope_motor_status['motor_idle'])

