
import unittest
import os
import inspect
import numpy as np
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class


class TestBeATS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = Java_Connection()

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, os.path.pardir, 'configfiles', 'seven_links.xml')
        dt = 2
        cls.model_manager = BeATS_Model_Manager_class(configfile, cls.conn.gateway, dt)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_beats_model_manager(self):
        # check the model manager
        self.assertTrue(TestBeATS.model_manager.is_valid())

    def test_evaluate(self):

        api = TestBeATS.model_manager.beats_api

        T = 3600.0
        dt = 2.0

        start_time = 0.0
        n = int(T/dt)

        # create a demand assignment
        commodity_list = api.get_commodity_ids()

        # rout_list is a dictionary of [path_id]:[link_1, ...]
        route_list = {}
        route_list[1L] = [0L, 1L]
        route_list[2L] = [0L, 2L]

        # Test used to validate the Demand_Assignment_Class# Creating the demand assignment for initialization
        demand_assignment = Demand_Assignment_class(route_list, commodity_list, n, dt)
        demands = {}
        demand_value = np.zeros(n)
        demand_value1 = np.zeros(n)
        demand_value[0] = 20
        demand_value1[0] = 20
        demands[(1L, 1L)] = demand_value
        demands[(2L, 1L)] = demand_value1
        demand_assignment.set_all_demands(demands)

        # request path travel time output
        for path_id in demand_assignment.get_path_list():
            api.request_path_travel_time(path_id, 60.0)

        # clear demands in beats
        api.clear_all_demands()

        # send demand assignment to beats
        for key, values in demand_assignment.get_all_demands().iteritems():
            array = TestBeATS.conn.gateway.jvm.java.util.ArrayList()
            for v in values:
                array.add(v)
            api.set_demand_on_path_in_vph(key[0], key[1], start_time, dt, array)

        # run BeATS
        api.run(start_time, dt, T)

        # extract the path costs
        path_costs = Path_Costs_class(n, dt)
        comm_id = 1
        for path_data in api.get_output_data():
            cost_list = path_data.compute_travel_time_for_start_times(start_time, dt, n)
            path_costs.set_costs_path_commodity(path_data.getPathId(), comm_id, cost_list)
