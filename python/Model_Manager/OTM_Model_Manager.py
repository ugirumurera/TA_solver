# This is the model manager for link-based models
from __future__ import division
from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class

import numpy as np
import timeit
from operator import add

class OTM_Model_Manager_class(Abstract_Model_Manager_class):

    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, traffic_model_name, gateway, sim_dt, instantaneous = False):
        Abstract_Model_Manager_class.__init__(self, configfile, traffic_model_name, sim_dt, gateway)

        self.run_complete = False
        self.sample_dt = np.NaN
        self.num_samp = np.NaN
        self.instantaneous = instantaneous

    def set_instantaneous(self, flag):
        self.instantaneous = flag

    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    # If instantaneous bool is true, indicates model return instantaneous travel time rather than predicted
    def evaluate(self, demand_assignment, time_horizon, initial_state=None, request_link_data=False):

        start_time = 0.0
        self.sample_dt = float(demand_assignment.get_dt())
        self.num_samp = demand_assignment.get_num_time_step()

        # reset the simulation
        self.reset()

        # request path travel time output
        for path_id in demand_assignment.get_path_list():
            self.otm_api.request_path_travel_time(path_id, self.sample_dt)

        # request link vehicles output
        if request_link_data:
            for comm_id in demand_assignment.get_commodity_list():
                paths = demand_assignment.get_paths_for_commodity(comm_id)
                for path_id, path_links in paths.iteritems():
                    java_path_array = self.gateway.jvm.java.util.ArrayList()
                    for p in path_links:
                        java_path_array.add(long(p))
                    self.otm_api.request_links_veh(comm_id, java_path_array, self.sample_dt)

        # send demand assignment to beats
        for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
            path_id = path_comm[0]
            comm_id = path_comm[1]
            java_array = self.gateway.jvm.java.util.ArrayList()
            for d in demand_list:
                java_array.add(float(d))
            self.otm_api.set_demand_on_path_in_vph(path_id, comm_id, start_time, self.sample_dt, java_array)

        # run OTM
        self.otm_api.set_random_seed(1)      #Initialize the random seed
        self.otm_api.run(float(start_time), float(time_horizon))
        self.run_complete = True

        # extract the path costs
        path_costs = Path_Costs_class(self.num_samp, self.sample_dt)
        path_costs.set_path_list(demand_assignment.get_path_list())
        path_costs.set_comm_list(demand_assignment.get_commodity_list())
        keys = demand_assignment.get_all_demands().keys()

        for data_obj in self.otm_api.get_output_data():
            java_class = str(data_obj.getClass())
            if java_class=='class output.PathTravelTimeWriter':
                if self.instantaneous:
                    cost_list = list(
                        data_obj.compute_instantaneous_travel_times(start_time, self.sample_dt, self.num_samp))
                else:
                    # Error returns nan's for now
                    # cost_list = list(data_obj.compute_predictive_travel_times(start_time, self.sample_dt, self.num_samp))
                    cost_list = list(data_obj.get_travel_times_sec())
                    del cost_list[0]
                # path_costs.set_costs_path_commodity(data_obj.get_path_id(), data_obj.get_commodity_id(), cost_list)
                path_costs.set_costs_path_keys(data_obj.get_subnetwork_id(), keys, cost_list)

        return path_costs

    def reset(self):
        self.otm_api.clear_output_requests()
        self.otm_api.clear_all_demands()
        self.run_complete = False

    def get_state_trajectory(self):

        if not self.run_complete:
            print('Please run the simulation first.')
            return None

        link_list = self.otm_api.get_link_ids()
        state_traj = {link_id: np.zeros(self.num_samp) for link_id in link_list}

        for data_obj in self.otm_api.get_output_data():
            java_class = str(data_obj.getClass())
            if java_class=='class output.LinkVehicles':
                for link_id in data_obj.get_link_ids():
                    profile = data_obj.get_profile_for_linkid(link_id)
                    vehs = list(profile.get_values())
                    state_traj[link_id] = map(add, state_traj[link_id], vehs[:-1])

        return state_traj