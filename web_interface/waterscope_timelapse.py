from __future__ import division

import io
import time
import datetime
import sys
import os
import picamera
import numpy as np
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
        # TODO: implement a higher camera resolution and then resize to lower resolution for streaming?
        cls.image_seq = 0
        cls.fps = 15
        # reduce the fps for video recording to reduce the file size
        cls.video_recording_fps = 3
        cls.stream_resolution = (1648,1232)
        cls.video_resolution = (824, 616)
        cls.image_resolution = (4056,3040)
        # how many seconds before we automatically stop recording
        cls.record_timeout = 600
        # Change: 75 or 85 to see the streaming quality
        cls.stream_quality = 85
        cls.starting_time = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')

    @classmethod
    def update_camera_setting(cls):
        with open('config_picamera.yaml') as config_file:
            config = yaml.load(config_file)
            # consistent imaging condition
            cls.camera.awb_mode = config['awb_mode']
            cls.camera.awb_gains = (config['red_gain'], config['blue_gain'])
            # Richard's library to set analog and digital gains
            set_analog_gain(cls.camera, config['analog_gain'])
            set_digital_gain(cls.camera, config['digital_gain'])
            cls.camera.shutter_speed = config['shutter_speed']
            cls.camera.saturation = config['saturation']
            cls.camera.led = False

    # TODO: a zoom function with picamera https://picamera.readthedocs.io/en/release-1.13/api_camera.html
    @classmethod
    def change_zoom(cls, zoom_value=1):
        zoom_value = float(zoom_value)
        if zoom_value <1:
            zoom_value = 1
        # Richard's code for zooming !
        fov = cls.camera.zoom
        centre = np.array([fov[0] + fov[2]/2.0, fov[1] + fov[3]/2.0])
        size = 1.0/zoom_value
        # If the new zoom value would be invalid, move the centre to
        # keep it within the camera's sensor (this is only relevant 
        # when zooming out, if the FoV is not centred on (0.5, 0.5)
        for i in range(2):
            if np.abs(centre[i] - 0.5) + size/2 > 0.5:
                centre[i] = 0.5 + (1.0 - size)/2 * np.sign(centre[i]-0.5)
        print("setting zoom, centre {}, size {}".format(centre, size))
        new_fov = (centre[0] - size/2, centre[1] - size/2, size, size)
        cls.camera.zoom = new_fov

    @classmethod
    def initialise_data_folder(cls):
        if not os.path.exists('timelapse_data'):
            os.mkdir('timelapse_data')
        cls.folder_path = 'timelapse_data/{}'.format(cls.starting_time)
        if not os.path.exists(cls.folder_path):
            os.mkdir(cls.folder_path)

    @classmethod
    def take_image(cls, filename = '', resolution='normal'):
        cls.initialise_data_folder()
        # NOTE: when file name is not specified, use a counter
        if filename == '':
            filename = cls.folder_path+'/{:04d}.jpg'.format(cls.image_seq)
        else:
            filename = cls.folder_path+'/{:04d}-{}.jpg'.format(cls.image_seq, filename)
        print('taking image')
        if resolution == 'normal':
            cls.camera.capture(filename, format = 'jpeg', quality=100, bayer = False, use_video_port=True)
        elif resolution == 'high_res':
            print('taking high_res image')
            # when taking photos at high res, need to stop the video channel first
            cls.camera.stop_recording(splitter_port=1)
            time.sleep(0)
            cls.camera.resolution = cls.image_resolution
            # Remove bayer = Ture if dont care about RAW
            cls.camera.capture(filename, format = 'jpeg', quality=100, bayer = False)
            time.sleep(0)
            # reduce the resolution for video streaming
            cls.camera.resolution = cls.stream_resolution
            # resume the video channel
            # Warning: be careful about the cls.camera.start_recording. 'bgr' for opencv and 'mjpeg' for picamera
            cls.camera.start_recording(cls.stream, format='mjpeg', quality = cls.stream_quality, splitter_port=1)
            # cls.camera.start_recording(cls.stream, format='bgr', splitter_port=1)

        cls.image_seq = cls.image_seq + 1
