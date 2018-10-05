# picamera test
import picamera
import time

camera = picamera.PiCamera()
try:
#    camera.resolution=(1920,900)
    camera.resolution=(3280,2464)
    camera.still_stats = False
#    camera.resolution= '720p'
    camera.start_preview()
    camera.awb_mode = 'off' 
    camera.awb_gains = (1,1.2)
    camera.flash_mode = 'off'
    camera.drc_strength = 'off'
#    camera.exposure_mode = 'off'
    
#    camera.still_stats = True

    camera.meter_mode = 'spot'
    camera.brightness = 40

    while True:
        time.sleep(1)
        print('awb:',camera.awb_gains)
        print('camera_exposure_compensation:',camera.exposure_compensation)
	print('digital_gain:', camera.digital_gain)
	print('analog_gain:',camera.analog_gain)
	print('brightness:',camera.brightness)
	print('ISO:',camera.iso)

finally:
    camera.close()
