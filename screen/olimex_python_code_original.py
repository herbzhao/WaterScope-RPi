# i2ctest.py
# A brief demonstration of the Raspberry Pi I2C interface, using the Sparkfun
# Pi Wedge breakout board and a SparkFun MCP4725 breakout board:
# https://www.sparkfun.com/products/8736

import smbus
import time

# I2C channel 1 is connected to the GPIO pins
channel = 1

#  MCP4725 defaults to address 0x60
address = 0x30

# Register addresses (with "normal mode" power-down bits)
reg_write_dac = 0x62

# Initialize I2C (SMBus)
bus = smbus.SMBus(channel)
msg = []
# Create a sawtooth wave 16 times

def setBrightness(value):
    bus.write_word_data(address,0x62,value)
    
def writeChar(x,y,data):
    vals = [y, x, data]
    bus.write_i2c_block_data(address,0x61,vals)
    time.sleep(0.03)
    
def clearLCD():
    bus.write_byte(address,0x60)
    time.sleep(0.03)
def readButtons():
    bus.write_byte(address,0x05)
    return (bus.read_byte(address))
setBrightness(155)
clearLCD()
writeChar(0,1,35)
writeChar(1,1,36)
writeChar(2,1,ord('l'))
writeChar(3,1,ord('l'))
writeChar(4,1,ord('o'))
writeChar(0,0,ord('T'))
writeChar(1,0,ord('i'))
writeChar(2,0,ord('a'))
writeChar(3,0,ord('n'))
time.sleep(1)

while True:
    but = (readButtons())
    print("BUT 1:",bool(but & 0x01),end =" ")
    print("BUT 2:",bool((but & 0x02)/2),end =" ")
    print("BUT 3:",bool((but & 0x04)/4),end =" ")
    print("BUT 4:",bool((but & 0x08)/8))
    time.sleep(0.2)
