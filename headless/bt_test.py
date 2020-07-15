import serial
import base64
import time
import os
import signal
import subprocess

time.sleep(1)
#serial.Serial('/dev/rfcomm0', 1000000).close()

print('continuing')
#subprocess.call(['sudo', 'rfcomm', 'watch', 'hci0'])

def read_bluetooth():
    eol = b'$\n'
    leneol = len(eol)
    line = bytearray()
    while True:
        c = ser.read(1)
        if c:
            line += c
            if line[-leneol:] == eol:
                break
        else:
            break
    return bytes(line[:-leneol])
ser = serial.Serial('/dev/rfcomm0', 1000000)
ser.close()
ser = serial.Serial('/dev/rfcomm0', 1000000)
print('paired')    
ser.write('connected$\n'.encode("utf-8"))
ser.write('version=1.0$\n'.encode("utf-8"))
ser.write('temp=37.21$\n'.encode("utf-8"))
ser.write('inc_time=1000$\n'.encode("utf-8"))

with open("foo.jpg", "rb") as imageFile:
     text = base64.b64encode(imageFile.read())
while True:
    result = read_bluetooth().decode("utf-8")
    print(result)
    if ((result) == 'sample_preview'):
        ser.write('preview=data:image/png;base64,'.encode("utf-8"))
        ser.write(text)
        ser.write('$\n'.encode("utf-8"))
        print('image sent')
    if ((result) == 'full_analysis'):
        ser.write('coliform=15,ecoli=23$\n'.encode("utf-8"))
        print('commencing full analysis')
        #print(text)
    if ((result) == 'incubator_off'):
        ser.write('Incubator off$\n'.encode("utf-8"))
    if ((result) == 'incubator_37'):
        ser.write('Incubator started at 37C $\n'.encode("utf-8"))
    if ((result) == 'incubator_44'):
        ser.write('Incubator started at 44C $\n'.encode("utf-8"))           


