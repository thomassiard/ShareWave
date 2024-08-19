import unittest
from unittest.mock import patch, MagicMock
from src.client_handler import ClientHandler

class TestClientHandler(unittest.TestCase):
    
    def setUp(self):
        # Postavljanje osnovnih parametara za inicijalizaciju ClientHandler-a
        self.client = ClientHandler('127.0.0.1', 8881, '127.0.0.1', 8888)
    
    @patch('src.client_handler.socket.socket')
    def test_get_torrent_list_success(self, mock_socket):
        # Mockiranje uspješnog odgovora od trackera
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn
        mock_conn.recv.return_value = '{"RET": 0, "TORRENTS": ["file1.torrent", "file2.torrent"]}'.encode()

        with patch('builtins.print') as mocked_print:
            self.client.get_torrent_list()
            mocked_print.assert_any_call("Available torrents:", ["file1.torrent", "file2.torrent"])

    @patch('src.client_handler.socket.socket')
    def test_download_torrent_fail(self, mock_socket):
        # Mockiranje neuspješnog preuzimanja torrenta
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn
        mock_conn.recv.return_value = '{"RET": 1}'.encode()

        with patch('builtins.print') as mocked_print:
            self.client.download_torrent()
            mocked_print.assert_any_call("Failed to download torrent.")

    @patch('src.client_handler.socket.socket')
    def test_upload_file_not_found(self, mock_socket):
        # Testiranje situacije kad datoteka nije pronađena
        with patch('builtins.input', return_value='nonexistentfile.ext'):
            with patch('builtins.print') as mocked_print:
                self.client.upload_file()
                mocked_print.assert_any_call("File not found.")

    @patch('src.client_handler.socket.socket')
    def test_send_request(self, mock_socket):
        # Testiranje slanja zahtjeva trackeru
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn
        mock_conn.recv.return_value = '{"RET": 0}'.encode()

        request = {"OPC": 10, "IP_ADDRESS": "127.0.0.1", "PORT": 8881}
        response = self.client.send_request(request)
        self.assertEqual(response, {"RET": 0})
        mock_conn.sendall.assert_called_once_with(b'{"OPC": 10, "IP_ADDRESS": "127.0.0.1", "PORT": 8881}')

if __name__ == "__main__":
    unittest.main()
