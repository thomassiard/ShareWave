import socket
from protocol import Protocol
import logging

class Peer:
    def __init__(self, ip, port, tracker_ip, tracker_port):
        self.ip = ip
        self.port = port
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.protocol = Protocol()
        self.setup_logging()

    def setup_logging(self):
        log_filename = f'src/logs/client_{self.port}.log'
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, 
                            format='%(asctime)s %(message)s')
        logging.info('Peer initialized')

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.bind((self.ip, self.port))
            self.connect_to_tracker(client_socket)
            self.listen_for_requests(client_socket)

    def connect_to_tracker(self, client_socket):
        client_socket.connect((self.tracker_ip, self.tracker_port))
        request = self.protocol.create_registration_request(self.ip, self.port)
        self.protocol.send(client_socket, request)
        response = self.protocol.receive(client_socket)
        logging.info(f'Received from tracker: {response}')

    def listen_for_requests(self, client_socket):
        while True:
            data = self.protocol.receive(client_socket)
            if data:
                logging.info(f'Received data: {data}')
                # Handle data

if __name__ == "__main__":
    peer = Peer('127.0.0.1', 8881, '127.0.0.1', 8888)
    peer.start()
