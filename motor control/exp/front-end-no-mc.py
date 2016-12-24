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
# import kivy misc
from kivy.uix.screenmanager import (Screen,  # This manage different pages
                                    ScreenManager)
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput

from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout

kivy.require('1.9.1')   # replace with your current kivy version !

#import microscope control parts


def create_exit_button():
    exit_button = Button(text = 'exit', size_hint_y = 0.2 , background_color = [1, 0, 0, 1])

    def exit_GUI(instance):
        """function to quit GUI"""
        print('quitting')
        raise SystemExit(0)

    exit_button.bind(on_press = exit_GUI)

    return exit_button


def create_preview_buttons():
    start_preview_button = Button(text = 'preview')
    stop_preview_button = Button(text = 'stop preview')
    def preview_control(instance):
        pass
    """	mc.fov = 1.00 #initialise the zoom level
        if instance.text == 'preview':
            microscope_control.start_preview()
        else:
            microscope_control.stop_preview()

    microscope_control = microscope_map_controller()"""

    start_preview_button.bind(on_press = preview_control)  #start_preview functions
    stop_preview_button.bind(on_press = preview_control)

    return start_preview_button, stop_preview_button


def create_save_buttons():
    save_button = Button(text = 'save image')
    timelapse_button = Button(text = 'time lapse')
    return save_button, timelapse_button


'''def create_page_buttons():
    """Button to switch between pages"""
    settings_button = Button(text = 'settings')
    back_to_main_button = Button(text = 'back')

    def go_to_page(instance):
        """switch to page/screen based on button.text"""
        if instance.text == "settings":
            sm.current = 'settings page'
        if instance.text == "back":
            sm.current = 'main page'

    settings_button.bind(on_press = go_to_page)
    back_to_main_button.bind(on_press = go_to_page)

    return settings_button, back_to_main_button
'''

def create_step_slider():
    """Manipulate step of motor movement"""
    step_slider_label = Label(
        text='\n Motor \n steps: \n'+'{}'.format(100),
        color = [0.2,0.2,1,1], halign = 'center', valign = 'middle',
        size_hint_y = 0.1)
    step_slider = Slider(
        min=0, max=1000, value= 100,
        orientation = 'vertical', size_hint_y = 0.35)

    def motor_step_control(instance, value):
        """change step and update label when using step_slider"""
        slider_value = int(value)
        print(value)
        step_slider_label.text = '\n Motor \n steps: \n'+'{}'.format(slider_value)
        print (value)

    step_slider.bind(value = motor_step_control)

    return step_slider_label, step_slider


def create_settings_dropdown():
    settings_button = Button(text = 'settings', background_color = [0, 1, 1, 1])
    setting_popup = Popup( title='Setting', size_hint=(0.8, 0.2))
    setting_popup.pos_hint =  {'x':0.5-setting_popup.size_hint[0]/2,
                               'y':0.2-setting_popup.size_hint[1]/2} # distance from popup.center
    setting_popup_content = GridLayout(cols=1) # a blank layout to put other widgets in
    setting_popup.content = setting_popup_content # link the popup.content to a widget
    # controllers to add to content
    brightness_controller, contrast_controller = create_settings_controllers()

    def setting_popup_content_switch(instance, *value):
        """show popup with corresponding setting"""
        setting_popup_content.clear_widgets()
        if instance == contrast_button:
            setting_popup_content.add_widget(contrast_controller)
        elif instance == brightness_button:
            setting_popup_content.add_widget(brightness_controller)
        setting_popup.open()

    contrast_button = Button(text='contrast', size_hint_y = None,  background_color = [0, 1, 1, 1])
    brightness_button = Button(text='brightness', size_hint_y = None,  background_color = [0, 1, 1, 1])
    contrast_button.bind(on_release= setting_popup_content_switch)
    brightness_button.bind(on_release= setting_popup_content_switch)


    settings_dropdown = DropDown()

    for i in [contrast_button, brightness_button]:
        settings_dropdown.add_widget(i)
    def show_dropdown(instance):
        settings_dropdown.open(settings_button) # use DropDown.open() to bind dropdown with button
    settings_button.bind(on_release = show_dropdown)

    return settings_button



def create_settings_controllers():
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
        """single feedback for sliders to control brightness, contrast, etc"""
        # when slide, update the input box text in real-time
        if instance == brightness_slider or instance == brightness_input:
            if instance == brightness_slider:
                # unified variable to define brightness
                # returns a tuple due to optional arguments
                brightness_value = int(value[0])
                brightness_input.text = str(brightness_value)
            elif instance == brightness_input:
                # when value is out of range, set it to max/min
                if int(instance.text) >= brightness_slider.max:
                    instance.text = str(int(brightness_slider.max)) # 100.0 will give error for slider
                elif int(instance.text) <= brightness_slider.min:
                    instance.text = str(int(brightness_slider.min))
                brightness_value = int(instance.text)
                brightness_slider.value = brightness_value
            # update both slider and input box value
            print('brightness', brightness_value, type(brightness_value))

        elif instance == contrast_slider or instance == contrast_input:
            if instance == contrast_slider:
                contrast_value = int(value[0])
                contrast_input.text = str(contrast_value)
            elif instance == contrast_input:
                if int(instance.text) >= contrast_slider.max:
                    instance.text = str(int(contrast_slider.max))
                elif int(instance.text) <= contrast_slider.min:
                    instance.text = str(int(contrast_slider.min))
                contrast_value = int(instance.text)
                contrast_slider.value = contrast_value
            print('contrast', contrast_value, type(contrast_value))
        #mc.camera_library('brightness',brightness_value)

    # bind sliders and input box to callback functions
    for i in [brightness_slider, contrast_slider]:
        i.bind(value = settings_control)
    for i in [brightness_input, contrast_input]:
        i.bind(on_text_validate = settings_control)
    return brightness_controller, contrast_controller

