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


    # Set default value for folder and filename



class create_buttons():
    def __init__(self):
        pass

    def create_grid(self, resolution):
        map_grid = GridLayout(rows = resolution)
        map_buttons = []
        for i in range(0,resolution**2):
            map_buttons.append(Button(text = '{}'.format(i+1), background_color = [0, 0.1, 0, 0.5]))
            map_grid.add_widget(map_buttons[i])
        
        return map_grid

    def create_gallery(self):
        folder_chooser_button = Button(text = 'File viewer \nto choose folder', size_hint_x = 0.2) # a button to popup filechooser
        self.folder_chooser = FileChooser()
        self.folder_chooser.path = r'C:\Users\herbz\OneDrive - University Of Cambridge\Documents\GitHub\WaterScope-RPi\motor control'
        self.folder_chooser.add_widget(FileChooserIconLayout())
    # a popup window to choose folder
        folder_chooser_popup = Popup(title = 'choose folder to save image', size_hint = (0.9, 0.9))
        folder_chooser_popup.pos_hint =  {'x':0.5-folder_chooser_popup.size_hint[0]/2,
                                'y':0.5-folder_chooser_popup.size_hint[1]/2} 
        folder_chooser_popup.content = self.folder_chooser

        image_viewer_popup = Popup(title = 'image viewer', size_hint = (0.8, 0.8))
        
        def activate_folder_chooser(instance):
            folder_chooser_popup.open()
        def choose_image(instance, value):
            '''Callback function for FileChooser'''
            # change from "['C:\\abc.jpg']" to "C:\\abc.jpg"
            filepath = str(value).replace('[','').replace(']','').replace('\'','')
            print(filepath)
            # check the file type
            filepath_split = filepath.split('.')
            print(filepath_split[-1])
            if filepath_split[-1] in ['jpg', 'jpeg', 'png', 'tif', 'tiff']:
                image_object = Image(source = filepath, size_hint_x = 0.8, size_hint_y = 0.8)
                image_viewer_popup.content = image_object
                image_viewer_popup.open()

        self.folder_chooser.bind(selection = choose_image)
        folder_chooser_button.bind(on_release = activate_folder_chooser)
        
        return folder_chooser_button
    

if __name__ == '__main__':
    new_buttons = create_buttons()
    #map_grid = new_buttons.create_grid(resolution = 9)
    folder_chooser_button = new_buttons.create_gallery()
    Window.add_widget(folder_chooser_button)
    runTouchApp()