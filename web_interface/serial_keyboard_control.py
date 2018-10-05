from readchar import readkey
import serial
import serial.tools.list_ports
import numpy as np
import time
import threading
import yaml

from serial_communication import serial_controller_class

class arduino_controller_class():
    def __init__(self, fergboard_connect=False, arduino_connect=False, waterscope_connect=False):
        # some parameters
        self.move_keys = {
            'w': [0,-1,0],
            's': [0,1,0],
            'a': [-1,0,0],
            'd': [1,0,0],
            'q': [0,0,1],
            'e': [0,0,-1]
                    }
        # self.fergboard_speed = np.array([200, 200, 200])
        self.fergboard_connect = fergboard_connect
        self.arduino_connect = arduino_connect
        self.waterscope_connect = waterscope_connect
        # later on save it to a YAML
        with open('config_serial.yaml') as config_serial_file:
            self.serial_controllers_config = yaml.load(config_serial_file)
        self.initialse_serial_connection()
    
    def initialse_serial_connection(self):
        # to store the names for the arduinos that want to be connected
        serial_controllers_names = []
        # create an empty dict to store all the serial_controller_class
        self.serial_controllers = {}

        if self.fergboard_connect is True:
            serial_controllers_names.append('ferg')
        if self.arduino_connect is True:
            serial_controllers_names.append('parabolic')
        if self.waterscope_connect is True:
            serial_controllers_names.append('waterscope')

        # initialise the connection with existing arduinos using the settings in the dictionary
        for name in serial_controllers_names:
            self.serial_controllers[name] = serial_controller_class()
            self.serial_controllers[name].serial_connect(
                port_names=self.serial_controllers_config[name]['port_names'], 
                baudrate=self.serial_controllers_config[name]['baudrate'])
            self.serial_controllers[name].serial_read_threading(options=self.serial_controllers_config[name]['serial_read_options'])

    def key_input(self):
        while True:
            # read keyboard input (from SSH or from Raspberry Pi)
            k = readkey()

            if k in self.move_keys.keys():
                ''' Motor movement'''
                serial_command = 'jog({},{},{})'.format(self.move_keys[k][0], self.move_keys[k][1], self.move_keys[k][2])
                if self.fergboard_connect is True:
                    self.serial_controllers['ferg'].serial_write(serial_command, parser='ferg')

                elif self.fergboard_connect is False:
                    print(serial_command)
            
            
            elif k in ['[', ']',  't', 'y']:
                if k == ']':
                    serial_command = 'set_speed(increase)'
                elif k == '[':
                    serial_command = 'set_speed(decrease)'
                # elif k == 't':
                #     serial_command = 'move(1000,1000,1000)'
                # elif k == 'y':
                #     serial_command = 'move(-1000,-1000,-1000)'
                    
                self.serial_controllers['ferg'].serial_write(serial_command, parser='ferg')
                if self.fergboard_connect is False:
                    print(serial_command)

            # arduino connection for temperature control
            elif k in ['v', 'b', 'o', 'l']:
                ''' peltier controlling'''
                if k == 'v':
                    print('start cooling')
                    serial_command = 'cool'
                elif k == 'b':
                    print('start heating')
                    serial_command = 'heat'
                elif k =='o':
                    serial_command = 'led_on'
                elif k == 'l':
                    serial_command = 'led_off'
                    
                if self.arduino_connect is True:
                    self.serial_controllers['parabolic'].serial_write(serial_command, parser='parabolic')

            elif k in ['x']:
                print('Exiting...')
                if self.fergboard_connect is True:
                    self.serial_controllers['ferg'].close()
                if self.arduino_connect is True:
                    self.serial_controllers['parabolic'].close()
                break


if __name__ == "__main__":
    # now threading0 runs regardless of user input
    arduino_controller = arduino_controller_class(fergboard_connect=True, arduino_connect=True)
    threading_keyinput = threading.Thread(target=arduino_controller.key_input())
    threading_keyinput.daemon = True
    threading_keyinput.start()


    # running the program continuously
    while True:
        if not threading_keyinput.isAlive():
            break
        