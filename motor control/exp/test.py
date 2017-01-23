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

    def create_exit_button(self):
        self.exit_button = Button(text = 'exit', size_hint_y = 0.2 , background_color = [1, 0, 0, 1])
        self.exit_button.bind(on_press = self.exit_GUI)

    def exit_GUI(self, instance):
        """function to quit GUI"""
        print('quitting')
        raise SystemExit(0)

    

if __name__ == '__main__':
    new_buttons = create_buttons()
    exit_button = new_buttons.create_exit_button()

    a = [0.3, 2.3, 5.3, 4.3]
    for i in range(len(a)):
        a[i] = int(a[i])
    
    b = tuple(a)
    print(a)
    print(b)


    Window.add_widget(exit_button)
    runTouchApp()