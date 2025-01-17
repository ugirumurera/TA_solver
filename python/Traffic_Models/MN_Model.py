#Static Traffic Model, assuming the demand is fixed

from __future__ import division
from Traffic_Models.Abstract_Traffic_Model import Abstract_Traffic_Model_class
from Data_Types.State_Trajectory_Class import State_Trajectory_class
from Traffic_States.MN_Traffic_State import MN_Traffic_State_class
import numpy as np

class MN_Model_Class(Abstract_Traffic_Model_class):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, beats_api, gateway):
        self.gateway = gateway
        self.model_type = 'mn'     #Indicates that this is a static model
        Abstract_Traffic_Model_class.__init__(self, beats_api)

    # def Validate_Configfile(self):
    #     # If the configfile indicates varying demand, return with an error
    #     # We first want to check the configfile to make sure it is in correct format
    #     demand_array = self.beats_api.get_demands()
    #     valid = True
    #     i = 0 # index in the demand_array matrix
    #     while i < demand_array.__len__() and valid:
    #         if demand_array[i].getProfile().num_values() > 1:
    #             return False
    #         i = i + 1
    #     return True

    # Overides the Run_Model function in the abstract class
    # Returns an array of link states where each entry indicates the flow per link, per commodity and per time step
    def Run_Model(self, demand_assignment, initial_state=None, time_horizon=None,Vectorize = None):
        start_time = 0.0
        #comm_id = 1L
        comm_list = demand_assignment.get_commodity_list()
        path_cost_dt = float(demand_assignment.get_dt())
        demand_dt = float(demand_assignment.get_dt())

        api = self.beats_api

        # Clear the path requests .............
        api.clear_output_requests()

        # request link veh output ..............
        java_array = self.gateway.jvm.java.util.ArrayList()
        for d in demand_assignment.get_list_of_links():
            java_array.add(d)

        #request flow on links for all commodities
        for comm_id in comm_list:
            api.request_links_flow(comm_id, java_array, path_cost_dt)

        # clear demands in beats ................
        api.clear_all_demands()

        # # send demand assignment to beats ............
        for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
            path_id = path_comm[0]
            comm_id = path_comm[1]
            java_array = self.gateway.jvm.java.util.ArrayList()
            for d in demand_list:
                java_array.add(float(d))

            api.set_demand_on_path_in_vph(path_id, comm_id, start_time, demand_dt, java_array)

        # run BeATS .................
        # api.set_random_seed(1)
        api.run(float(start_time), float(time_horizon))

        # cycle through beats outputs
        sampling_dt = demand_assignment.get_dt()
        num_steps = int(time_horizon/sampling_dt)

        # We do this when vectorize it true, that we want to vectorize BPR
        if Vectorize:
            list_of_link_ids = self.beats_api.get_link_ids()
            num_steps = demand_assignment.get_num_time_step()

            # create a matrix to hold the states of all the links for num_steps
            link_states = np.zeros((len(list_of_link_ids), num_steps))

            for output in api.get_output_data():
                for link_id in output.get_link_ids():
                    #link_states.add_linkId(link_id)
                    capacity_vph = self.beats_api.get_link_with_id(link_id).get_capacity_vps()*3600
                    #volume = output.get_profile_for_linkid(link_id)

                    #To be added once we have needed function
                    #link_states[link_id,:] = flow_per_link
                    #flow_per_link = np.divide(volume,capacity_vph)
                    for i in range(num_steps):
                        link_states[link_id,i] = output.get_flow_vph_for_linkid_timestep(link_id,i)/capacity_vph

        else:

            link_states = State_Trajectory_class(list([]),
                                             list(self.beats_api.get_commodity_ids()), num_steps, sampling_dt)

            for output in api.get_output_data():
                for link_id in output.get_link_ids():
                    link_states.add_linkId(link_id)
                    comm = output.get_commodity_id()
                    capacity_vph = self.beats_api.get_link_with_id(link_id).get_capacity_vps()*3600

                    for i in range(num_steps):
                        state = MN_Traffic_State_class()
                        volume = output.get_flow_vph_for_linkid_timestep(link_id,i)
                        state.set_state_parameters(volume, capacity_vph)
                        link_states.set_state_on_link_comm_time(link_id, comm, i, state)

            #print "\n"
            #link_states.print_all()

        return link_states

    def get_total_demand(self):
        demands = self.beats_api.get_demands()
        total_demand = 0

        for demand in demands:
            total_demand = total_demand + demand.getProfile().get_value(0)*3600

        return total_demand