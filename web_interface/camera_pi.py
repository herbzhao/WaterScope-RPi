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
        cls.fps = 20
        cls.stream_resolution = (1648,1232)
        cls.video_resolution = (824, 616)
        cls.image_resolution = (3280,2464)
        # Change: 75 or 85 to see the streaming quality
        cls.jpeg_quality = 75
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
    def record_video(cls, option='', filename=''):
        ''' the basic function, then needs to be run in a thread ''' 
        folder_path = 'timelapse_data/{}'.format(cls.starting_time)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        if filename == '':
            filename = folder_path+'/{:04d}.h264'.format(cls.image_seq)
        else:
            filename = folder_path+'/{:04d}-{}.h264'.format(cls.image_seq, filename)
        # DEBUG: changing resolution and quality until having a reasonable results
        cls.image_seq = cls.image_seq + 1    
        print(cls.image_seq)
        cls.camera.start_recording(filename, splitter_port=3, resize=cls.steam_resolution, quality=25)

        while True:
            if cls.video_recording_flag == 'stop':
                cls.camera.stop_recording(splitter_port=3)
                break
            pass

    @classmethod
    def record_video_thread(cls, option='', filename=''):
        if option == 'stop':
            cls.video_recording_flag = 'stop'
            print('stop recording')
        else:
            ''' if not running a thread, the capture will not continue ''' 
            cls.threading_recording = threading.Thread(target=cls.record_video, args=[option, filename])
            cls.threading_recording.daemon = True
            cls.threading_recording.start()
            cls.video_recording_flag = 'start'
            print('start recording')



    @classmethod
    def take_image(cls, filename = '', resolution='normal'):
        # folder_path = '/home/pi/WaterScope-RPi/water_test/timelapse/{}'.format(cls.starting_time)
        folder_path = 'timelapse_data/{}'.format(cls.starting_time)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        # NOTE: when file name is not specified, use a counter
        if filename == '':
            filename = folder_path+'/{:04d}.jpg'.format(cls.image_seq)
        else:
            filename = folder_path+'/{:04d}-{}.jpg'.format(cls.image_seq, filename)
        print('taking image')
        if resolution == 'normal':
            cls.camera.capture(filename, format = 'jpeg', quality=100, bayer = False, use_video_port=True)
        elif resolution == 'high':
            # when taking photos at high res, need to stop the video channel first
            cls.camera.stop_recording(splitter_port=1)
            cls.camera.resolution = cls.image_resolution
            # Remove bayer = Ture if dont care about RAW
            cls.camera.capture(filename, format = 'jpeg', quality=100, bayer = True)
            # reduce the resolution for video streaming
            cls.camera.resolution = cls.stream_resolution
            # resume the video channel
            # Warning: be careful about the cls.camera.start_recording. 'bgr' for opencv and 'mjpeg' for picamera
            cls.camera.start_recording(cls.stream, format='mjpeg', quality = cls.jpeg_quality, splitter_port=1)
            # cls.camera.start_recording(cls.stream, format='bgr', splitter_port=1)

        cls.image_seq = cls.image_seq + 1

    
    # Change:  Sync bove 
    @staticmethod
    def frames(cls):
        # run this initialisation method
        cls.initialisation()
        cls.stream_method = 'PiCamera'
        with picamera.PiCamera() as cls.camera:
            # let camera warm up
            time.sleep(0.1)
            cls.camera.resolution = cls.stream_resolution
            cls.camera.framerate = cls.fps
            # setting config
            cls.update_camera_setting()

            # streaming
            cls.stream = io.BytesIO()
            cls.camera.start_recording(cls.stream, format='mjpeg', quality = cls.jpeg_quality, splitter_port=1)
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

