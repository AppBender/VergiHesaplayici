import unittest

from src.app import app


class AppTest(unittest.TestCase):

    def setUp(self):
        # Set up the test client for Flask
        self.app = app.test_client()
        self.app.testing = True

    def test_welcome(self):
        # Test the welcome route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html>', response.data)  # Example check for HTML content

    def tearDown(self):
        # Clean up after each test if necessary
        pass


if __name__ == '__main__':
    unittest.main()
