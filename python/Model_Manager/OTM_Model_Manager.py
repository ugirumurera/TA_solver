# This is the model manager for link-based models
from __future__ import division
from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class
from multiprocessing import Pool
from functools import partial
from contextlib import closing

import numpy as np
import timeit
from operator import add


# def set_costs(self, data_obj, comm_id=long(0), start_time=0.0):
#     java_class = str(data_obj.getClass())
#     if java_class == 'class output.PathTravelTimeWriter':
#         if self.instantaneous:
#             cost_list = list(
#                 data_obj.compute_instantaneous_travel_times(start_time, self.sample_dt, self.num_samp))
#         else:
#             # Error returns nan's for now
#             # cost_list = list(data_obj.compute_predictive_travel_times(start_time, self.sample_dt, self.num_samp))
#             cost_list = list(data_obj.get_travel_times_sec())
#             del cost_list[0]
#         # path_costs.set_costs_path_commodity(data_obj.get_path_id(), data_obj.get_commodity_id(), cost_list)
#         # if len(comm_list) == 1:
#         #     path_costs.set_costs_path_commodity(data_obj.get_subnetwork_id(), comm_list[0], cost_list)
#         # else:
#         #     path_costs.set_costs_path_keys(data_obj.get_subnetwork_id(), keys, cost_list)
#     {(data_obj.get_subnetwork_id(), comm_id), np.asarray(cost_list)}

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

    def set_demand(self, path_comm, demand_list, start_time = 0.0):
        path_id = path_comm[0]
        comm_id = path_comm[1]
        java_array = self.gateway.jvm.java.util.ArrayList()
        for d in demand_list:
            java_array.add(float(d))
        self.otm_api.set_demand_on_path_in_vph(path_id, comm_id, start_time, self.sample_dt, java_array)


    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    # If instantaneous bool is true, indicates model return instantaneous travel time rather than predicted
    def evaluate(self, demand_assignment, time_horizon, initial_state=None, request_link_data=False):


        # for i in range(num_links):
        #     link_info = model_manager.otm_api.get_link_with_id(long(i))
        #     fft = (link_info.getFull_length() / 1000
        #            / link_info.get_ffspeed_kph())
        #     coefficients[long(i)] = np.zeros(num_coeff)
        #     coefficients[i][0] = copy(fft)
        #     coefficients[i][4] = copy(fft * 0.15)


        start_time = 0.0
        self.sample_dt = float(demand_assignment.get_dt())
        self.num_samp = demand_assignment.get_num_time_step()
        comm_list = demand_assignment.get_commodity_list()

        # Initialize the path cost object
        path_costs = Path_Costs_class(self.num_samp, self.sample_dt)
        path_costs.set_path_list(demand_assignment.get_path_list())
        path_costs.set_comm_list(demand_assignment.get_commodity_list())
        keys = demand_assignment.get_all_demands().keys()

        if not np.any(demand_assignment.get_all_demands().values()):
            # if the demand is zero, we return the free flow travel time per path
            for path_id, path_list in demand_assignment.get_path_list().iteritems():
                link_list = [ self.otm_api.scenario().get_link_with_id(long(link_id)) for link_id in path_list]
                cost_list = np.ones(self.num_samp)*sum([(link_info.getFull_length() / 1000/
                                                         link_info.get_ffspeed_kph()) for link_info in link_list])
                path_costs.set_costs_path_commodity(path_id, comm_list[0], cost_list)
        else:
            # reset the simulation
            self.reset()

            # request path travel time output
            # with Pool(4) as p:
            #     print(p.map(f, [1, 2, 3]))
            #     p.map(self.otm_api.request_path_travel_time,)
            #results = pool.map(partial(merge_names, b='Sons'), names)
            #
            # with Pool(4) as p:
            #     p.map(partial(self.otm_api.request_path_travel_time,self.sample_dt),demand_assignment.get_path_list())
            for path_id in demand_assignment.get_path_list():
                self.otm_api.output().request_path_travel_time(path_id, self.sample_dt)

            # request link vehicles output
            if request_link_data:
                for comm_id in demand_assignment.get_commodity_list():
                    paths = demand_assignment.get_paths_for_commodity(comm_id)
                    for path_id, path_links in paths.iteritems():
                        java_path_array = self.gateway.jvm.java.util.ArrayList()
                        for p in path_links:
                            java_path_array.add(long(p))
                        self.otm_api.request_links_veh(comm_id, java_path_array, self.sample_dt)

            start_time1 = timeit.default_timer()
            # send demand assignment to otm
            for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
                path_id = path_comm[0]
                comm_id = path_comm[1]
                java_array = self.gateway.jvm.java.util.ArrayList()
                for d in demand_list:
                    java_array.add(float(d))
                self.otm_api.scenario().set_demand_on_path_in_vph(path_id, comm_id, start_time, self.sample_dt, java_array)

            elapsed1 = timeit.default_timer() - start_time1
            print "request took : ", elapsed1

            start_time1 = timeit.default_timer()
            # run OTM
            self.otm_api.set_random_seed(1)      #Initialize the random seed
            self.otm_api.run(float(start_time), float(time_horizon))
            self.run_complete = True
            elapsed1 = timeit.default_timer() - start_time1
            print "just sim took : ", elapsed1


            # extract the path costs

            start_time1 = timeit.default_timer()

            for data_obj in self.otm_api.output().get_data():
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

                    if len(comm_list) == 1: path_costs.set_costs_path_commodity(data_obj.get_subnetwork_id(),comm_list[0],cost_list)
                    else: path_costs.set_costs_path_keys(data_obj.get_subnetwork_id(), keys, cost_list)

            elapsed1 = timeit.default_timer() - start_time1
            # print "assignment took : ", elapsed1

        return path_costs

    def reset(self):
        #This two lines are for previous java 8 otm-sim
        # self.otm_api.clear_output_requests()
        # self.otm_api.clear_all_demands()
        self.otm_api.output().clear()
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