import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
arduino_device_name = 'Linux'

for port in ports:
    if arduino_device_name in port[1]:
	arduino_port = port[0]

print(arduino_port)
	
