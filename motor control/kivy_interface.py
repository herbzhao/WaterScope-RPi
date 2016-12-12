# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 09:15:28 2016

@author: herbz
"""

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


'''import misc'''
#This helps define window size, center..
from kivy.core.window import Window

'''import microscope_control'''
import microscope_control as mc



class microscope_controller():
	'put down the action here to control external motors, image operations, etc.'
	def __init__(self):
		pass	

	def drag_right(self):
		mc.stage_library('move_x','-')

	def drag_left(self):
		mc.stage_library('move_x','+')

	def drag_top(self):
		mc.stage_library('move_y','+')

	def drag_bot(self):
		mc.stage_library('move_y','-')

	def pinch_out(self):
		mc.camera_library('zoom_out')

	def pinch_in(self):
		mc.camera_library('zoom_in')

	def start_preview(self):
		mc.camera_library('start_preview')
		
	def stop_preview(self):
		mc.camera_library('stop_preview')


def anchoring(x, y, widget):
	# a short function to create anchored objected
	'''anchoring(center, left, btn1)'''
	a_layout = AnchorLayout(anchor_x=x, anchor_y=y, )
	a_layout.add_widget(widget)
	return a_layout

def create_preview_buttons():
	def preview_control(instance):
		mc.fov = 1.00 #initialise the zoom level
		if instance.text == 'preview':
			microscope_control.start_preview()
		else:
			microscope_control.stop_preview()
	
	microscope_control = microscope_controller()
	# create exit button at left - top position
	preview_button = Button(text = 'preview', \
	center = (Window.center[0]*0.1,Window.center[1]*0.5), \
	size_hint = (None,None))
	preview_button_right_top = anchoring('right', 'top', preview_button)

	# Create Exit button
	stop_preview_button = Button(text = 'stop_preview', \
	center = (Window.center[0]*0.1,Window.center[1]*0.5), \
	size_hint = (None,None))
	stop_preview_button_right_mid = anchoring('right', 'center', stop_preview_button)

	# call back for the buttons
	preview_button.bind(on_press = preview_control)  #start_preview functions
	stop_preview_button.bind(on_press = preview_control)
	
	return preview_button_right_top, stop_preview_button_right_mid




def create_exit_button():
	# create exit button at left - top position
	def exit_GUI(instance):
		#function to quit GUI
			print('quitting')
			raise SystemExit(0)

	# Create Exit button
	exit_button = Button(text = 'exit', \
	center = (Window.center[0]*0.1,Window.center[1]*0.5), \
	size_hint = (None,None))

	exit_button.bind(on_press = exit_GUI)

	exit_button_left_top = anchoring('left', 'top', exit_button)
	return exit_button_left_top




def create_controller():
	#create controller for swiping and pinching in the center

	# few parameters for scaling

	# this defines the active area of dragging/zooming
	normal_scale = 1
	# amount of pinch for zoom in and out
	zoom_in_scale = 5.5
	zoom_out_scale = 4.5
	# distance to drag in x and y direction for action
	x_sensitive= Window.center[0]/3
	y_sensitive = Window.center[1]/3


	# Controller(scatter object) that can be scaled and translate
	controller = Scatter(size_hint = (None,None), do_rotation=False, do_translation=True,
	do_scale=True, scale = normal_scale,
	scale_min= zoom_out_scale, scale_max=zoom_in_scale, center = Window.center)

	# a reference object to show the active area
	control_object = Image()
	controller.add_widget(control_object)

	#create microscope control parts
	microscope_control = microscope_controller()
	mc.step = 100

# this provides actions when moving and zooming the scatter objects
	def control_feedback(arg1, arg2):
		'the callback functions for controller scatter object'

		if controller.center[0] - Window.center[0] > x_sensitive:
			microscope_control.drag_right()

		elif controller.center[0] - Window.center[0] < -1* x_sensitive:
			microscope_control.drag_left()

		elif controller.center[1] - Window.center[1] > y_sensitive:
			microscope_control.drag_top()

		elif controller.center[1] - Window.center[1] < -1*y_sensitive:
			microscope_control.drag_bot()

		elif controller.scale < zoom_out_scale*1.1:
			microscope_control.pinch_out()

		elif controller.scale > zoom_in_scale*0.9:
			microscope_control.pinch_in()

		'after taking actions, reset scatter location and scale'
		controller.center = Window.center
		controller.scale = normal_scale


	# bind a function to controller when release touch
	controller.bind(on_touch_up = control_feedback)

	return controller


class create_widgets(FloatLayout):
	def __init__(self, **kwargs):
		super(create_widgets, self).__init__(**kwargs)


		# add widget to the GUI
		controller = create_controller()
		self.add_widget(controller)
		
		# add exit button
		exit_button = create_exit_button()
		self.add_widget(exit_button)

		preview_button, stop_preview_button = create_preview_buttons()
		self.add_widget(preview_button)
		self.add_widget(stop_preview_button)

		# add carousel:
		#spin = create_carousel()
		#self.add_widget(spin)



class WaterScope_GUI(App):
	#create kivy app
	#only ever need to change the name of Myapp
	def build(self):
	#function initialize and return your Root Widget.
		Widgets = create_widgets()

		return Widgets



if __name__ == '__main__':
	WaterScope_GUI().run()

