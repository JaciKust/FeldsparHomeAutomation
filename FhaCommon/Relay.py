import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from RPi import GPIO
from FhaCommon.Toggleable import Toggleable


class Relay(Toggleable):
    def __init__(self, pin):
        super().__init__()

        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def _execute_set_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.is_on = True

    def _execute_set_off(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.is_on = False

    def pulse(self):
        try:
            self.set_on()
            time.sleep(0.1)
        finally:
            self.set_off()
        self.set_off()
