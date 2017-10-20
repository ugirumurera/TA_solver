
import unittest
import os
import inspect
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class


class TestMN(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = Java_Connection()

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, os.path.pardir, 'configfiles', 'seven_links.xml')
        sim_dt = 2
        coefficients = {0L: [1, 0, 0, 0, 1], 1L: [1, 0, 0, 0, 1], 2L: [2, 0, 0, 0, 2], 3L: [1, 0, 0, 0, 1],
                        4L: [2, 0, 0, 0, 2], 5L: [1, 0, 0, 0, 1], 6L: [1, 0, 0, 0, 1]}

        cls.model_manager = Link_Model_Manager_class(configfile, cls.conn.gateway, "mn", sim_dt, "bpr", coefficients)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_mn_model_manager(self):
        self.assertTrue(TestMN.model_manager.is_valid())

    # def test_evaluate(self):
    #
    #     api = TestMN.model_manager.beats_api
    #
    #     comm_id = 1
    #     time_horizon = 3600.0
    #     start_time = 0.0
    #     path_cost_dt = 60.0
    #     path_cost_n = int(time_horizon/path_cost_dt)
    #     demand_dt = 1800.0
    #     demand_n = int(time_horizon/demand_dt)
    #
    #     # create a demand assignment
    #     commodity_list = api.get_commodity_ids()
    #
    #     # rout_list is a dictionary of [path_id]:[link_1, ...]
    #     route_list = {1L: [0L, 1L],
    #                   2L: [0L, 2L]}
    #
    #     # Test used to validate the Demand_Assignment_Class# Creating the demand assignment for initialization
    #     demand_assignment = Demand_Assignment_class(route_list, commodity_list, demand_n, demand_dt)
    #     demand_assignment.set_all_demands({(1L, 1L): [20, 0],
    #                                        (2L, 1L): [20, 0]})
    #
    #     # request path travel time output
    #     for path_id in demand_assignment.get_path_list():
    #         api.request_path_travel_time(path_id, path_cost_dt)
    #
    #     # clear demands in beats
    #     api.clear_all_demands()
    #
    #     # send demand assignment to beats
    #     for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
    #         path_id = path_comm[0]
    #         comm_id = path_comm[1]
    #         array = TestMN.conn.gateway.jvm.java.util.ArrayList()
    #         for v in demand_list:
    #             array.add(float(v))
    #         api.set_demand_on_path_in_vph(path_id, comm_id, start_time, demand_dt, array)
    #
    #     # run BeATS
    #     api.run(start_time, time_horizon)

        # extract the path costs
        # path_costs = Path_Costs_class(path_cost_n, path_cost_dt)
        # for path_data in api.get_output_data():
        #     cost_list = path_data.compute_travel_time_for_start_times(start_time, path_cost_dt, demand_n)
        #     path_costs.set_costs_path_commodity(path_data.getPathId(), comm_id, cost_list)

    def test_model_manager(self):

        api = TestMN.model_manager.beats_api

        comm_id = 1L
        sim_dt = 2.0
        time_horizon = 3600.0
        demand_dt = 1200.0
        demand_n = int(time_horizon/demand_dt)

        # create a demand assignment
        commodity_list = api.get_commodity_ids()

        # rout_list is a dictionary of [path_id]:[link_1, ...]
        route_list = {1L: [0L, 1L, 3L, 6L],
                      2L: [0L, 2L, 4L, 6L],
                      3L: [0L, 1L, 5L]}

        # Test used to validate the Demand_Assignment_Class# Creating the demand assignment for initialization
        demand_assignment = Demand_Assignment_class(route_list, commodity_list, demand_n, demand_dt)
        demand_assignment.set_all_demands({(1L, comm_id): [1000, 1000, 1000],
                                           (2L, comm_id): [0, 0, 0],
                                           (3L, comm_id): [0, 0, 0]})

        TestMN.model_manager.evaluate(demand_assignment, sim_dt, time_horizon)
