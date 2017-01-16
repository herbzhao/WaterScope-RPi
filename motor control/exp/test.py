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
from datetime import datetime
from kivy.config import Config
import os

if __name__ == '__main__':
    # Set default value for folder and filename
    '''    
    global number_of_image # save function can alter this value
    folder = '/home/pi/Desktop/photos/' 
    number_of_image = 1 
    filename = '{:%Y%m%d}-image-{:03}.jpg'.format(datetime.today(), number_of_image)
    filepath = folder + filename

    filepath_controller = BoxLayout(orientation = 'horizontal', size_hint_y = 0.1)
    folder_button = Button(text = 'Choose folder') # a button to popup filechooser
    filepath_input = TextInput(size_hint_x = 0.8, multiline = True)
    filepath_input.text = filepath

    for i in [filepath_input, folder_button]:
        filepath_controller.add_widget(i)
    
    folder = FileChooser(size_hint = (1,1))
    folder.add_widget(FileChooserIconLayout())

    folder_popup = Popup(title = 'choose folder to save image', size_hint = (0.8, 0.8))
    folder_popup.content = folder
    folder_button.bind(on_release = folder_popup.open)
    def choose_folder(instance, value):
        #print(instance)
        folder = str(value) + '\\'
        print(folder)
        filepath = folder + filename
        filepath_input.text = filepath
    folder.bind(path = choose_folder)'''


    # config
    
    Config.set('kivy', 'keyboard_mode', 'systemandmulti')

    # a panel to host different option buttons
    settings_panel = BoxLayout()
    contrast_button = Button(text='contrast', size_hint_y = 1)
    brightness_button = Button(text='brightness', size_hint_y = 1)
    for i in [contrast_button, brightness_button]:
        settings_panel.add_widget(i)
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
        """update sliders with TextInput and vice versa. update camera settings"""
        # update Slider and TextInput
        for slider, textinput in [  # for i, j = [[1,2][3,4]]  >>>i = 1,3  j = 2,4
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
        # update camera settings 
        if instance in [brightness_slider, brightness_input]:
            print('brightness', updated_value, type(updated_value))
        elif instance in [contrast_slider, contrast_input]:
            print('contrast', updated_value, type(updated_value))

    # bind sliders and input box to callback functions
    for i in [brightness_slider, contrast_slider]:
        i.bind(value = settings_control)
    for i in [brightness_input, contrast_input]:
        i.bind(on_text_validate = settings_control)

    
    # a button to call out settings panel
    settings_button = Button(text = 'settings', size_hint = (0.3,0.3))

    # configure a popup window to display settings and parameters
    settings_popup = Popup( title='Settings', size_hint=(0.8, 0.2))
    settings_popup.pos_hint =  {'x':0.5-settings_popup.size_hint[0]/2,
                               'y':0.1-settings_popup.size_hint[1]/2} # distance from popup.center
    settings_popup_content = GridLayout(cols=1) # a blank layout to put other widgets in
    settings_popup.content = settings_popup_content
    
    def fullscreen_preview(instance):
        """when popup get dismissed, revert camera preview window to normal"""
        print('popup dismissed')
    def reduced_size_preview(instance):
        """when popup get opened, reduce camera preview window size to prevent blocking"""
        print('popup opened')
        
    settings_popup.bind(on_dismiss = fullscreen_preview)
    settings_popup.bind(on_open = reduced_size_preview)

    def settings_popup_content_switch(instance):
        """alter popup content when clicking buttons"""
        settings_popup_content.clear_widgets()
        settings_popup.open()
        if instance == settings_button:
            settings_popup_content.add_widget(settings_panel)
        elif instance == contrast_button:
            settings_popup_content.add_widget(contrast_controller)
        elif instance == brightness_button:
            settings_popup_content.add_widget(brightness_controller)

    settings_button.bind(on_release= settings_popup_content_switch)
    contrast_button.bind(on_release= settings_popup_content_switch)
    brightness_button.bind(on_release= settings_popup_content_switch)




    Window.add_widget(settings_button)
    runTouchApp()