def create_filepath_input():
    filepath_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    filepath_chooser = Button(label = 'filechooser')

    filepath_input = TextInput(
        size_hint_x = 0.8,
        multiline = False,
        text = '/home/pi/Desktop/photos/test.jpg')
    def on_enter(instance):
        global filepath
        filepath = instance.text
        print(filepath)
    filepath_input.bind(on_text_validate = on_enter)
    return filepath_input

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
        if instance.text == '+':
            print('focus + ')
        elif instance.text == '-':
            print('focus - ')

    focus_button_up.bind(on_press = focus_control)  #start_preview functions
    focus_button_down.bind(on_press = focus_control)

    return focus_label, focus_button_up, focus_button_down





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
    x_sensitive = Window.width*0.3
    y_sensitive = Window.height*0.3
    # dummy object showing active area
    map_controller.add_widget(Image())

    def map_control_feedback(instance, value):
        """the callback functions for map_controller scatter object"""
        if map_controller.center[0] - Window.center[0] > x_sensitive:
            #microscope_control.drag_right()
            print('moving x+')
        elif map_controller.center[0] - Window.center[0] < -1* x_sensitive:
            #microscope_control.drag_left()
            pass
        elif map_controller.center[1] - Window.center[1] > y_sensitive:
            #microscope_control.drag_top()
            print('moving y+')
        elif map_controller.center[1] - Window.center[1] < -1*y_sensitive:
            #microscope_control.drag_bot()
            pass
        elif map_controller.scale < default_scale*0.9:
            #microscope_control.pinch_out()
            print('pinch')
        elif map_controller.scale > default_scale*1.1:
            #microscope_control.pinch_in()
            pass
        #after taking actions, reset scatter location and scale to default
        map_controller.center = Window.center
        map_controller.scale = default_scale

    map_controller.bind(on_touch_up = map_control_feedback)

    return map_controller


def add_main_page_widgets(page):
    """Add layouts and widgets to a page (main page)"""
    # defining all the elements here: buttons, sliders, map_controllers
    exit_button = create_exit_button()
    start_preview_button, stop_preview_button = create_preview_buttons()
    save_button, timelapse_button = create_save_buttons()
    #settings_button, back_to_main_button = create_page_buttons()
    settings_button = create_settings_dropdown()
    focus_label, focus_button_up, focus_button_down = create_focus_buttons()
    step_slider_label, step_slider  = create_step_slider()
    map_controller = create_map_controller()

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
    horizontal_layout_3.add_widget(save_button)
    horizontal_layout_3.add_widget(timelapse_button)
    horizontal_layout_3.add_widget(settings_button)

    # add the basic layout to new screen
    page.add_widget(base_layout)


def add_settings_page_widgets(page):
    '''
    # defining all the elements here: buttons, sliders, map_controllers
    settings_button, back_to_main_button = create_page_buttons()
    brightness_control, contrast_control = create_settings_controllers()
    filepath_input = create_filepath_input()

    # Create the basic layout with vertical sections (basic skelton)
    base_layout = BoxLayout(orientation='vertical')

    # add different controllers to the layout.
    # The size is defined in create_settings_controllers function
    base_layout.add_widget(brightness_control)
    base_layout.add_widget(contrast_control)
    last_row = BoxLayout(size_hint_y = 0.2)
    base_layout.add_widget(last_row)
    last_row.add_widget(filepath_input)
    last_row.add_widget(back_to_main_button)

    # add widgets to page
    page.add_widget(base_layout)'''

    pass



def initialise_screens():
    """ use ScreenManager to create several screens/pages"""
    global sm
    sm = ScreenManager()

    main_page =  Screen(name = 'main page')
    # add widgets to main_page
    add_main_page_widgets(main_page)
    # add this screen to screen manager
    sm.add_widget(main_page)

    #settings page
    settings_page = Screen(name='settings page')
    add_settings_page_widgets(settings_page)
    sm.add_widget(settings_page)

    #this determines which page the app start with
    sm.current = 'main page'
    return sm

class WaterScopeApp(App):
    """create kivy app
    only ever need to change the name of Myapp"""
    def build(self):
        sm = initialise_screens()
        return sm

if __name__ == "__main__":
     WaterScopeApp().run()
