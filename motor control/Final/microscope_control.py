# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Simple stage control for Fergus Riche's "fergboard" controller.

Written 2016 by Richard Bowman, Abhishek Ambekar, James Sharkey and Darryl Foo

Released under GNU GPL v3 or later.

Usage:
    microscope move <x> <y> [<z>]
    microscope focus <z>
    microscope [options] control [<step_size>]
    microscope [options]

Options:
      --output=<filepath>   Set output directory/filename [default: ~/Desktop/images]
      -h --help             Show this screen.
"""

import io
import sys
import os
import time
import smbus
import serial
import numpy as np
import docopt
import curses
import curses.ascii
import picamera

class Stage:
    def __init__(self, config_dict=None, **kwargs):
        """Class representing a 3-axis microscope stage.
        :param config_file: Either file path or dictionary.
        :param kwargs: Valid ones are the xyz_bound, microsteps and channel."""

        # If config_file is entered as a path string, the file from the path
        # will be read. If it is a dictionary, it is not changed. This
        # prevents the config file being read repeatedly by different
        # objects, rather than once and its value passed around.
        if config_dict is None:
            config_dict = {
                    'backlash':[0]*3,
                    'xyz_bound':[320000]*3,
                    'microsteps':1, #not sure this is used any more?
                    'override':False,
                    'channel':1,
                    }

        self.config_dict = config_dict

        # Check these bounds.
        self._XYZ_BOUND = np.array(self.config_dict["xyz_bound"])
        # How many micro-steps per step?
        self._MICROSTEPS = self.config_dict["microsteps"]

        self.bus = smbus.SMBus(self.config_dict["channel"])
        time.sleep(0.2)
        self.position = np.array([0, 0, 0])

    def move_rel(self, vector, backlash=None, override=None):
        """Move the stage by (x,y,z) micro steps.
        :param vector: The increment to move by along [x, y, z].
        :param backlash: An array of the backlash along [x, y, z].
        :param override: Set to True to ignore the limits set by _XYZ_BOUND,
        otherwise an error is raised when the bounds are exceeded."""

        if backlash is None:
            backlash = self.config_dict.get('backlash',[0,0,0])
        if override is None:
            override = self.config_dict.get('override',False)

        # Check backlash  and the vector to move by have the correct format.
        assert np.all(backlash >= 0), "Backlash must >= 0 for all [x, y, z]."
        #backlash = h.verify_vector(backlash)
        r = np.array(vector) #h.verify_vector(vector)

        # Generate the list of movements to make. If backlash is [0, 0, 0],
        # there is only one motion to make.
        movements = []
        if np.any(backlash != np.zeros(3)):
            # Subtract an extra amount where vector is negative.
            r[r < 0] -= backlash[np.where(r < 0)]
            r2 = np.zeros(3)
            r2[r < 0] = backlash[np.where(r < 0)]
            movements.append(r2)
        movements.insert(0, r)

        for movement in movements:
            new_pos = np.add(self.position, movement)
            # If all elements of the new position vector are inside bounds (OR
            # overridden):
            if np.all(np.less_equal(
                    np.absolute(new_pos), self._XYZ_BOUND)) or override:
                _move_motors(self.bus, *tuple(movement))
                self.position = new_pos
            else:
                raise ValueError('New position is outside allowed range.')

    def move_to_pos(self, final, override=None):

        #[override] = h.check_defaults([override], self.config_dict, ["override"])
        if override is None:
            override = self.config_dict('override')

        new_position = final#h.verify_vector(final)
        rel_mov = np.subtract(new_position, self.position)
        return self.move_rel(rel_mov, override=override)

    def focus_rel(self, z):
        """Move the stage in the Z direction by z micro steps."""
        self.move_rel([0, 0, z])

    def centre_stage(self):
        """Move the stage such that self.position is (0,0,0) which in theory
        centres it."""
        self.move_to_pos([0, 0, 0])

    def _reset_pos(self):
        # Hard resets the stored position, just in case things go wrong.
        self.position = np.array([0, 0, 0])


def _move_motors(bus, x, y, z):
    """Move the motors for the connected module (addresses hardcoded) by a
    certain number of steps.
    :param bus: The smbus.SMBus object connected to appropriate i2c channel.
    :param x: Move x-direction-controlling motor by specified number of steps.
    :param y: "
    :param z: "."""
    [x, y, z] = [int(x), int(y), int(z)]

    # The arguments for write_byte_data are: the I2C address of each motor,
    # the register and how much to move it by. Currently hardcoded in.
    bus.write_byte_data(0x08, x >> 8, x & 255)
    bus.write_byte_data(0x10, y >> 8, y & 255)
    bus.write_byte_data(0x18, z >> 8, z & 255)

    # Empirical formula for how micro step values relate to rotational speed.
    # This is only valid for the specific set of motors tested.
    time.sleep(np.ceil(max([abs(x), abs(y), abs(z)]))*(1.4/1000) + 0.1)

