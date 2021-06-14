import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import logging
import threading
import time

import zmq
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

from FhaCommon.Constants import Button as ButtonConstant
from FhaDataObjects.ButtonColor import ButtonColor
from FhaDataObjects.RemoteRelayState import RemoteRelayState
from FhaDataObjects.Pulse import Pulse
from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState


current_state = AwakeLightsOnState()
current_state.execute_state_change()

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def run_message_server():
    while True:
        #  Wait for next request from client
        message = incoming_socket.recv()
        incoming_socket.send(b"ack")
        # logging.info("Received request: %s" % message)
        name, press_time = decode_button_press(message)
        set_new_state(current_state.get_state_for(name, press_time))

        sleep_time_seconds = 1
        time.sleep(sleep_time_seconds)


def send_to_desk_buttons(data):
    send(data, DeskButtonConstant.IP_ADDR, DeskButtonConstant.PORT, DeskButtonConstant.REQUEST_RETRIES,
         DeskButtonConstant.REQUEST_TIMEOUT)


def set_up_and_send_to_desk_buttons(right_colors, left_colors, rear_colors):
    right = list(map(lambda a: a.as_rgb_array(), right_colors))
    left = list(map(lambda a: a.as_rgb_array(), left_colors))
    rear = list(map(lambda a: a.as_rgb_array(), rear_colors))

    obj = [
        ButtonColor(right, for_category='Accessory').__dict__,
        ButtonColor(left, for_category='Primary').__dict__,
        ButtonColor(rear, for_category='Special').__dict__
    ]

    data = json.dumps(obj)
    send_to_desk_buttons(data)


def set_up_and_send_relay_change_to_desk_buttons(pin, is_on):
    obj = RemoteRelayState(pin, is_on)
    data = json.dumps(obj.__dict__)
    # TODO: Re-enable
    # send_to_desk_buttons(data)


def set_up_and_send_pulse_relay_to_desk_buttons(pin):
    obj = Pulse(pin)
    data = json.dumps(obj.__dict__)
    # TODO: Re-enable
    #send_to_desk_buttons(data)


def throw(pin, is_on):
    raise Exception('Cannot change state. Only pulse.')


RelayConstant.SOUND_SYSTEM_RELAY.send = set_up_and_send_relay_change_to_desk_buttons
RelayConstant.POWER_RELAY.pulse = set_up_and_send_pulse_relay_to_desk_buttons
RelayConstant.POWER_RELAY.send = throw


def send(data, ip_addr, port, request_retries, request_timeout):
    # logging.info("Connecting to server…")
    client = context.socket(zmq.REQ)
    client.connect("tcp://{}:{}".format(ip_addr, port))

    request = str(data).encode()
    #logging.info("Sending (%s)", request)
    client.send(request)

    retries_left = request_retries
    while True:
        if (client.poll(request_timeout) & zmq.POLLIN) != 0:
            reply = client.recv()
            if reply == b"ack":
                # logging.info("Server replied OK (%s)", reply)
                break
            else:
                # logging.error("Malformed reply from server: %s", reply)
                continue

        retries_left -= 1
        # logging.warning("No response from server")
        # Socket is confused. Close and remove it.
        client.setsockopt(zmq.LINGER, 0)
        client.close()
        if retries_left == 0:
            # logging.error("Server seems to be offline, abandoning")
            return

        # logging.info("Reconnecting to server…")
        # Create new connection
        client = context.socket(zmq.REQ)
        client.connect("tcp://{}:{}".format(ip_addr, port))
        #logging.info("Resending (%s)", request)
        client.send(request)


def decode_button_press(message):
    parts = message.decode("utf-8").split('~')
    button_name = parts[0]
    button_press_time = float(parts[1])
    return button_name, button_press_time


context = zmq.Context()
incoming_socket = context.socket(zmq.REP)
incoming_socket.bind("tcp://{}:{}".format(MessageServerConstant.BIND_TO_ADDR, MessageServerConstant.BIND_TO_PORT))
socket_thread = threading.Thread(target=run_message_server)

def set_new_state(state):
    global current_state
    if state is None:
        set_all_button_colors_to_default(current_state)
    else:
        old_state = current_state
        current_state = state
        logging.info("Setting state to: " + str(current_state))
        set_all_button_colors_to_default(current_state)

        old_state.execute_state_leave()
        current_state.execute_state_change()

        del old_state


def wait_for_button_release(channel):
    while GPIO.input(channel) == ButtonConstant.BUTTON_PRESSED_VALUE:
        time.sleep(0.1)


def init():
    logging.info('Starting')
    set_all_button_colors_to_default(current_state)

    socket_thread.start()


def set_all_button_colors_to_default(from_state):
    send_thread = threading.Thread(target=set_up_and_send_to_desk_buttons, args=(
        from_state.get_desk_right_button_colors(), from_state.get_desk_left_button_colors(),
        from_state.get_desk_rear_button_colors()))

    send_thread.start()

class Runner:
    def __init__(self):
        logging.info('Starting')
        set_all_button_colors_to_default(current_state)

        socket_thread.start()

    def set_all_button_colors_to_default(from_state):
        send_thread = threading.Thread(target=set_up_and_send_to_desk_buttons, args=(
            from_state.get_desk_right_button_colors(), from_state.get_desk_left_button_colors(),
            from_state.get_desk_rear_button_colors()))

        send_thread.start()


if __name__ == '__main__':
    init()

    while True:
        time.sleep(10)
        try:
            new_state = current_state.on_time_check()

            if new_state is not None:
                current_state = new_state
                current_state.execute_state_change()
                set_all_button_colors_to_default(current_state)

        except Exception as e:
            print("Throwing shit from loop.")
            t, v, tb = sys.exc_info()
            logging.error("An error was encountered of type: {}".format(t))
            logging.error("Value: {}".format(v))
            logging.error(str(tb))
