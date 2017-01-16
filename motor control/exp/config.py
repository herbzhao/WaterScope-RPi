from kivy.config import Config

Config.set('kivy', 'keyboard_mode', 'systemanddock')
#Config.set('kivy', 'keyboard_layout', 'numeric_mod.json')
Config.set('kivy', 'keyboard_layout', 'qwerty')
Config.write()

print('restart to take effect')