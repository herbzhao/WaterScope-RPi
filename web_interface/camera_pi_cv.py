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
# use requests to send command for arduino via the web interface
import requests

# custom library
from base_camera import BaseCamera
# Richard's fix gain
from set_picamera_gain import set_analog_gain, set_digital_gain

# opencv specific import
import cv2
import math

class Camera(BaseCamera):
    @classmethod
    def initialisation(cls):
        # TODO: implement a higher camera resolution and then resize to lower resolution for streaming?
        cls.image_seq = 0
        cls.fps = 5
        # reduce the fps for video recording to reduce the file size
        cls.video_recording_fps = 3
        # for OPENCV we use a lower resolution
        # list of available resolutions
        # cls.stream_resolution = (3280, 2464)
        # cls.stream_resolution = (1648,1232)
        # cls.stream_resolution = (832, 624)
        cls.stream_resolution = (656, 496)

        cls.video_resolution = (824, 616)
        cls.image_resolution = (3280,2464)
        # how many seconds before we automatically stop recording
        cls.record_timeout = 600
        # Change: 75 or 85 to see the streaming quality
        cls.stream_quality = 20
        cls.starting_time = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        # URL for requests
        cls.base_URL = "http://localhost:5000"

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
    def record_video_with_splitter_channel(cls, filename=''):
        ''' This method directly use another splitter channel to record the video to local files
        it allows video to be recorded at different  resolution, but it is slow''' 
        time_start = time.time()
        cls.initialise_data_folder()
        if filename == '':
            filename = cls.folder_path+'/{:04d}.h264'.format(cls.image_seq)
        else:
            filename = cls.folder_path+'/{:04d}-{}.h264'.format(cls.image_seq, filename)
        cls.image_seq = cls.image_seq + 1

        cls.camera.start_recording(filename, splitter_port=3, resize=cls.video_resolution, quality=25)

        while True:
            # Use a thread to sniff for the flag change and stop the video recording?
            if time.time() - time_start > cls.record_timeout:
                cls.recording_flag = False

            if cls.recording_flag is False:
                cls.camera.stop_recording(splitter_port=1)
                time.sleep(0.5)
                cls.camera.stop_recording(splitter_port=3)
                time.sleep(0.5)
                # Warning: be careful about the cls.camera.start_recording. 'bgr' for opencv and 'mjpeg' for picamera
                cls.camera.start_recording(cls.stream, format='mjpeg', quality = cls.stream_quality, splitter_port=1)
                # cls.camera.start_recording(cls.stream, format='bgr', splitter_port=1)
                break


        

    @classmethod
    def capture_video_from_stream(cls, filename=''):
        ''' This method directly save the stream into a local file, so it should consume less computing power ''' 
        cls.initialise_data_folder()
        time_start = time.time()
        if filename == '':
            filename = cls.folder_path+'/{:04d}.mjpeg'.format(cls.image_seq)
        else:
            filename = cls.folder_path+'/{:04d}-{}.mjpeg'.format(cls.image_seq, filename)
        cls.image_seq = cls.image_seq + 1

        # NOTE: this mjpeg_headings is required to add before each frame for VLC to render the video properly
        mjpeg_headings = b'''

--myboundary
Content Type: image/jpeg
FPS: {}
'''.format(cls.video_recording_fps)

        # open the file and append new frames
        with open(filename, 'a+') as f:
            while True:
                time_now = time.time()
                try:
                    if cls.frame_to_capture:
                        f.write(mjpeg_headings)
                        time.sleep(0)
                        f.write(str(cls.frame_to_capture))
                        # after capturing it, destorying the frame
                        del(cls.frame_to_capture)
                        # use a lower fps than the stream to reduce the file size
                        time.sleep(1/cls.video_recording_fps)
                # when there is no frame, just wait for a bit
                except AttributeError:
                    time.sleep(1/cls.fps*0.05)

                # after certain time of recording, automatically close
                if time_now - time_start > cls.record_timeout:
                    cls.recording_flag = False

                # close the thread with the flag
                if cls.recording_flag is False:
                    break


    @classmethod
    def video_recording_thread(cls, video_record_method='capture_video_from_stream', recording_flag = True, filename=''):
        if recording_flag is True:
            # first stop the recording
            cls.recording_flag = False
            time.sleep(1)
            # then resume
            cls.recording_flag = True
            if video_record_method == 'record_video_with_splitter_channel':
                cls.threading_recording = threading.Thread(target=cls.record_video_with_splitter_channel, args=[filename])
            elif video_record_method == 'capture_video_from_stream':
                cls.threading_recording = threading.Thread(target=cls.capture_video_from_stream, args=[filename])
            cls.threading_recording.daemon = True
            cls.threading_recording.start()
            print('start recording')
        else:
            cls.recording_flag = False
            print('stop recording')



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
            # cls.camera.stop_recording(splitter_port=1)
            cls.camera.stop_recording()
            time.sleep(0)
            cls.camera.resolution = cls.image_resolution
            # Remove bayer = Ture if dont care about RAW
            cls.camera.capture(filename, format = 'jpeg', quality=100, bayer = False)
            time.sleep(0)
            # reduce the resolution for video streaming
            cls.camera.resolution = cls.stream_resolution
            # resume the video channel
            # Warning: be careful about the cls.camera.start_recording. 'bgr' for opencv and 'mjpeg' for picamera
            # cls.camera.start_recording(cls.stream, format='mjpeg', quality = cls.stream_quality, splitter_port=1)
            cls.camera.start_recording(cls.stream, format='bgr', splitter_port=1)

        cls.image_seq = cls.image_seq + 1

    @classmethod
    def move_to(cls, destination=100):
        # send serial command to move the motor
        if destination == 'home':
            move_motor_url = cls.base_URL + "/send_serial/?value=home_opt&board=waterscope"
        else:
            move_motor_url = cls.base_URL + "/send_serial/?value=move_to_opt({0})&board=waterscope".format(destination)

        requests.get(move_motor_url)
        # DEBUG: a delay to allow serial command to be executed and motor becomes busy
        while True:
            waterscope_motor_status_url = cls.base_URL+ "/waterscope_motor_status"
            waterscope_motor_status = requests.get(waterscope_motor_status_url).json()
            if waterscope_motor_status['stepper_optics_busy']:
                break
            else:
                time.sleep(1)
                break

        while True:
            # print('waiting for motor to finish movement')
            waterscope_motor_status_url = cls.base_URL+ "/waterscope_motor_status"
            waterscope_motor_status = requests.get(waterscope_motor_status_url).json()
            time.sleep(0.1)
            if waterscope_motor_status['stepper_optics_busy'] is False:
                cls.absolute_pos_opt = waterscope_motor_status['absolute_pos_opt']
                break
                
    
    # Change:  Sync above 
    @classmethod
    def initialise_cv(cls):
        ''' which functions to use during the opencv stream''' 
        cls.ROI = []
        cls.annotation_text = ''
        cls.cv_libraries = [
            cls.define_ROI,
            # cls.edge_detection,
            # cls.thresholding,
            cls.variance_of_laplacian, 
            cls.annotating
        ]

    # openCV functions
    @classmethod
    def annotating(cls):
        # CV font
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(
            cls.image, cls.annotation_text,
            (int(cls.image.shape[0]*0.9), int(cls.image.shape[1]*0.1)), 
            font, 2, (0, 0, 255))

    # openCV functions
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
        box_size = int(image_x*0.2)
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
    def thresholding(cls):
        # do some modification
        # NOTE: it seems like the thresholding is better to do not in RGB scale
        gray = cv2.cvtColor(cls.image, cv2.COLOR_BGR2GRAY)
        ret,thresh1 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
        ret,thresh2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
        ret,thresh3 = cv2.threshold(gray,127,255,cv2.THRESH_TRUNC)
        ret,thresh4 = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO)
        ret,thresh5 = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO_INV)
        cls.image = thresh5
    

    @classmethod
    def variance_of_laplacian(cls):
        ''' focus calculation ''' 
        if cls.ROI == []:
            cls.ROI = cls.image
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        cls.focus_value = cv2.Laplacian(cls.ROI, cv2.CV_64F).var()
        focus_text = 'f: {:.2f}'.format(cls.focus_value)
        # CV font
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(
            cls.image, focus_text,
            (int(cls.image.shape[0]*0.1), int(cls.image.shape[1]*0.1)), 
            font, 2, (0, 0, 255))


    @classmethod
    def auto_focus(cls):
        def focus_measure_at_z(new_z):
            cls.move_to(new_z)
            # DEBUG: wait for 1 second to stablise the mechanical stage
            time.sleep(0.2)
            focus_value =  cls.focus_value
            print("Focus value at {0} is: {1}".format(new_z, focus_value))
            return focus_value

        def create_z_scan_map(central_point = 5000, range = 1000, nubmer_of_points = 10):
            " using a central point and scan up and down with half of the range"
            z_scan_map = np.linspace(central_point-range/2, central_point+range/2, nubmer_of_points)
            for new_z in z_scan_map:
                focus_value = focus_measure_at_z(new_z)
                # use 2 arrays to keep record of z and focus
                cls.z_scan_values.append(new_z)
                cls.z_scan_focus_values.append(focus_value)

        def iterate_z_scan_map(starting_z=2500):
            ' automatically create several scan map from coarse to fine, using first guess and next best focus point' 
            start_time = time.time()
            # first scan is based on the best guess
            create_z_scan_map(starting_z, 2000, 10)
            # this will refine the best focus within range/points*2 = 400

            # Then finer scan  use the best focus value as the index for the z value
            for z_scan_range in [400]:

                local_optimal_z = cls.z_scan_values[cls.z_scan_focus_values.index(max(cls.z_scan_focus_values))]
                create_z_scan_map(local_optimal_z, z_scan_range, 5)
            
            global_optimal_z = cls.z_scan_values[cls.z_scan_focus_values.index(max(cls.z_scan_focus_values))]
            cls.move_to(global_optimal_z)
            print('find the focus in {0:.2f} seconds at Z: {1}'.format(time.time() - start_time, global_optimal_z))

        # NOTE: Autofocus code runs from here

        # DEBUG: allow some time for system to be ready
        cls.camera_ready = False
        while True:
            # wait until the image is ready before starting the auto focus
            try:
                cls.focus_value
                break
            except AttributeError:
                print('waiting for the camera to be ready')

        cls.annotation_text = 'Autofocusing'
        # home the stage for absolute_z
        cls.move_to('home')

        #  a dictionary to record different z with its corresponding focus value
        cls.z_scan_values = []
        cls.z_scan_focus_values = []
        iterate_z_scan_map()
        print('you are at the best focus now')

        #  annotate when auto focus finish to notify the user
        cls.annotation_text = 'Focus ready'

        # send requests to change the status to done
        requests.get(cls.base_URL + '/auto_focus/?command=done' )
        

    @classmethod
    def start_auto_focus_thread(cls):
        # threading for auto focusing    
        threading_af = threading.Thread(target=cls.auto_focus)
        threading_af.daemon = True
        threading_af.start()
    

    stream_method = 'OpenCV'
    @staticmethod
    def frames(cls):
        # run this initialisation method
        cls.initialisation()
        cls.initialise_cv()
        # cls.start_auto_focus_thread()

        with picamera.PiCamera() as cls.camera:
            # let camera warm up
            time.sleep(0.1)
            # opencv is much slower, so the resolution is limited
            cls.camera.resolution = cls.stream_resolution
            cls.camera.framerate = cls.fps
            # read configs
            cls.update_camera_setting()

            # streaming - using bgr so we do not need to encode->decode->encode
            cls.stream = io.BytesIO()
            cls.camera.start_recording(cls.stream, format='bgr', splitter_port=1)
            print('starting now')

            while True:
                # reset stream for next frame
                cls.stream.seek(0)
                cls.stream.truncate()
                # to stream, read the new frame
                # it has to generate frames faster than displaying the frames, otherwise some random bug will occur
                time.sleep(1/cls.fps*0.2)
                # yield the result to be read
                frame = cls.stream.getvalue()
                ''' ensure the size of package is right''' 
                if len(frame) == 0:
                    pass
                else:
                    cls.camera_ready = True
                    # convert the stream string into np.arrry
                    ncols, nrows = cls.camera.resolution

                    data = np.fromstring(frame, dtype=np.uint8).reshape(nrows, ncols, 3)
                    # data = cv2.resize(data, None, fx=0.5, fy=0.5)
                    cls.image = data

                    # place to run some filters, calculations
                    for library in cls.cv_libraries:
                        library()

                    # encode the frame into jpg for displaying in html
                    cls.image = cv2.imencode('.jpg', cls.image)[1].tostring()
                    # yield the result to be read
                    yield cls.image

