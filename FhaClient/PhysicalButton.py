import time
from datetime import datetime

from RPi import GPIO
from FhaCommon.Constants import Button as ButtonConstant, Color as ColorConstant
from FhaClient import PwmHat


class PhysicalButton:
    current_color = None
    previous_color = None
    LED_MAXIMUM = 100

    def __init__(self, name, red_pwm_channel, green_pwm_channel, blue_pwm_channel, trigger_pin):

        GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.name = name
        self.pwm_hat = PwmHat.default_i2c_hat

        self.red_pwm_channel = red_pwm_channel
        self.green_pwm_channel = green_pwm_channel
        self.blue_pwm_channel = blue_pwm_channel
        self.trigger_pin = trigger_pin
        pass

    def set_button_color(self, color):
        if self.previous_color == color:
            return
        self.previous_color = color
        self.pwm_hat.set_color(self.red_pwm_channel, color[ColorConstant.RED_LOCATION])
        self.pwm_hat.set_color(self.green_pwm_channel, color[ColorConstant.GREEN_LOCATION])
        self.pwm_hat.set_color(self.blue_pwm_channel, color[ColorConstant.BLUE_LOCATION])

    def handle_button_color(self, button_start_press_time, has_long_press_been_set, has_short_press_been_set,
                            button_colors):
        button_press_time = time.time() - button_start_press_time
        if not has_long_press_been_set and button_press_time >= ButtonConstant.LONG_PRESS_MIN:
            has_long_press_been_set = True
            self.set_button_color(button_colors[ButtonConstant.LONG_PRESS_COLOR_LOCATION])
        elif not has_short_press_been_set:
            has_short_press_been_set = True
            self.set_button_color(button_colors[ButtonConstant.PRESS_COLOR_LOCATION])
        time.sleep(0.1)
        return button_press_time, has_long_press_been_set, has_short_press_been_set

    def log_data(self, data):
        now = str(datetime.now())
        data = str(data)
        output = '[{}] {}'.format(now, data)
        print(output)
