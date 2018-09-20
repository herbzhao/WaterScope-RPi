from __future__ import division


# import the necessary packages 
from picamera.array import PiRGBArray
import picamera
import io
import time
import cv2
import numpy as np
import threading

from read_config import initialise_config
# Richard's fix gain
from set_picamera_gain import set_analog_gain, set_digital_gain
# for auto focusing
from serial_communication import serial_controller_class



class cv_stream_class():
    def __init__(self):
        self.ROI = []

    def update_camera_setting(self):
        # consistent imaging condition
        config = initialise_config()
        config.read_config_file()
        self.camera.awb_mode = config.awb_mode
        self.camera.awb_gains = config.awb_gains

        # Richard's library to set analog and digital gains
        set_analog_gain(self.camera, config.analog_gain)
        set_digital_gain(self.camera, config.digital_gain)
        self.camera.shutter_speed = config.shutter_speed
        # self.camera.iso = config.iso
        self.camera.saturation = config.saturation
        self.camera.led = False

        ''' sync above '''
        # openCV functions

    def streaming(self):    
        ''' streaming '''

        # initialize the camera and grab a reference to the raw camera capture
        with picamera.PiCamera() as self.camera:
            self.camera.resolution = (int(640), int(480))
            fps = 15
            self.camera.framerate = fps
            # allow the camera to warmup
            time.sleep(0.1)

            # use the memory stream, may be faster?
            stream = io.BytesIO()
            self.update_camera_setting()

            ''' camera ''' 
            self.camera.start_recording(stream, format='bgr')

            # move the imshow window to centre
            cv2.namedWindow('stream')        # Create a named window
            cv2.moveWindow('stream', 0, 200)  # Move it to (40,30)

            # a default step size
            #focuser = focuser_class()
            while True:
                
                while True:
                    # reset stream for next frame
                    stream.seek(0)
                    stream.truncate()
                    # this delay has to be faster than generating
                    time.sleep(1/fps*0.2)

                    # return current frame, which is just a string
                    frame = stream.getvalue()
                    ''' ensure the size of package is right''' 
                    if len(frame) != 0:
                        break
                    else:
                        pass
                        
                
                # convert the stream string into np.arrry
                ncols, nrows = self.camera.resolution
                data = np.fromstring(frame, dtype=np.uint8).reshape(nrows, ncols, 3)
                # no need to decode (it is already bgr)
                self.image = data
                
                # place to run some filters, calculations
                for library in self.cv_libraries:
                    library()

                

                # show the frame
                cv2.imshow('stream', self.image)


                key = cv2.waitKey(1) & 0xFF
                # if the `x` key was pressed, break from the loop
                if key == ord("x"):
                    break
                    

    def variance_of_laplacian(self):
        ''' focus detection ''' 
        if self.ROI == []:
            self.ROI = self.image
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        self.focus_value = cv2.Laplacian(self.ROI, cv2.CV_64F).var()
        focus_text = 'f: {}'.format(self.focus_value)
        # CV font
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            self.image,focus_text,
            (int(self.image.shape[0]*0.2), int(self.image.shape[1]*0.1)), 
            font, 1,(255,255,255))



    def edge_detection(self):
        # do some modification
        self.image = cv2.Canny(self.image,100,100)


    def define_ROI(self):
        # do some modification
        # the opencv size is (y,x)
        image_y, image_x = self.image.shape[:2]

        # a square from the centre of image
        box_size = int(image_x*0.1)
        roi_box = {
            'x1': int(image_x/2-box_size/2), 'y1':int(image_y/2-box_size/2), 
            'x2': int(image_x/2+box_size/2), 'y2':int(image_y/2+box_size/2)}
        
        # the rectangle affects the laplacian, draw it outside the ROI
        # draw the rectangle

        cv2.rectangle(
            self.image, 
            pt1=(roi_box['x1']-5, roi_box['y1']-5),
            pt2=(roi_box['x2']+5, roi_box['y2']+5), 
            color=(0,0,255),
            thickness=2)
        
        # crop the image
        self.ROI = self.image[roi_box['y1']: roi_box['y2'], roi_box['x1']:roi_box['x2']]



    def thresholding(self, image):
        # do some modification
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret,thresh1 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
        ret,thresh2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
        ret,thresh3 = cv2.threshold(gray,127,255,cv2.THRESH_TRUNC)
        ret,thresh4 = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO)
        ret,thresh5 = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO_INV)
        image = thresh5
        return image


    def init_focusing(self):
        # numpy array to store everything
        self.motor_moving_time = 2
        self.step = 0
        self.focus_value = 0
        self.focus_values = np.array([])
        self.z_values = np.array([])
        
        # a plan for mapping
        self.define_steps_plan()

        ''' arduino '''
        # connect to serial
        #global ser
        self.serial_controller = serial_controller_class()
        self.serial_controller.serial_read_threading()
        # turn on the light
        self.serial_controller.send_arduino_command('66')
        time.sleep(1)



    def define_steps_plan(self):
        self.steps_plan = []
        # first move up to the end stop and go back to centre
        self.steps_plan += [-8000, 4000]

        # first plan: 2000
        self.steps_plan += [0]
        self.steps_plan += [500]*4
        self.steps_plan += [-6*500]
        self.steps_plan += [-500]*4
        self.steps_plan.append('phase 1 complete')


        # first plan: 2000
        self.steps_plan += [200]*3
        self.steps_plan += [-3*200]
        self.steps_plan += [-200]*3
        self.steps_plan.append('phase 1 complete')

        # finer plan : 800
        self.steps_plan += [100]*3
        self.steps_plan += [-3*100]
        self.steps_plan += [-100]*3
        self.steps_plan.append('phase 2 complete')

        # finest plan: 400
        self.steps_plan += [50]*3
        self.steps_plan += [-3*50]
        self.steps_plan += [-50]*3
        self.steps_plan.append('phase 3 complete')
        self.steps_plan.append('auto-focusing complete')


        # finest plan: 200
        self.steps_plan += [25]*3
        self.steps_plan += [-3*25]
        self.steps_plan += [-25]*3
        self.steps_plan.append('phase 4 complete')
        self.steps_plan.append('auto-focusing complete')

    def retrieve_mapping_step(self):
        self.step = self.steps_plan[0]
        self.steps_plan = self.steps_plan[1:]


    def wait_for_motor_movement(self):
        ''' in the future can be something smarter '''
        # change the waiting time based on step size
        if abs(self.step) >= 500:
            self.motor_moving_time = abs(self.step)/100
        elif abs(self.step) <= 100:
            self.motor_moving_time = 2
        else:
            self.motor_moving_time = abs(self.step)/50

        print('waiting for {} seconds'.format(self.motor_moving_time))
        time.sleep(self.motor_moving_time)


    def auto_focus(self):
        while True:
            try: 
                # wait for the imaging system to boot up
                self.image

                # start to change step when the system is boot up (focus value is non 0)
                # when there are more planned steps, retrieve one by one and measure the focus
                self.retrieve_mapping_step()
                # otherwise we just continue with mapping
                if type(self.step) is not str:   
                    pass
            
                # a string is sent when each phase finished.
                # then we update the steps by going to local optimal
                elif type(self.step) is str:
                    if self.step != 'auto-focusing complete':
                        z_max_focus = self.z_values[np.argmax(self.focus_values)]
                        print('now moving to the local maxima: focus:{} , z: {}'.format(max(self.focus_values), z_max_focus))
                        self.step = z_max_focus - self.z_values[-1]
                
                    elif self.step == 'auto-focusing complete':
                        print('focus done! the optimal focus value is {}'.format(self.focus_value))
                        break 

                # move
                print('Z move: {}'.format(self.step))
                self.serial_controller.send_arduino_command('move {}'.format(self.step))
                self.wait_for_motor_movement()

                # record the new position - initialisation
                if len(self.z_values) == 0:
                    self.z_values = np.append(self.z_values, 0)
                else:
                    self.z_values = np.append(self.z_values, self.z_values[-1]+self.step)
                
                # record the new focus value at new z_value
                # the focus_value is calculated in the main thread
                self.focus_values = np.append(self.focus_values, self.focus_value)

                print('current position: {}'.format(self.z_values[-1]))
                print('focus: {}'.format(self.focus_values[-1]))
                print('')

            # wait for the imaging system to boot up
            except AttributeError:
                time.sleep(2)

                
                
            
if __name__ == '__main__':

    #     # now threading1 runs regardless of user input

    # while True:
    #     pass
    cv_stream = cv_stream_class()
    cv_stream.init_focusing()

    # threading for auto focusing    
    threading1 = threading.Thread(target=cv_stream.auto_focus)
    threading1.daemon = True
    threading1.start()

    cv_stream.cv_libraries = [
        cv_stream.define_ROI,
        #cv_stream.edge_detection,
        cv_stream.variance_of_laplacian, 
        ]
    cv_stream.streaming()
    # cv_stream.init_focusing()

    # while True:
    #     pass
        # # move the imshow window to centre
        # cv2.namedWindow('stream')        # Create a named window
        # # cv2.moveWindow('stream', 0,0)  # Move it to (40,30)
        # # show the frame
        # cv2.imshow('stream', cv_stream.image)


        # key = cv2.waitKey(1) & 0xFF
        # # if the `x` key was pressed, break from the loop
        # if key == ord("x"):
        #     break


