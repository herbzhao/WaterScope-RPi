# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 09:15:28 2016

@author: herbz
"""
import time
import kivy
kivy.require('1.9.1') # replace with your current kivy version !
from kivy.app import App
# base Class of your App inherits from the App class

'''import widgets'''
#text
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
# This can be moved, resized and rotated by interactions
# including the child widgets
from kivy.uix.scatter import Scatter
from kivy.uix.carousel import Carousel


'''import layout'''
#  A layout is a special kind of widget that manages the size and/or position of its child widgets
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
# Floatlayout can be resized, moved easily
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout

'''import misc'''
#This helps define window size, center..
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout, FileChooserIconView


'''import misc'''
#This helps define window size, center..
from kivy.core.window import Window
from kivy.base import runTouchApp


if __name__ == '__main__':
    '''
    #crate a horizontal boxlayout to include label, slider and input box
    brightness_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    brightness_label = Label(text = 'Brightness:', size_hint_x = 0.2)
    brightness_slider = Slider(min = 0, max = 100, value = 50, size_hint_x = 0.5)
    brightness_input = TextInput(
        text = '{}'.format(brightness_slider.value), multiline = False,  size_hint_x = 0.3)
    # add widgets to the boxlayout (controller)
    for i in [brightness_label, brightness_input, brightness_slider]:
        brightness_controller.add_widget(i)

    #contrast control
    contrast_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    contrast_label = Label(text = 'Contrast:', size_hint_x = 0.2)
    contrast_slider = Slider(min=0, max=64, value= 1,  size_hint_x = 0.5)
    contrast_input = TextInput(
        text = '{}'.format(contrast_slider.value), multiline = False, size_hint_x = 0.3)
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
    


    setting_popup = Popup( title='Setting', size_hint=(0.8, 0.2))
    setting_popup.pos_hint =  {'x':0.5-setting_popup.size_hint[0]/2,
                               'y':0.2-setting_popup.size_hint[1]/2} # distance from popup.center
    setting_popup_content = GridLayout(cols=1) # a blank layout to put other widgets in
    setting_popup.content = setting_popup_content # link the popup.content to a widget
    def setting_popup_content_switch(instance, *value):
        """show popup with corresponding setting"""
        setting_popup_content.clear_widgets()
        if instance == contrast_button:
            setting_popup_content.add_widget(contrast_controller)
        elif instance == brightness_button:
            setting_popup_content.add_widget(brightness_controller)
        setting_popup.open()
 
    contrast_button = Button(text='contrast', size_hint = (1,None))
    brightness_button = Button(text='brightness', size_hint = (1,None))
    contrast_button.bind(on_release= setting_popup_content_switch)
    brightness_button.bind(on_release= setting_popup_content_switch)

    settings_button = Button(text = 'settings', size_hint = (0.2, 0.2))
    settings_dropdown = DropDown()

    for i in [contrast_button, brightness_button]:
        settings_dropdown.add_widget(i)
    def show_dropdown(instance):
        settings_dropdown.open(settings_button) # use DropDown.open() to bind dropdown with button
    settings_button.bind(on_release = show_dropdown)

    Window.add_widget(settings_button)'''

    filepath = '/home/pi/Desktop/photos/'
    n = 1
    filename = 'image{:04}.jpg'.format(n)
    
    filepath_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    filepath_chooser_button = Button(text = 'filechooser')
    filepath_input = TextInput(
        size_hint_x = 0.8,
        multiline = False,
        text = '{}{}'.format(filepath, filename))

    for i in [filepath_input, filepath_chooser_button]:
        filepath_controller.add_widget(i)
    
    def on_enter(instance):
        global filepath
        filepath = instance.text
        print(filepath)
    filepath_input.bind(on_text_validate = on_enter)


    filepath_chooser = FileChooser(size_hint = (1,1))
    filepath_chooser.add_widget(FileChooserIconLayout())

    filepath_popup = Popup(title = 'choose folder to save image', size_hint = (0.8, 0.8))
    filepath_popup.content = filepath_chooser
    filepath_chooser_button.bind(on_release = filepath_popup.open)

    filepath_chooser.bind(path=lambda *x: print("path: %s" % x[1:]))


    Window.add_widget(filepath_controller)
    runTouchApp()