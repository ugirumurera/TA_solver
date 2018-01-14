#Static Traffic Model, assuming the demand is fixed

from __future__ import division
from Abstract_Traffic_Model import Abstract_Traffic_Model_class
from Data_Types.State_Trajectory_Class import State_Trajectory_class
from Traffic_States.Static_Traffic_State import Static_Traffic_State_class
import numpy as np


class Static_Model_Class(Abstract_Traffic_Model_class):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, beats_api):
        Abstract_Traffic_Model_class.__init__(self, beats_api)
        self.model_type = 'static'     #Indicates that this is a static model

        if not self.Validate_Configfile():
            self.beats_api = None
            return

    def Validate_Configfile(self):
        '''
        # If the configfile indicates varying demand, return with an error
        # We first want to check the configfile to make sure it is in correct format
        demand_array = self.beats_api.get_demands()
        valid = True
        i = 0 # index in the demand_arrary matrix
        while i < demand_array.__len__() and valid:
            if demand_array[i].getProfile().num_values() > 1:
                return False
            i = i + 1
        '''
        return True

    # Overides the Run_Model function in the abstract class
    # Returns an array of link states where each entry indicates the flow per link, per commodity and per time step
    def Run_Model(self, demand_assignments, initial_state = None,T = None, Vectorize = False):
        if Vectorize:
            list_of_link_ids = self.beats_api.get_link_ids()
            num_steps = demand_assignments.get_num_time_step()

            # create a matrix of to hold the states of all the links for num_steps
            link_states = np.zeros((len(list_of_link_ids), num_steps))

            for key in demand_assignments.get_all_demands().keys():
                path = list(demand_assignments.get_path_with_id(key[0]))

                # Get the capacity of links in path
                capacities = [self.beats_api.get_link_with_id(link_id).get_capacity_vps() * 3600 for link_id in path]

                # Get indices of links in the path
                # link_indices = [list_of_link_ids.index(l) for l in path]
                demand = demand_assignments.get_all_demands_on_path_comm(key[0], key[1])
                demand = np.reshape(demand, (1, len(demand)))
                inverse_cap = np.divide(np.ones((len(path), 1)), np.asarray(capacities).reshape((len(path), 1)))
                demand_to_add = np.matmul(inverse_cap, demand)
                link_states[path, :] = np.add(link_states[path, :], demand_to_add)
        else:
            # Initialize the State_Trajectory object
            sampling_dt = demand_assignments.get_dt()
            num_steps = int(T/sampling_dt)
            link_states = State_Trajectory_class( list([]),
                                                 list(self.beats_api.get_commodity_ids()), num_steps, sampling_dt)

            #demand_assignments.print_all()

            for key in demand_assignments.get_all_demands().keys():
                route = demand_assignments.get_path_list()[key[0]]
                for link_id in route:
                    not_seen = link_states.add_linkId(link_id)
                    #We initialize a list on num_steps none objects to hold the link states
                    if not_seen:
                        lst_objects =  [None] * num_steps
                        link_states.initialize_states(link_id, key[1], lst_objects)

                    for i in range(num_steps):

                        if link_states.get_state_on_link_comm_time(link_id, key[1], i) is None:
                            state = Static_Traffic_State_class()
                            link_states.set_state_on_link_comm_time(link_id, key[1], i, state)
                            capacity = self.beats_api.get_link_with_id(link_id).get_capacity_vps() * 3600
                            state.set_capacity(capacity)

                        capacity = self.beats_api.get_link_with_id(link_id).get_capacity_vps() * 3600
                        demand_value = demand_assignments.get_demand_at_path_comm_time(key[0], key[1], i)
                        #Devide volume by capacity to get the flow
                        flow = demand_value/capacity
                        link_states.get_state_on_link_comm_time(link_id, key[1], i).add_flow(flow)


            #link_states.print_all()



        return link_states

    def mod_Run_Model(self,demand_assignments, T = None, initial_state = None):
        list_of_link_ids = self.beats_api.get_link_ids()
        num_steps = demand_assignments.get_num_time_step()

        #create a matrix of to hold the states of all the links for num_steps
        link_states = np.zeros((len(list_of_link_ids),num_steps))

        for key in demand_assignments.get_all_demands().keys():
            path = list(demand_assignments.get_path_with_id(key[0]))

            #Get the capacity of links in path
            capacities = [self.beats_api.get_link_with_id(link_id).get_capacity_vps() * 3600 for link_id in path]

            # Get indices of links in the path
            #link_indices = [list_of_link_ids.index(l) for l in path]
            demand = demand_assignments.get_all_demands_on_path_comm(key[0],key[1])
            demand = np.reshape(demand,(1,len(demand)))
            inverse_cap = np.divide(np.ones((len(path),1)),np.asarray(capacities).reshape((len(path),1)))
            demand_to_add = np.matmul(inverse_cap,demand)
            link_states[path,:] = np.add(link_states[path,:],demand_to_add)

        return link_states

    def get_total_demand(self):
        demands = self.beats_api.get_demands()
        total_demand = 0

        for demand in demands:
            total_demand = total_demand + demand.getProfile().get_value(0)*3600

        return total_demand