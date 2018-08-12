import serial
import time
import sys

available_ports = list(serial.tools.list_ports.comports())
for port in available_ports():
    pass



ser=serial.Serial(arduino_port,9600)  #change ACM number as found from ls /dev/tty/ACM*
ser.baudrate=9600

# wait for 2 sec and move up and down in the beginnging to confirm the connection
time.sleep(2)
# For arduino, positive is move up
ser.write('1000')
# move down
ser.write('-1000')


while True:
    command = input('Enter your input:')
    if command == 'exit' or 'Exit' :
        sys.exit()
    else:
        try:
            ser.write('command')
        except:
            pass
