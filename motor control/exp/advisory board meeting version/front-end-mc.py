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

from datetime import datetime
import time

import kivy
from kivy.app import App  # base Class of your App inherits from the App class
from kivy.core.window import Window  # This helps define window size, center..
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
# import layout
# A layout is a special kind of widget that manages the size and/or position of its child widgets
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
# import widgets
from kivy.uix.label import Label
# This can be moved, resized and rotated by interactions
from kivy.uix.scatter import Scatter
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout
# import kivy misc
from kivy.clock import Clock

#kivy.require('1.9.1')   # replace with your current kivy version !

#import microscope control parts
import microscope_control as mc

def create_exit_button():
    exit_button = Button(text = 'exit', size_hint_y = 0.2 , background_color = [1, 0, 0, 1])

    def exit_GUI(instance):
        """function to quit GUI"""
        print('quitting')
        raise SystemExit(0)

    exit_button.bind(on_press = exit_GUI)

    return exit_button


def create_map_controller():
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
    x_sensitive = Window.width*0.2
    y_sensitive = Window.height*0.2
    # dummy object showing active area
    # map_controller.add_widget(Image())

    def map_control_feedback(instance, value):
        """the callback functions for map_controller scatter object"""
        if map_controller.center[0] - Window.center[0] > x_sensitive:
            mc.stage_library('move_x', '-')
        elif map_controller.center[0] - Window.center[0] < -1* x_sensitive:
            mc.stage_library('move_x', '+')
        elif map_controller.center[1] - Window.center[1] > y_sensitive:
            mc.stage_library('move_y', '-')
        elif map_controller.center[1] - Window.center[1] < -1*y_sensitive:
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

def create_preview_buttons():
    start_preview_button = Button(text = 'preview')
    stop_preview_button = Button(text = 'stop \npreview')
    def preview_control(instance):
        mc.fov = 1.00 #initialise the zoom level
        if instance.text == 'preview':
            mc.camera_library('start_preview')
        else:
            mc.camera_library('stop_preview')

    start_preview_button.bind(on_press = preview_control)  #start_preview functions
    stop_preview_button.bind(on_press = preview_control)

    return start_preview_button, stop_preview_button

def create_focus_buttons():
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
        if instance == focus_button_up:
            mc.stage_library('move_z','+')
        elif instance == focus_button_down:
            mc.stage_library('move_z','-')

    focus_button_up.bind(on_press = focus_control)  #start_preview functions
    focus_button_down.bind(on_press = focus_control)
    return focus_label, focus_button_up, focus_button_down

def create_step_slider():
    """Manipulate step of motor movement"""
    step_value = 300 # default value
    mc.step = step_value
    step_slider_label = Label(
        text='\n Motor \n steps: \n'+'{}'.format(step_value),
        color = [0.2,0.2,1,1], halign = 'center', valign = 'middle',
        size_hint_y = 0.1)
    step_slider = Slider(
        min=0, max=1000, value= step_value,
        orientation = 'vertical', size_hint_y = 0.35)

    def motor_step_control(instance, value):
        """change step and update label when using step_slider"""
        step_value = int(value)
        step_slider_label.text = '\n Motor \n steps: \n'+'{}'.format(step_value)
        mc.step = step_value
    
    step_slider.bind(value = motor_step_control)

    return step_slider_label, step_slider


