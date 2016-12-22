# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 23:28:56 2016

@author: Eng. SANGA Valerian
"""
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.screenmanager import ScreenManager, Screen,  SwapTransition,WipeTransition, SlideTransition, FadeTransition, ShaderTransition



# Declare both screens
sm = ScreenManager(transition= SwapTransition())
screen_1 = Screen(name='first')
button_1 = Button(text= 'screen 1')
screen_1.add_widget(button_1)
screen_2 = Screen(name='second')
button_2 = Button(text= 'screen 2')
screen_2.add_widget(button_2)
sm.add_widget(screen_1)
sm.add_widget(screen_2)

def change_screen(instance):
    if instance.text == 'screen 1':
        sm.current = 'second'
    elif instance.text == 'screen 2':
        sm.current = 'first'

button_1.bind(on_press = change_screen)
button_2.bind(on_press = change_screen)


# By default, the first added screen will be shown. If you want to
# show another one, just set the 'current' property.
sm.current = 'second'


# Create the manager

class testPagesApp(App):
    def build(self):

        return sm
        
   # return
if __name__ == "__main__":
     testPagesApp().run()