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
kivy.require('1.9.1')   # replace with your current kivy version !
from kivy.app import App    # base Class of your App inherits from the App class
# import widgets
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter    # This can be moved, resized and rotated by interactions
from kivy.uix.slider import Slider
# import layout
# A layout is a special kind of widget that manages the size and/or position of its child widgets
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
#import kivy misc
from kivy.uix.screenmanager import ScreenManager, Screen    #This manage different pages
from kivy.core.window import Window    #This helps define window size, center..

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
    start_preview_button = Button(text = 'preview', markup=True)
    stop_preview_button = Button(text = 'stop preview', markup=True)

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
    save_button = Button(text = 'save image', markup=True)
    timelapse_button = Button(text = 'time lapse', markup=True)
    return save_button, timelapse_button


def create_page_buttons():
    """Button to switch between pages"""
    settings_button = Button(text = 'settings', markup=True)
    back_to_main_button = Button(text = 'back', markup=True)
    
    def go_to_page(instance):
        """switch to page/screen based on button.text"""
        if instance.text == "settings":
            sm.current = 'settings page'
        if instance.text == "back":
            sm.current = 'main page'

    settings_button.bind(on_press = go_to_page)
    back_to_main_button.bind(on_press = go_to_page)
    return settings_button, back_to_main_button


def create_step_slider():
    """Manipulate step of motor movement"""
    step_slider_label = Label(
        text='Motor Steps: \n'+'{}'.format(100), markup=True, 
        color = [0.2,0.2,1,1], halign = 'center', valign = 'middle',
        size_hint_y = 0.05)
    step_slider = Slider(
        min=0, max=1000, value= 100, 
        orientation = 'vertical', size_hint_y = 0.4)

    def motor_step_control(instance, value):
        """what happens when change slider"""
        slider_value = int(value)
        step_slider_label.text = 'Motor Steps: \n'+'{}'.format(slider_value)
        print (value)

    step_slider.bind(value = motor_step_control)

    return step_slider_label, step_slider



def create_settings_controllers():
    def settings_slider_control(instance,value):
        if instance == brightness_slider:
            brightness_input.text = str(instance.value)
        elif instance == contrast_slider:
            contrast_input.text = str(instance.value)

    def settings_input_control(instance):
        # make sure the input does not go beyond range
        if float(instance.text) > brightness_slider.max:
            instance.text = str(brightness_slider.max)
        elif float(instance.text) < brightness_slider.min:
            instance.text = str(brightness_slider.min)
        if instance == brightness_input:
            brightness_slider.value = float(brightness_input.text)

        if float(instance.text) > contrast_slider.max:
            instance.text = str(contrast_slider.max)
        elif float(instance.text) < contrast_slider.min:
            instance.text = str(contrast_slider.min)
        if instance == contrast_input:
            contrast_slider.value = float(contrast_input.text)

    #crate a horizontal boxlayout to include label, slider and input box
    brightness_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    brightness_label = Label(text = 'Brightness', size_hint_x = 0.2)
    brightness_slider = Slider(min=0, max=64, value= 1,  size_hint_x = 0.5)
    brightness_input = TextInput(text = '50', multiline = False,  size_hint_x = 0.3)

    brightness_slider.bind(value = settings_slider_control)
    brightness_input.bind(on_text_validate = settings_input_control)

    # add widgets to the boxlayout (controller)
    for i in [brightness_label, brightness_slider, brightness_input]:
        brightness_controller.add_widget(i)

    #crate a horizontal boxlayout to include label, slider and input box
    contrast_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    contrast_label = Label(text = 'Contrast', size_hint_x = 0.2)
    contrast_slider = Slider(min=0, max=64, value= 1,  size_hint_x = 0.5)
    contrast_input = TextInput(text = '50', multiline = False,  size_hint_x = 0.3)

    contrast_slider.bind(value = settings_slider_control)
    contrast_input.bind(on_text_validate = settings_input_control)

    # add widgets to the boxlayout (controller)
    for i in [contrast_label, contrast_slider, contrast_input]:
        contrast_controller.add_widget(i)

    return brightness_controller, contrast_controller




