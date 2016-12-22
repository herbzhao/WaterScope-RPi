# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 12:18:29 2016

@author: Eng. SANGA Valerian
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import ScreenManager, Screen

#defining sliders
step_slider = Slider(value_track=True, value_track_color=[1, 0, 0, 1])
focus_slider = Slider(value_track=True, value_track_color=[1, 0, 0, 1], value_normalized = 0.5)

Builder.load_string("""
<MainScreen>:
#    BoxLayout:
#        Button:
#            text: 'Goto settings'
#            on_press: root.manager.current = 'settings'
#        Button:
#            text: 'Quit'

<SettingsScreen>:
#    BoxLayout:
#        Button:
#            text: 'My settings button'
#        Button:
#            text: 'Back to menu'
#            on_press: root.manager.current = 'menu'
""")
    
    
# Declare both screens
class MainScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

# Create the screen manager
sm = ScreenManager()
sm.add_widget(MainScreen(name='menu'))
sm.add_widget(SettingsScreen(name='settings'))

class WaterScopeApp(App):
    def build(self):
        
        #defining the buttons to be used
        exit_btn = Button(text='[b]Exit[/b]', markup=True, size_hint=(.25, 1))
        start_preview_btn = Button(text='[b]Start Preview[/b]', markup=True)
        stop_preview_btn = Button(text='[b]Stop Preview[/b]', markup=True)
        save_btn = Button(text='[b]Save[/b]', markup=True)
        settings_btn = Button(text='[b]Setings[/b]', markup=True)
        
        #creating button functions
        def btn_function(instance):
            
            if instance.text == '[b]Exit[/b]':
                raise SystemExit(0)
                
            elif instance.text == '[b]Start Preview[/b]':
                pass
                
            elif instance.text == '[b]Stop Preview[/b]':
                pass
                
            elif instance.text == '[b]Save[/b]':
                pass
                
            elif instance.text == '[b]Setings[/b]':
                pass
        
        #creating slider functions
        def change_focus(instance,value):
            if focus_slider.value_normalized<0.05 or focus_slider.value_normalized>=0.95:
                focus_slider.value_normalized=0.5
            
        #defining the Layouts
        vertical_box_layout = BoxLayout(orientation='vertical',row_default_height=40)
        gridLayout1 = GridLayout(cols=5)
        gridLayout2= GridLayout(cols=4)
        
        #Box Layout
        vertical_box_2 = Button(size_hint=(10, 10),background_color=(0, 0, 1, 1))
        vertical_box_layout.add_widget(gridLayout1)
        vertical_box_layout.add_widget(vertical_box_2)
        vertical_box_layout.add_widget(gridLayout2)
        
        
        #grid Layout
          #Top Grid Settings
        gridLayout1.add_widget(Label(text='[b]Motor Steps[/b]', markup=True, size_hint=(.35, 1)))
        gridLayout1.add_widget(step_slider)
        gridLayout1.add_widget(Label(text='[b]Focus[/b]', markup=True, size_hint=(.25, 1)))
        gridLayout1.add_widget(focus_slider)
        gridLayout1.add_widget(exit_btn)
        
          #TBottom Grid Settings
        gridLayout2.add_widget(start_preview_btn)
        gridLayout2.add_widget(stop_preview_btn)
        gridLayout2.add_widget(save_btn)
        gridLayout2.add_widget(settings_btn)
        
        
        #defining buttons actions
        exit_btn.bind(on_press = btn_function)
        start_preview_btn.bind(on_press = btn_function)
        stop_preview_btn.bind(on_press = btn_function)
        save_btn.bind(on_press = btn_function)
        settings_btn.bind(on_press = btn_function)
        
        #setting the values for focus slides
        focus_slider.bind(value=change_focus)
        
       #     on_press: root.manager.current = 'settings'
        
        
        return vertical_box_layout

if __name__ == "__main__":
     WaterScopeApp().run()