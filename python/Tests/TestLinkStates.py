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
        cls.model_manager = Link_Model_Manager_class(configfile, cls.connection, "static", None, "bpr", bpr_coefficients)

        # create a demand assignment
        time_period = 1  # Only have one time period for static model
        # paths_list = TestDemandAssignment.model_manager.beats_api.get_path_ids()
        commodity_list = cls.model_manager.beats_api.get_commodity_ids()

        # rout_list is a dictionary of [path_id]:[link_1, ...]
        route_list = {}
        route_list[1L] = [0L, 1L]
        route_list[2L] = [0L, 2L]

        # Test used to validate the Demand_Assignment_Class
        # Creating the demand assignment for initialization
        demand_assignments = Demand_Assignment_class(route_list, commodity_list, time_period)
        demands = {}
        demand_value = np.zeros(time_period)
        demand_value1 = np.zeros(time_period)
        demand_value[0] = 20
        demand_value1[0] = 20
        demands[(1L, 1L)] = demand_value
        demands[(2L, 1L)] = demand_value1
        demand_assignments.set_all_demands(demands)

        # create link states
        cls.link_states = cls.model_manager.traffic_model.Run_Model(demand_assignments)


    def test_get_state_on_link_comm_time(self):
        TestLinkStates.link_states.get_state_on_link_comm_time(0L, 1, 0).print_state()

    def test_get_all_states_on_link(self):
        result = TestLinkStates.link_states.get_all_states_on_link(2)

    def test_get_all_states_on_link_comm(self):
        result = TestLinkStates.link_states.get_all_states_on_link_comm(0, 1)

    def test_get_all_states_on_link_time_step(self):
        result = TestLinkStates.link_states.get_all_states_on_link_time_step(2, 0)

    def test_get_all_states_for_commodity(self):
        result = TestLinkStates.link_states.get_all_states_for_commodity(1)

    def test_get_all_states_on_comm_time_step(self):
        result = TestLinkStates.link_states.get_all_states_on_comm_time_step(1, 0)

    def test_get_all_states_for_time_step(self):
        result = TestLinkStates.link_states.get_all_states_for_time_step(0)

    def test_set_all_states(self):
        TestLinkStates.link_states.set_all_states(TestLinkStates.link_states.get_all_states())

    def test_rest(self):

        state = Static_Traffic_State_class()
        state.set_flow(576)
        state_list = list()
        state_list.append(state)
        comm_list = {1L: state_list}

        TestLinkStates.link_states.set_all_states_on_link(1, comm_list)

        TestLinkStates.link_states.set_all_states_on_link_comm(1, 1, state_list)

        comm_list1 = {1L: state}
        TestLinkStates.link_states.set_all_states_on_link_time_step(1, 0, comm_list1)

        TestLinkStates.link_states.set_all_states_for_commodity(1, comm_list)

        TestLinkStates.link_states.set_all_states_on_comm_time_step(1, 0, comm_list1)

        comm_list1 = {(2L, 2L): state}
        TestLinkStates.link_states.set_all_demands_for_time_step(0, comm_list1)

        TestLinkStates.link_states.print_all()