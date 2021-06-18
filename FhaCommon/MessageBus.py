import json
from collections import namedtuple
import threading
import time
import zmq
import logging

from events import Events


class MessageBus:
    def __init__(self, outgoing_ip, incoming_ip, incoming_port, outgoing_port, request_timeout, request_retries):
        logging.info('Starting Message bus')

        self.outgoing_ip = outgoing_ip
        self.incoming_ip = incoming_ip
        self.incoming_port = incoming_port
        self.outgoing_port = outgoing_port
        self.request_timeout = request_timeout
        self.request_retries = request_retries

        self.context = zmq.Context()
        self.incoming_socket = self.context.socket(zmq.REP)
        self.incoming_socket.bind(
            "tcp://{}:{}".format(
                self.incoming_ip,
                self.incoming_port
            )
        )

        self.server_events = Events()
        self.socket_thread = threading.Thread(target=self.run_message_server)
        self.socket_thread.start()

    def __del__(self):
        self.continue_message_server = False

    def _decoder(self, dict):
        return namedtuple('X', dict.keys())(*dict.values())

    continue_message_server = True

    def run_message_server(self):
        while self.continue_message_server:
            #  Wait for next request from client
            message = self.incoming_socket.recv()
            if message != b"ack":
                logging.info("Received request: %s" % message)
                self.incoming_socket.send(b"ack")
                data = json.loads(message.decode('utf-8'), object_hook=self._decoder)
                self.server_events.on_message_receive(data)
            time.sleep(0.2)

    def send(self, data):
        print("Sending!!!! " + str(data))
        data = json.dumps(data.__dict__)
        logging.info("Connecting to server…")
        client = self.context.socket(zmq.REQ)
        client.connect("tcp://{}:{}".format(self.outgoing_ip, self.outgoing_port))

        request = str(data).encode()
        #logging.info("Sending (%s)", request)
        client.send(request)

        retries_left = self.request_retries
        while True:
            if (client.poll(self.request_timeout) & zmq.POLLIN) != 0:
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
            client.connect("tcp://{}:{}".format(self.outgoing_ip, self.outgoing_port))
            logging.info("Resending (%s)", request)
            client.send(request)
