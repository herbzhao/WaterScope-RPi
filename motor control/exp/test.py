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
# Floatlayout can be resized, moved easily
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout

'''import misc'''
#This helps define window size, center..
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.vkeyboard import VKeyboard


'''import misc'''
#This helps define window size, center..
from kivy.core.window import Window


class create_widgets(FloatLayout):
	def __init__(self, **kwargs):
		super(create_widgets, self).__init__(**kwargs)
		# add widget to the GUI
		
		vertical_box_layout = BoxLayout(orientation = 'vertical')
		vertical_box_layout.add_widget(Button())
		vertical_box_layout.add_widget(Button())
		vertical_box_layout.add_widget(Button())
		self.add_widget(vertical_box_layout)
		


		def on_enter(instance):
			global file_path
			file_path = instance.text
			
		
		filepath = TextInput(size_hint=(None,None), size = (Window.width*0.8, Window.height*0.1),
		multiline = False, 
		 text = '/home/pi/Desktop/photos/test.jpg')
		filepath.center = (Window.center[0],Window.center[1]*1.5)
		filepath.bind(on_text_validate = on_enter)
		self.add_widget(filepath)


		#todo: add a button to store the inputbox.text into a variable

		def drag_control(instance,value):
			if drag.value_normalized <= 0.05 or drag.value_normalized >= 0.95:
				drag.value_normalized = 0.5
				print(file_path)

		drag = Slider(min=-100, max=100, value=0, size_hint = (None,None), width = Window.width*0.5, 
		center = Window.center)

		drag.bind(value = drag_control)

		self.add_widget(drag)



		

class WaterScope_GUI(App):
	#create kivy app
	#only ever need to change the name of Myapp
	def build(self):
	#function initialize and return your Root Widget.
		Widgets = create_widgets()

		return Widgets



if __name__ == '__main__':
	WaterScope_GUI().run()

