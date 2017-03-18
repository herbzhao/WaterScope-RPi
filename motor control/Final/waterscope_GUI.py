#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

Kivy interface for WaterScope motor control and picamera control

Usage:
    0. Change the line debug_mode = True to debug_mode = False when using on RaspberryPi
    1. Press start preview to start streaming microscopic image
    2. swipe horizontal and vertical to move field of view
    3. pinch in and out to zoom in and out
    4. Press + and - to move focus up and down

@author: Tianheng Zhao
"""
# set this to True for development on computer, set to Fals to run on RaspberryPi
debug_mode = True
expert_mode = False

import time
from datetime import datetime
from functools import partial

import kivy
from kivy.app import App  # base Class of your App inherits from the App class
# import kivy misc
from kivy.clock import Clock
from kivy.core.window import Window  # This helps define window size, center..
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout
from kivy.uix.floatlayout import FloatLayout
# import layout
# A layout is a special kind of widget that manages the size and/or position of its child widgets
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
# import widgets
from kivy.uix.label import Label
from kivy.uix.popup import Popup
# This can be moved, resized and rotated by interactions
from kivy.uix.scatter import Scatter
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

from PIL import Image as PIL_Image
import os
# customised modules
from read_config import initialise_config
config = initialise_config()
# only read microscope_control if on Pi
if debug_mode is False:
    from microscope_control import camera_control
    try:
        mc = camera_control()
        mc.fov = 1.00 #initialise the zoom level
    except:
        # if there is no camera connected, default set the software to run at debug_mode
        debug_mode = True



#kivy.require('1.9.1')   # replace with your current kivy version !

#import microscope control parts

class create_control_elements(object):
    def __init__(self):
        """ Some default class-wide values"""
        # this determines how much user need to swipe before motor moves in x-y directions
        self.drag_x_sensitive = Window.width*0.15
        self.drag_y_sensitive = Window.height*0.15
        # these are default values for file saving
        self.folder_sign = '/' # different os may use different sign / or \
        self.image_number = 1
        self.folder = self.folder_sign.join(['','home', 'pi', 'Desktop', 'images'])
        # set root folder for FileChooser, prevent saving files to random places
        self.root_folder = self.folder_sign.join(['','home', 'pi', ''])
        self.filename='{:%Y%m%d}'.format(datetime.today())
        self.filetype = '.jpg'
        self.filepath_update = True
        self.time_lapse_interval = 30
        
        if debug_mode is False and expert_mode is False:
            config.read_config_file()
            mc.camera_library('set_iso', config.iso)
            mc.camera_library('set_shutter_speed', config.shutter_speed)
            mc.camera_library('set_white_balance', config.red_gain, config.blue_gain)
        
    def create_exit_button(self):
        exit_button = Button(text = 'exit', size_hint_y = 0.2 , background_color = [1, 0, 0, 1])

        def exit_GUI(instance):
            """ Callback function to quit GUI"""
            print('quitting')
            if debug_mode is False:
                mc.camera_library('stop_preview')
            raise SystemExit(0)

        exit_button.bind(on_press = exit_GUI)
        return exit_button

    def create_focus_buttons(self):
        """+ and - buttons to control focus/Z axis"""
        focus_label = Label(
            text='Focus', color = [0, 1, 0, 1],
            halign = 'center', valign = 'middle', size_hint_y = 0.05)
        focus_button_up = Button(
            text = '+',
            background_color = [0, 1, 0, 1], size_hint_y = 0.15)
        focus_button_down = Button(
            text = '-',
            background_color = [0, 1, 0, 1], size_hint_y = 0.15)

        def focus_control(instance):
            if debug_mode is True:
                if instance.text == '+':
                    print('focus + ')
                elif instance.text == '-':
                    print('focus - ')
            elif debug_mode is False:
                if instance == focus_button_up:
                    mc.stage_library('move_z','+')
                elif instance == focus_button_down:
                    mc.stage_library('move_z','-')

        focus_button_up.bind(on_press = focus_control)  #start_preview functions
        focus_button_down.bind(on_press = focus_control)
        return focus_label, focus_button_up, focus_button_down

    def create_step_slider(self):
        """ Manipulate step of motor movement"""
        default_step = 500
        if debug_mode is False:
            mc.step = default_step
        step_slider_label = Label(
            text='\n Motor \n steps: \n'+'{}'.format(default_step),
            color = [0.2,0.2,1,1], halign = 'center', valign = 'middle',
            size_hint_y = 0.1)
        step_slider = Slider(
            min=0, max=1000, value= default_step,
            orientation = 'vertical', size_hint_y = 0.35)

        def motor_step_control(instance, value):
            """ Change step and update label when using step_slider"""
            self.step_value = int(value)
            step_slider_label.text = '\n Motor \n steps: \n'+'{}'.format(control_elements.step_value)
            if debug_mode is False:
                mc.step = self.step_value

        step_slider.bind(value = motor_step_control)
        return step_slider_label, step_slider

    def create_map_controller(self):
        """ A scatter object to manipulate motor movement"""
        map_controller = Scatter(
            size_hint = (1,1), do_rotation=False, do_translation=True,
            do_scale=True,auto_bring_to_front = False)
        map_controller.center = Window.center
        # automatically determine the size based on screen size
        default_scale = Window.height / map_controller.height*1
        # determine the size of active area
        map_controller.scale = default_scale
        # determine the amount of zoom and drag needed before moving
        map_controller.scale_max = default_scale*1.2
        map_controller.scale_min = default_scale*0.8
        # dummy object showing active area
        if debug_mode is True:
            map_controller.add_widget(Image())
    
        def map_control_feedback(instance, value):
            """the callback functions for map_controller scatter object"""
            if debug_mode is True: 
                if map_controller.center[0] - Window.center[0] > self.drag_x_sensitive:
                    print('moving x+')
                elif map_controller.center[0] - Window.center[0] < -1* self.drag_x_sensitive:
                    print('moving x-')
                elif map_controller.center[1] - Window.center[1] > self.drag_y_sensitive:
                    print('moving y+')
                elif map_controller.center[1] - Window.center[1] < -1* self.drag_y_sensitive:
                    print('moving y-')
                elif map_controller.scale < default_scale*0.9:
                    print('pinch -')
                elif map_controller.scale > default_scale*1.1:
                    print('pinch +')
            elif debug_mode is False:
                if map_controller.center[0] - Window.center[0] > self.drag_x_sensitive:
                    mc.stage_library('move_x', '-')
                elif map_controller.center[0] - Window.center[0] < -1* self.drag_x_sensitive:
                    mc.stage_library('move_x', '+')
                elif map_controller.center[1] - Window.center[1] > self.drag_y_sensitive:
                    mc.stage_library('move_y', '-')
                elif map_controller.center[1] - Window.center[1] < -1*self.drag_y_sensitive:
                    mc.stage_library('move_y', '+')
                elif map_controller.scale < default_scale*0.9:
                    mc.camera_library('zoom_out')
                elif map_controller.scale > default_scale*1.1:
                    mc.camera_library('zoom_in')
            #after taking actions, reset scatter location and scale to default
            map_controller.center = Window.center
            map_controller.scale = default_scale

        map_controller.bind(on_touch_up = map_control_feedback)
        return map_controller

    def create_preview_buttons(self):
        """ Preview and stop preview buttons"""
        start_preview_button = Button(text = 'preview', size_hint_y = 0.1)
        stop_preview_button = Button(text = 'stop \npreview', size_hint_y = 0.1)
        
        def preview_control(instance):
            """ Callback function for preview/stop_preview"""
            if debug_mode is True:
                if instance.text == 'preview':
                    print('start_preview')
                else:
                    print('stop_preview')
            elif debug_mode is False:
                if instance.text == 'preview':
                    mc.camera_library('start_preview')
                else:
                    mc.camera_library('stop_preview')


        start_preview_button.bind(on_press = preview_control)  #start_preview functions
        stop_preview_button.bind(on_press = preview_control)
        return start_preview_button, stop_preview_button

    def create_settings_button(self):
        '''setting button will trigger popup with different settings'''
        # a button to call out settings panel
        settings_button = Button(text = 'settings', size_hint_y = 0.2)

        # configure a popup window to display settings and parameters
        settings_popup = Popup( title='Settings', size_hint=(0.8, 0.2))
        settings_popup.pos_hint =  {'x':0.5-settings_popup.size_hint[0]/2,
                                'y':0.9-settings_popup.size_hint[1]/2} # distance from popup.center
        settings_popup_content = GridLayout(cols=1) # a blank layout to put other widgets in
        settings_popup.content = settings_popup_content

        def preview_window_resize(argv, instance):
            ''' resize the window when popup oppens to prevent camera preview blocks the option
            
            Using partial() makes first argument argv rather than intance'''

            if debug_mode is True:
                if argv == 'fullscreen':
                    print('full screen preview')
                if argv == 'resized':
                    print('resized preview')
            if debug_mode is False:
                if argv == 'fullscreen':
                    mc.camera_library('stop_preview')
                    mc.camera_library('fullscreen_preview')
                if argv == 'resized':
                    mc.camera_library('stop_preview')
                    reduced_size_window = (
                        int(Window.width*0.2), int(Window.height*0.25),
                        int(Window.width*0.6), int(Window.width*0.6/1.33))
                    mc.camera_library('reduced_size_preview', reduced_size_window)
            
        settings_popup.bind(on_dismiss = partial(preview_window_resize, 'fullscreen'))
        settings_popup.bind(on_open = partial(preview_window_resize, 'resized') )
        
        def switch_settings_popup_content(instance):
            """ Callback for different options buttons
            
            alter popup content when clicking buttons"""

            settings_popup_content.clear_widgets()
            settings_popup.open()
            if instance == settings_button:
                settings_popup_content.add_widget(settings_panel)
            elif instance == contrast_button:
                settings_popup_content.add_widget(contrast_controller)
            elif instance == brightness_button:
                settings_popup_content.add_widget(brightness_controller)
            elif instance == white_balance_button:
                settings_popup_content.add_widget(white_balance_controller)
            elif instance == filepath_button:
                if debug_mode is False:
                    mc.camera_library('stop_preview') # the preview will block the keyboard
                settings_popup_content.add_widget(filepath_controller)
                # Update the filepath_input and folder_chooser (after taking images, possibly)
                self.filepath_input.text = self.format_filepath(update = True)
                # go to different folder to refresh the folder_chooser
                self.folder_chooser.path = self.folder

        # add buttons to call out popups
        # settings_panel with 3 buttons on it
        settings_panel, contrast_button, brightness_button, white_balance_button, filepath_button = self.create_settings_panel()
        brightness_controller, contrast_controller, white_balance_controller = self.create_settings_controllers()
        filepath_controller = self.create_filepath_controller()
        for button in [settings_button, contrast_button, brightness_button, white_balance_button, filepath_button]:
            button.bind(on_release= switch_settings_popup_content)
        return settings_button

    def create_settings_panel(self):
        """a panel to host different option buttons to call individual popup"""
        settings_panel = BoxLayout()
        contrast_button = Button(text='contrast')
        brightness_button = Button(text='brightness')
        white_balance_button = Button(text='white balance')
        filepath_button = Button(text='change filepath')
        for i in [contrast_button, brightness_button, white_balance_button, filepath_button]:
            settings_panel.add_widget(i)
        return settings_panel, contrast_button, brightness_button, white_balance_button, filepath_button

    def create_settings_controllers(self):
        '''controllers(slider, input box) for brightness, contrast, etc.'''
        # brightness control
        brightness_controller = BoxLayout(orientation = 'horizontal')
        brightness_slider = Slider(min = 0, max = 100, value = 50, size_hint_x = 0.7)
        brightness_label = Label(
            text = 'Brightness: {}'.format(int(brightness_slider.value),
            size_hint_x = 0.3), font_size='20sp')
        # add widgets to the boxlayout (controller)
        for i in [brightness_label, brightness_slider]:
            brightness_controller.add_widget(i)
        # contrast control
        contrast_controller = BoxLayout(orientation = 'horizontal')
        contrast_slider = Slider(min=0, max=64, value= 1,  size_hint_x = 0.7)
        contrast_label = Label(
            text = 'Brightness:{}'.format(int(contrast_slider.value),
            size_hint_x = 0.3), font_size='20sp')

        for i in [contrast_label, contrast_slider]:
            contrast_controller.add_widget(i)

        # white balance control
        white_balance_controller = BoxLayout(orientation = 'horizontal')
        blue_gain_slider = Slider(min = 0, max = 8.0, value = 1.5, size_hint_x = 0.7)
        blue_gain_label = Label(text = 'Blue gain: {}'.format(float(blue_gain_slider.value)), size_hint_x = 0.3)
        red_gain_slider = Slider(min = 0, max = 8.0, value = 1, size_hint_x = 0.7)
        red_gain_label = Label(text = 'Blue gain: {}'.format(float(blue_gain_slider.value)), size_hint_x = 0.3)
        for i in [blue_gain_label, blue_gain_slider, red_gain_label, red_gain_slider]:
            white_balance_controller.add_widget(i)

        def setting_slider_update_label(instance,*value):
            """callback function of sliders and input box for brightness/contrast 
            update sliders with TextInput and vice versa. update camera settings"""
            # update Slider and TextInput
            for slider, label in [  # for i, j in [[1,2],[3,4]]: >>>i = 1,3  j = 2,4
                [brightness_slider, brightness_label],
                [contrast_slider, contrast_label],
                [red_gain_slider, red_gain_label],
                [blue_gain_slider, blue_gain_label]]: 
                if instance == slider:
                    label.text = label.text.split(':')[0] + ': ' + '{:.1f}'.format(slider.value)
                # call microscope library to update the brightness and contrast 
                if debug_mode is True:
                    print('brightness: {}'.format(brightness_slider.value))
                    print('contrast: {}'.format(contrast_slider.value))
                    print('white balance: red gain: {}, blue gain: {}'.format(red_gain_slider.value, blue_gain_slider.value))
                elif debug_mode is False:
                    mc.camera_library('set_brightness', brightness_slider.value)
                    mc.camera_library('set_contrast', contrast_slider.value)
                    mc.camera_library('set_white_balance', red_gain_slider.value, blue_gain_slider.value)

        # bind sliders and input box to callback functions
        for slider, label in [  # for i, j in [[1,2],[3,4]]: >>>i = 1,3  j = 2,4
            [brightness_slider, brightness_label],
            [contrast_slider, contrast_label],
            [red_gain_slider, red_gain_label],
            [blue_gain_slider, blue_gain_label]]:
            slider.bind(value = setting_slider_update_label)
        return brightness_controller, contrast_controller, white_balance_controller


    def create_filepath_controller(self):
        filepath_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
        folder_chooser_button = Button(text = 'File viewer \nto choose folder', size_hint_x = 0.2) # a button to popup filechooser
        self.filepath_input = TextInput(multiline = False, 
            size_hint_x = 1 - folder_chooser_button.size_hint_x)
        for i in [self.filepath_input, folder_chooser_button]:
            filepath_controller.add_widget(i)
        self.folder_chooser = FileChooser()
        self.folder_chooser.add_widget(FileChooserIconLayout())
    # a popup window to choose folder
        self.folder_chooser_popup = Popup(title = 'choose folder to save image', size_hint = (0.8, 0.8))
        self.folder_chooser_popup.pos_hint =  {'x':0.5-self.folder_chooser_popup.size_hint[0]/2,
                                'y':0.5-self.folder_chooser_popup.size_hint[1]/2} 
        self.folder_chooser_popup.content = self.folder_chooser
        # set the rootpath that user can get access to
        self.folder_chooser.rootpath = self.root_folder
        self.folder_chooser.path = self.folder
        
        def activate_folder_chooser(instance):
            # default open the folder that is selected for saving images
            self.folder_chooser.path = self.folder
            self.folder_chooser_popup.open()
        def choose_folder(instance, value):
            '''Callback function for FileChooser when select folders'''
            self.folder = str(value)
            self.filepath = self.format_filepath(update = True)
            self.filepath_input.text = self.filepath

        def update_filepath_input(instance):
            '''Callback function for TextInput'''
            # seperate filepath_input elements
            self.filepath = self.filepath_input.text
            filepath_split = self.filepath.split(self.folder_sign)
            self.filename = filepath_split[-1] # last element after the folder sign 
            self.folder = self.folder_sign.join(filepath_split[0:-1])
            # format filepath and update filepath_input
            self.filepath = self.format_filepath(update = True)
            self.filepath_input.text = self.filepath

        folder_chooser_button.bind(on_release = activate_folder_chooser)
        self.folder_chooser.bind(path = choose_folder)
        self.filepath_input.bind(on_text_validate = update_filepath_input)
        return filepath_controller

    def image_viewer(self):
        '''A quick and easy image viewer without leaving kivy'''
        image_viewer_button = Button(text = 'image viewer', size_hint_y = 0.2, background_color = [1, 1, 0, 1])
        
        # a popup window to display image
        image_viewer_popup = Popup(title = 'image viewer', size_hint = (1,1))
        image_viewer_exit_button = Button(text = 'exit image preview', size_hint_y = 0.1, font_size='20sp')
        self.image_object = Image(size_hint_y = 0.9)
        image_viewer_layout = BoxLayout(orientation = "vertical")
        image_viewer_layout.add_widget(self.image_object)
        image_viewer_layout.add_widget(image_viewer_exit_button)
        image_viewer_popup.content = image_viewer_layout
        # A count number for preview
        self.temp_file_number = 0

        def activate_folder_chooser(instance):
            if debug_mode is False:
            # When click the time_lapse_interval_input, stop the preview
                mc.camera_library('stop_preview')
            self.folder_chooser.path = self.folder
            self.folder_chooser_popup.open()

        def view_image(instance, value):
            # Callback function for FileChooser when select files
            # change from "['C:\\abc.jpg']" to "C:\\abc.jpg"
            filepath = str(value).replace('[','').replace(']','').replace('\'','')
            # check the file type
            filepath_split = filepath.split('.')

            if filepath_split[-1] in ['jpg', 'jpeg', 'png', 'tif', 'tiff']:
                # if the file is a image, then open the image_viewer
                # use pillow to create a thumbnail of the image, save memory
                size = (Window.width*0.9, Window.height*0.9)
                temp_file_location = "/home/pi/microscope/temp/{}.jpg".format(self.temp_file_number)   
                im = PIL_Image.open(filepath)
                im.thumbnail(size)
                # save as a temporary file
                im.save(temp_file_location, "JPEG")
                im.close()
                im = None
                # load the image again as a kivy object
                self.image_object.source = temp_file_location
                self.temp_file_number += 1
                # scatter_image_object = Scatter(size_hint_x = 0.5, size_hint_y = 0.5)
                # scatter_image_object.add_widget(image_object)
                # image_viewer_popup.content = scatter_image_object
                # add a layout with an exit button
                image_viewer_popup.open()
                os.remove(temp_file_location)

        def dismiss_image_viewer_popup(instance, *value):
            image_viewer_popup.dismiss()
            self.image_object.source = ''

        image_viewer_button.bind(on_release = activate_folder_chooser)
        image_viewer_exit_button.bind(on_release = dismiss_image_viewer_popup)
        # self.folder_chooser.bind(selection = view_image)
        return image_viewer_button


    def format_filepath(self, update):
        """set default value for filepath, also allow update """
        # Keep track of change of folder and filename and update filepath immediately"""
        # this is global so timelapse function can change it
        # if user have input a filetype
        filename_elements = self.filename.split('.')
        try:
            if update == True: # only change image_number when user change filepath_input
                 # automatically change the filetype based on user input
                if filename_elements[1] in ['jpg', 'jpeg', 'JPG', 'JPEG']:
                    self.filetype = '.jpg'
                elif filename_elements[1] in ['tif', 'tiff', 'TIF', 'TIFF']:
                    self.filetype = '.tiff'
                else:
                    self.filetype = '.jpg'
        except IndexError:
            self.filetype = '.jpg'
        # if user have input a image_number
        filename_elements = filename_elements[0].split('-')
        if len(filename_elements) == 1:
            self.filename = filename_elements[0]
        if len(filename_elements) >= 2:
            # only change image_number when user change filepath_input
            if update is True: 
                try: 
                    self.image_number = int(filename_elements[-1])
                except ValueError:
                    self.image_number = 1
            self.filename = '-'.join(filename_elements[0:-1])
                
        # if there is no specified self.image_number, then use the system-wide number (default: 1)
        self.filename = self.filename + '-{:03}'.format(self.image_number) + self.filetype
        self.filepath = self.folder + self.folder_sign + self.filename
        return self.filepath

    def create_save_image_buttons(self):
        time_lapse_layout = BoxLayout(orientation = 'vertical', size_hint_y = 0.6)
        save_image_button = Button(text = 'save image', size_hint_y = 0.2, background_color = [0, 0.3, 1, 1]) 
        time_lapse_interval_input = TextInput(text = str(self.time_lapse_interval), multiline = False, size_hint_y = 0.3)
        time_lapse_interval_label = Label(text = 'time_lapse\ninterval(sec)', size_hint_y = 0.15, color = [0, 1, 0, 1])
        time_lapse_button = Switch(size_hint_y = 0.2) # need to make a popup to choose time_interval etc.
        time_lapse_button_label = Label(text = 'on/off\ntime_lapse', size_hint_y = 0.15,  color = [0, 1, 0, 1])
        
        def save_image(instance):
            ''' Callback for save_image_button'''
            self.filepath_update = False # this prevents saving image mess up naming 
            self.filepath = self.format_filepath(update = False)
            if debug_mode is True:
                print('save image to {}'.format(self.filepath))
            if debug_mode is False:
                mc.camera_library('save_image', self.folder, self.filepath)
            self.image_number = self.image_number + 1

        def start_time_lapse(instance, value):
            ''' Callback for time_lapse_button'''
            update_time_lapse_interval(time_lapse_interval_input)
            if value is True:
                # start time lapse
                save_image('')
                self.event = Clock.schedule_interval(save_image, self.time_lapse_interval)
            if value is False:
                Clock.unschedule(self.event)
        def update_time_lapse_interval(instance):
            try: 
                self.time_lapse_interval = float(time_lapse_interval_input.text)
            except:
                # if the text_input is not a valid value, use 60 as default value
                time_lapse_interval_input.text = str(self.time_lapse_interval)
                self.time_lapse_interval = float(time_lapse_interval_input.text)
                print(self.time_lapse_interval)
            
        save_image_button.bind(on_release = save_image)
        time_lapse_button.bind(active = start_time_lapse)
        if debug_mode is False:
            # When click the time_lapse_interval_input, stop the preview
            time_lapse_interval_input.bind(focus = partial(mc.camera_library, 'stop_preview'))
        time_lapse_interval_input.bind(on_text_validate = update_time_lapse_interval)
        for i in [save_image_button, time_lapse_interval_label, time_lapse_interval_input, time_lapse_button_label, time_lapse_button]:
            time_lapse_layout.add_widget(i)

        return time_lapse_layout


    def create_new_sample_button(self):
        ''' new_sample button, only shows up when expert mode is off'''
        new_sample_button = Button(text = 'new \nsample', size_hint_y = 0.2, background_color = [1, 1, 0, 1])
        def create_new_sample(isinstance, *value):
            config.read_config_file()
            config.record_new_sample()
            config.read_config_file()
            self.folder = '/home/pi/sample_{}'.format(config.last_sample_number)
            self.filename='sample{}'.format(config.last_sample_number)
            self.filetype = '.jpg'
            self.filepath_update = True    
        new_sample_button.bind(on_press = create_new_sample)
        return new_sample_button


