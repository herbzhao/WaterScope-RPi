# example code G01 Z10 F200
import serial
import time
import os
debug_mode = True

if debug_mode is False:
    import picamera


class camera_control():
    def __init__(self):
        camera_resolution = (3280, 2464)
        self.camera = picamera.PiCamera(resolution = camera_resolution)
        # some initial default values
        
        self.camera.awb_mode = 'sun'
        #self.camera.awb_gains = (1.5,1.1)
        self.camera.iso = 0
        # when set exposure_mode to "off", output will be black
        #self.camera.exposure_mode = 'auto'
        self.camera.shutter_speed = 5000 # condenser require much lower shutter speed
        self.camera.CAPTURE_TIMEOUT = 10
        self.camera.saturation = 0
        self.camera.annotate_text_size = int(camera_resolution[0]*0.03) # reasonable ratio for any resolution
        self.filename = 1

    def save_image(self):
        #self.camera.capture(image_filepath, format = None)
        image_filepath = '/home/pi/desktop/20170323/'
        if not os.path.isdir(image_filepath):
            os.mkdir(image_filepath)
        self.camera.capture('{}'.format(self.filename), 'jpeg', bayer = False)
        self.camera.annotate_text = "Image saved"

    def image_naming(self):
        self.filename = self.filename + 1

class microscope_stage_arduino():
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.port = 'COM3' # change this with port value
        self.ser.open()
        self.led_command = ''
        self.LED_switch

        '''self.speed = 200
        self.step = 20
        time.sleep(2) # required boot up time when connecting to serial
        

    def format_stage_command(self):
        command_string = 'G01 {}{} F{}'.format(self.axis, self.movement, self.speed)
        command_byte = command_string.encode(encoding='UTF-8')
        self.ser.flush()
        self.ser.write(command_byte)
        print(command_byte)

    def stage_library(self, command, direction):
        "Use this class from kivy interface to use motors, change picamera etc."        
        #stage settings
        if command == 'move_x':
            self.axis = 'X'
            if direction == '+':
                self.movement = self.step
            else:
                self.movement = -self.step
            self.format_stage_command()

        if command == 'move_y':
            self.axis = 'Y'
            if direction == '+':
                self.movement = self.step
            else:
                self.movement = -self.step
            self.format_stage_command()
        
        if command == 'move_z':
            self.axis = 'Z'
            if direction == '+':
                self.movement = self.step
            else:
                self.movement = -self.step
            self.format_stage_command()'''
    

    def LED_control(self, RGB):
        self.led_command = RGB # example: 255,255,255
        self.format_LED_command()

    def LED_switch(self, switch):
        if switch == 'off':
            self.LED_control('0,0,0')
        elif switch == 'on':
            self.LED_control('255,255,255')

    def format_LED_command(self):
        #command_byte = command_string.encode(encoding='UTF-8')
        #self.ser.flush()
        command_string = self.led_command
        command_byte = command_string.encode(encoding='UTF-8')
        self.ser.write(command_byte)

if __name__ == '__main__':
    stage = microscope_stage_arduino()
    if debug_mode is False:
        camera = camera_control()
    #stage.stage_library('move_x','+')
    #time.sleep(3)
    #stage.stage_library('move_y','-')
    while True:
        if debug_mode is False:
            camera.save_image()
            camera.image_naming()
        stage.LED_control('0,0,255')
        time.sleep(5)
        stage.LED_control('0,0,0')
        time.sleep(5)

