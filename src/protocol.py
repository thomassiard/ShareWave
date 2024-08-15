import json
import socket

class Protocol:
    def __init__(self):
        pass

    def send(self, conn, data):
        """Šalje JSON enkodirane podatke preko konekcije."""
        try:
            message = json.dumps(data).encode()
            conn.sendall(message)
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive(self, conn):
        """Prima JSON dekodirane podatke preko konekcije."""
        try:
            data = conn.recv(4096)  # Povećana veličina bafera za prijem većih poruka
            if not data:
                return None
            return json.loads(data.decode())
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None

    def create_registration_request(self, ip, port):
        """Kreira zahtjev za registraciju peer-a na tracker."""
        return {
            'OPC': 14,  # Opcionalni kod za registraciju (npr. 14)
            'IP_ADDRESS': ip,
            'PORT': port
        }

    def create_torrent_list_request(self, ip, port):
        """Kreira zahtjev za dobivanje liste dostupnih torrenta."""
        return {
            'OPC': 10,  # Opcionalni kod za zahtjev liste torrenta
            'IP_ADDRESS': ip,
            'PORT': port
        }

    def create_download_request(self, ip, port, torrent_id):
        """Kreira zahtjev za preuzimanje određenog torrenta."""
        return {
            'OPC': 11,  # Opcionalni kod za preuzimanje torrenta
            'IP_ADDRESS': ip,
            'PORT': port,
            'TORRENT_ID': torrent_id
        }

    def create_upload_request(self, ip, port, filename, num_of_pieces):
        """Kreira zahtjev za upload novog file-a na tracker."""
        return {
            'OPC': 14,  # Opcionalni kod za upload file-a
            'IP_ADDRESS': ip,
            'PORT': port,
            'FILE_NAME': filename,
            'NUM_OF_PIECES': num_of_pieces
        }

    def process_request(self, request, peers):
        """Procesira različite tipove zahtjeva od peer-ova."""
        opc = request.get('OPC')

        if opc == 10:  # Zahtjev za listu torrenta
            return self.handle_torrent_list_request(request)
        elif opc == 11:  # Zahtjev za preuzimanje torrenta
            return self.handle_download_request(request)
        elif opc == 14:  # Zahtjev za upload file-a
            return self.handle_upload_request(request, peers)
        else:
            return {'RET': -1, 'MSG': 'Invalid request'}

    def handle_torrent_list_request(self, request):
        """Rukuje zahtjevom za listu torrenta (mock funkcionalnost)."""
        # Mock response
        torrents = ['torrent1', 'torrent2', 'torrent3']
        return {'RET': 0, 'TORRENTS': torrents}

    def handle_download_request(self, request):
        """Rukuje zahtjevom za preuzimanje torrenta (mock funkcionalnost)."""
        torrent_id = request.get('TORRENT_ID')
        # Mock response
        return {'RET': 0, 'TORRENT_ID': torrent_id, 'STATUS': 'Downloading'}

    def handle_upload_request(self, request, peers):
        """Rukuje zahtjevom za upload file-a (mock funkcionalnost)."""
        filename = request.get('FILE_NAME')
        num_of_pieces = request.get('NUM_OF_PIECES')
        # Mock response
        return {'RET': 0, 'FILE_NAME': filename, 'NUM_OF_PIECES': num_of_pieces, 'STATUS': 'Uploaded'}

if __name__ == "__main__":
    protocol = Protocol()
