import socket
from protocol import Protocol
import logging
import threading

class Peer:
    def __init__(self, ip, port, tracker_ip, tracker_port):
        self.ip = ip
        self.port = port
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.protocol = Protocol()
        self.setup_logging()
        self.running = True  # Kontrola rada peer-a

    def setup_logging(self):
        log_filename = f'src/logs/client_{self.port}.log'
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, 
                            format='%(asctime)s %(message)s')
        logging.info('Peer initialized')

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.bind((self.ip, self.port))
            self.connect_to_tracker(client_socket)
            threading.Thread(target=self.listen_for_requests, args=(client_socket,)).start()

    def connect_to_tracker(self, client_socket):
        try:
            client_socket.connect((self.tracker_ip, self.tracker_port))
            request = self.protocol.create_registration_request(self.ip, self.port)
            self.protocol.send(client_socket, request)
            response = self.protocol.receive(client_socket)
            logging.info(f'Received from tracker: {response}')
        except Exception as e:
            logging.error(f"Failed to connect to tracker: {e}")

    def listen_for_requests(self, client_socket):
        while self.running:
            try:
                data = self.protocol.receive(client_socket)
                if data:
                    logging.info("f'Received data: {data}")
                    # Ovdje dodaj logiku za obradu primljenih podataka
                    # self.handle_data(data)
            except Exception as e:
                logging.error(f"Error receiving data: {e}")
                self.running = False  # Zaustavi peer u slučaju greške

    def handle_data(self, data):
        # Obradi podatke ovdje, npr. preuzimanje ili slanje dijelova datoteke
        pass

    def stop(self):
        logging.info("Stopping peer...")
        self.running = False

if __name__ == "__main__":
    peer = Peer('127.0.0.1', 8881, '127.0.0.1', 8888)
    try:
        peer.start()
    except KeyboardInterrupt:
        peer.stop()
        print("Peer stopped by user.")
