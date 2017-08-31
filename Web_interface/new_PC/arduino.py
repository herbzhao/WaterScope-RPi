import nanpy
import time

class Arduino:
    def __init__(self):
        self.DEVICE = '/dev/ttyACM0'
        self.PIN_SWITCH = 10  # Pin number for switch
        self.PIN_LED = 7  # Pin number for LED
        self.led_state = False  # LED is off by default
        self.connected = False

    def connect(self):
        self.connection = nanpy.SerialManager(device=self.DEVICE)
        self.arduino = nanpy.ArduinoApi(connection=self.connection)
        a = self.arduino
        a.pinMode(self.PIN_LED, a.OUTPUT)
        a.pinMode(self.PIN_SWITCH, a.INPUT)
        self.connected = True

    def debounce(self, pin):
        a = self.arduino
        previous_state = a.digitalRead(pin)
        i = 0
        while i < 25:
            time.sleep(0.001)
            state = a.digitalRead(pin)
            if state != previous_state:
                i = 0
                previous_state = state
            i += 1
        return state

    def led(self, led_state=None):
        """
        Sets LED on if state is True, off if state is False
        Otherwise, returns LED status
        """
        a = self.arduino
        if led_state == True:
            a.digitalWrite(self.PIN_LED, a.HIGH)
            self.led_state = True
        elif led_state == False:
            a.digitalWrite(self.PIN_LED, a.LOW)
            self.led_state = False
        else:
            return self.led_state

    def microswitch(self):
        """
        Returns True if microswitch is pressed, False otherwise
        """
        if self.debounce(self.PIN_SWITCH) == 0:
            return True
        else:
            return False
