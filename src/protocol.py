import json
import socket

class Protocol:
    def __init__(self):
        pass

    def send(self, conn, data):
        message = json.dumps(data).encode()
        conn.sendall(message)

    def receive(self, conn):
        data = conn.recv(1024)
        return json.loads(data.decode())

    def create_registration_request(self, ip, port):
        return {
            'OPC': 14, 'IP_ADDRESS': ip, 'PORT': port
        }

    def process_request(self, request, peers):
        # Process different request types here
        return {}

if __name__ == "__main__":
    protocol = Protocol()
