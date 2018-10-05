# example code G01 Z10 F200
import serial
import time

class microscope_stage_arduino():
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.port = 'COM8'
        self.ser.open()
        self.speed = 200
        self.step = 20
        time.sleep(2) # required boot up time when connecting to serial
        

    def format_command(self):
        command_string = 'G01 {}{} F{}'.format(self.axis, self.movement, self.speed)
        command_byte = command_string.encode(encoding='UTF-8')
        self.ser.flush()
        self.ser.write(command_byte)
        print(command_byte)

    def stage_library(self, command, direction):
        "Use this class from kivy interface to use motors, change picamera etc."        
        #stage settings
        if command == 'move_x':
            self.axis = 'X'
            if direction == '+':
                self.movement = self.step
            else:
                self.movement = -self.step
            self.format_command()

        if command == 'move_y':
            self.axis = 'Y'
            if direction == '+':
                self.movement = self.step
            else:
                self.movement = -self.step
            self.format_command()
        
        if command == 'move_z':
            self.axis = 'Z'
            if direction == '+':
                self.movement = self.step
            else:
                self.movement = -self.step
            self.format_command()


if __name__ == '__main__':
    stage = microscope_stage_arduino()
    stage.stage_library('move_x','+')
    time.sleep(3)
    stage.stage_library('move_y','-')

