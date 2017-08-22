
import unittest
import os
import inspect
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Java_Connection import Java_Connection


class TestBeATS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = Java_Connection()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_beats_model_manager(self):
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, os.path.pardir, 'configfiles', 'seven_links.xml')
        dt = 2
        model_manager = BeATS_Model_Manager_class(configfile, TestBeATS.conn, dt)

        # check the model manager
        self.assertTrue(model_manager.is_valid())
