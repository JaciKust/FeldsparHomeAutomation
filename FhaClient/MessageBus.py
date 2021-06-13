import json
from collections import namedtuple
import threading
import time
import zmq
import logging


class MessageBus:
    def __init__(self, light_server_json, handler):
        logging.info('Starting')

        self.light_server_json = light_server_json
        self.handler = handler
        self.context = zmq.Context()
        self.incoming_socket = self.context.socket(zmq.REP)
        self.incoming_socket.bind(
            "tcp://{}:{}".format(
                self.light_server_json.incomming_ip_address,
                self.light_server_json.server_to_me_port
            )
        )

        self.socket_thread = threading.Thread(target=self.run_message_server)
        self.socket_thread.start()

    def _decoder(self, dict):
        return namedtuple('X', dict.keys())(*dict.values())

    def run_message_server(self):
        while True:
            #  Wait for next request from client
            message = self.incoming_socket.recv()
            self.incoming_socket.send(b"ack")
            logging.info("Received request: %s" % message)
            data = json.loads(message.decode('utf-8'), object_hook=self._decoder)
            self.handler(data)
            time.sleep(0.2)

    def send_to_light_server(self, data):
        logging.info("Connecting to server…")
        client = self.context.socket(zmq.REQ)
        client.connect("tcp://{}:{}".format(self.light_server_json.ip_address, self.light_server_json.me_to_server_port))

        request = str(data).encode()
        logging.info("Sending (%s)", request)
        client.send(request)

        retries_left = self.light_server_json.request_retries
        while True:
            if (client.poll(self.light_server_json.request_timeout) & zmq.POLLIN) != 0:
                reply = client.recv()
                if reply == b"ack":
                    logging.info("Server replied OK (%s)", reply)
                    break
                else:
                    logging.error("Malformed reply from server: %s", reply)
                    continue

            retries_left -= 1
            logging.warning("No response from server")
            # Socket is confused. Close and remove it.
            client.setsockopt(zmq.LINGER, 0)
            client.close()
            if retries_left == 0:
                logging.error("Server seems to be offline, abandoning")
                return

            logging.info("Reconnecting to server…")
            # Create new connection
            client = self.context.socket(zmq.REQ)
            client.connect("tcp://{}:{}".format(self.light_server_json.ip_address, self.light_server_json.me_to_server_port))
            logging.info("Resending (%s)", request)
            client.send(request)
