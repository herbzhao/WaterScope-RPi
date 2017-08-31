from __future__ import print_function
import sweep
import picamera

import scipy.signal

class Autofocus():
	def __init__(self):
		pass

	def autofocus(self):
		# sweep and move to max fm angle
		with picamera.PiCamera() as camera:
		    angles = range(1, 159, 1)
		    fms = sweep.sweep(angles, camera, (640, 480))
		max_angle = angles[fms.index(max(scipy.signal.medfilt(fms)))]
		sweep.move(max_angle)
		print('autofocused at %d degrees' % max_angle)
