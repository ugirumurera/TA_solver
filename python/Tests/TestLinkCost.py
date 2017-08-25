import unittest
import os
import inspect
from Java_Connection import Java_Connection
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
import numpy as np


class TestLinkCost(unittest.TestCase):

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

    def test(self):
        # Initialize the BPR cost function
        traffic_model = TestLinkCost.model_manager.traffic_model
        link_states = traffic_model.Run_Model(TestLinkCost.demand_assignments)
        link_costs = TestLinkCost.model_manager.cost_function.evaluate_Cost_Function(link_states)
        self.assertTrue(self.check_link_costs(link_costs))

        # Test for Link_Costs_Class
        self.assertTrue(link_costs.get_cost_at_link_comm_time(0, 1, 0) != False)
        self.assertTrue(link_costs.get_all_costs_on_link(2) != False)
        self.assertTrue(link_costs.get_all_costs_on_link_comm(1, 1))
        self.assertTrue(link_costs.get_all_costs_on_link_time_step(1, 0))
        self.assertTrue(link_costs.get_all_costs_for_commodity(1))
        self.assertTrue(link_costs.get_all_costs_on_comm_time_step(1, 0))
        self.assertTrue(link_costs.get_all_costs_for_time_step(0))

        link_costs.set_all_costs(link_costs.get_all_costs())
        comm_cost = {1L: [20]}
        link_costs.set_all_costs_on_link(1, comm_cost)
        self.assertTrue(link_costs.get_cost_at_link_comm_time(1, 1, 0) == 20)

        self.assertTrue(link_costs.set_all_costs_on_link_comm(1, 1, [-48]) == False)

        link_costs.set_all_costs_on_link_time_step(2, 0, {1L: 1085})
        self.assertTrue(link_costs.get_cost_at_link_comm_time(2, 1, 0) == 1085)

        link_costs.set_all_costs_for_commodity(1, comm_cost)
        self.assertTrue(link_costs.get_cost_at_link_comm_time(1, 1, 0) == 20)

        self.assertTrue(link_costs.set_all_costs_on_comm_time_step(1, 0, {3L: [4657, 12], 5L: 3649}) == False)

        link_costs.set_all_costs_for_time_step(0, {(3L, 1L): 374, (5L, 1L): 4659})
        self.assertTrue(link_costs.get_cost_at_link_comm_time(3, 1, 0) == 374)
        self.assertTrue(link_costs.get_cost_at_link_comm_time(5, 1, 0) == 4659)

    def check_link_costs(self, link_costs):
        cost_links = {(0L,1L): [1297], (1L,1L): [257], (2L,1L): [85], (3L,1L): [34],
                       (4L,1L): [34], (5L,1L): [17], (6L,1L): [1285]}

        states = link_costs.get_all_costs()
        for key in states.keys():
            if states[key][0] != cost_links[key][0]:
                return False

        return True