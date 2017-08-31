"""
Thanks to Fergus Riche: https://github.com/fr293/motor_board for the board, the code and the expertise!
"""
import smbus

class Motors():
    def __init__(self):
        self.connected = False

    def connect(self):
        self.bus = smbus.SMBus(1)
        self.connected = True

    def move(self, x, y, z):
        self.bus.write_byte_data(8, x >> 8, x & 255)
        self.bus.write_byte_data(16, y >> 8, y & 255)
        self.bus.write_byte_data(24, z >> 8, z & 255)
