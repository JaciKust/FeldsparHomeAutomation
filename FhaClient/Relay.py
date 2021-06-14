import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from RPi import GPIO
from FhaClient.DatabaseToggleable import DatabaseToggleable


class Relay(DatabaseToggleable):
    def __init__(self, pin, database_id):
        super().__init__(database_id)

        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def _execute_set_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        super()._execute_set_on()

    def _execute_set_off(self):
        GPIO.output(self.pin, GPIO.LOW)
        super()._execute_set_off()

    def pulse(self):
        try:
            self.set_on()
            time.sleep(0.1)
        finally:
            self.set_off()
        self.set_off()
