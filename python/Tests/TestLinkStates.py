import unittest
import numpy as np
import os
import inspect
from Java_Connection import Java_Connection
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Traffic_States.Static_Traffic_State import Static_Traffic_State_class


class TestLinkStates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # make Java connection
        cls.connection = Java_Connection()

        # create a static/bpr model managers
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
        bpr_coefficients = {0L: [1, 0, 0, 0, 1], 1L: [1, 0, 0, 0, 1], 2L: [5, 0, 0, 0, 5], 3L: [2, 0, 0, 0, 2],
                            4L: [2, 0, 0, 0, 2], 5L: [1, 0, 0, 0, 1], 6L: [5, 0, 0, 0, 5]}
        cls.model_manager = Link_Model_Manager_class(configfile, "static", cls.connection, None, "bpr", bpr_coefficients)

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

    def test_get_state_on_link_comm_time(self):
        self.assertTrue(TestLinkStates.link_states.get_state_on_link_comm_time(0L, 1, 0)!= False)

    def test_get_all_states_on_link(self):
        self.assertTrue(TestLinkStates.link_states.get_all_states_on_link(10) == False)

    def test_get_all_states_on_link_comm(self):
        self.assertTrue(TestLinkStates.link_states.get_all_states_on_link_comm(0, 1) != False)

    def test_get_all_states_on_link_time_step(self):
        self.assertTrue(TestLinkStates.link_states.get_all_states_on_link_time_step(2, 0) != False)

    def test_get_all_states_for_commodity(self):
        self.assertTrue(TestLinkStates.link_states.get_all_states_for_commodity(1) != False)

    def test_get_all_states_on_comm_time_step(self):
        self.assertTrue(TestLinkStates.link_states.get_all_states_on_comm_time_step(1, 0) != False)


    def test_get_all_states_for_time_step(self):
        self.assertTrue(TestLinkStates.link_states.get_all_states_for_time_step(0) != False)


    def test_rest(self):

        state = Static_Traffic_State_class()
        state.set_flow(576)
        state_list = list()
        state_list.append(state)
        comm_list = {1L: state_list}

        TestLinkStates.link_states.set_all_states_on_link(1, comm_list)
        self.assertTrue(TestLinkStates.link_states.get_state_on_link_comm_time(1, 1, 0).get_flow() == 576)

        state.set_flow(674)
        TestLinkStates.link_states.set_all_states_on_link_comm(1, 1, state_list)
        self.assertTrue(TestLinkStates.link_states.get_state_on_link_comm_time(1, 1, 0).get_flow() == 674)

        comm_list1 = {1L: state}
        TestLinkStates.link_states.set_all_states_on_link_time_step(3, 0, comm_list1)
        self.assertTrue(TestLinkStates.link_states.get_state_on_link_comm_time(3, 1, 0).get_flow() == 674)

        state.set_flow(100)
        TestLinkStates.link_states.set_all_states_for_commodity(1, comm_list)
        self.assertTrue(TestLinkStates.link_states.get_state_on_link_comm_time(1, 1, 0).get_flow() == 100)

        state.set_flow(200)
        TestLinkStates.link_states.set_all_states_on_comm_time_step(1, 0, comm_list1)
        self.assertTrue(TestLinkStates.link_states.get_state_on_link_comm_time(1, 1, 0).get_flow() == 200)

        comm_list1 = {(2L, 2L): state}
        self.assertTrue(TestLinkStates.link_states.set_all_demands_for_time_step(0, comm_list1) == False)
