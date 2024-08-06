# tests/test_file_service.py
import unittest
from server.main import app

class FileServiceTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_no_file(self):
        response = self.app.post('/files/upload', data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No file part', response.data)

if __name__ == "__main__":
    unittest.main()
