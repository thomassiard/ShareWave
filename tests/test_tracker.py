import unittest
from unittest.mock import patch, MagicMock
from src.tracker import Tracker

class TestTracker(unittest.TestCase):

    def setUp(self):
        # Inicijalizacija Tracker instance prije svakog testa
        self.tracker = Tracker('127.0.0.1', 8888)

    def test_initialization(self):
        # Testiranje ispravne inicijalizacije Trackera
        self.assertEqual(self.tracker.ip, '127.0.0.1')
        self.assertEqual(self.tracker.port, 8888)

    @patch('src.tracker.socket.socket')
    def test_start_tracker(self, mock_socket):
        # Testiranje pokretanja Trackera s mockiranim socketom
        mock_server_socket = MagicMock()
        mock_socket.return_value = mock_server_socket

        with patch('src.tracker.Tracker.handle_client', return_value=None) as mock_handle_client:
            with patch('threading.Thread.start', return_value=None) as mock_thread_start:
                self.tracker.start_tracker()

                mock_server_socket.bind.assert_called_once_with(('127.0.0.1', 8888))
                mock_server_socket.listen.assert_called_once()
                mock_handle_client.assert_not_called()
                mock_thread_start.assert_not_called()

    @patch('src.tracker.socket.socket')
    def test_handle_client(self, mock_socket):
        # Testiranje rukovanja klijentom
        mock_client_socket = MagicMock()
        self.tracker.handle_client(mock_client_socket)

        mock_client_socket.send.assert_called_once_with(b"Tracker is running")
        mock_client_socket.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
    print("All tests have been run successfully.")
