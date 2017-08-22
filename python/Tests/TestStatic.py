
import unittest
import numpy as np

from Solvers.Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from Solvers.Decomposition_Solver import Decomposition_Solver
import timeit
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class

import os
import inspect


class TestStatic(unittest.TestCase):

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

        # create a demand assignment
        api = TestStatic.model_manager.beats_api

        time_period = 1  # Only have one time period for static model
        paths_list = list(api.get_path_ids())
        commodity_list = list(api.get_commodity_ids())
        route_list = {}

        for path_id in paths_list:
            route_list[path_id] = api.get_subnetwork_with_id(path_id).get_link_ids()

        # Creating the demand assignment for initialization
        cls.demand_assignments = Demand_Assignment_class(route_list, commodity_list, time_period, dt=time_period)
        demands = {}
        demand_value = np.zeros(time_period)
        demand_value1 = np.zeros(time_period)
        demand_value[0] = 2
        demand_value1[0] = 2
        demands[(1L, 1L)] = demand_value
        demands[(2L, 1L)] = demand_value1
        cls.demand_assignments.set_all_demands(demands)
        # print("\nDemand Assignment on path is as follows (Demand_Assignment class):")
        # demand_assignments.print_all()

    def check_manager(self):
        self.assertTrue(TestStatic.model_manager.is_valid())

    def test_model_run(self):
        traffic_model = TestStatic.model_manager.traffic_model
        link_states = traffic_model.Run_Model(TestStatic.demand_assignments)
        link_states.print_all()

    def test_link_cost(self):
        print("\nCalculating the cost per link (Link Cost class)")
        print("We initialize the BPR function with the following coefficients: ")
        cost_function = TestStatic.model_manager.cost_function
        print(cost_function.__Coefficients)

    def test_path_based_fw(self):
        num_steps = 1
        start_time1 = timeit.default_timer()
        assignment_seq = Path_Based_Frank_Wolfe_Solver(self.model_manager, num_steps)
        elapsed1 = timeit.default_timer() - start_time1

    def test_decomposition_solver(self):
        number_of_subproblems = 1
        start_time1 = timeit.default_timer()
        assignment_dec, error = Decomposition_Solver(self.traffic_scenario, self.Cost_Function, number_of_subproblems)
        print "Decomposition finished with error ", error
        elapsed1 = timeit.default_timer() - start_time1
        print ("Decomposition Path-based took  %s seconds" % elapsed1)

    def test_link_based_fw(self):
        start_time1 = timeit.default_timer()
        frank_sol = Frank_Wolfe_Solver(self.model_manager)
        elapsed1 = timeit.default_timer() - start_time1
