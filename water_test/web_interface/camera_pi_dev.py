from __future__ import division

import io
import time
import datetime
import sys
import os
import picamera
# DEBUG: is this neccessary?
# from threading import Condition
import threading
import yaml

# custom library
from base_camera import BaseCamera
# Richard's fix gain
from set_picamera_gain import set_analog_gain, set_digital_gain


class Camera(BaseCamera):
    @classmethod
    def initialisation(cls):
        cls.image_seq = 0
        cls.fps = 30
        cls.stream_resolution = (1648,1232)
        cls.image_resolution = (3280,2464)
        cls.starting_time = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        os.mkdir('/home/pi/WaterScope-RPi/water_test/timelapse/{}'.format(cls.starting_time))


    @classmethod
    def update_camera_setting(cls, camera):
        with open('config.yaml') as config_file:
            config = yaml.load(config_file)
            # consistent imaging condition
            camera.awb_mode = config['awb_mode']
            camera.awb_gains = (config['red_gain'], config['blue_gain'])
            # Richard's library to set analog and digital gains
            set_analog_gain(camera, config['analog_gain'])
            set_digital_gain(camera, config['digital_gain'])
            camera.shutter_speed = config['shutter_speed']
            camera.saturation = config['saturation']
            camera.led = False

    
    @classmethod
    def take_image(cls, camera):
        # when taking photos, increase the resolution and everything
        # need to stop the video channel first
        camera.stop_recording()
        camera.resolution = cls.image_resolution
        filename = '/home/pi/WaterScope-RPi/water_test/timelapse/{}/timelapse_{:03d}.jpg'.format(Camera.starting_time, cls.image_seq)
        print('taking image')
        #camera.capture(filename, format = 'jpeg', bayer = True)
        camera.capture(filename, format = 'jpeg', quality=100, bayer = True)
        # reduce the resolution for video streaming
        camera.resolution = cls.stream_resolution
        # Warning: be careful about the camera.start_recording. 'bgr' for opencv and 'mjpeg' for picamera
        # resume the video channel
        camera.start_recording(cls.stream, format='mjpeg', quality = 100)
        # camera.start_recording(cls.stream, format='bgr')
        cls.image_seq = cls.image_seq + 1

    
    # Change:  Sync above 
    @staticmethod
    def frames(cls):
        # run this initialisation method
        cls.initialisation()
        cls.stream_type = 'pi'
        with picamera.PiCamera() as cls.camera:
            time.sleep(0.1)
            cls.stream = io.BytesIO()
            #     # let camera warm up
            time.sleep(0.1)
            cls.camera.resolution = cls.stream_resolution
            cls.camera.framerate = cls.fps
            # setting config
            cls.update_camera_setting(cls.camera)

            # streaming
            # cls.stream = io.BytesIO()
            cls.camera.start_recording(cls.stream, format='mjpeg', quality = 100)


            while True:
                # reset stream for next frame
                cls.stream.seek(0)
                cls.stream.truncate()
                # to stream, read the new frame
                # it has to generate frames faster than displaying the frames, otherwise some random bug will occur
                time.sleep(1/cls.fps*0.1)
                # yield the result to be read
                frame = cls.stream.getvalue()
                ''' ensure the size of package is right''' 
                if len(frame) == 0:
                    pass
                else:
                    yield frame

