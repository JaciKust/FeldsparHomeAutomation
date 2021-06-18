import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ControlPanelClient import ButtonColorSet
from ControlPanelClient.ControlPanelButton import ControlPanelButton
from FhaDataObjects.ButtonClickEvent import ButtonClickEvent


from RPi import GPIO
import time
import logging
from FhaCommon.MessageBus import MessageBus
from FhaCommon import JsonConfigurationReader
from ControlPanelClient.ControlPanel import ControlPanel

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

class Runner:
    def __init__(self):
        logging.info('starting')

        configuration = JsonConfigurationReader.default_reader.read('ChaiseConfig')
        self.control_panel = self._init_control_panel(configuration)
        self.control_panel.input_events.on_control_clicked += self._send_button_click_to_server

        mb_config = JsonConfigurationReader.default_reader.read('LightServer')
        self.message_bus = MessageBus(
            mb_config.outgoing_ip,
            mb_config.incoming_ip,
            mb_config.incoming_port,
            mb_config.outgoing_port,
            mb_config.request_timeout,
            mb_config.request_retries,
            False
        )

        self.message_bus.server_events.on_message_receive += self.on_server_receive

    def _init_control_panel(self, configuration):
        created = []
        buttons = configuration.rgb_buttons
        for button in buttons:
            #TODO: Replace this with configurable
            button_colors = self._get_colors_for_button(button)
            rgb_button = ControlPanelButton(button_colors, button)
            created.append(rgb_button)
        return ControlPanel(created, "First Control Panel")

    def _get_colors_for_button(self, button):
        if button.category == "Accessory":
            return ButtonColorSet.SECONDARY_BUTTON_COLOR_SET
        elif button.category == "Primary":
            return ButtonColorSet.PRIMARY_BUTTON_COLOR_SET
        elif button.category == "Special":
            return ButtonColorSet.SPECIAL_BUTTON_COLOR_SET

    def _send_button_click_to_server(self, name, group, category, trigger_pin, button_press_time, control_panel_name):
        button_click_event = ButtonClickEvent(
            name,
            group,
            category,
            trigger_pin,
            button_press_time
        )
        self.message_bus.send(button_click_event)

    def on_server_receive(self, data):
        #for command in data:
        if data.name == 'Panel State':
            self.control_panel.set_control_panel_state(data.state)


if __name__ == '__main__':
    Runner()

    while True:
        time.sleep(1)