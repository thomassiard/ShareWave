import os
import socket
import threading
import logging
import argparse
from protocol import Protocol

# Definišite putanju do direktorijuma sa logovima
# Koristite apsolutnu putanju ako je moguće da biste izbegli greške sa relativnim putanjama
base_dir = os.path.dirname(os.path.abspath(__file__))  # Ovo daje apsolutnu putanju do trenutnog direktorijuma
log_dir = os.path.join(base_dir, 'logs')
log_file = os.path.join(log_dir, 'tracker.log')

# Kreirajte direktorijume ako ne postoje
os.makedirs(log_dir, exist_ok=True)  # Kreira direktorijum ako ne postoji

# Postavljanje osnovnih postavki za logiranje
logging.basicConfig(filename=log_file,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
        
        # Prikazivanje poruke u željenom formatu
        print(f"[TRACKER] Serving on ({self.host}, {self.port})")
        logging.info(f"Tracker is running on {self.host}:{self.port}")
        
        try:
            while True:
                client_socket, addr = server.accept()
                logging.info(f"Accepted connection from {addr}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.daemon = True
                client_handler.start()
        except KeyboardInterrupt:
            print("\nShutting down the tracker...")
            logging.info("Tracker shutting down.")
        finally:
            server.close()

    def handle_client(self, client_socket):
        try:
            request = self.protocol.receive(client_socket)
            if request:
                response = self.protocol.process_request(request, self.peers)
                # Dodajemo stanje trackera (npr. "seeding" ili "peering") kao deo odgovora
                response['status'] = 'seeding' if 'SEED' in request else 'peering'
                self.protocol.send(client_socket, response)
                logging.info(f"Processed request: {request} with response: {response}")
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a tracker server.')
    parser.add_argument('port', type=int, help='Port to listen on')
    args = parser.parse_args()

    # Get the host IP address for display
    host_ip = socket.gethostbyname(socket.gethostname())
    tracker = Tracker(host=host_ip, port=args.port)
    tracker.start()
