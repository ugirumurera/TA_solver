import unittest
import os
import inspect
from Java_Connection import Java_Connection
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np


class TestPathCost(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # make Java connection
        cls.connection = Java_Connection()

        # create a static/bpr model manager
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
        bpr_coefficients = {0L: [1, 0, 0, 0, 1], 1L: [1, 0, 0, 0, 1], 2L: [5, 0, 0, 0, 5], 3L: [2, 0, 0, 0, 2],
                        4L: [2, 0, 0, 0, 2], 5L: [1, 0, 0, 0, 1], 6L: [5, 0, 0, 0, 5]}
        cls.model_manager = Link_Model_Manager_class(configfile, cls.connection, "static", None, "bpr", bpr_coefficients)
        api = cls.model_manager.beats_api

        time_period = 1  # Only have one time period for static model
        paths_list = list(api.get_path_ids())
        commodity_list = list(api.get_commodity_ids())
        route_list = {}

        for path_id in paths_list:
            route_list[path_id] = api.get_subnetwork_with_id(path_id).get_link_ids()

        # Test used to validate the Demand_Assignment_Class
        # Creating the demand assignment for initialization
        cls.demand_assignments = Demand_Assignment_class(route_list, commodity_list, time_period, dt = time_period)
        demands = {}
        demand_value = np.zeros(time_period)
        demand_value1 = np.zeros(time_period)
        demand_value[0] = 2
        demand_value1[0] = 2
        demands[(1L, 1L)] = demand_value
        demands[(2L, 1L)] = demand_value1
        demands[(3L, 1L)] = demand_value
        cls.demand_assignments.set_all_demands(demands)

        # create link states
        cls.link_states = cls.model_manager.traffic_model.Run_Model(cls.demand_assignments)
        traffic_model = TestPathCost.model_manager.traffic_model
        link_states = traffic_model.Run_Model(TestPathCost.demand_assignments)
        cls.link_costs = TestPathCost.model_manager.cost_function.evaluate_Cost_Function(link_states)

    def test(self):
        time_period = self.link_costs.get_num_time_step()
        path_costs = Path_Costs_class(time_period, dt = time_period)

        path_costs = path_costs.get_path_costs(self.link_costs, self.demand_assignments)
        self.assertTrue(self.check_path_costs(path_costs))

    def check_path_costs(self, path_costs):
        cost_paths = {(1L, 1L): [2873], (2L, 1L): [2701], (3L, 1L): [1571]}
        costs = path_costs.get_all_path_cots()
        for key in costs.keys():
            if costs[key][0] != cost_paths[key][0]:
                return False
        return True