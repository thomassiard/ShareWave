# src/tracker.py

import socket
import threading

def handle_client(client_socket):
    # Ovdje dodajte kod za rukovanje klijentima
    client_socket.send("Tracker is running".encode())
    client_socket.close()

def start_tracker(host='127.0.0.1', port=8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Tracker is running on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_tracker()
