# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Glue code between Tian's Kivy interface and Richard's microscope library.
"""

import io
import sys
import os
import time
import numpy as np
import picamera
from openflexure_stage import OpenFlexureStage
from picamera import PiCamera
from openflexure_microscope import Microscope, load_microscope
from read_config import initialise_config
from contextlib import contextmanager


# this is to interface with the kivy
class camera_control():
    def __init__(self, camera=None, stage=None, config=None, configure_camera=True):
    #defines some camera parameters 
        if camera is None:
            camera_resolution = (3280, 2464)
            #camera_resolution = (1024, 768)
            camera = picamera.PiCamera(resolution = camera_resolution)
            time.sleep(2)
        if config is None:
            config = initialise_config()
        self.camera = camera
        # some initial default values - modified in microscope_config.txt

        if stage is None:
            # automatically determine the port name
            self.arduino_port = config.detect_arduino_port()
            stage = OpenFlexureStage(self.arduino_port)
        self.stage = stage
        #self.step = 300 # step of motor movement
        if configure_camera:
            self.configure_camera(config)

    def configure_camera(self, config):
        config.read_config_file()
        self.camera.shutter_speed = int(config.shutter_speed)
        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = config.awb_mode
        self.camera.awb_gains = (float(config.red_gain), float(config.blue_gain))
        self.camera.iso = int(config.iso)
        self.camera.saturation = int(config.saturation)
        self.camera.brightness = 50
        self.camera.annotate_text_size = int(self.camera.resolution[0]*0.03) # reasonable ratio for any resolution
        

    def stage_library(self, command, direction):
        """Use this class from kivy interface to use motors, change picamera etc.
        
        in case there is no stage connected, use the exception to avoid crash"""        
        try:
            if command == 'move_x':
                if direction == '+':
                    self.stage.move_rel([-self.step,0,0])
                else:
                    self.stage.move_rel([self.step,0,0])
            if command == 'move_y':
                if direction == '+':
                    self.stage.move_rel([0,self.step,0])
                else:
                    self.stage.move_rel([0,-self.step,0])
            if command == 'move_z':
                if direction == '+':
                    self.stage.move_rel([0,0,self.step])
                else:
                    self.stage.move_rel([0,0,-self.step])
            if command == 'change_self.step':
                if direction == '+':
                    self.step = self.step*2
                else:
                    self.step = self.step/2
        except IOError:
            # When there is no actual motorised stage connected, do nothing
            pass

    def camera_library(self, argv, *value):
        "Use this function from kivy interface to change picamera etc."
        if argv == 'start_preview':
            self.camera.start_preview()
        elif argv == 'stop_preview':
            self.camera.stop_preview()
        elif argv == 'reduced_size_preview':
            self.camera.start_preview(fullscreen = False, window = value[0])
        elif argv == 'fullscreen_preview':  
            self.camera.start_preview(fullscreen = True) 
        elif argv == 'set_contrast':
            self.camera.contrast = int(value[0])
        elif argv == 'set_brightness':
            self.camera.brightness = int(value[0])
        elif argv == 'set_white_balance':
            self.camera.awb_gains = (value[0],value[1])
        elif argv == 'set_iso':
            self.camera.iso = int(value[0])
        elif argv == 'set_shutter_speed':
            self.camera.shutter_speed = int(value[0])
        elif argv == 'set_saturation':
            self.camera.saturation = int(value[0])
        elif argv == 'change_annotation':
            self.camera.annotate_text  = value[0]
        # 'save_image' cannot be the last elif for some reason?
        elif argv == 'save_image':
            # remove any text overlay
            folder = value[0]
            if not os.path.isdir(folder):
                os.mkdir(folder)
            image_filepath = value[1]
            # format can be 'jpg', 'jpeg', 'raw', 'png'
            file_format = value[2]

            while True:
                # if there is a file with same name, add a -new behind file name
                if os.path.isfile(image_filepath+'.jpeg') or os.path.isfile(image_filepath+'.png'):
                    image_filepath = image_filepath + '-new.'
                else:
                    break

            if file_format == 'raw':
                self.camera.capture(image_filepath + '.jpeg', format = 'jpeg', bayer = True)
            elif file_format == 'png':
                self.camera.capture(image_filepath + '.png', format = 'png')                
            else:
                self.camera.capture(image_filepath + '.jpeg', format = 'jpeg')
            time.sleep(2)
            self.camera.annotate_text = "Image saved as {}".format(image_filepath)
            
        elif argv == 'zoom_in' or 'zoom_out':
            if argv == 'zoom_in':
                self.fov = self.fov*3/4
            elif argv == 'zoom_out' and self.fov < 1:
                self.fov = self.fov*4/3
            self.camera.zoom = (0.5-self.fov/2, 0.5-self.fov/2, self.fov, self.fov)
            self.camera.annotate_text = 'magnification: {0:.2f}X'.format(1/self.fov)

@contextmanager
def camera_control_context():
    """This is a context manager which yields the camera_control object for Kivy"""
    config = initialise_config()
    camera_resolution = (3280, 2464)

    # automatically determine the port name
    with load_microscope("microscope_settings.npz") as ms:
        controller = camera_control(camera=ms.camera, stage=ms.stage, config=config)
        yield controller


