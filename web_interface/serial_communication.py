from __future__ import division

import threading
import serial.tools.list_ports
import serial
import time
import datetime
import numpy as np
import os
# regex for parsing the output
import re

# empty Arduino class which will attach more properties later
class Arduinos():
    def __init__(self):
        pass


class serial_controller_class():
    def __init__(self):
        self.starting_time = time.time()
        self.serial_output = ''
        self.starting_time = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    def time_logger(self):
        self.time_elapsed = '{:.1f}'.format(time.time() - self.starting_time)


    def serial_connect(self, port_names=['SERIAL'], baudrate=9600 ):
        ''' automatically detect the Ardunio port and connect '''
        # Find Arduino serial port first
        available_ports = list(serial.tools.list_ports.comports())
        for port in available_ports:
            for name in port_names:
                if name in port[1]:
                    serial_port = port[0]

        self.ser = serial.Serial()
        self.ser.port = serial_port
        self.ser.baudrate = baudrate
        # TODO: check the meaning of the time out
        # self.ser.timeout = 0
        self.ser.open()
        # print('serial connection is ready for {}'.format(serial_port))
        

    def serial_write(self, serial_command, parser):
        ''' sending the parsed serial_commands'''
        if parser == 'waterscope' or parser == 'ws':
            self.serial_command = self.parsing_command_waterscope(serial_command)
        elif parser == 'fergboard' or parser == 'ferg':
            self.serial_command = self.parsing_command_fergboard(serial_command)
        elif parser == 'parabolic_flight' or parser == 'parabolic':
            self.serial_command = self.parsing_command_parabolic_flight(serial_command)
        else:
            self.serial_command = serial_command

        print('serial_command to send: {}'.format(self.serial_command))
        self.ser.write('{} \n\r'.format(str(self.serial_command)).encode())

    def parsing_command_waterscope(self, serial_command):
        ''' parsing the command from interface for WaterScope water testing kit (Sammy code)'''
        # move(500) --> move=500
        # LED_RGB(5,6,7) --> LED_RGB=5,6,7
        serial_command = serial_command.replace(' ','').replace('(','=').replace(')','')
        return serial_command

    def parsing_command_fergboard(self, serial_command):
        ''' parsing the command from interface for fergboard (fergus)'''
        try: 
            self.fergboard_speed 
        except AttributeError:
            self.fergboard_speed = np.array([600, 600, 600])
            # DEBUG: initialise the speed, seems to cause lag
            print('set initial speed')
            serial_command = 'STV ({}, {}, {})'.format(self.fergboard_speed[0], self.fergboard_speed[1], self.fergboard_speed[2])
            # initialise the serial_out so that motor can move 
            self.fin_flag = ['FIN']

        # move(x, y, z)
        if 'move' in serial_command:
            serial_command = serial_command.replace('move', 'MOV')

        # set_speed(increase), set_speed(decrease)
        elif 'set_speed' in serial_command:
            if 'increase' in serial_command:
                self.fergboard_speed += 100
            elif 'decrease' in serial_command:
                self.fergboard_speed -= 100
            # limit the speed  between 50 and 500
            if self.fergboard_speed[0] > 600:
                self.fergboard_speed = np.array([600,600,600])
            elif self.fergboard_speed[0] < 200:
                self.fergboard_speed = np.array([200,200,200])
            self.fergboard_speed = self.fergboard_speed.astype('int')
            serial_command = 'STV ({}, {}, {})'.format(self.fergboard_speed[0], self.fergboard_speed[1], self.fergboard_speed[2])

        # jog(x,y,z)
        elif 'jog' in serial_command:
            # NOTE: if the motor is not ready, the serial_command to send will be empty
            if len(self.fin_flag) == 0:
                serial_command = ''
            # NOTE: the fin_flag is consumed each time the motor moves.
            else:
                serial_command = serial_command.replace('jog', 'JOG') 
                self.fin_flag.pop()
            # serial_command = serial_command.replace('jog', 'JOG') 
            # time.sleep(0.05)

        elif 'reset' in serial_command:
            self.fin_flag = ['FIN']
            # https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.reset_input_buffer
            #  flush the input and output to prevent filling up the whole buffer
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.flush()

        serial_command = serial_command.replace('(',' 1 ').replace(')','').replace(",", " ")
        return serial_command

    def parsing_command_parabolic_flight(self, serial_command):
        ''' parsing the command from interface for parabolic flight arduino'''
        # usage
        #T_fin(20), T_start(20), T_prep(20)
        #LED_RGB(255,255,255)
        #led_on
        
        serial_command = serial_command.replace(' ','').replace('(','=').replace(')','')
        return serial_command


    def serial_output_parse(self, options=[]):
        ''' parsing the arduino output for logging. motor control purposes'''
        if 'fergboard_motor' in options:
            # a 'FIN' flag is used to indicate the motor movement is finished, this needs to be specified in Arduino
            if 'FIN' in self.serial_output:
                self.fin_flag.append('FIN')

        if 'waterscope_motor' in options:
            try: 
                self.motor_idle
            except AttributeError:
                self.motor_idle = True
            try: 
                self.absolute_z
            except AttributeError:
                self.absolute_z = 0
                
            # "Moving the motor, stop accepting commands"
            # "Finished the movement in"
            #  waterscope_moving tag can be used to determine the sleep duration
            if 'Moving the motor' in self.serial_output:
                self.motor_idle = False
            elif 'Finished the movement' in self.serial_output:
                self.motor_idle = True
            elif 'Absolute position' in self.serial_output:
                # Absolute position: 1500
                self.absolute_z = float(self.serial_output.replace('Absolute position: ', ''))

        if 'temperature' in options:
            # store temperature and time in a log dict
            try:
                self.log
            except AttributeError:
                self.log = {'temp':[], 'time':[], 'heating_effort':[]}
                # use regex to match the arduino output: 18.57 *C  4.05 s
                self.temp_re = re.compile('\d+.\d+\s\*C')
                self.time_re = re.compile('\d+.\d+\ss')
                # Heating effort is: 11.00
                self.heating_effort_re = re.compile("Heating effort")
            # extract time and temperature value
            if self.temp_re.findall(self.serial_output):
                self.log['temp'].append(float(self.serial_output.replace(' *C','')))
                self.last_logged_temp = self.log['temp'][-1]
                # print(self.last_logged_temp)
            elif self.time_re.findall(self.serial_output):
                self.log['time'].append(float(self.serial_output.replace(' s','')))
            elif self.heating_effort_re.findall(self.serial_output):
                self.log['heating_effort'].append(float(self.serial_output.replace('Heating effort is:','')))
                self.last_logged_heating_effort = self.log['heating_effort'][-1]


    def serial_read(self, options=['quiet'], parsers=['motor', 'temperature', 'waterscope_motor']):
        self.stop_threading = False
        # set a default tag
        while True:
            # incorporate a flag that stop the thread 
            if self.stop_threading is True:
                break
            else:
                # time.sleep(0)
                # only when serial is available to read
                if self.ser.in_waiting:
                    try:
                        self.serial_output = self.ser.readline().decode()                        
                        # parse the output directly for other purposes
                        self.serial_output_parse(options = parsers)
                        # decide whether to print the output or store in a txt file
                        if options[0] == 'quiet':
                            pass
                        elif options[0] == 'normal':
                            print(self.serial_output)
                        elif options[0] == 'logging':
                            print(self.serial_output)
                            # NOTE: the options[1] is the folder name
                            # if not specified the folder name, use the starting time for the folder name
                            if len(options) == 1:
                                options.append(self.starting_time)
                            # create the folder for the first time.
                            if not os.path.exists("{}".format(options[1])):
                                os.mkdir("{}".format(options[1]))
                            log_file_location = "{}/temp_log.txt".format(options[1])
                            with open(log_file_location, 'a+') as log_file:
                                log_file.writelines(self.serial_output)
                        elif options[0] == 'logging_time_temp':
                            if not os.path.exists("timelapse_data"):
                                os.mkdir("timelapse_data")
                            if not os.path.exists("timelapse_data/arduino"):
                                os.mkdir("timelapse_data/arduino")
                            log_file_location = "timelapse_data/arduino/{}.csv".format(self.starting_time)
                            with open(log_file_location, 'a+') as log_file:
                                now = datetime.datetime.now()
                                time_value_formatted = now.strftime("%Y-%m-%d %H:%M:%S.%f")
                                # heating effort: Heating effort is: 11.00
                                
                                try:
                                    if self.last_logged_temp and self.last_logged_heating_effort:
                                    # if self.last_logged_temp and self.last_logged_heating_effort:
                                        log_file.write(time_value_formatted+',')
                                        log_file.write(str(self.last_logged_temp)+',')
                                        log_file.write(str(self.last_logged_heating_effort))
                                        log_file.write('\n')
                                        del(self.last_logged_temp)
                                        del(self.last_logged_heating_effort)
                                except AttributeError:
                                    pass
                    except UnicodeDecodeError:
                        # when arduino serial boots up, it sometimes have error
                        pass
                
    def serial_read_threading(self, options=['quiet'], parsers=['motor', 'temperature', 'waterscope_motor']):
        ''' used to start threading for reading the serial'''
        # now threading1 runs regardless of user input
        self.threading_ser_read = threading.Thread(target=self.serial_read, args=[options, parsers])
        self.threading_ser_read.daemon = True
        self.threading_ser_read.start()
        time.sleep(0)

    def close(self):
        # TODO: add a way to shut the thread, possibly by passing a flag to each loop
        self.stop_threading = True
        time.sleep(0.2)
        self.ser.close()

#############################################
# code starts here
# TODO: change this example 
if __name__ == '__main__':
    serial_controller = serial_controller_class()
    serial_controller.serial_connect(port_names=['Serial'], baudrate=9600)
    #serial_controller.serial_connect(port_names=['Micro'], baudrate=115200)
    serial_controller.serial_read_threading(options=['logging_time_temp'])

    # accept user input
    while True:
        user_input = str(input())
        serial_controller.serial_write(user_input, 'waterscope')
