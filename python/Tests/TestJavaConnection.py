
import unittest

from Java_Connection import Java_Connection


class TestJavaConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = Java_Connection()

    def test(self):
        self.assertTrue(TestJavaConnection.conn.is_valid())

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
