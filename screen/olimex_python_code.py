# i2ctest.py
# A brief demonstration of the Raspberry Pi I2C interface, using the Sparkfun
# Pi Wedge breakout board and a SparkFun MCP4725 breakout board:
# https://www.sparkfun.com/products/8736

import smbus
import time
import threading

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
    
def writeChar(x, line, data):
    if line == 1:
        y = 1
    elif line == 2:
        y = 0
    vals = [y, x, data]
    bus.write_i2c_block_data(address,0x61,vals)
    time.sleep(0.03)
    
def clearLCD():
    bus.write_byte(address,0x60)
    time.sleep(0.03)

def readButtons():
    bus.write_byte(address, 0x05)
    button_stat = bus.read_byte(address)

    button = None
    if not bool(button_stat & 0x01):
        button = 0
    elif not bool((button_stat & 0x02)/2):
        button = 1
    elif not bool((button_stat & 0x04)/4):
        button = 2
    elif not bool((button_stat & 0x08)/8):
        button = 3

    return button

def wait_for_buttons():
    while True:
        button = readButtons()


def write_helper(text='', line=1):
    # if it is given a list, it is the options for button 1-4
    if type(text) == list:
        new_text = ""
        for item in text:
            # adding padding and truncate to 3 chars
            new_text += (item[:3] + " "*4)[:4]
        
    elif type(text) == str:
        new_text = text[:16]

    for index,  char in enumerate(new_text):
        writeChar(index, line, ord(char))
    time.sleep(0.1)
    

def template(question, options, response_function):
    clearLCD()
    write_helper(question, line=1)
    write_helper(options, line=2)
    while True:
        button = readButtons()
        if button is not None:
            response_function(options[button])
            break

def answer_name(answer):
    clearLCD()
    write_helper("welcome back: {}".format(answer))
    
def answer_activity(answer):
    clearLCD()
    write_helper("Enjoy {}!".format(answer))



if __name__ == "__main__":
    clearLCD()
    setBrightness(100)
    response = []
    template(question="who are you?",options=['TZ','SM','NP','AP'],response_function=answer_name)
    template(question="What are you doing?",options=['Eat','Pty','Slp','Bac'],response_function=answer_activity)


    print('ok')
    # options = ["Eat", "Pty", "SLP", "BAC"]
    # write_helper(options, line=2)
    
    # while True:
    #     button = readButtons()
    #     if button is not None:
    #         clearLCD()
    #         write_helper("Welcome: {}".format(options[button]))
    #         break