def validate_filepath(filepath):
    """Check the filepath is valid, creating dirs if needed
    The final format is  ~/Desktop/images/image_%d.img  
    %d is formatted with number by (filepath %n)
    https://pyformat.info/"""

    filepath = os.path.expanduser(filepath)
    if "%d" not in filepath and ".jp" not in filepath:
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        return os.path.join(filepath, "image_%03d.jpg")

    elif "%d" not in filepath and ".jp" in filepath:
        'add automatic numbering to filename'

        return filepath
    
    elif "%d" in filepath and ".jp" in filepath:
        return filepath
    
    else:
        raise ValueError("Error setting output filepath.  Valid filepaths should"
                         " either be [creatable] directories, or end with a "
                         "filename that contains '%d' and ends in '.jpg' or '.jpeg'")

class camera_control():
    def __init__(self):
    #defines some camera parameters 
        self.stage = Stage()
        camera_resolution = (3280, 2464)
        #camera_resolution = (1024, 768)
        self.camera = picamera.PiCamera(resolution = camera_resolution)
        # some initial default values
        
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = (1.5,1.1)
        self.camera.iso = 0
        # when set exposure_mode to "off", output will be black
        #self.camera.exposure_mode = 'auto'
        self.camera.shutter_speed = 50 # condenser require much lower shutter speed
        self.camera.saturation = 0
        self.camera.annotate_text_size = int(camera_resolution[0]*0.03) # reasonable ratio for any resolution
        self.step = 300

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
        # 'save_image' cannot be the last elif for some reason?
        elif argv == 'save_image':
            # remove any text overlay
            self.camera.annotate_text = ""
            folder = value[0]
            if not os.path.isdir(folder):
                os.mkdir(folder)
            image_filepath = value[1]
            while True:
                if os.path.isfile(image_filepath):
                    # if there is a file with same name, add a -new behind file name
                    image_filepath = image_filepath.split('.')
                    image_filepath = image_filepath[0] + '-new.' + image_filepath[1]
                else:
                    break
            # save the raw data on jpeg
            self.camera.capture(image_filepath, 'jpeg', bayer = True)
            # self.camera.capture(image_filepath, 'jpeg', bayer = False)
            self.camera.annotate_text = "Image saved as {}".format(image_filepath)
        elif argv == 'zoom_in' or 'zoom_out':
            if argv == 'zoom_in':
                self.fov = self.fov*3/4
            elif argv == 'zoom_out' and self.fov < 1:
                self.fov = self.fov*4/3
            self.camera.zoom = (0.5-self.fov/2, 0.5-self.fov/2, self.fov, self.fov)
            self.camera.annotate_text = 'magnification: {0:.2f}X'.format(1/self.fov)


