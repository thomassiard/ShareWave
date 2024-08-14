# src/client_handler.py

import socket
import sys
import json
import logging
from protocol import Protocol

# Postavite osnovne postavke za logiranje
logging.basicConfig(filename='src/logs/client_handler.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ClientHandler:
    def __init__(self, src_ip, src_port, tracker_ip, tracker_port):
        self.src_ip = src_ip
        self.src_port = int(src_port)
        self.tracker_ip = tracker_ip
        self.tracker_port = int(tracker_port)
        self.protocol = Protocol()

        # Povezivanje s trackerom
        self.server_address = (self.tracker_ip, self.tracker_port)

    def run(self):
        while True:
            self.show_menu()
            choice = input("[p2py client]: ").strip()

            if choice == '1':
                self.get_torrent_list()
            elif choice == '2':
                self.download_torrent()
            elif choice == '3':
                self.upload_file()
            elif choice == '4':
                self.show_help()
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def show_menu(self):
        print("\nChoose an option:")
        print("[1] Get & display list of torrents")
        print("[2] Download Torrent")
        print("[3] Upload a new file")
        print("[4] Help")
        print("[5] Exit")

    def send_request(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server_address)
            logging.info(f"Sending request: {request}")
            sock.sendall(json.dumps(request).encode())
            response = sock.recv(4096).decode()
            logging.info(f"Received response: {response}")
            return json.loads(response)

    def get_torrent_list(self):
        request = {"OPC": 10, "IP_ADDRESS": self.src_ip, "PORT": self.src_port}
        response = self.send_request(request)
        if response.get('RET') == 0:
            print("Available torrents:", response.get('TORRENTS'))
        else:
            print("Failed to get torrent list.")

    def download_torrent(self):
        torrent_id = input("Please enter the torrent id: ").strip()
        request = {"OPC": 11, "IP_ADDRESS": self.src_ip, "PORT": self.src_port, "TORRENT_ID": int(torrent_id)}
        response = self.send_request(request)
        if response.get('RET') == 0:
            print("Downloading torrent...")
        else:
            print("Failed to download torrent.")

    def upload_file(self):
        filename = input("Please enter the filename.ext: ").strip()
        try:
            with open(f'src/input/{filename}', 'rb') as file:
                file_data = file.read()
                num_of_pieces = (len(file_data) + 1023) // 1024  # Example logic for splitting into pieces
                request = {
                    "OPC": 14,
                    "IP_ADDRESS": self.src_ip,
                    "PORT": self.src_port,
                    "FILE_NAME": filename,
                    "NUM_OF_PIECES": num_of_pieces
                }
                response = self.send_request(request)
                if response.get('RET') == 0:
                    print("File uploaded successfully.")
                else:
                    print("Failed to upload file.")
        except FileNotFoundError:
            print("File not found.")

    def show_help(self):
        print("Help: Use the menu options to interact with the ShareWave client.")
        print("1) Get & display list of torrents: Fetches and displays available torrents from the tracker.")
        print("2) Download Torrent: Downloads a torrent by ID.")
        print("3) Upload a new file: Uploads a new file to the tracker.")
        print("4) Help: Displays this help message.")
        print("5) Exit: Exits the client application.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 src/client_handler.py [src_ip] [src_port] [tracker_ip] [tracker_port]")
        sys.exit(1)

    src_ip = sys.argv[1]
    src_port = sys.argv[2]
    tracker_ip = sys.argv[3]
    tracker_port = sys.argv[4]

    client = ClientHandler(src_ip, src_port, tracker_ip, tracker_port)
    client.run()
