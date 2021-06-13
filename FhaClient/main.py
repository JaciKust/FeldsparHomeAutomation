import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from RPi import GPIO
import time
import logging
from FhaClient.RgbButton import RgbButton
from FhaClient.MessageBus import MessageBus
from FhaCommon import JsonConfigurationReader
from FhaCommon.Constants import Button as ButtonConstant
from FhaClient.ControlPanel import ControlPanel

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class Runner:
    def __init__(self):
        logging.info('starting')

        configuration = JsonConfigurationReader.default_reader.read('ChaiseConfig')
        self.control_panel = self._init_control_panel(configuration)

        mb_config = JsonConfigurationReader.default_reader.read('LightServer')
        self.message_bus = MessageBus(mb_config, self.on_server_receive)

    def _init_control_panel(self, configuration):
        created = []
        buttons = configuration.rgb_buttons
        for button in buttons:
            rgb_button = RgbButton(button)
            created.append(rgb_button)
            GPIO.add_event_detect(rgb_button.trigger_pin, GPIO.RISING,
                                  callback=self.on_button_press,
                                  bouncetime=ButtonConstant.BOUNCE_TIME_MS)
        return ControlPanel(created)

    def on_server_receive(self, data):
        for command in data:
            if command.name == 'Button Color':
                self.control_panel.set_button_colors(command)
        # TODO: Enable relay functionality.

    #TODO: Move most of this logic to the RgbButton class. No need for the Runner to know about or care about how the button works.
    is_pressed = False

    def on_button_press(self, channel):
        button = self.control_panel.get_button_from_channel(channel)
        try:
            if self.is_pressed:
                return
            self.is_pressed = True
            button_start_press_time = time.time()
            button_press_time = 0
            has_long_press_been_set = False
            has_short_press_been_set = False
            time.sleep(0.01)

            while GPIO.input(button.trigger_pin) == ButtonConstant.BUTTON_PRESSED_VALUE and \
                    button_press_time < ButtonConstant.EXTRA_LONG_PRESS_MIN:  # Wait for the button up

                button_press_time, has_long_press_been_set, has_short_press_been_set = \
                    button.handle_button_color(button_start_press_time, has_long_press_been_set,
                                               has_short_press_been_set)
            if button_press_time < 0.1:
                self.is_pressed = False
                return
            logging.info("{} Button pressed for {} seconds".format(button.name, round(button_press_time, 3)))

            self.message_bus.send_to_light_server("%s~%f" % (button.name, button_press_time))
            self.wait_for_button_release(button.trigger_pin)

        except Exception:
            t, v, tb = sys.exc_info()
            logging.error("An error was encountered of type: {}".format(t))
            logging.error("Value: {}".format(v))
            logging.error(str(tb))
            raise
        finally:
            self.is_pressed = False

    def wait_for_button_release(self, channel):
        while GPIO.input(channel) == ButtonConstant.BUTTON_PRESSED_VALUE:
            time.sleep(0.1)


if __name__ == '__main__':
    Runner()

    while True:
        time.sleep(1)
