import os
import re
from datetime import datetime

#self.config_file_directory = r'C:\Users\herbz\OneDrive - University Of Cambridge\Documents\GitHub\WaterScope-RPi\motor control\Final'
#self.config_file = open(os.path.join(self.config_file_directory, 'microscope_self.config.txt'),"r")
class initialise_config():
    def __init__(self):
        self.config_file = open(r'C:\Users\herbz\OneDrive - University Of Cambridge\Documents\GitHub\WaterScope-RPi\motor control\Final\microscope_config.txt','a+')
        self.config_file.seek(0,0) # change the pointer to the beginnging of the file
        self.config_file_content = self.config_file.read()
        
        # regex for text index
        self.red_gain_re = re.compile('red_gain.*')
        self.blue_gain_re = re.compile('blue_gain.*')
        self.iso_re = re.compile('iso.*')
        self.shutter_speed_re = re.compile('shutter_speed.*')
        self.saturation_re = re.compile('saturation.*')
        self.sample_number_re = re.compile('sample.*')

    def format_microscope_config(self):
        config = {}
        self.config_content = {}
        for i,j in [
            [self.red_gain_re, 'red_gain'], [self.blue_gain_re, 'blue_gain'], 
            [self.iso_re, 'iso'],
            [self.shutter_speed_re, 'shutter_speed'],[self.saturation_re, 'saturation'],
            [self.sample_number_re, 'sample']]:
            config[j] = i.findall(self.config_file_content)
            try:
                # in case there is no sample information
                self.config_content[j] = config[j][-1].replace(j,'').replace('=','').replace(' ','')
            except IndexError:
                self.config_content[j] = 0
            
        red_gain = self.config_content['red_gain']
        blue_gain = self.config_content['blue_gain']
        awb_gain = (float(red_gain), float(blue_gain))
        print('awb_gains = {}'.format(awb_gain))
        iso = int(self.config_content['iso'])
        print('iso',iso)
        shutter_speed = int(self.config_content['shutter_speed'])
        print('shutter_speed', shutter_speed)
        saturation = int(self.config_content['saturation'])
        print('saturation', saturation)
        self.last_sample_number = self.config_content['sample']
        print('last_sample_number = ', self.last_sample_number)
        return awb_gain, iso, shutter_speed, saturation

    def write_new_sample(self):
        # create new sample
        self.config_file.write('\n')
        self.config_file.write('{:%Y%m%d %H:%M:%S}'.format(datetime.today()))
        self.config_file.write('\n')
        print(self.last_sample_number)
        self.config_file.write('sample = {}'.format(int(self.last_sample_number)+1))

        

if __name__ == '__main__':
    config = initialise_config()
    config.format_microscope_config()
    config.write_new_sample()