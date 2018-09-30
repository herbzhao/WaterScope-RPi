from __future__ import division

import io
import time
import datetime
import sys
import os
import picamera
# DEBUG: is this neccessary?
from threading import Condition
import threading

# custom library
from base_camera import BaseCamera
from  read_config import config
# Richard's fix gain
from set_picamera_gain import set_analog_gain, set_digital_gain

# opencv specific import
import cv2
import numpy as np
from serial_communication import serial_controller_class


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
    def update_camera_setting(cls):
        # consistent imaging condition
        cls.camera.awb_mode = config['awb_mode']
        cls.camera.awb_gains = config['awb_gains']
        # Richard's library to set analog and digital gains
        set_analog_gain(cls.camera, config['analog_gain'])
        set_digital_gain(cls.camera, config['digital_gain'])
        cls.camera.shutter_speed = config['shutter_speed']
        cls.camera.saturation = config['saturation']
        cls.camera.led = False


    ''' CAUTION: be careful about the cls.camera.start_recording, use 'bgr' format!! '''
    @classmethod
    def take_image(cls):
        # when taking photos, increase the resolution and everything
        # need to stop the video channel first
        cls.camera.stop_recording()
        cls.camera.resolution = cls.image_resolution
        filename = '/home/pi/WaterScope-RPi/water_test/timelapse/{}/timelapse_{:03d}.jpg'.format(Camera.starting_time, cls.image_seq)
        print('taking image')
        #cls.camera.capture(filename, format = 'jpeg', bayer = True)
        cls.camera.capture(filename, format = 'jpeg', quality=100, bayer = True)
        # reduce the resolution for video streaming
        cls.camera.resolution = cls.stream_resolution
        # resume the video channel
        cls.camera.start_recording(cls.stream, format='bgr')
        cls.image_seq = cls.image_seq + 1


    ''' sync above '''
    @classmethod
    def init_cv(cls):
        cls.ROI = []
        cls.cv_libraries = [
            cls.define_ROI,
            #cv_stream.edge_detection,
            cls.variance_of_laplacian, 
        ]


    # openCV functions
    @classmethod
    def variance_of_laplacian(cls):
        ''' focus detection ''' 
        if cls.ROI == []:
            cls.ROI = cls.image
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        cls.focus_value = cv2.Laplacian(cls.ROI, cv2.CV_64F).var()
        focus_text = 'f: {}'.format(cls.focus_value)
        # CV font
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            cls.image,focus_text,
            (int(cls.image.shape[0]*0.2), int(cls.image.shape[1]*0.1)), 
            font, 1,(255,255,255))


    @classmethod
    def edge_detection(cls):
        # do some modification
        cls.image = cv2.Canny(cls.image,100,100)

    @classmethod
    def define_ROI(cls):
        # do some modification
        # the opencv size is (y,x)
        image_y, image_x = cls.image.shape[:2]

        # a square from the centre of image
        box_size = int(image_x*0.1)
        roi_box = {
            'x1': int(image_x/2-box_size/2), 'y1':int(image_y/2-box_size/2), 
            'x2': int(image_x/2+box_size/2), 'y2':int(image_y/2+box_size/2)}
        
        # the rectangle affects the laplacian, draw it outside the ROI
        # draw the rectangle

        cv2.rectangle(
            cls.image, 
            pt1=(roi_box['x1']-5, roi_box['y1']-5),
            pt2=(roi_box['x2']+5, roi_box['y2']+5), 
            color=(0,0,255),
            thickness=2)
        
        # crop the image
        cls.ROI = cls.image[roi_box['y1']: roi_box['y2'], roi_box['x1']:roi_box['x2']]


    @classmethod
    def thresholding(cls, image):
        # do some modification
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret,thresh1 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
        ret,thresh2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
        ret,thresh3 = cv2.threshold(gray,127,255,cv2.THRESH_TRUNC)
        ret,thresh4 = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO)
        ret,thresh5 = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO_INV)
        image = thresh5
        return image

    @classmethod
    def initialise_focusing(cls):
        # numpy array to store everything
        cls.motor_moving_time = 2
        cls.step = 0
        cls.focus_value = 0
        cls.focus_values = np.array([])
        cls.z_values = np.array([])
        
        # a plan for mapping
        cls.define_steps_plan()

        ''' arduino '''
        # connect to serial
        #global ser
        cls.serial_controller = serial_controller_class()
        cls.serial_controller.serial_read_threading()
        # turn on the light
        cls.serial_controller.send_arduino_command('66')
        time.sleep(1)

    # TODO: move the lists to another file
    @classmethod
    def define_steps_plan(cls):
        cls.steps_plan = []
        # first move up to the end stop and go back to centre
        cls.steps_plan += [-8000, 4000]

        # first plan: 2000
        cls.steps_plan += [0]
        cls.steps_plan += [500]*4
        cls.steps_plan += [-4*500]
        cls.steps_plan += [-500]*4
        cls.steps_plan.append('phase 1 complete')


        # first plan: 2000
        cls.steps_plan += [200]*3
        cls.steps_plan += [-3*200]
        cls.steps_plan += [-200]*3
        cls.steps_plan.append('phase 1 complete')

        # finer plan : 800
        cls.steps_plan += [100]*3
        cls.steps_plan += [-3*100]
        cls.steps_plan += [-100]*3
        cls.steps_plan.append('phase 2 complete')

        # finest plan: 400
        cls.steps_plan += [50]*3
        cls.steps_plan += [-3*50]
        cls.steps_plan += [-50]*3
        cls.steps_plan.append('phase 3 complete')


        # finest plan: 200
        cls.steps_plan += [25]*3
        cls.steps_plan += [-3*25]
        cls.steps_plan += [-25]*3
        cls.steps_plan.append('phase 4 complete')
        cls.steps_plan.append('auto-focusing complete')
    
    @classmethod
    def retrieve_mapping_step(cls):
        cls.step = cls.steps_plan[0]
        cls.steps_plan = cls.steps_plan[1:]

    @classmethod
    def wait_for_motor_movement(cls):
        ''' in the future can be something smarter '''
        # change the waiting time based on step size
        if abs(cls.step) >= 500:
            cls.motor_moving_time = abs(cls.step)/100
        elif abs(cls.step) <= 100:
            cls.motor_moving_time = 2
        else:
            cls.motor_moving_time = abs(cls.step)/50

        print('waiting for {} seconds'.format(cls.motor_moving_time))
        time.sleep(cls.motor_moving_time)
        print('waiting finished')

    @classmethod
    def auto_focus(cls):
        while True:
            try: 
                # wait for the imaging system to boot up
                cls.image
            # DEBUG: check if this will cause any problem that we move the except uphere
            except AttributeError:
                # wait for the imaging system to boot up
                time.sleep(2)

                # start to change step when the system is boot up (focus value is non 0)
                # when there are more planned steps, retrieve one by one and measure the focus
                cls.retrieve_mapping_step()
                # otherwise we just continue with mapping
                if type(cls.step) is not str:   
                    pass
            
                # a string is sent when each phase finished.
                # then we update the steps by going to local optimal
                elif type(cls.step) is str:
                    if cls.step != 'auto-focusing complete':
                        z_max_focus = cls.z_values[np.argmax(cls.focus_values)]
                        print('now moving to the local maxima: focus:{} , z: {}'.format(max(cls.focus_values), z_max_focus))
                        cls.step = z_max_focus - cls.z_values[-1]
                
                    elif cls.step == 'auto-focusing complete':
                        print('focus done! the optimal focus value is {}'.format(cls.focus_value))
                        break 

                # move
                print('Z move: {}'.format(cls.step))
                cls.serial_controller.send_arduino_command('move {}'.format(cls.step))
                cls.wait_for_motor_movement()

                # record the new position - initialisation
                if len(cls.z_values) == 0:
                    cls.z_values = np.append(cls.z_values, 0)
                else:
                    cls.z_values = np.append(cls.z_values, cls.z_values[-1]+cls.step)
                
                # record the new focus value at new z_value
                # the focus_value is calculated in the main thread
                cls.focus_values = np.append(cls.focus_values, cls.focus_value)

                print('current position: {}'.format(cls.z_values[-1]))
                print('focus: {}'.format(cls.focus_values[-1]))
                print('')



    @classmethod
    def auto_focus_thread(cls):
        cls.initialise_focusing()
        # threading for auto focusing    
        threading_af = threading.Thread(target=cls.auto_focus)
        threading_af.daemon = True
        threading_af.start()
    
    stream_type = 'opencv'
    @staticmethod
    def frames(cls):
        # run this initialisation method
        cls.initialisation()
        cls.init_cv()
        
        with picamera.PiCamera() as cls.camera:
            # let camera warm up
            time.sleep(0.1)
            fps = 24
            # opencv is much slower, so the resolution is limited
            cls.camera.resolution = cls.stream_resolution

            cls.camera.framerate = fps
            # read configs
            cls.update_camera_setting()

            # streaming - using bgr so we do not need to encode->decode->encode
            cls.stream = io.BytesIO()
            cls.camera.start_recording(cls.stream, format='bgr')
            print('starting now')

            while True:
                # reset stream for next frame
                cls.stream.seek(0)
                cls.stream.truncate()
                # to stream, read the new frame
                # it has to generate frames faster than displaying the frames, otherwise some random bug will occur
                time.sleep(1/fps*0.2)
                # yield the result to be read
                frame = cls.stream.getvalue()
                ''' ensure the size of package is right''' 
                if len(frame) == 0:
                    pass
                else:
                    # convert the stream string into np.arrry
                    ncols, nrows = cls.camera.resolution
                    data = np.fromstring(frame, dtype=np.uint8).reshape(nrows, ncols, 3)
                    cls.image = data

                    # place to run some filters, calculations
                    for library in cls.cv_libraries:
                        library()

                    # encode the frame into jpg for displaying in html
                    cls.image = cv2.imencode('.jpg', cls.image)[1].tostring()
                    # yield the result to be read
                    yield cls.image
