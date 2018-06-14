
import unittest
import numpy as np
import os
import inspect


from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Java_Connection import Java_Connection

class TestDemandAssignment(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # make Java connection
        cls.connection = Java_Connection()

        # create a static/bpr model manager
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
        bpr_coefficients = {0L: [1, 0, 0, 0, 1], 1L: [1, 0, 0, 0, 1], 2L: [5, 0, 0, 0, 5], 3L: [2, 0, 0, 0, 2],
                        4L: [2, 0, 0, 0, 2], 5L: [1, 0, 0, 0, 1], 6L: [5, 0, 0, 0, 5]}
        cls.model_manager = Link_Model_Manager_class(configfile, "static", cls.connection, None, "bpr", bpr_coefficients)

    def setUp(self):

        # create a demand assignment
        time_period = 1  # Only have one time period for static model
        # paths_list = TestDemandAssignment.model_manager.beats_api.get_path_ids()
        commodity_list = TestDemandAssignment.model_manager.beats_api.get_commodity_ids()

        # rout_list is a dictionary of [path_id]:[link_1, ...]
        route_list = {}
        route_list[1L] = [0L, 1L]
        route_list[2L] = [0L, 2L]

        # Test used to validate the Demand_Assignment_Class
        # Creating the demand assignment for initialization
        self.demand_assignment = Demand_Assignment_class(route_list, commodity_list, time_period,dt=time_period)
        demands = {}
        self.demand_value = np.zeros(time_period)
        self.demand_value1 = np.zeros(time_period)
        self.demand_value[0] = 20
        self.demand_value1[0] = 20
        demands[(1L, 1L)] = self.demand_value
        demands[(2L, 1L)] = self.demand_value1
        self.demand_assignment.set_all_demands(demands)

    def test_set_all_demands_on_path(self):
        self.demand_assignment.set_all_demands_on_path(1L, {1L: self.demand_value1})
        self.assertTrue(self.demand_assignment.get_all_demands_on_path(1L)== {1L: self.demand_value1})

    def test_all_demands_on_path(self):
        path = [0L, 1L, 2L]
        self.demand_assignment.add_all_demands_on_path(4L, path , {1L: self.demand_value1})
        x = self.demand_assignment.get_path_list()[4L]
        self.assertTrue(self.demand_assignment.get_all_demands_on_path(4L)[1L][0] == self.demand_value1[0] and
                        all(self.demand_assignment.get_path_list()[4L][i] == path[i] for i in range(len(path))))


    def test_all_demands_on_path_comm(self):
        self.assertTrue(self.demand_assignment.set_all_demands_on_path_comm(4L, 1L, self.demand_value) == False)


    def test_add_all_demands_on_path_comm(self):
        path = [0L, 1L, 2L]
        self.demand_assignment.add_all_demands_on_path_comm(14L, path, 1L, self.demand_value1)
        self.assertTrue(self.demand_assignment.get_all_demands_on_path_comm(14,1L)[0] == self.demand_value1[0] and
                        all(self.demand_assignment.get_path_list()[14L][i] == path[i] for i in range(len(path))))

    def test_add_all_demands_on_path_time_step(self):
        path = [0L, 1L, 2L]
        self.demand_assignment.add_all_demands_on_path_time_step(45L, path, 0, {1L: 90})
        self.assertTrue(self.demand_assignment.get_all_demands_on_path_time_step(45L, 0)[1L] == 90 and
                        all(self.demand_assignment.get_path_list()[45L][i] == path[i] for i in range(len(path))))

    def test_set_all_demands_for_commodity(self):
        self.assertTrue(self.demand_assignment.set_all_demands_for_commodity(1L, {43L: self.demand_value}) == False)

    def test_set_all_demands_on_comm_time_step(self):
        path = [0L, 1L, 2L]
        self.demand_assignment.add_all_demands_on_path_time_step(45L, path, 0, {1L: 90})
        self.demand_assignment.set_all_demands_on_comm_time_step(1L, 0, {45L: 273})
        self.assertTrue(self.demand_assignment.get_all_demands_on_comm_time_step(1L,0)[45L] == 273)

    def test_set_all_demands_for_time_step(self):
        path = [0L, 1L, 2L]
        self.demand_assignment.add_all_demands_on_path_time_step(45L, path, 0, {1L: 90})
        self.demand_assignment.set_all_demands_for_time_step(0, {(45L, 1L): 467})
        self.assertTrue(self.demand_assignment.get_all_demands_for_time_step(0)[(45L, 1L)] == 467)
