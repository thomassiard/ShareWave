import unittest
from unittest.mock import patch, MagicMock
import json  # Dodajte ovo uvođenje
from src.tracker import Tracker

class TestTracker(unittest.TestCase):

    def setUp(self):
        # Inicijalizacija Tracker instance prije svakog testa
        self.tracker = Tracker('127.0.0.1', 8888)

    def test_initialization(self):
        # Testiranje ispravne inicijalizacije Trackera
        self.assertEqual(self.tracker.host, '127.0.0.1')
        self.assertEqual(self.tracker.port, 8888)

    @patch('src.tracker.socket.socket')
    def test_start_tracker(self, mock_socket):
        # Testiranje pokretanja Trackera s mockiranim socketom
        mock_server_socket = MagicMock()
        mock_socket.return_value = mock_server_socket

        with patch('src.tracker.Tracker.handle_client', return_value=None) as mock_handle_client:
            with patch('threading.Thread.start', return_value=None) as mock_thread_start:
                self.tracker.start()  # Koristite stvarno ime metode

                mock_server_socket.bind.assert_called_once_with(('127.0.0.1', 8888))
                mock_server_socket.listen.assert_called_once()
                # Provjerite da li metoda handle_client nije pozvana
                # Ovdje očekujemo da ne bude pozvana jer nije bilo stvarnog klijenta
                mock_handle_client.assert_not_called()
                mock_thread_start.assert_not_called()

    @patch('src.tracker.socket.socket')
    def test_handle_client(self, mock_socket):
        # Testiranje rukovanja klijentom
        mock_client_socket = MagicMock()
        mock_client_socket.recv.return_value = json.dumps({"status": "OK"}).encode()

        with patch('src.tracker.Protocol') as mock_protocol:
            mock_protocol.return_value.process_request.return_value = {'status': 'OK'}
            self.tracker.handle_client(mock_client_socket)

            # Provjerite da li je send pozvan s ispravnim podacima
            mock_client_socket.send.assert_called_once_with(json.dumps({'status': 'OK'}).encode())
            mock_client_socket.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
    print("All tests have been run successfully.")
