import time
from datetime import datetime

from RPi import GPIO
from FhaCommon.Constants import Button as ButtonConstant
from FhaClient import PwmHat
from FhaCommon import Color

class RgbButton:
    current_color = None
    previous_color = None
    LED_MAXIMUM = 100

    def __init__(self, json_button):
        GPIO.setup(json_button.trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.colors = [Color.BLACK.as_rgb_array(), Color.BLACK.as_rgb_array(), Color.BLACK.as_rgb_array()]
        self.pwm_hat = PwmHat.default_i2c_hat

        self.group = json_button.group
        self.name = json_button.name
        self.category = json_button.category

        self.red_pwm_channel = json_button.red_pwm_channel
        self.green_pwm_channel = json_button.green_pwm_channel
        self.blue_pwm_channel = json_button.blue_pwm_channel
        self.trigger_pin = json_button.trigger_pin

    def set_button_color(self, color):
        if self.previous_color == color:
            return
        self.previous_color = color
        self.pwm_hat.set_color(self.red_pwm_channel, color[Color.RED_LOCATION])
        self.pwm_hat.set_color(self.green_pwm_channel, color[Color.GREEN_LOCATION])
        self.pwm_hat.set_color(self.blue_pwm_channel, color[Color.BLUE_LOCATION])

    def set_if_for(self, button_color):
        # TODO: impl for_group and for_name.
        if button_color.for_category is not None and button_color.for_category == self.category:
            self.colors = button_color.colors

    def handle_button_color(self, button_start_press_time, has_long_press_been_set, has_short_press_been_set):
        button_press_time = time.time() - button_start_press_time
        if not has_long_press_been_set and button_press_time >= ButtonConstant.LONG_PRESS_MIN:
            has_long_press_been_set = True
            self.set_button_color(self.colors[ButtonConstant.LONG_PRESS_COLOR_LOCATION])
        elif not has_short_press_been_set:
            has_short_press_been_set = True
            self.set_button_color(self.colors[ButtonConstant.PRESS_COLOR_LOCATION])
        time.sleep(0.1)
        return button_press_time, has_long_press_been_set, has_short_press_been_set

    def log_data(self, data):
        now = str(datetime.now())
        data = str(data)
        output = '[{}] {}'.format(now, data)
        print(output)
