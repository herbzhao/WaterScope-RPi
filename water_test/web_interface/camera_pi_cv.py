from __future__ import division

import io
import time
import datetime
import sys
import os
import picamera
import cv2
import numpy as np

# custom library
from base_camera import BaseCamera
from read_config import initialise_config
# Richard's fix gain
from set_picamera_gain import set_analog_gain, set_digital_gain


from threading import Condition



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
        config = initialise_config()
        config.read_config_file()
        cls.camera.awb_mode = config.awb_mode
        cls.camera.awb_gains = config.awb_gains

        # Richard's library to set analog and digital gains
        set_analog_gain(cls.camera, config.analog_gain)
        set_digital_gain(cls.camera, config.digital_gain)
        cls.camera.shutter_speed = config.shutter_speed
        # cls.camera.iso = config.iso
        cls.camera.saturation = config.saturation
        cls.camera.led = False
    

    ''' be careful about the cls.camera.start_recording, use 'bgr' format!! '''
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
    # openCV functions
    @classmethod
    def variance_of_laplacian(cls, image, ROI=[]):
        ''' focus detection ''' 
        if ROI == []:
            ROI = image
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        focus_value = cv2.Laplacian(ROI, cv2.CV_64F).var()
        focus_text = 'f: {}'.format(focus_value)
        # CV font
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            image,focus_text,
            (int(image.shape[0]*0.2), int(image.shape[1]*0.1)), 
            font, 1,(255,255,255))

        return image


    @classmethod
    def edge_detection(cls, image):
        # do some modification
        image = cv2.Canny(image,100,100)
        return image

    
    
    @classmethod
    def face_detection(cls, image):
        # eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        # gray scale image for faster calculation?
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        #time.sleep(0.2)

        for (x,y,w,h) in faces:
            cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = image[y:y+h, x:x+w]
        #     eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        return image

    @classmethod
    def define_ROI(cls, image):
        # do some modification
        # the opencv size is (y,x)
        image_y, image_x = image.shape[:2]

        # a square from the centre of image
        box_size = int(image_x*0.2)
        roi_box = {
            'x1': int(image_x/2-box_size/2), 'y1':int(image_y/2-box_size/2), 
            'x2': int(image_x/2+box_size/2), 'y2':int(image_y/2+box_size/2)}
        # draw the rectangle
        cv2.rectangle(
            image, 
            pt1=(roi_box['x1'], roi_box['y1']),
            pt2=(roi_box['x2'], roi_box['y2']), 
            color=(255,0,0),
            thickness=2)
        
        # crop the image
        ROI = image[roi_box['y1']: roi_box['y2'], roi_box['x1']:roi_box['x2']]

        return image, ROI

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


    
    @staticmethod
    def frames(cls):
        # run this initialisation method
        cls.initialisation()

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
                    image = data
                    

                    ''' free to do any modification of array'''
                    # image = cls.edge_detection(image)
                    # image = cls.thresholding(image)
                    image, ROI = cls.define_ROI(image)
                    image = cls.variance_of_laplacian(image, ROI)
                    #image = cls.annotate_image(image)
                    # image = cls.variance_of_laplacian(image)
                    #image = cls.face_detection(image)

                    # encode the frame into jpg for displaying in html
                    image = cv2.imencode('.jpg', image)[1].tostring()
                    # yield the result to be read
                    yield image