def create_settings_button():
    # a button to call out settings panel
    settings_button = Button(text = 'settings')

    # configure a popup window to display settings and parameters
    settings_popup = Popup( title='Settings', size_hint=(0.8, 0.2))
    settings_popup.pos_hint =  {'x':0.5-settings_popup.size_hint[0]/2,
                               'y':0.9-settings_popup.size_hint[1]/2} # distance from popup.center
    settings_popup_content = GridLayout(cols=1) # a blank layout to put other widgets in
    settings_popup.content = settings_popup_content
    
    # when popup occurs, rezie the preview screen to prevent blockage?
    def fullscreen_preview(instance):
        """when popup get dismissed, revert camera preview window to normal"""
        mc.camera_library('stop_preview')
        mc.camera_library('fullscreen_preview')
    def reduced_size_preview(instance):
        """when popup get opened, reduce camera preview window size to prevent blocking"""
        mc.camera_library('stop_preview')
        reduced_size_window = (int(Window.width*0.2), int(Window.height*0.25), int(Window.width*0.6), int(Window.width*0.6/1.33))
        mc.camera_library('reduced_size_preview',reduced_size_window)
        
    settings_popup.bind(on_dismiss = fullscreen_preview)
    settings_popup.bind(on_open = reduced_size_preview)

    def switch_settings_popup_content(instance):
        """alter popup content when clicking buttons"""
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
            mc.camera_library('stop_preview') # the preview will block the keyboard
            filepath_input.text = format_filepath()

    
    # add buttons to call out popups
    # settings_panel with 3 buttons on it
    settings_panel, contrast_button, brightness_button, filepath_button = create_settings_panel()
    brightness_controller, contrast_controller = create_settings_controllers()
    filepath_controller = create_filepath_controller()

    for button in [settings_button, contrast_button, brightness_button, filepath_button]:
        button.bind(on_release= switch_settings_popup_content)

    return settings_button

def create_settings_panel():
    """a panel to host different option buttons to call individual popup"""
    settings_panel = BoxLayout()
    contrast_button = Button(text='contrast')
    brightness_button = Button(text='brightness')
    filepath_button = Button(text='change filepath')
    for i in [contrast_button, brightness_button, filepath_button]:
        settings_panel.add_widget(i)
    return settings_panel, contrast_button, brightness_button, filepath_button

def create_settings_controllers():
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
    contrast_slider = Slider(min=-100, max=100, value= 0,  size_hint_x = 0.5)
    contrast_input = TextInput(
        text = '{}'.format(int(contrast_slider.value)),
        multiline = False, size_hint_x = 0.3)
    for i in [contrast_label, contrast_input, contrast_slider]:
        contrast_controller.add_widget(i)

    def settings_control(instance,*value):
        """update sliders with TextInput and vice versa. update camera settings"""
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
            mc.camera_library('set_brightness', brightness_slider.value)
            mc.camera_library('set_contrast', contrast_slider.value)

    # bind sliders and input box to callback functions
    for slider, textinput in [  # for i, j = [[1,2][3,4]]  >>>i = 1,3  j = 2,4
            [brightness_slider, brightness_input],
            [contrast_slider, contrast_input]]: 
        slider.bind(value = settings_control)
        textinput.bind(on_text_validate = settings_control)

    return brightness_controller, contrast_controller


def create_filepath_controller():
    global filepath_input # require to update in another function
    
    filepath_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    folder_chooser_button = Button(text = 'File viewer \nto choose folder', size_hint_x = 0.2) # a button to popup filechooser
    filepath_input = TextInput(multiline = False, 
        size_hint_x = 1 - folder_chooser_button.size_hint_x)
    filepath = format_filepath() # use the default value which contains date and start from 001
    filepath_input.text = filepath
    for i in [filepath_input, folder_chooser_button]:
        filepath_controller.add_widget(i)

    folder_chooser = FileChooser()
    folder_chooser.add_widget(FileChooserIconLayout())
# a popup window to choose folder
    folder_chooser_popup = Popup(title = 'choose folder to save image', size_hint = (0.8, 0.8))
    folder_chooser_popup.pos_hint =  {'x':0.5-folder_chooser_popup.size_hint[0]/2,
                               'y':0.5-folder_chooser_popup.size_hint[1]/2} 
    folder_chooser_popup.content = folder_chooser
    folder_chooser_button.bind(on_release = folder_chooser_popup.open)
    
    def choose_folder(instance, value):
        global folder, folder_sign
        folder = str(value) + folder_sign
        filepath = format_filepath()
        filepath_input.text = filepath
    
    folder_chooser.bind(path = choose_folder)

    def update_filepath_input(instance):
        global folder, filename, folder_sign, filetype
        # seperate filepath_input elements
        filepath = filepath_input.text
        filepath_split = filepath.split(folder_sign)
        filename = filepath_split[-1] # last element after the folder sign 
        folder = folder_sign.join(filepath_split[0:-1]) + folder_sign 
        # format filepath and update filepath_input
        filepath = format_filepath()
        filepath_input.text = filepath

    filepath_input.bind(on_text_validate = update_filepath_input)

    return filepath_controller


