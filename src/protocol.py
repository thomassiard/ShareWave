import json
import os
import logging

# Postavljanje osnovnog logger-a za zapisivanje u fajl
log_dir = 'src/logs'
log_file = 'protocol.log'
log_path = os.path.join(log_dir, log_file)

# Kreirajte log folder ako ne postoji
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Konfiguracija osnovnog logovanja
logging.basicConfig(filename=log_path,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Definiranje opcija i povratnih kodova
OPT_GET_LIST = 10
OPT_GET_PIECE = 11
OPT_GET_PEERS = 12
OPT_REGISTER = 14

RET_NO_AVAILABLE_TORRENTS = 1

# Definiranje ključeva za protokol
OPC = "OPC"
IP = "IP_ADDRESS"
PORT = "PORT"
PID = "PID"
TID = "TORRENT_ID"
PIECE_IDX = "PIECE_IDX"
PEER_LIST = "PEER_LIST"
RET = "RET"

class Protocol:
    def __init__(self):
        # Direktorij za pohranu datoteka (možete ga prilagoditi prema potrebi)
        self.file_storage_dir = 'src/input'
        if not os.path.exists(self.file_storage_dir):
            os.makedirs(self.file_storage_dir)

    def send(self, conn, data):
        try:
            message = json.dumps(data).encode()
            conn.sendall(message)
        except Exception as e:
            logging.error(f"Error sending data: {e}")

    def receive(self, conn):
        try:
            data = conn.recv(4096)  # Povećana veličina bafera za prijem većih poruka
            if not data:
                return None
            return json.loads(data.decode())
        except Exception as e:
            logging.error(f"Error receiving data: {e}")
            return None

    def create_registration_request(self, ip, port):
        return {
            OPC: OPT_REGISTER,  # Opcionalni kod za registraciju
            IP: ip,
            PORT: port
        }

    def create_torrent_list_request(self, ip, port):
        return {
            OPC: OPT_GET_LIST,  # Opcionalni kod za zahtjev liste torrenta
            IP: ip,
            PORT: port
        }

    def create_download_request(self, ip, port, torrent_id):
        return {
            OPC: OPT_GET_PIECE,  # Opcionalni kod za preuzimanje torrenta
            IP: ip,
            PORT: port,
            TID: torrent_id
        }

    def create_upload_request(self, ip, port, filename, num_of_pieces):
        return {
            OPC: OPT_REGISTER,  # Opcionalni kod za upload file-a
            IP: ip,
            PORT: port,
            "FILE_NAME": filename,
            "NUM_OF_PIECES": num_of_pieces
        }

    def process_request(self, request, peers):
        opc = request.get(OPC)

        if opc == OPT_GET_LIST:  # Zahtjev za listu torrenta
            return self.handle_torrent_list_request(request)
        elif opc == OPT_GET_PIECE:  # Zahtjev za preuzimanje torrenta
            return self.handle_download_request(request)
        elif opc == OPT_REGISTER:  # Zahtjev za upload file-a
            return self.handle_upload_request(request, peers)
        else:
            return {RET: -1, 'MSG': 'Invalid request'}

    def handle_torrent_list_request(self, request):
        # Mock response za listu torrenta
        torrents = ['torrent1', 'torrent2', 'torrent3']
        return {RET: 0, 'TORRENTS': torrents}

    def handle_download_request(self, request):
        torrent_id = request.get(TID)
        # Dohvat podataka o datoteci (samo mock u ovom primjeru)
        file_data = self.get_file_data(torrent_id)
        if file_data:
            return {RET: 0, 'FILE_DATA': file_data}
        else:
            return {RET: -1, 'MSG': 'File not found'}

    def handle_upload_request(self, request, peers):
        filename = request.get('FILE_NAME')
        num_of_pieces = request.get('NUM_OF_PIECES')
        # Primanje stvarnih podataka o datoteci
        file_data = self.receive_file_data(request)
        if file_data:
            self.store_file(filename, file_data)
            return {RET: 0, 'FILE_NAME': filename, 'NUM_OF_PIECES': num_of_pieces, 'STATUS': 'Uploaded'}
        else:
            return {RET: -1, 'MSG': 'Upload failed'}

    def get_file_data(self, torrent_id):
        # Simulacija dohvaćanja podataka datoteke
        file_path = os.path.join(self.file_storage_dir, f'{torrent_id}.file')
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                return file.read()
        else:
            return None

    def store_file(self, filename, file_data):
        # Pohrana datoteke na disk
        path = os.path.join(self.file_storage_dir, filename)
        with open(path, 'wb') as file:
            file.write(file_data)

    def receive_file_data(self, request):
        # Simulacija primanja podataka datoteke
        # U stvarnoj primjeni, trebali biste primiti stvarne podatke o datoteci putem više paketa
        return b'Sample file data'  # Zamijenite s stvarnim podatkom

if __name__ == "__main__":
    protocol = Protocol()
