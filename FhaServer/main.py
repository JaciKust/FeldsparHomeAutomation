import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from FhaCommon import JsonConfigurationReader
from FhaCommon.MessageBus import MessageBus
from FhaDataObjects.PanelStateCommand import PanelState


import logging
import time

from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class Runner:
    def __init__(self):
        self.current_state = AwakeLightsOnState()
        logging.info('Starting')

        self.current_state.execute_state_change()

        self.client = JsonConfigurationReader.default_reader.read('Clients')[0]
        self.message_bus = MessageBus(
            outgoing_ip=self.client.ip_address,
            incoming_ip="192.168.0.162",
            incoming_port=self.client.from_client_port,
            outgoing_port=self.client.to_client_port,
            request_timeout=self.client.request_timeout,
            request_retries=self.client.request_retries
        )

        self.message_bus.server_events.on_message_receive += self.on_server_receive

    def on_server_receive(self, data):
        # for command in data:
        if data.name == 'Button Click':
            self.handle_button_click(data)

    def handle_button_click(self, command):
        assert command.name == 'Button Click', 'The name of the command passed must be "Button Click"'
        s = self.current_state.get_state_for(command.category, command.button_press_time)
        self.set_new_state(s)

    current_state = None

    def set_new_state(self, state):
        if state is None:
            self.message_bus.send(PanelState(self.current_state.panel_state))
        else:
            old_state = self.current_state
            self.current_state = state
            logging.info("Setting state to: " + str(self.current_state))
            self.message_bus.send(PanelState(self.current_state.panel_state))

            old_state.execute_state_leave()
            self.current_state.execute_state_change()

            del old_state


if __name__ == '__main__':
    r = Runner()

    while True:
        time.sleep(10)
        try:
            new_state = r.current_state.on_time_check()

            if new_state is not None:
                r.set_new_state(new_state)

        except Exception as e:
            print("Throwing shit from loop.")
            t, v, tb = sys.exc_info()
            logging.error("An error was encountered of type: {}".format(t))
            logging.error("Value: {}".format(v))
            logging.error(str(tb))