# default value when initialise the app
folder_sign = '/' # different os may use different sign / or \
image_number = 1
folder=folder_sign.join(['','home', 'pi', 'Desktop', 'images',''])
filename='{:%Y%m%d}'.format(datetime.today())
filetype = '.jpg'
def format_filepath(update = False):
    """set default value for filepath, also allow update """
    # Keep track of change of folder and filename and update filepath immediately"""
      # this is global so timelapse function can change it
    # if user have input a filetype 
    global image_number, folder, filename, filetype
    filename_elements = filename.split('.')
    try:
        if update == False: # only change image_number when user change filepath_input
            if filename_elements[1] in ['jpg', 'jpeg', 'JPG', 'JPEG']:
                filetype = '.jpg'
            if filename_elements[1] in ['tif', 'tiff', 'TIF', 'TIFF']:
                filetype = '.tiff'
    except IndexError:
        filetype = '.jpg'
    # if user have input a image_number
    filename_elements = filename_elements[0].split('-')
    if len(filename_elements) == 1:
        filename = filename_elements[0]
    if len(filename_elements) >= 2:
        if update == False: # only change image_number when user change filepath_input
            try: 
                image_number = int(filename_elements[-1])
            except ValueError:
                image_number = 1
        filename = '-'.join(filename_elements[0:-1])
            
    # if there is no specified image_number, then use the system-wide number (default: 1)
    filename = filename + '-{:03}'.format(image_number) + filetype
    filepath = folder + filename
    return filepath


def create_save_image_buttons():
    '''a global filepath to save image to'''
    save_image_button = Button(text = 'save image')
    time_lapse_button = Button(text = 'start \ntime lapse') # need to make a popup to choose time_interval etc.

    def save_image(instance):
        global image_number
        filepath = format_filepath(update = True)
        print(folder)
        print(filepath)
        mc.camera_library('save_image', folder, filepath)
        image_number = image_number + 1

    def start_time_lapse(instance):
        '''time_lapse_state = False
        time_lapse_state = not time_lapse_state
        time_lapse_interval = .5
        event = Clock.schedule_interval(save_image, time_lapse_interval)'''
        pass
        
    save_image_button.bind(on_release = save_image)
    time_lapse_button.bind(on_release = start_time_lapse)
    return save_image_button, time_lapse_button

def add_main_page_widgets():
    """Add layouts and widgets to a page (main page)"""
    # defining all the elements here: buttons, sliders, map_controllers
    exit_button = create_exit_button()
    start_preview_button, stop_preview_button = create_preview_buttons()
    save_image_button, time_lapse_button = create_save_image_buttons()
    #settings_button, back_to_main_button = create_page_buttons()
    settings_button = create_settings_button()
    focus_label, focus_button_up, focus_button_down = create_focus_buttons()
    step_slider_label, step_slider  = create_step_slider()
    map_controller = create_map_controller()

    #  Create the basic layout with 3 horizontal sections (basic skelton)
    base_layout = BoxLayout(orientation='horizontal')

    # Create the horizontal BoxLayouts in vertical element
    # The preview window's aspect ratio is 4:3 and the touch screen is 5:3.
    # There are gaps with Window.width*0.1 on left and right side
    horizontal_layout_1 = BoxLayout(size_hint_x = 0.1, orientation = 'vertical')
    horizontal_layout_2 = GridLayout(size_hint_x = 0.8, cols = 0)  
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
    horizontal_layout_3.add_widget(save_image_button)
    horizontal_layout_3.add_widget(time_lapse_button)
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
