# -*- coding: utf-8 -*-
"""

Kivy interface for WaterScope motor control and picamera control

Usage:
    1. Press start preview to start streaming microscopic image
    2. swipe horizontal and vertical to move field of view
    3. pinch in and out to zoom in and out
    4. Press + and - to move focus up and down

@author: Tianheng Zhao
"""
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


#kivy.require('1.9.1')   # replace with your current kivy version !

#import microscope control parts

class control_elements(object):
    def __init__(self):
        self.drag_x_sensitive = Window.width*0.2
        self.drag_y_sensitive = Window.height*0.2
        self.folder_sign = '/' # different os may use different sign / or \
        self.image_number = 1
        self.folder=self.folder_sign.join(['','home', 'pi', 'Desktop',''])
        self.filename='{:%Y%m%d}'.format(datetime.today())
        self.filetype = '.jpg'
        self.filepath_update = True
        self.time_lapse_interval = 0.5


    def create_exit_button(self):
        exit_button = Button(text = 'exit', size_hint_y = 0.2 , background_color = [1, 0, 0, 1])

        def exit_GUI(instance):
            """function to quit GUI"""
            print('quitting')
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
            if instance.text == '+':
                print('focus + ')
            elif instance.text == '-':
                print('focus - ')

        focus_button_up.bind(on_press = focus_control)  #start_preview functions
        focus_button_down.bind(on_press = focus_control)
        return focus_label, focus_button_up, focus_button_down

    def create_step_slider(self):
        """Manipulate step of motor movement"""
        default_step = 300
        step_slider_label = Label(
            text='\n Motor \n steps: \n'+'{}'.format(default_step),
            color = [0.2,0.2,1,1], halign = 'center', valign = 'middle',
            size_hint_y = 0.1)
        step_slider = Slider(
            min=0, max=1000, value= default_step,
            orientation = 'vertical', size_hint_y = 0.35)

        def motor_step_control(instance, value):
            """change step and update label when using step_slider"""
            control_elements.step_value = int(value)
            step_slider_label.text = '\n Motor \n steps: \n'+'{}'.format(control_elements.step_value)
            # mc.step = control_elements.step_value

        step_slider.bind(value = motor_step_control)
        return step_slider_label, step_slider

    def create_map_controller(self):
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
        map_controller.add_widget(Image())

        def map_control_feedback(instance, value):
            """the callback functions for map_controller scatter object"""
            if map_controller.center[0] - Window.center[0] > self.drag_x_sensitive:
                # mc.stage_library('move_x', '-')
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
        #after taking actions, reset scatter location and scale to default
        map_controller.center = Window.center
        map_controller.scale = default_scale

        map_controller.bind(on_touch_up = map_control_feedback)
        return map_controller

    def create_preview_buttons(self):
        start_preview_button = Button(text = 'preview', size_hint_y = 0.1)
        stop_preview_button = Button(text = 'stop \npreview', size_hint_y = 0.1)
        
        def preview_control(instance):
            if instance.text == 'preview':
                print('start_preview')
            else:
                print('stop_preview')

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
                                'y':0.95-settings_popup.size_hint[1]/2} # distance from popup.center
        settings_popup_content = GridLayout(cols=1) # a blank layout to put other widgets in
        settings_popup.content = settings_popup_content

        def preview_window_resize(instance, argv):
            if argv == 'fullscreen':
                print('full screen preview')
            if argv == 'resized':
                print('resized preview')
            """when popup get dismissed, revert camera preview window to normal"""
            '''mc.camera_library('stop_preview')
            mc.camera_library('fullscreen_preview')'''
            pass
        def reduced_size_preview(instance):
            """when popup get opened, reduce camera preview window size to prevent blocking"""
            '''mc.camera_library('stop_preview')
            reduced_size_window = [Window.width*0.2, Window.height*0.25, Window.width*0.6, Window.width*0.6/1.33]
            for i in range(len(reduced_size_window)):
                reduced_size_window[i] = int(reduced_size_window[i])
            reduced_size_window = tuple(reduced_size_window)
            mc.camera_library('reduced_size_preview', reduced_size_window)'''
            pass
            
        settings_popup.bind(on_dismiss = partial(preview_window_resize, 'fullscreen'))
        settings_popup.bind(on_open =  partial(preview_window_resize, 'resized'))
        
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
            elif instance == filepath_button:
                settings_popup_content.add_widget(filepath_controller)
                self.filepath_input.text = self.format_filepath()

        # add buttons to call out popups
        # settings_panel with 3 buttons on it
        settings_panel, contrast_button, brightness_button, filepath_button = self.create_settings_panel()
        brightness_controller, contrast_controller = self.create_settings_controllers()
        filepath_controller = self.create_filepath_controller()
        for button in [settings_button, contrast_button, brightness_button, filepath_button]:
            button.bind(on_release= switch_settings_popup_content)
        return settings_button

    def create_settings_panel(self):
        """a panel to host different option buttons to call individual popup"""
        settings_panel = BoxLayout()
        contrast_button = Button(text='contrast')
        brightness_button = Button(text='brightness')
        filepath_button = Button(text='change filepath')
        for i in [contrast_button, brightness_button, filepath_button]:
            settings_panel.add_widget(i)
        return settings_panel, contrast_button, brightness_button, filepath_button

    def create_settings_controllers(self):
        '''controllers(slider, input box) for brightness, contrast, etc.'''
        # crate a horizontal boxlayout to include label, slider and input box
        brightness_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
        brightness_label = Label(text = 'Brightness:', size_hint_x = 0.2)
        brightness_slider = Slider(min = 0, max = 100, value = 50, size_hint_x = 0.5)
        brightness_input = TextInput(
            text = '{}'.format(int(brightness_slider.value)),
            multiline = False,  size_hint_x = 0.3)
        # add widgets to the boxlayout (controller)
        for i in [brightness_label, brightness_input, brightness_slider]:
            brightness_controller.add_widget(i)
        # contrast control
        contrast_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
        contrast_label = Label(text = 'Contrast:', size_hint_x = 0.2)
        contrast_slider = Slider(min=0, max=64, value= 1,  size_hint_x = 0.5)
        contrast_input = TextInput(
            text = '{}'.format(int(contrast_slider.value)),
            multiline = False, size_hint_x = 0.3)
        for i in [contrast_label, contrast_input, contrast_slider]:
            contrast_controller.add_widget(i)

        def settings_control(instance,*value):
            """callback function of sliders and input box for brightness/contrast
            
            update sliders with TextInput and vice versa. update camera settings"""
            # update Slider and TextInput
            for slider, textinput in [  # for i, j in [[1,2],[3,4]]: >>>i = 1,3  j = 2,4
                [brightness_slider, brightness_input],
                [contrast_slider, contrast_input]]: 

                if instance == slider:
                    # unified variable to define brightness
                    # returns a tuple due to optional arguments
                    updated_value = int(slider.value)
                    textinput.text = str(updated_value)
                elif instance == textinput:
                    # when value is out of range, set it to max/min
                    if int(textinput.text) >= slider.max:
                        textinput.text = str(int(slider.max)) # float will give error for slider
                    elif int(textinput.text) <= slider.min:
                        textinput.text = str(int(slider.min))
                    updated_value = int(textinput.text)
                    slider.value = updated_value
                # call microscope library to update the brightness and contrast 
                print('brightness: {}'.format(brightness_slider.value))
                print('contrast: {}'.format(contrast_slider.value))

        # bind sliders and input box to callback functions
        for slider, textinput in [  # for i, j = [[1,2][3,4]]  >>>i = 1,3  j = 2,4
                [brightness_slider, brightness_input],
                [contrast_slider, contrast_input]]: 
            slider.bind(value = settings_control)
            textinput.bind(on_text_validate = settings_control)
        return brightness_controller, contrast_controller


    def create_filepath_controller(self):
        filepath_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
        folder_chooser_button = Button(text = 'File viewer \nto choose folder', size_hint_x = 0.2) # a button to popup filechooser
        self.filepath_input = TextInput(multiline = False, 
            size_hint_x = 1 - folder_chooser_button.size_hint_x)
        control_elements.filepath = self.format_filepath() # use the default value which contains date and start from 001
        self.filepath_input.text = control_elements.filepath
        for i in [self.filepath_input, folder_chooser_button]:
            filepath_controller.add_widget(i)
        folder_chooser = FileChooser()
        folder_chooser.add_widget(FileChooserIconLayout())
    # a popup window to choose folder
        folder_chooser_popup = Popup(title = 'choose folder to save image', size_hint = (0.8, 0.8))
        folder_chooser_popup.pos_hint =  {'x':0.5-folder_chooser_popup.size_hint[0]/2,
                                'y':0.5-folder_chooser_popup.size_hint[1]/2} 
        folder_chooser_popup.content = folder_chooser
            
        def choose_folder(instance, value):
            '''Callback function for FileChooser'''
            self.folder = str(value) + self.folder_sign
            print(self.folder)
            self.filepath = self.format_filepath()
            self.filepath_input.text = self.filepath
        

        def update_filepath_input(instance):
            '''Callback function for TextInput'''
            # seperate filepath_input elements
            self.filepath = self.filepath_input.text
            filepath_split = self.filepath.split(self.folder_sign)
            self.filename = filepath_split[-1] # last element after the folder sign 
            self.folder = self.folder_sign.join(filepath_split[0:-1]) + self.folder_sign 
            # format filepath and update filepath_input
            self.filepath = self.format_filepath()
            self.filepath_input.text = self.filepath

        folder_chooser_button.bind(on_release = folder_chooser_popup.open)
        folder_chooser.bind(path = choose_folder)
        self.filepath_input.bind(on_text_validate = update_filepath_input)
        return filepath_controller

    def format_filepath(self):
        """set default value for filepath, also allow update """
        # Keep track of change of folder and filename and update filepath immediately"""
        # this is global so timelapse function can change it
        # if user have input a filetype
        filename_elements = self.filename.split('.')
        try:
            if self.filepath_update == True: # only change image_number when user change filepath_input
                if filename_elements[1] in ['jpg', 'jpeg', 'JPG', 'JPEG']:
                    self.filetype = '.jpg'
                if filename_elements[1] in ['tif', 'tiff', 'TIF', 'TIFF']:
                    self.filetype = '.tiff'
        except IndexError:
            self.filetype = '.jpg'
        # if user have input a image_number
        filename_elements = filename_elements[0].split('-')
        if len(filename_elements) == 1:
            self.filename = filename_elements[0]
        if len(filename_elements) >= 2:
            # only change image_number when user change filepath_input
            if self.filepath_update == True: 
                try: 
                    self.image_number = int(filename_elements[-1])
                except ValueError:
                    self.image_number = 1
            self.filename = '-'.join(filename_elements[0:-1])
                
        # if there is no specified self.image_number, then use the system-wide number (default: 1)
        self.filename = self.filename + '-{:03}'.format(self.image_number) + self.filetype
        self.filepath = self.folder + self.filename
        return self.filepath




    def create_save_image_buttons(self):
        '''a global filepath to save image to'''
        time_lapse_layout = BoxLayout(orientation = 'vertical', size_hint_y = 0.6)
        save_image_button = Button(text = 'save image', size_hint_y = 0.2, background_color = [0, 0.3, 1, 1]) 
        time_lapse_interval_input = TextInput(text = '60', multiline = False, size_hint_y = 0.3)
        time_lapse_interval_label = Label(text = 'time_lapse\ninterval(sec)', size_hint_y = 0.15, color = [0, 1, 0, 1])
        time_lapse_button = Switch(size_hint_y = 0.2) # need to make a popup to choose time_interval etc.
        time_lapse_button_label = Label(text = 'on/off\ntime_lapse', size_hint_y = 0.15,  color = [0, 1, 0, 1])
        

        def save_image(instance):
            ''' Callback for save_image_button'''
            self.filepath_update = False # this prevents saving image mess up naming 
            self.filepath = self.format_filepath()
            self.filepath_update = True 
            print('save image to {}'.format(self.filepath))
            self.image_number = self.image_number + 1

        def start_time_lapse(instance, value):
            ''' Callback for time_lapse_button'''
            try: 
                self.time_lapse_interval = float(time_lapse_interval_input.text)
            except:
                time_lapse_interval_input.text = '60'
                self.time_lapse_interval = float(time_lapse_interval_input.text)

            print(self.time_lapse_interval)
            if value is True:
                self.event = Clock.schedule_interval(save_image, self.time_lapse_interval)
                self.event()
            elif value is False:
                # unschedule using cancel
                Clock.unschedule(self.event)

        save_image_button.bind(on_release = save_image)
        time_lapse_button.bind(active = start_time_lapse)
        for i in [save_image_button, time_lapse_interval_label, time_lapse_interval_input, time_lapse_button_label, time_lapse_button]:
            time_lapse_layout.add_widget(i)

        return time_lapse_layout

def add_main_page_widgets():
    """Add layouts and widgets to a page (main page)"""
    # defining all the elements here: buttons, sliders, map_controllers
    buttons = control_elements()
    exit_button = buttons.create_exit_button()
    start_preview_button, stop_preview_button = buttons.create_preview_buttons()
    time_lapse_layout = buttons.create_save_image_buttons()
    #settings_button, back_to_main_button = create_page_buttons()
    settings_button = buttons.create_settings_button()
    focus_label, focus_button_up, focus_button_down = buttons.create_focus_buttons()
    step_slider_label, step_slider  = buttons.create_step_slider()
    map_controller = buttons.create_map_controller()

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
    horizontal_layout_3.add_widget(settings_button)

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
