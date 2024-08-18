import socket
import threading
import logging
from protocol import Protocol

# Postavljanje osnovnih postavki za logiranje
logging.basicConfig(filename='src/logs/tracker.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Tracker:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.protocol = Protocol()
        self.peers = {}  # Skladište za praćenje registriranih peer-ova

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        logging.info(f"Tracker is running on {self.host}:{self.port}")
        
        # Notifikacija u konzoli kada se tracker uspješno pokrene
        print(f"Tracker successfully running on {self.host}:{self.port}")
        
        while True:
            client_socket, addr = server.accept()
            logging.info(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        try:
            request = self.protocol.receive(client_socket)
            if request:
                response = self.protocol.process_request(request, self.peers)
                # Dodajemo stanje trackera (npr. "seeding" ili "peering") kao dio odgovora
                response['status'] = 'seeding' if 'SEED' in request else 'peering'
                self.protocol.send(client_socket, response)
                logging.info(f"Processed request: {request} with response: {response}")
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