def add_main_page_widgets():
    """Add layouts and widgets to a page (main page)"""
    # defining all the elements here: buttons, sliders, map_controllers
    control_element = create_control_elements()
    focus_label, focus_button_up, focus_button_down = control_element.create_focus_buttons()
    step_slider_label, step_slider  = control_element.create_step_slider()
    exit_button = control_element.create_exit_button()
    map_controller = control_element.create_map_controller()
    start_preview_button, stop_preview_button = control_element.create_preview_buttons()
    time_lapse_layout = control_element.create_save_image_buttons()
    settings_button = control_element.create_settings_button()


    # image_viewer_button = control_element.image_viewer()
    new_sample_button = control_element.create_new_sample_button()

    #  Create the basic layout with 3 horizontal sections (basic skelton)
    base_layout = BoxLayout(orientation='horizontal')

    # Create the horizontal BoxLayouts in vertical element
    # The preview window's aspect ratio is 4:3 and the touch screen is 5:3.
    # There are gaps with Window.width*0.1 on left and right side
    horizontal_layout_1 = BoxLayout(size_hint_x = 0.1, orientation = 'vertical')
    horizontal_layout_2 = GridLayout(size_hint_x = 0.8, cols = 0)    #there is some minor bug to fix
    horizontal_layout_3 = BoxLayout(size_hint_x = 0.1,  orientation = 'vertical')
    # add 3 layers to base_layout
    base_layout.add_widget(horizontal_layout_1)
    base_layout.add_widget(horizontal_layout_2)
    base_layout.add_widget(horizontal_layout_3)
    if expert_mode is True:
        # Left section - horizontal_layout_1
        horizontal_layout_1.add_widget(step_slider_label)
        horizontal_layout_1.add_widget(step_slider)
        horizontal_layout_1.add_widget(focus_label)
        horizontal_layout_1.add_widget(focus_button_up)
        horizontal_layout_1.add_widget(focus_button_down)
        horizontal_layout_1.add_widget(exit_button)

        # middle section  - horizontal_layout_2
        horizontal_layout_2.add_widget(map_controller)

        # right section - horizontal_layout_3
        horizontal_layout_3.add_widget(start_preview_button)
        horizontal_layout_3.add_widget(stop_preview_button)
        horizontal_layout_3.add_widget(time_lapse_layout)
        #horizontal_layout_3.add_widget(image_viewer_button)
        horizontal_layout_3.add_widget(settings_button)

    if expert_mode is False:
        if debug_mode is False:
            mc.camera_library('start_preview')
        # Left section - horizontal_layout_1
        # middle section  - horizontal_layout_2
        # right section - horizontal_layout_3
        horizontal_layout_3.add_widget(start_preview_button)
        horizontal_layout_3.add_widget(stop_preview_button)
        horizontal_layout_3.add_widget(new_sample_button)
    # add the basic layout to new screen
    return base_layout


class WaterScopeApp(App):
    """create kivy app
    only ever need to change the name of Myapp"""
    def build(self):
        main_page = add_main_page_widgets()
        return main_page
        
if __name__ == "__main__":
     WaterScopeApp().run()
