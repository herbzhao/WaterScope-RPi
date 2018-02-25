import os
import re
from datetime import datetime
import serial.tools.list_ports

#self.config_file_directory = r'C:\Users\herbz\OneDrive - University Of Cambridge\Documents\GitHub\WaterScope-RPi\motor control\Final'
#self.config_file = open(os.path.join(self.config_file_directory, 'microscope_self.config.txt'),"r")
class initialise_config():
    def __init__(self):
        #self.last_sample_number = 0
        # regex for text index
        self.awb_mode_re = re.compile('awb_mode:.*')
        self.red_gain_re = re.compile('red_gain:.*')
        self.blue_gain_re = re.compile('blue_gain:.*')
        self.iso_re = re.compile('iso:.*')
        self.shutter_speed_re = re.compile('shutter_speed:.*')
        self.saturation_re = re.compile('saturation:.*')
        self.sample_number_re = re.compile('sample_.*')
        self.config_file_path = r'config.txt'
    
    def detect_arduino_port(self):
        ports = list(serial.tools.list_ports.comports())
        # default port
        arduino_port = 'COM3'
        # change this based on arduino device's manufacturer
        arduino_device_name = 'Linux'

        for port in ports:
            if arduino_device_name in port[1]:
	            arduino_port = port[0]
        return arduino_port
        
    def read_config_file(self):
        self.config_file = open(self.config_file_path,'r')
        self.config_file.seek(0,0) # change the pointer to the beginnging of the file
        self.config_file_content = self.config_file.read()

        config = {}
        self.config_content = {}
        for i,j in [
            [self.awb_mode_re, 'awb_mode'],[self.red_gain_re, 'red_gain'], [self.blue_gain_re, 'blue_gain'], 
            [self.iso_re, 'iso'],
            [self.shutter_speed_re, 'shutter_speed'],[self.saturation_re, 'saturation'],
            [self.sample_number_re, 'sample']]:
            config[j] = i.findall(self.config_file_content)
            try:
                # in case there is no sample information
                self.config_content[j] = config[j][-1].replace(j,'').replace('=','').replace(' ','').replace(":","").replace("\r","").replace("_","")
            except IndexError:
                self.config_content[j] = 0
        
        self.awb_mode = str(self.config_content['awb_mode'])
        self.red_gain = float(self.config_content['red_gain'])
        self.blue_gain = float(self.config_content['blue_gain'])
        self.awb_gain = (self.red_gain, self.blue_gain)
        print('awb_gains = {}'.format(self.awb_gain))
        self.iso = int(self.config_content['iso'])
        print('iso',self.iso)
        self.shutter_speed = int(self.config_content['shutter_speed'])
        print('shutter_speed', self.shutter_speed)
        self.saturation = int(self.config_content['saturation'])
        print('saturation', self.saturation)
        self.last_sample_number = self.config_content['sample']
        print('last_sample_number = ', self.last_sample_number)

        self.config_file.close()

    def record_new_sample(self):
        self.config_file = open(self.config_file_path,'a+')
        # create new sample
        self.config_file.write('\r\n{:%Y%m%d %H:%M:%S}\r\n'.format(datetime.today()))
        if self.last_sample_number is None:
            self.last_sample_number = 0
        self.new_sample_number = int(self.last_sample_number) + 1
        print('new sample:{:03d}'.format(self.new_sample_number))
        self.config_file.write('sample_{:03d}'.format(self.new_sample_number))
        self.config_file.close()
        

if __name__ == '__main__':
    config = initialise_config()
    config.read_config_file()
    config.record_new_sample()