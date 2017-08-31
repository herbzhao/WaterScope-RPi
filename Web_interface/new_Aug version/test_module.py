import time
import csv
import datetime
import re
import json




class test_modules:
    def __init__(self):
        self.file_number = 0
        self.folder = r""

    def time_lapse_write_file(self):
        for i in range(0,5):
            print(i)

            csvfile = open(self.folder+'python_alive.csv', "a+", newline="")
            spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(str(datetime.datetime.now()))
            print('writing row')
            time.sleep(1)
    
    def update_file_with_argument(self, brightness, contrast):
        parameter_file = open (self.folder+'config.txt', 'w+')
        parameter_file.writelines('iso: {}\n'.format(brightness))
        parameter_file.writelines('shutter_speed: {}\n'.format(contrast))
        parameter_file.writelines('saturation: {}\n'.format(brightness))
        parameter_file.writelines('red_gain: {}\n'.format(contrast))
        parameter_file.writelines('blue_gain: {}\n'.format(contrast))



        
    def read_config_file(self):
        
        self.red_gain_re = re.compile('red_gain.*')
        self.blue_gain_re = re.compile('blue_gain.*')
        self.iso_re = re.compile('iso.*')
        self.shutter_speed_re = re.compile('shutter_speed.*')
        self.saturation_re = re.compile('saturation.*')
        self.sample_number_re = re.compile('sample.*')
        self.config_file_path = r'config.txt'

        self.config_file = open(self.folder+'config.txt','r')
        self.config_file.seek(0,0) # change the pointer to the beginnging of the file
        self.config_file_content = self.config_file.read()

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
                self.config_content[j] = config[j][-1].replace(j,'').replace('=','').replace(' ','').replace(':','')
            except IndexError:
                self.config_content[j] = 0
        
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
        parameters = {'red_gain':self.red_gain, 'blue_gain':self.blue_gain, 'iso':self.iso, 'saturation':self.saturation,
                        'brightness':self.iso, 'contrast':self.saturation}
        return (parameters)


testing_module = test_modules()
a = testing_module.read_config_file()
