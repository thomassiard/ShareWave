import unittest
from unittest.mock import patch, MagicMock
from src.peer import Peer

class TestPeer(unittest.TestCase):
    
    def setUp(self):
        # Postavljanje osnovnih parametara za inicijalizaciju Peer-a
        self.peer = Peer('127.0.0.1', 8881, '127.0.0.1', 8888)

    def test_peer_initialization(self):
        # Testiranje ispravne inicijalizacije Peer-a
        self.assertEqual(self.peer.ip, '127.0.0.1')
        self.assertEqual(self.peer.port, 8881)
        self.assertEqual(self.peer.tracker_ip, '127.0.0.1')
        self.assertEqual(self.peer.tracker_port, 8888)

    @patch('src.peer.socket.socket')
    def test_peer_connect_to_tracker(self, mock_socket):
        # Mockiranje povezivanja s trackerom
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn

        self.peer.connect_to_tracker(mock_conn)

        # Provjera je li poslan ispravan zahtjev trackeru
        mock_conn.connect.assert_called_once_with(('127.0.0.1', 8888))
        self.assertTrue(mock_conn.sendall.called)

    @patch('src.peer.socket.socket')
    def test_peer_listen_for_requests(self, mock_socket):
        # Mockiranje primanja podataka
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn
        mock_conn.recv.return_value = b'{"some": "data"}'

        with patch('src.peer.Protocol.receive', return_value={"some": "data"}) as mock_receive:
            self.peer.listen_for_requests(mock_conn)
            mock_receive.assert_called_once_with(mock_conn)

if __name__ == "__main__":
    unittest.main()
