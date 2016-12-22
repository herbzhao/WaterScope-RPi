# picamera test
import picamera
import time

camera = picamera.PiCamera()
try:
    camera.start_preview()
    camera.resolution = (2560, 1440)
    time.sleep(5)
finally:
    camera.close()
