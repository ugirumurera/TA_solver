# This is the model manager for link-based models
from __future__ import division
from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class
from copy import copy, deepcopy
import numpy as np
import timeit

class BeATS_Model_Manager_class(Abstract_Model_Manager_class):

    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, traffic_model_name, gateway, sim_dt):
        Abstract_Model_Manager_class.__init__(self, configfile, traffic_model_name, sim_dt, gateway)

    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignment, time_horizon, initial_state=None):

        start_time = 0.0
        read_time = demand_assignment.get_dt()*0.0    # Hack, heuristic, need a state estimator
        path_cost_dt = float(demand_assignment.get_dt())
        path_cost_n = demand_assignment.get_num_time_step()  # int(time_horizon/path_cost_dt)
        demand_dt = path_cost_dt
        demand_n = int(time_horizon/demand_dt)

        #Clear the path requests
        self.beats_api.clear_output_requests()

        # request path travel time output
        for path_id in demand_assignment.get_path_list():
            self.beats_api.request_path_travel_time(path_id, path_cost_dt)

        # clear demands in beats
        self.beats_api.clear_all_demands()

        # send demand assignment to beats
        for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
            path_id = path_comm[0]
            comm_id = path_comm[1]
            java_array = self.gateway.jvm.java.util.ArrayList()
            for d in demand_list:
                java_array.add(float(d))
            self.beats_api.set_demand_on_path_in_vph(path_id, comm_id, start_time, demand_dt, java_array)

        # run BeATS
        self.beats_api.set_random_seed(1)      #Initialize the random seed
        self.beats_api.run(float(start_time), float(time_horizon))

        # extract the path costs
        path_costs = Path_Costs_class(path_cost_n, demand_dt)
        path_costs.set_path_list(demand_assignment.get_path_list())
        path_costs.set_comm_list(demand_assignment.get_commodity_list())

        for path_data in self.beats_api.get_output_data():
            cost_list = path_data.compute_travel_time_for_start_times(read_time, path_cost_dt, demand_n)
            path_costs.set_costs_path_commodity(path_data.get_path_id(), None, cost_list)

        return path_costs
