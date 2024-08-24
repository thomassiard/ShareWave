import socket
import sys
import json
import logging
import os
from protocol import Protocol

# Postavljanje osnovnog logger-a za zapisivanje u fajl
log_dir = 'src/logs'
log_file = 'client_handler.log'
log_path = os.path.join(log_dir, log_file)

# Kreirajte log folder ako ne postoji
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Konfiguracija osnovnog logovanja
logging.basicConfig(filename=log_path,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ClientHandler:
    def __init__(self, src_ip, src_port, tracker_ip, tracker_port, client_name="client"):
        self.src_ip = src_ip
        self.src_port = int(src_port)
        self.tracker_ip = tracker_ip
        self.tracker_port = int(tracker_port)
        self.protocol = Protocol()
        self.client_name = client_name

        # Postavljanje osnovnih vrednosti za konfiguraciju
        self.chunk_size = 1024  # Predefinisana vrednost za chunk_size

    def run(self):
        while True:
            self.show_menu()
            choice = input(f"[{self.client_name} client]: ").strip()

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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)  # 10 seconds timeout
                sock.connect((self.tracker_ip, self.tracker_port))
                logging.info(f"Sending request: {request}")
                sock.sendall(json.dumps(request).encode())
                response = sock.recv(4096).decode()
                logging.info(f"Received response: {response}")
                return json.loads(response)
        except (socket.timeout, socket.error, json.JSONDecodeError) as e:
            logging.error(f"Failed to send request or decode response: {e}")
            print("An error occurred while communicating with the tracker. Please try again later.")
            return {"RET": -1}

    def get_torrent_list(self):
        request = {"OPC": 10, "IP_ADDRESS": self.src_ip, "PORT": self.src_port}
        response = self.send_request(request)
        if response.get('RET') == 0:
            torrents = response.get('TORRENTS', [])
            for idx, name in enumerate(torrents, start=1):
                print(f"{idx}. {name}")
        else:
            print("Failed to get torrent list.")

    def download_torrent(self):
        try:
            torrent_index = int(input("Please enter the torrent number: ").strip()) - 1
            request = {"OPC": 11, "IP_ADDRESS": self.src_ip, "PORT": self.src_port, "TORRENT_INDEX": torrent_index}
            response = self.send_request(request)
            
            if response.get('RET') == 0:
                print("Downloading torrent...")
                file_data = response.get('FILE_DATA')
                if file_data:
                    output_path = os.path.join('src', 'output', 'downloaded_file.file')
                    with open(output_path, 'wb') as file:
                        file.write(file_data)
                    print("File downloaded successfully.")
                else:
                    print("No file data received.")
            else:
                print("Failed to download torrent.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def upload_file(self):
        filename = input("Please enter the filename.ext: ").strip()
        file_path = os.path.join('src', 'input', filename)  # Postavljanje ispravne putanje

        print(f"Checking file at: {file_path}")

        if not os.path.exists(file_path):
            print(f"File {filename} does not exist in the input folder.")
            return

        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                num_of_pieces = (len(file_data) + self.chunk_size - 1) // self.chunk_size  # Računanje broja komadića
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
        except OSError as e:
            logging.error(f"Error accessing file: {e}")
            print("An error occurred while accessing the file.")

    def show_help(self):
        print("Help: Use the menu options to interact with the ShareWave client.")
        print("1) Get & display list of torrents: Fetches and displays available torrents from the tracker.")
        print("2) Download Torrent: Downloads a torrent by ID.")
        print("3) Upload a new file: Uploads a new file to the tracker.")
        print("4) Help: Displays this help message.")
        print("5) Exit: Exits the client application.")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 src/client_handler.py [src_ip] [src_port] [tracker_ip] [tracker_port] [client_name]")
        sys.exit(1)

    src_ip = sys.argv[1]
    src_port = sys.argv[2]
    tracker_ip = sys.argv[3]
    tracker_port = sys.argv[4]
    client_name = sys.argv[5]

    client = ClientHandler(src_ip, src_port, tracker_ip, tracker_port, client_name)
    client.run()