#run microscope_control.py directly
if __name__ == '__main__':
    argv = docopt.docopt(__doc__, options_first=True)
    
    stage = Stage()

    if argv['move']:
        x, y, z = [int(argv.get(d, 0)) for d in ['<x>', '<y>', '<z>']]
        print ("moving", x, y, z)
        stage.move_rel([x, y, z])
    elif argv['focus']:
        stage.focus_rel(int(argv['<z>']))
    else: #if argv['control']:
        def move_stage_with_keyboard(stdscr):
            stdscr.addstr(0,0,"wasd to move in X/Y, qe for Z\n"
                          "r/f to decrease/increase step.\n"
                          "v/b to start/stop video preview.\n"
                          "i/o to zoom in/out.\n"
                          "t/g to adjust contrast, y/h to adjust brightness.\n"
                          "j to save jpeg file, k to change output path.\n"
                          "x to quit\n")
            step = int(argv.get('<step>',100))
            filepath = validate_filepath(argv['--output'])
            fov = 1
            with picamera.PiCamera(sensor_mode=2, resolution=(3280,2464)) as camera:
                while True:
                    c = stdscr.getch()
                    if curses.ascii.isascii(c):
                        c = chr(c)
                    if c == 'x':
                        break
                    elif c == 'w' or c == curses.KEY_UP:
                        stage.move_rel([0,step,0])
                    elif c == 'a' or c == curses.KEY_LEFT:
                        stage.move_rel([step,0,0])
                    elif c == 's' or c == curses.KEY_DOWN:
                        stage.move_rel([0,-step,0])
                    elif c == 'd' or c == curses.KEY_RIGHT:
                        stage.move_rel([-step,0,0])
                    elif c == 'q' or c == curses.KEY_PPAGE:
                        stage.move_rel([0,0,-step])
                    elif c == 'e' or c == curses.KEY_NPAGE:
                        stage.move_rel([0,0,step])
                    elif c == "r" or c == '-' or c == '_':
                        step /= 2
                    elif c == "f" or c == '+' or c == '=':
                        step *= 2
                    elif c == 'i':
                        fov *= 0.75
                        camera.zoom = (0.5-fov/2, 0.5-fov/2, fov, fov)
                    elif c == 'o':
                        if fov < 1.0:
                            fov *= 4.0/3.0
                        camera.zoom = (0.5-fov/2, 0.5-fov/2, fov, fov)
                    elif c == 't':
                        if camera.contrast <= 90:
                            camera.contrast += 10
                    elif c == 'g':
                        if camera.contrast >= -90:
                            camera.contrast -= 10
                    elif c == 'y':
                        if camera.brightness <= 90:
                            camera.brightness += 10
                    elif c == 'h':
                        if camera.brightness >= -90:
                            camera.brightness -= 10
                    elif c == 'n':
                        if camera.shutter_speed <= 1000000:
                            camera.shutter_speed += 1000
                    elif c == 'm':
                        if camera.shutter_speed >= 1000:
                            camera.shutter_speed -= 1000
                    elif c == "v":
                        camera.start_preview()
                    elif c == "b":
                        camera.stop_preview()
                    elif c == "j":
                        n = 0
                        while os.path.isfile(os.path.join(filepath % n)):
                            n += 1
                        camera.capture(filepath % n, format="jpeg", use_video_port=True)
                        camera.annotate_text="Saved '%s'" % (filepath % n)
                        try:
                            stdscr.addstr("Saved '%s'\n" % (filepath % n))
                        except:
                            pass
                        time.sleep(0.5)
                        camera.annotate_text=""
                    elif c == "k":
                        camera.stop_preview()
                        stdscr.addstr("The new output location can be a directory or \n"
                                      "a filepath.  Directories will be created if they \n"
                                      "don't exist, filenames must contain '%d' and '.jp'.\n"
                                      "New filepath: ")
                        curses.echo()
                        new_filepath = stdscr.getstr()
                        curses.noecho()
                        if len(new_filepath) > 3:
                            filepath = validate_filepath(new_filepath)
                        stdscr.addstr("New output filepath: %s\n" % filepath)

        curses.wrapper(move_stage_with_keyboard)


