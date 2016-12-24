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

import os

if __name__ == '__main__':
    # Set default value for folder and filename
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
    folder.bind(path = choose_folder)


    Window.add_widget(filepath_controller)
    runTouchApp()