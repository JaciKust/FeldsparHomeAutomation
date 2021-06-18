import sys
import time
from datetime import datetime

from RPi import GPIO
from FhaCommon.Constants import Button as ButtonConstant
from FhaClient import PwmHat
from FhaCommon import Color
from events import Events


class RgbButton:
    current_color = None
    previous_color = None
    LED_MAXIMUM = 100

    def __init__(self, red_pwm_channel, green_pwm_channel, blue_pwm_channel, trigger_pin):
        GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            trigger_pin,
            GPIO.RISING,
            callback=self._capture_button_press,
            bouncetime=ButtonConstant.BOUNCE_TIME_MS
        )

        self.pwm_hat = PwmHat.default_i2c_hat

        self.red_pwm_channel = red_pwm_channel
        self.green_pwm_channel = green_pwm_channel
        self.blue_pwm_channel = blue_pwm_channel
        self.trigger_pin = trigger_pin

        self.colors = [Color.BLACK.as_rgb_array(), Color.BLACK.as_rgb_array(), Color.BLACK.as_rgb_array()]
        self.refresh_color()

        self.button_events = Events()

    def refresh_color(self):
        self.set_button_color(self.colors[ButtonConstant.DEFAULT_COLOR])

    def set_button_color(self, color):
        if self.previous_color == color:
            return
        self.previous_color = color
        self.pwm_hat.set_color(self.red_pwm_channel, color[Color.RED_LOCATION])
        self.pwm_hat.set_color(self.green_pwm_channel, color[Color.GREEN_LOCATION])
        self.pwm_hat.set_color(self.blue_pwm_channel, color[Color.BLUE_LOCATION])

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

    _is_pressed = False

    def _capture_button_press(self, channel):
        try:
            if self._is_pressed:
                return
            self._is_pressed = True
            button_start_press_time = time.time()
            button_press_time = 0
            has_long_press_been_set = False
            has_short_press_been_set = False
            time.sleep(0.01)

            # TODO: Refactor this to make more sense. The handle method shouldn't be returning
            # three variables.
            while GPIO.input(self.trigger_pin) == ButtonConstant.BUTTON_PRESSED_VALUE and \
                    button_press_time < ButtonConstant.EXTRA_LONG_PRESS_MIN:  # Wait for the button up

                button_press_time, has_long_press_been_set, has_short_press_been_set = \
                    self.handle_button_color(button_start_press_time, has_long_press_been_set,
                                               has_short_press_been_set)

            if button_press_time < ButtonConstant.NOISE_THRESHOLD:
                # Write off as noise -- ignore.
                self._is_pressed = False
                return
            self.log_data("{} Button pressed for {} seconds".format(self.trigger_pin, round(button_press_time, 3)))

            #self.message_bus.send_to_light_server("%s~%f" % (self.name, button_press_time))
            # TODO: Eventually this should send the start and end time of the button press.
            # This would allow for doing double button presses or whatever.

            self.button_events.on_depressed(self.trigger_pin, button_press_time)
            self.wait_for_button_release(self.trigger_pin)

        except Exception:
            t, v, tb = sys.exc_info()
            self.log_data("An error was encountered of type: {}".format(t))
            self.log_data("Value: {}".format(v))
            self.log_data(str(tb))
            raise
        finally:
            self._is_pressed = False

    def wait_for_button_release(self, channel):
        while GPIO.input(channel) == ButtonConstant.BUTTON_PRESSED_VALUE:
            time.sleep(0.01)

    def log_data(self, data):
        now = str(datetime.now())
        data = str(data)
        output = '[{}] {}'.format(now, data)
        print(output)
