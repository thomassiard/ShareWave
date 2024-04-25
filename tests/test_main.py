import unittest
from server.main import app, files

class TestMain(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_file(self):
        response = self.app.post('/upload', data=dict(filename='test.txt', file=(BytesIO(b'my file contents'), 'test.txt')))
        self.assertEqual(response.status_code, 200)

    def test_search_file(self):
        response = self.app.get('/search?query=test')
        self.assertEqual(response.status_code, 200)
        # Provjerite je li testiranje pretraživanja datoteka ispravno

    def test_download_file(self):
        response = self.app.get('/download/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test.txt', response.data)

if __name__ == '__main__':
    unittest.main()
