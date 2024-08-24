import os
import socket
import logging
import threading
from protocol import Protocol

class Peer:
    def __init__(self, ip, port, tracker_ip, tracker_port):
        self.ip = ip
        self.port = port
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.protocol = Protocol()
        self.setup_logging()
        self.running = True

    def setup_logging(self):
        # Definirajte putanju do direktorija za logove
        log_dir = 'src/logs'
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, 'peer.log')
        
        # Postavite osnovne postavke za logiranje
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info('Peer initialized')

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.bind((self.ip, self.port))
            client_socket.listen(1)  # Listen for incoming connections
            self.connect_to_tracker(client_socket)
            listener_thread = threading.Thread(target=self.listen_for_requests, args=(client_socket,))
            listener_thread.start()
            listener_thread.join()  # Ensure the thread completes

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
                    logging.info(f"Received data: {data}")
                    self.handle_data(client_socket, data)
            except Exception as e:
                logging.error(f"Error receiving data: {e}")
                self.running = False

    def handle_data(self, client_socket, data):
        try:
            message_type = data.get('type')
            
            if message_type == 'request_piece':
                piece_index = data.get('piece_index')
                logging.info(f"Request for piece {piece_index} received.")
                self.send_piece(client_socket, piece_index)
            
            elif message_type == 'send_piece':
                piece_index = data.get('piece_index')
                piece_data = data.get('piece_data')
                logging.info(f"Piece {piece_index} received.")
                self.save_piece(piece_index, piece_data)
            
            elif message_type == 'update_status':
                new_status = data.get('status')
                logging.info(f"Status update received: {new_status}")

            else:
                logging.warning(f"Unknown message type received: {message_type}")

        except Exception as e:
            logging.error(f"Error handling data: {e}")

    def send_piece(self, client_socket, piece_index):
        try:
            piece_data = self.get_piece_data(piece_index)
            response = {
                'type': 'send_piece',
                'piece_index': piece_index,
                'piece_data': piece_data
            }
            self.protocol.send(client_socket, response)
            logging.info(f"Sent piece {piece_index} to client.")
        except Exception as e:
            logging.error(f"Error sending piece {piece_index}: {e}")

    def save_piece(self, piece_index, piece_data):
        try:
            with open(f'src/output/piece_{piece_index}.part', 'wb') as f:
                f.write(piece_data)
            logging.info(f"Saved piece {piece_index}.")
        except Exception as e:
            logging.error(f"Error saving piece {piece_index}: {e}")

    def get_piece_data(self, piece_index):
        try:
            with open(f'src/output/piece_{piece_index}.part', 'rb') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error retrieving piece {piece_index}: {e}")
            return None

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
