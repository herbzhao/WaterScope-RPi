from __future__ import division

import io
import time
import datetime
import sys
import os
import picamera


# custom library
from base_camera import BaseCamera
from read_config import initialise_config


from threading import Condition




class Camera(BaseCamera):

    @classmethod
    def initialisation(cls):
        cls.i = 0
        cls.starting_time = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        os.mkdir('/home/pi/WaterScope-RPi/water_test/timelapse/{}'.format(cls.starting_time))
    
    @staticmethod
    def frames(cls):
        # run this initialisation method
        cls.initialisation()

        with picamera.PiCamera() as cls.camera:
            # let camera warm up
            time.sleep(2)
            fps = 24
            cls.camera.resolution = (1640, 1232)

            cls.camera.framerate = fps
            # read configs
            cls.read_camera_setting()

            # streaming
            cls.stream = io.BytesIO()
            cls.camera.start_recording(cls.stream, format='mjpeg')

            # this is required otherwise it may bug out
            time.sleep(2)

            while True:
                # reset stream for next frame
                cls.stream.seek(0)
                cls.stream.truncate()
                # to stream, read the new frame
                # it has to generate frames faster than displaying the frames, otherwise some random bug will occur
                time.sleep(1/(fps*0.8))
                # yield the result to be read
                yield cls.stream.getvalue()


    @classmethod
    def read_camera_setting(cls):
        # consistent imaging condition
        config = initialise_config()
        config.read_config_file()
        
        cls.camera.awb_mode = config.awb_mode
        cls.camera.awb_gains = config.awb_gains
        cls.camera.iso = config.iso
        cls.camera.shutter_speed = config.shutter_speed
        cls.camera.saturation = config.saturation

    
    @classmethod
    def take_image(cls):
            # when taking photos, increase the resolution and everything
            # need to stop the video channel first
            cls.camera.stop_recording()
            cls.camera.resolution = (3280,2464)
            filename = '/home/pi/WaterScope-RPi/water_test/timelapse/{}/timelapse_{:03d}.jpg'.format(Camera.starting_time, Camera.i)
            print('taking image')
            #cls.camera.capture(filename, format = 'jpeg', bayer = True)
            cls.camera.capture(filename, format = 'jpeg', quality=100)

            # reduce the resolution for video streaming
            cls.camera.resolution = (1640, 1232)
            # resume the video channel
            cls.camera.start_recording(cls.stream, format='mjpeg')
            # give some time for image to be taken
            time.sleep(0.5)

            cls.i = cls.i + 1