def create_focus_buttons():
    """+ and - buttons to control focus/Z axis"""

    # Create start_preview and stop_preview button
    focus_label = Label(text='Focus', markup=True, color = [0, 1, 0, 1], \
    halign = 'center', valign = 'middle', size_hint_y = 0.05)
    focus_button_up = Button(text = '+', markup=True, \
    background_color = [0, 1, 0, 1], size_hint_y = 0.15)
    focus_button_down = Button(text = '-', markup=True, \
    background_color = [0, 1, 0, 1], size_hint_y = 0.15)

    def focus_control(instance):
        if instance.text == '+':
            print('focus + ')
        elif instance.text == '-':
            print('focus - ')

    # call back for the buttons
    focus_button_up.bind(on_press = focus_control)  #start_preview functions
    focus_button_down.bind(on_press = focus_control)

    return focus_label, focus_button_up, focus_button_down


def create_filepath_input():
    def on_enter(instance):
        global filepath
        filepath = instance.text
        print(filepath)

    filepath_input = TextInput(size_hint_x = 0.8,
    multiline = False,
        text = '/home/pi/Desktop/photos/test.jpg')
    filepath_input.bind(on_text_validate = on_enter)
    return filepath_input


def create_map_controller():
        def map_control_feedback(instance, value):
            'the callback functions for map_controller scatter object'
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

            #after taking actions, reset scatter location and scale'
            map_controller.center = Window.center
            map_controller.scale = default_scale


        map_controller = Scatter(size_hint = (1,1), do_rotation=False, do_translation=True,
        do_scale=True, scale = 1, center = Window.center)

        #automatically determine the size based on screen size
        default_scale = Window.height / map_controller.height*0.75

        map_controller.scale = default_scale
        map_controller.scale_max = default_scale*1.2
        map_controller.scale_min = default_scale*0.8

        x_sensitive = Window.width*0.3
        y_sensitive = Window.height*0.3

        # indication of active area
        map_controller.add_widget(Image())
        map_controller.bind(on_touch_up = map_control_feedback)


        return map_controller


def add_main_page_widgets(page):

    #defining all the elements here: buttons, sliders, map_controllers
    exit_button = create_exit_button()
    start_preview_button, stop_preview_button = create_preview_buttons()
    save_button, timelapse_button = create_save_buttons()
    settings_button, back_to_main_button = create_page_buttons()
    focus_label, focus_button_up, focus_button_down = create_focus_buttons()
    step_slider_label, step_slider  = create_step_slider()
    map_controller = create_map_controller()

    #Create the basic layout with 3 horizontal sections (basic skelton)
    base_layout = BoxLayout(orientation='horizontal')

    #Create the horizontal BoxLayouts in vertical element
    #The preview window's aspect ratio is 4:3 and the touch screen is 5:3.
    #There are gaps with Window.width*0.1 on left and right side
    horizontal_layout_1 = BoxLayout(size_hint_x = 0.1, orientation = 'vertical')
    horizontal_layout_2 = GridLayout(size_hint_x = 0.8)
    horizontal_layout_3 = BoxLayout(size_hint_x = 0.1,  orientation = 'vertical')

    # add 3 layers to base_layout
    base_layout.add_widget(horizontal_layout_1)
    base_layout.add_widget(horizontal_layout_2)
    base_layout.add_widget(horizontal_layout_3)

    #Left section - horizontal_layout_1
    horizontal_layout_1.add_widget(step_slider_label)
    horizontal_layout_1.add_widget(step_slider)
    horizontal_layout_1.add_widget(focus_label)
    horizontal_layout_1.add_widget(focus_button_up)
    horizontal_layout_1.add_widget(focus_button_down)
    horizontal_layout_1.add_widget(exit_button)


    # middle section  - horizontal_layout_2
    horizontal_layout_2.add_widget(map_controller)

    #right section - horizontal_layout_3
    horizontal_layout_3.add_widget(start_preview_button)
    horizontal_layout_3.add_widget(stop_preview_button)
    horizontal_layout_3.add_widget(save_button)
    horizontal_layout_3.add_widget(timelapse_button)
    horizontal_layout_3.add_widget(settings_button)

    # add the basic layout to new screen
    page.add_widget(base_layout)


def add_settings_page_widgets(page):

    #defining all the elements here: buttons, sliders, map_controllers
    settings_button, back_to_main_button = create_page_buttons()
    brightness_control, contrast_control = create_settings_controllers()
    filepath_input = create_filepath_input()

    #Create the basic layout with vertical sections (basic skelton)
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
    page.add_widget(base_layout)



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
