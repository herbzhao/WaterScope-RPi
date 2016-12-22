# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 23:28:56 2016

@author: Eng. SANGA Valerian
"""
from kivy.app import App
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition


Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        Button:
            text: 'Goto settings'
            on_press: root.manager.current = 'settings'
        Button:
            text: 'Quit'

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'My settings button'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
""")


# Declare both screens
class MenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

# Create the manager
sm = ScreenManager(transition=WipeTransition())
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SettingsScreen(name='settings'))

class testPagesApp(App):
    def build(self):
          return sm
        
   # return
if __name__ == "__main__":
     testPagesApp().run()